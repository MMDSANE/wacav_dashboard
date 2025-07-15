import time, json
from django.core.cache import cache
from django.http import JsonResponse
import logging
from core.constraints import *

# Middleware ای برای کنترل و محدود کردن تعداد درخواست‌ها از کاربران مشخص در کل پروژه.
#
# هدف اصلی:
# - جلوگیری از حملات DDoS و اسپم با محدود کردن تعداد درخواست‌ها در بازه‌های زمانی مشخص.
# - هر کاربر در یک دوره زمانی مشخص (مثلاً 30 دقیقه) روی هر URL جداگانه حداکثر تعداد مشخصی درخواست می‌تواند بفرستد.
#
# نحوه عملکرد:
# 1. شناسایی کاربر از طریق user_key (کاربر احراز هویت شده، شماره تلفن، یا X-User-Key)
# 2. برای هر ترکیب (user_key + URL)، یک شمارنده جداگانه در کش نگه داشته می‌شود
# 3. اگر تعداد درخواست‌ها از حد مجاز (مثلاً 100) تجاوز کرد، کاربر تا پایان دوره زمانی بلاک می‌شود
# 4. در شروع دوره جدید، شمارنده‌ها ریست می‌شوند
#
# مثال:
# - کاربر A می‌تواند در 30 دقیقه روی /api/users/ حداکثر 100 درخواست بفرستد
# - همزمان همین کاربر A می‌تواند روی /api/products/ هم 100 درخواست بفرستد
# - اگر کاربر A به حد 100 درخواست در /api/users/ رسید، فقط از /api/users/ بلاک می‌شود
# - بعد از پایان 30 دقیقه، شمارنده‌ها ریست شده و کاربر دوباره می‌تواند درخواست بفرستد

logger = logging.getLogger(__name__)


class RateLimiterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.user_limit_per_url = USER_LIMIT_PER_URL  # مثلاً 100 درخواست
        self.time_window_seconds = TIME_WINDOW_SECONDS  # مثلاً 30 دقیقه = 1800 ثانیه

    def __call__(self, request):
        path = request.path
        user_key = self.get_user_key(request)

        # اگر user_key موجود نیست، از IP استفاده می‌کنیم
        if not user_key:
            user_key = f"ip_{self.get_client_ip(request)}"

        # بررسی محدودیت برای این کاربر روی این URL
        if not self.check_user_url_limit(user_key, path):
            logger.warning(f"User {user_key} blocked on path {path} due to too many requests")
            return JsonResponse(
                {
                    "error": "Too many requests on this URL. Please try again later.",
                    "retry_after_seconds": self.time_window_seconds
                },
                status=429
            )

        # اگر همه چیز اوکی بود، درخواست به view بعدی برود
        return self.get_response(request)

    def get_client_ip(self, request):
        """استخراج IP واقعی کاربر"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def get_user_key(self, request):
        """استخراج شناسه منحصر به فرد کاربر"""

        # اگر کاربر وارد شده باشد
        if request.user.is_authenticated:
            return f"authenticated_user_{request.user.id}"

        # اگر درخواست POST باشد و مسیر برای ارسال OTP باشد
        if request.method == 'POST' and request.path.startswith('/api/auth/send_otp'):
            try:
                data = json.loads(request.body)
                phone = data.get('phone_number')
                if phone:
                    return f"unauthenticated_phone_{phone}"
            except Exception as e:
                logger.warning(f"Failed to extract phone_number: {e}")

        # تلاش برای گرفتن کلید کاربر از هدر X-User-Key
        return request.headers.get('X-User-Key')

    def check_user_url_limit(self, user_key, path):
        """
        بررسی محدودیت تعداد درخواست برای کاربر روی URL مشخص

        Args:
            user_key: شناسه کاربر
            path: مسیر URL

        Returns:
            bool: True اگر اجازه دارد، False اگر محدودیت رسیده
        """
        # کلید کش برای این ترکیب کاربر + URL
        cache_key = f"user_url_limit_{user_key}_{path}"

        # گرفتن تعداد درخواست‌های فعلی
        current_count = cache.get(cache_key, 0)

        # اگر به حد مجاز رسیده
        if current_count >= self.user_limit_per_url:
            return False

        # افزایش شمارنده
        if current_count == 0:
            # اولین درخواست - تنظیم شمارنده با timeout
            cache.set(cache_key, 1, timeout=self.time_window_seconds)
        else:
            # افزایش شمارنده موجود
            try:
                cache.incr(cache_key)
            except ValueError:
                # اگر کلید منقضی شده بود، دوباره تنظیم کن
                cache.set(cache_key, 1, timeout=self.time_window_seconds)

        return True

    def get_remaining_time(self, user_key, path):
        """
        محاسبه زمان باقی‌مانده تا پایان محدودیت

        Args:
            user_key: شناسه کاربر
            path: مسیر URL

        Returns:
            int: تعداد ثانیه‌های باقی‌مانده
        """
        cache_key = f"user_url_limit_{user_key}_{path}"

        # Django cache متد TTL ندارد، پس نمی‌تونیم دقیقاً بدونیم
        # بهتره از cache backend که TTL رو ساپورت می‌کنه استفاده کنیم
        # یا این که خودمون timestamp رو نگه داریم

        # برای حالا، time_window_seconds رو برمی‌گردونیم
        return self.time_window_seconds

    def get_user_stats(self, user_key, path):
        """
        گرفتن آمار استفاده کاربر از یک URL

        Args:
            user_key: شناسه کاربر
            path: مسیر URL

        Returns:
            dict: آمار شامل current_count و limit
        """
        cache_key = f"user_url_limit_{user_key}_{path}"
        current_count = cache.get(cache_key, 0)

        return {
            'current_count': current_count,
            'limit': self.user_limit_per_url,
            'remaining': max(0, self.user_limit_per_url - current_count),
            'time_window_seconds': self.time_window_seconds
        }