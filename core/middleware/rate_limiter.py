import time, json
from django.core.cache import cache
from django.http import JsonResponse
import logging
from core.constraints import *


    # Middleware ای برای کنترل و محدود کردن تعداد درخواست‌ها از یک IP و کاربر مشخص در کل پروژه.
    #
    # هدف اصلی:
    # - جلوگیری از حملات DOS و اسپم با محدود کردن تعداد درخواست‌ها در بازه‌های زمانی مشخص.
    # - ایجاد وقفه زمانی بین درخواست‌های مکرر از یک کاربر (مثلاً شماره تلفن یا ایمیل) برای عملیات‌هایی مثل ارسال OTP یا ایمیل.
    #
    # نحوه عملکرد:
    # 1. دریافت IP واقعی کلاینت از هدرهای HTTP یا اطلاعات اتصال.
    # 2. استخراج شناسه کاربر (user_key) از هدر درخواست (مثلاً شماره تلفن یا ایمیل) که در هدر X-User-Key ارسال می‌شود.
    # 3. بررسی تعداد درخواست‌های انجام شده از هر IP در یک بازه زمانی یک ساعته:
    #     - اگر تعداد درخواست‌ها از IP بیشتر از حد مجاز (مثلاً 100) بود، درخواست رد شده و پاسخ 429 (Too Many Requests) برمی‌گردد.
    # 4. بررسی وقفه زمانی بین درخواست‌های متوالی از یک user_key:
    #     - اگر فاصله زمانی بین دو درخواست کمتر از 2 دقیقه باشد، درخواست رد شده و پیام خطا به کاربر داده می‌شود.
    #     - در غیر اینصورت، زمان آخرین درخواست ذخیره شده و اجازه ادامه داده می‌شود.
    #
    # دلایل استفاده از این روش:
    # - بهبود امنیت برنامه با جلوگیری از درخواست‌های مکرر و ناخواسته.
    # - کاهش فشار روی سرور و منابع با محدود کردن نرخ درخواست‌ها.
    # - جلوگیری از سوءاستفاده و اسپم از طریق IP یا شناسه‌های کاربران.
    #
    # نکات مهم:
    # - شناسه کاربر باید در هدر X-User-Key ارسال شود. در صورت نبودن این مقدار، فقط محدودیت IP اعمال می‌شود.
    # - این Middleware به کش وابسته است (مثلاً Redis یا کش داخلی جنگو) تا تعداد درخواست‌ها و زمان‌ها ذخیره شوند.
    # - این روش بسیار ساده و ابتدایی است و می‌توان آن را با ابزارهای تخصصی‌تر مانند Django Ratelimit یا سرویس‌های بیرونی بهبود داد.
    # - در پروژه‌های پراستفاده، پیشنهاد می‌شود استفاده از راهکارهای پیشرفته‌تر و یا سرویس‌های Rate Limiting اختصاصی.
    #
    # نحوه فعال‌سازی:
    # - کافی است این کلاس را به تنظیمات MIDDLEWARE اضافه کنید.
    # - به تمام درخواست‌های ورودی اعمال شده و به صورت خودکار کنترل می‌کند.
    #
    # مثال ارسال درخواست با شناسه کاربر:
    #     curl -H "X-User-Key: user@example.com" http://yourdomain.com/api/...
    #
    # با این پیاده‌سازی، امنیت و پایداری پروژه شما در برابر درخواست‌های بیش‌ازحد تضمین می‌شود.

logger = logging.getLogger(__name__)

class RateLimiterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.per_user_cooldown = USER_LIMIT_COOLDOWN  # مثلاً ۲ دقیقه بین دو درخواست از یک کاربر
        self.ip_limit = IP_LIMIT  # مثلاً ۱۵۰ درخواست
        self.ip_window_seconds = IP_WINDOW_SECONDS  # مثلاً یک ساعت

    def __call__(self, request):
        ip = self.get_client_ip(request)       # گرفتن IP کلاینت
        path = request.path                    # مسیر URL فعلی (برای تفکیک محدودیت روی هر URL)
        user_key = self.get_user_key(request)  # استخراج شناسه‌ی کاربر (ID یا شماره تلفن یا X-User-Key)

        # محدودیت تعداد درخواست برای این IP در این مسیر خاص
        if not self.check_ip_limit(ip, path):
            logger.warning(f"IP {ip} blocked on path {path} due to too many requests")
            return JsonResponse(
                {"error": "Too many requests from this IP on this URL. Please try again later."},
                status=429
            )

        # محدودیت زمان‌بندی بین درخواست‌های کاربر (فقط اگر user_key موجود باشد)
        if user_key:
            allowed, wait = self.check_user_cooldown(user_key)
            if not allowed:
                return JsonResponse(
                    {"error": f"Please wait {wait} seconds before making another request."},
                    status=429
                )

        # در نهایت اگر همه چیز اوکی بود، درخواست به view بعدی برود
        return self.get_response(request)


    def get_client_ip(self, request):
        # تلاش برای گرفتن IP واقعی کاربر از هدر X-Forwarded-For
        # (مواقعی که پروژه پشت پروکسی یا Load Balancer است)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # اگر چند IP وجود داشت (چند پروکسی)، اولین IP معمولاً IP کلاینت واقعی است
            return x_forwarded_for.split(',')[0].strip()
        # در غیر این صورت، IP مستقیم از اتصال شبکه گرفته می‌شود
        return request.META.get('REMOTE_ADDR')

    def get_user_key(self, request):
        # اگر کاربر وارد شده (احراز هویت شده) باشد،
        # از ID کاربر به عنوان کلید استفاده می‌کنیم
        if request.user.is_authenticated:
            return f"authenticated_user_{request.user.id}"

        # اگر درخواست POST باشد و مسیر برای ارسال OTP باشد:
        if request.method == 'POST' and request.path.startswith('/api/auth/send_otp'):
            try:
                # پارس کردن بدنه‌ی JSON درخواست برای گرفتن شماره تلفن
                data = json.loads(request.body)
                phone = data.get('phone_number')
                if phone:
                    # ساخت کلید اختصاصی بر اساس شماره تلفن
                    return f"unauthenticated_phone_{phone}"
            except Exception as e:
                # اگر مشکلی در پارس کردن پیش آمد، در لاگ ثبت شود ولی درخواست قطع نشود
                logger.warning(f"Failed to extract phone_number: {e}")

        # در غیر این صورت، تلاش برای گرفتن کلید کاربر از هدر X-User-Key
        return request.headers.get('X-User-Key') or None

    def check_user_cooldown(self, user_key):
        # کلید کش مخصوص این کاربر برای نگه داشتن زمان آخرین درخواست
        cache_key = f"user_cooldown_{user_key}"

        # گرفتن زمان آخرین درخواست این کاربر از کش
        last_time = cache.get(cache_key)

        if last_time:
            # محاسبه مدت زمانی که از آخرین درخواست گذشته
            elapsed = time.time() - last_time

            # اگر این مدت زمان کمتر از محدوده‌ی تعیین‌شده (مثلاً 2 دقیقه) باشد:
            if elapsed < self.per_user_cooldown:
                # اجازه نده و تعداد ثانیه‌های باقی‌مانده تا پایان محدودیت را برگردان
                return False, int(self.per_user_cooldown - elapsed)

        # در غیر این صورت (اولین درخواست یا بعد از اتمام محدودیت):
        # زمان فعلی را به‌عنوان آخرین درخواست ذخیره کن
        cache.set(cache_key, time.time(), timeout=self.per_user_cooldown)

        # اجازه بده درخواست انجام بشه
        return True, 0

    def check_ip_limit(self, ip, path):
        # ساختن کلید کش بر اساس IP و مسیر URL برای اعمال محدودیت جداگانه روی هر مسیر
        cache_key = f"ip_counter_{ip}_{path}"

        # گرفتن تعداد درخواست‌های ارسال‌شده از این IP برای این مسیر
        count = cache.get(cache_key, 0)

        # اگر تعداد درخواست‌ها به حد مجاز رسیده باشد، درخواست رد شود
        if count >= self.ip_limit:
            return False

        if count == 0:
            # اگر اولین درخواست باشد، شمارنده را روی ۱ تنظیم و تایم‌اوت را برای پنجره زمانی (مثلاً یک ساعت) مشخص کن
            cache.set(cache_key, 1, timeout=self.ip_window_seconds)
        else:
            # در غیر این صورت شمارنده را یکی افزایش بده
            cache.incr(cache_key)

        # اگر محدودیت نرسیده، اجازه بده درخواست ادامه پیدا کند
        return True
