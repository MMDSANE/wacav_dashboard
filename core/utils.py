import random, string, json, re, secrets, requests, logging, uuid
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from django.core.cache import cache
from .constraints import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from html2text import html2text
from core.middleware.rate_limiter import RateLimiterMiddleware
from django.conf import settings
from typing import Tuple, Optional, List, Dict, Union
import traceback  # برای گرفتن stack trace خطاها
import inspect  # برای گرفتن اطلاعات ماژول و کلاس
from django.utils.timezone import now  # برای گرفتن زمان با تنظیمات Django
from core.models import LogEntry  # مدل LogEntry برای ذخیره لاگ در دیتابیس



def generate_random_code(length=8, chars=string.ascii_uppercase + string.digits) -> str:
    """
    یک رشته تصادفی با طول مشخص تولید می‌کند. می‌تواند برای کدهای تخفیف، کدهای ارجاع و غیره استفاده شود.
    """
    return ''.join(random.choice(chars) for _ in range(length))

def is_today_birthday(birth_date: date) -> bool:
    """
    بررسی می‌کند که آیا تاریخ امروز با ماه و روز تاریخ تولد داده شده مطابقت دارد یا خیر.
برای کمپین‌های تولد مفید است.
    """
    if not birth_date:
        return False
    today = date.today()
    return birth_date.month == today.month and birth_date.day == today.day


def parse_date_string(date_str: str, format_str: str = '%Y-%m-%d') -> date | None:
    """
یک رشته تاریخ را به یک شیء تاریخ تجزیه می‌کند. در صورت عدم موفقیت در تجزیه، None را برمی‌گرداند.
    """
    try:
        return datetime.strptime(date_str, format_str).date()
    except (ValueError, TypeError):
        return None


def soft_delete(obj) -> None:
    """
    انجام حذف نرم برای یک شیء مدل که از BaseModel ارث‌بری کرده است.
    وضعیت (status) شیء را به DELETED تغییر می‌دهد و آن را ذخیره می‌کند.
    """
    obj.status = obj.Status.DELETED  # Changed to DELETED
    obj.save(update_fields=['status', 'updated_at'])  # Added updated_at for consistency



def deactivate(obj) -> None:
    """
        انجام حذف نرم برای یک شیء مدل که از BaseModel ارث‌بری کرده است.
        وضعیت (status) شیء را به DEACTIVE تغییر می‌دهد و آن را ذخیره می‌کند.
    """
    obj.status = obj.Status.DEACTIVE
    obj.save(update_fields=['status', 'updated_at'])



def safe_decimal_conversion(value: any, default_value: Decimal = Decimal('0.00')) -> Decimal:
    """
    با خیال راحت یک مقدار را به اعشاری تبدیل می‌کند و ورودی‌های None یا غیر عددی را مدیریت می‌کند.
    """
    try:
        if value is None:
            return default_value
        return Decimal(str(value)) # Convert to string first to handle float precision issues
    except (TypeError, ValueError):
        return default_value


def get_today_jalali_date() -> str:
    """
    تاریخ امروز را در قالب تقویم جلالی (فارسی) برمی‌گرداند.
به یک کتابخانه تقویم فارسی نیاز دارد (مثلاً jdatetime).
اگر از jdatetime استفاده نمی‌شود، این تابع را حذف کنید.
    """
    try:
        import jdatetime
        return jdatetime.date.today().strftime('%Y/%m/%d')
    except ImportError:
        # Fallback to Gregorian if jdatetime is not installed
        return date.today().strftime('%Y-%m-%d')

def convert_to_gregorian(jalali_date_str: str, format_str: str = '%Y/%m/%d') -> date | None:
    """
    یک رشته تاریخ جلالی (فارسی) را به یک شیء تاریخ میلادی تبدیل می‌کند.
    به یک کتابخانه تقویم فارسی (مثلاً jdatetime) نیاز دارد.
    در صورت عدم موفقیت در تبدیل، None را برمی‌گرداند.
    """
    try:
        import jdatetime
        jdate = jdatetime.datetime.strptime(jalali_date_str, format_str).date()
        return jdate.togregorian()
    except (ImportError, ValueError, TypeError):
        return None


# Utility for JSON parsing (can be used in RuleEngine if JSONField is not available)
def parse_json_field(json_string: str, default: dict = None) -> dict:
    """
    یک رشته JSON را به طور ایمن به یک دیکشنری پایتون تجزیه می‌کند.
در صورت عدم موفقیت تجزیه یا خالی بودن/نبودن رشته، مقدار پیش‌فرض را برمی‌گرداند.
    """
    if default is None:
        default = {}
    if not json_string:
        return default
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        # Log this error for debugging malformed JSON in DB
        print(f"Warning: Malformed JSON string: {json_string}")
        return default


def calculate_age(birth_date: date) -> int:
    """
    محاسبه سن فعلی کاربر بر اساس تاریخ تولد.
    """
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def get_client_ip(request) -> str:
    """
    دریافت آدرس IP کلاینت از شیء request در Django.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def normalize_phone_number(phone: str) -> str:
    """
    نرمال‌سازی شماره موبایل به فرمت بین‌المللی ایران (+98).
    ورودی ممکن است با 0 یا 0098 یا +98 شروع شده باشد.
    خروجی همیشه با +98 شروع می‌شود.
    """
    # فقط ارقام را نگه دار
    digits = re.sub(r'\D', '', phone)

    if digits.startswith('0098'):
        digits = digits[4:]
    elif digits.startswith('098'):
        digits = digits[3:]
    elif digits.startswith('98'):
        digits = digits[2:]
    elif digits.startswith('0'):
        digits = digits[1:]
    else:
        raise ValueError('فرمت تلفن وارد شده نامعتبر است')

    return f'+98{digits}' if digits else ''


def days_since_last_login(user) -> int:
    """
    تعداد روزهایی که از آخرین ورود کاربر گذشته را محاسبه می‌کند.
    اگر کاربر هیچ‌وقت وارد نشده باشد، مقدار -1 برمی‌گرداند.
    """
    if not user.last_login:
        return -1
    delta = datetime.now() - user.last_login
    return delta.days



def get_loyalty_level(points: Union[int, float, Decimal], levels: List[Dict[str, Union[str, int, float, Decimal]]]) -> str:
    """
    تعیین سطح وفاداری مشتری بر اساس امتیاز و لیست سطح‌ها.

    levels باید لیستی از دیکشنری‌ها به شکل زیر باشد:
        [
            {"name": "برنزی", "min_points": 0},
            {"name": "نقره‌ای", "min_points": 1000},
            {"name": "طلایی", "min_points": 5000},
            {"name": "الماسی", "min_points": 10000},
        ]

    min_points می‌تواند عدد صحیح، float یا Decimal باشد.
    """

    try:
        points_decimal = Decimal(points)
    except (InvalidOperation, TypeError, ValueError):
        return "نامعتبر"

    if points_decimal < 0:
        return "نامعتبر"

    # مرتب‌سازی لیست سطوح بر اساس min_points به صورت Decimal
    sorted_levels = sorted(
        levels,
        key=lambda x: Decimal(x.get("min_points", 0))
    )

    result = "نامشخص"
    for level in sorted_levels:
        try:
            min_points = Decimal(level.get("min_points", 0))
        except (InvalidOperation, TypeError, ValueError):
            continue

        name = level.get("name", "نامشخص")

        if points_decimal >= min_points:
            result = name
        else:
            break

    return result



# تابع تولید رمز عبور تصادفی قوی
def generate_strong_password(length: int = 16) -> str:
    """
    تولید پسورد قوی با ترکیب:
    - حداقل یک حرف بزرگ
    - حداقل یک حرف کوچک
    - حداقل یک عدد
    - حداقل یک کاراکتر ویژه
    از ماژول امن `secrets` برای تولید رمز استفاده شده.
    """
    if length < 12:
        raise ValueError("طول پسورد باید حداقل 12 کاراکتر باشد")

    alphabet = {
        'upper': string.ascii_uppercase,
        'lower': string.ascii_lowercase,
        'digits': string.digits,
        'special': "!@#$%^&*()-_=+[]{}|;:,.<>?/~"
    }

    password_chars = [
        secrets.choice(alphabet['upper']),
        secrets.choice(alphabet['lower']),
        secrets.choice(alphabet['digits']),
        secrets.choice(alphabet['special']),
    ]

    all_chars = ''.join(alphabet.values())
    password_chars += [secrets.choice(all_chars) for _ in range(length - 4)]

    secrets.SystemRandom().shuffle(password_chars)

    return ''.join(password_chars)


# تابع تولید کد OTP عددی
def generate_numeric_otp(length: int = OTP_LENGTH) -> str:
    """
    تولید کد OTP عددی با استفاده از ماژول امن `secrets`.
    طول پیش‌فرض 6 رقم است، اما قابل تنظیم است.
    """
    if length <= 0:
        raise ValueError("طول OTP باید عددی مثبت باشد")

    digits = string.digits
    first_digit = secrets.choice('123456789')  # عدد اول ≠ ۰
    remaining_digits = ''.join(secrets.choice(digits) for _ in range(length - 1))

    return first_digit + remaining_digits

#### برای لاگ گرفتن در دو تابع بعدی استفاده می‌گردد ##
logger = logging.getLogger('app_logger')  # لاگر عمومی
#---------------------------------------------------

# ذخیره سازی OTP در کش
def store_otp(identifier: str, otp: str, ttl: int = OTP_EXPIRATION_SECONDS) -> None:
    """
یک رمز یکبار مصرف (OTP) را برای یک شناسه مشخص (شماره تلفن یا ایمیل) در حافظه پنهان ذخیره می‌کند.

    Args:
    شناسه (str): شماره تلفن یا ایمیلی که قرار است به رمز یکبار مصرف (OTP) مرتبط شود.
    otp (str): رمز عبور یکبار مصرف برای ذخیره.
    ttl (int، اختیاری): زمان باقی مانده برای رمز یکبار مصرف (OTP) بر حسب ثانیه. مقدار پیش‌فرض OTP_TTL است.
    """
    cache.set(identifier, otp, timeout=ttl)
    logger.debug(f"OTP stored: key={identifier}, value={otp}, ttl={ttl}")



# دریافت OTP از کش برای ورود موفق کاربر در دفعات بعدی
def retrieve_otp(identifier: str) -> str | None:
    """
    بازیابی کد OTP ذخیره‌شده برای یک شناسه (شماره تلفن یا ایمیل).

    Args:
        identifier (str): شماره تلفن یا ایمیل کاربر

    Returns:
        str | None: کد OTP یا None اگر موجود نبود
    """
    otp = cache.get(identifier)
    logger.debug(f"OTP retrieved for key='{identifier}': {otp}")
    return otp


# استان ها و شهر‌ها
def provinces_cities():
    pass

# # پنل پیامکی تست
# def send_pattern_sms(
#     api_key: str,
#     pattern_code: str,
#     sender: str,
#     recipient: str,
#     variables: dict
# ) -> dict:
#     """
#     ارسال پیامک از طریق IPPanel با استفاده از پترن آماده.
#
#     :param api_key: کلید API از پنل IPPanel
#     :param pattern_code: کد الگوی پیامک (Pattern Code)
#     :param sender: شماره فرستنده (مثلاً: +983000505)
#     :param recipient: شماره گیرنده (مثلاً: 09121234567)
#     :param variables: دیکشنری شامل متغیرهای مورد استفاده در پیام
#     :return: دیکشنری شامل پاسخ سرور (status, code, message و ...)
#     """
#     url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"
#
#     payload = {
#         "code": pattern_code,
#         "sender": sender,
#         "recipient": recipient,
#         "variable": variables
#     }
#
#     headers = {
#         "apikey": api_key,
#         "Content-Type": "application/json"
#     }
#
#     try:
#         response = requests.post(url, headers=headers, data=json.dumps(payload))
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.HTTPError as e:
#         return {"status": "error", "message": f"HTTP error: {e}"}
#     except Exception as e:
#         return {"status": "error", "message": f"Unexpected error: {e}"}

def generate_unique_slug(instance, field_name: str, slug_field_name: str = "slug") -> None:
    """
    تولید slug یکتا از یک فیلد دلخواه (مثلاً 'title' یا 'name') برای مدلی که slug دارد.

    Parameters:
    - instance: شیء مدل
    - field_name: نام فیلدی که از آن slug ساخته می‌شود (مثل 'reward_name')
    - slug_field_name: نام فیلد slug (پیش‌فرض 'slug')
    """

    base_value = getattr(instance, field_name, "")
    if not base_value:
        return

    # جایگزینی فاصله با - و حذف کاراکترهای غیرمجاز (فارسی و انگلیسی مجازند)
    base_slug = re.sub(r'[^\w\u0600-\u06FF-]', '', base_value.replace(' ', '-'))
    base_slug = re.sub(r'-{2,}', '-', base_slug).strip('-')

    ModelClass = instance.__class__
    slug = base_slug
    counter = 1

    # بررسی تکراری بودن slug در همان مدل
    while ModelClass.objects.filter(**{slug_field_name: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    setattr(instance, slug_field_name, slug)



# تولید uuid4
def generate_uuid() -> str:
    """
    تولید یک شناسه یکتا (UUID v4) به صورت رشته.
    """
    new_uuid = str(uuid.uuid4())
    return new_uuid


# ذخیره سازی UUID
def store_uuid(phone_or_id: Union[str, int]) -> str:
    """
    ذخیره یک UUID یکتا در کش برای یک کلید مشخص (مثلاً شماره تلفن یا شناسه کاربر).

    پارامترها:
    - phone_or_id: کلیدی که UUID برای آن ذخیره می‌شود (مثلاً شماره تلفن یا شناسه کاربر).

    بازگشت:
    - UUID تولید شده به صورت رشته.

    عملکرد:
    - تولید UUID یکتا با تابع generate_uuid()
    - ذخیره آن در کش با زمان انقضا مشخص توسط EMAIL_VERIFICATION_TOKEN_EXPIRATION_SECONDS
    - لاگ کردن عملیات ذخیره UUID با سطح debug
    """
    key = phone_or_id
    value = generate_uuid()
    logger.debug(f'Storing UUID for {key} : {value}')
    cache.set(key, value, timeout=settings.EMAIL_VERIFICATION_TOKEN_EXPIRATION_SECONDS)
    return value

# ابزار کلی برای ارسال تمامی ایمیل‌ها
def send_email(subject:str , to_email:str , template_name:str, context:dict, client_ip: str) -> Tuple[bool, str]:
    """
    ارسال ایمیل با موضوع و قالب مشخص، با پشتیبانی از قالب HTML و متن ساده، بدون محدودیت نرخ.

    پارامترها:
    - subject: موضوع ایمیل
    - to_email: آدرس ایمیل گیرنده
    - template_name: نام قالب HTML که باید رندر شود
    - context: دیکشنری داده‌ها برای رندر قالب
    - client_ip: آدرس IP کلاینت (فقط برای لاگ استفاده می‌شود)

    خروجی:
    - tuple: (success: bool, error_message: str)
    """
    logger.info(f'ارسال ایمیل به {to_email} با موضوع "{subject}" از IP {client_ip}')

    try:
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        from_email = settings.DEFAULT_FROM_EMAIL
        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, "text/html")
        email.send()
        logger.info(f'ایمیل با موفقیت به {to_email} ارسال شد')
        return True, ""
    except Exception as e:
        logger.error(f'خطا در ارسال ایمیل به {to_email}: {str(e)}')
        return False, f"خطا در ارسال ایمیل: {str(e)}"


# ارسال کد تایید برای کاربران
def send_conf_mail(userid: str, to_email: str, client_ip: str) -> Tuple[bool, str]:
    """
    ارسال ایمیل تایید با توکن UUID به کاربر، با اعمال محدودیت زمانی ۲ دقیقه.

    پارامترها:
    - userid: شناسه کاربر (برای کلید ذخیره UUID در کش)
    - to_email: آدرس ایمیل گیرنده
    - client_ip: آدرس IP کلاینت (فقط برای لاگ استفاده می‌شود)

    خروجی:
    - tuple: (success: bool, error_message: str)
    """
    logger.info(f'آماده‌سازی برای ارسال ایمیل تایید به کاربر {userid} از IP {client_ip}')

    # ایجاد نمونه‌ای از RateLimiterMiddleware
    rate_limiter = RateLimiterMiddleware(get_response=None)
    # بررسی محدودیت زمانی کاربر (to_email به‌عنوان user_key)
    allowed, wait = rate_limiter.check_user_cooldown(to_email)
    if not allowed:
        logger.warning(f'محدودیت زمانی برای {to_email} نقض شده است: {wait} ثانیه باقی‌مانده')
        return False, f"لطفاً {wait} ثانیه صبر کنید قبل از ارسال درخواست جدید."

    try:
        tokenid = store_uuid(userid)  # فرض می‌کنیم store_uuid از قبل تعریف شده
        context = {
            'token_id': tokenid,
            'userid': userid,
            'ttl_hours': settings.EMAIL_VERIFICATION_TOKEN_EXPIRATION_SECONDS // 3600,
        }
        success, error = send_email(subject='تایید ایمیل', to_email=to_email,
                                   template_name='confemail.html', context=context,
                                   client_ip=client_ip)
        if success:
            logger.info(f'ایمیل تایید با موفقیت به {to_email} ارسال شد')
        return success, error
    except Exception as e:
        logger.error(f'خطا در آماده‌سازی ایمیل تایید برای {to_email}: {str(e)}')
        return False, f"خطا در آماده‌سازی ایمیل: {str(e)}"

# استفاده از API
def call_api(url, method='GET', headers=None, params=None, data=None, json=None, timeout=10) -> requests.Response:
    """
    ارسال درخواست HTTP به API و دریافت پاسخ.

    پارامترها:
    - url: آدرس API (رشته)
    - method: متد HTTP ('GET'، 'POST'، 'PUT' و غیره)
    - headers: دیکشنری هدرهای HTTP (مثل Authorization)
    - params: دیکشنری پارامترهای کوئری (برای GET)
    - data: داده‌های فرم (برای POST/PUT)
    - json: داده‌های JSON (برای POST/PUT)
    - timeout: زمان انتظار به ثانیه (پیش‌فرض ۱۰ ثانیه)

    خروجی:
    - دیکشنری JSON پاسخ در صورت موفقیت (status_code 200-299)
    - None در صورت خطا
    """

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json,
            timeout=timeout
        )
        response.raise_for_status()  # اگر کد وضعیت 4xx یا 5xx بود خطا می‌اندازد

        # فرض می‌کنیم پاسخ JSON است
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None


# شناسیایی مرورگر کاربر و بازگردانی نام آن
def get_browser_name(self, user_agent: str | None) -> str:
    """
    شناسایی و بازگرداندن نام مرورگر بر اساس رشته user agent.

    پارامترها:
        user_agent (str): رشته‌ی user agent که معمولاً از هدر درخواست HTTP گرفته می‌شود.

    خروجی:
        str: نام مرورگر به صورت یکی از موارد زیر:
            - 'Chrome'
            - 'Firefox'
            - 'Safari'
            - 'Edge'
            - 'Internet Explorer'
            - 'Unknown' (اگر مرورگر شناسایی نشود)
    """

    user_agent = user_agent or ""  # برای جلوگیری از خطا در صورت None بودن

    ua = user_agent.lower()  # حروف کوچک برای مقایسه راحت‌تر

    if "chrome" in ua and "edge" not in ua and "edg" not in ua and "opr" not in ua:
        return "Chrome"
    elif "firefox" in ua:
        return "Firefox"
    elif "safari" in ua and "chrome" not in ua:
        return "Safari"
    elif "edge" in ua or "edg" in ua:
        return "Edge"
    elif "msie" in ua or "trident" in ua:
        return "Internet Explorer"
    else:
        return "Unknown"


# ابزار لاگ گیری کامل با تمامی اطلاعات
if not logger.handlers:  # جلوگیری از هندلرهای تکراری
    formatter = logging.Formatter(  # فرمت لاگ
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s | %(extra_data)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler('errors.log', encoding='utf-8')  # فایل لاگ
    file_handler.setFormatter(formatter)  # اعمال فرمت
    logger.addHandler(file_handler)  # اضافه کردن هندلر
    logger.setLevel(logging.DEBUG)  # پشتیبانی از همه سطوح لاگ

def error_log(level=logging.ERROR, message="An event occurred", exception=None, request=None, context=None, logger_name='app_logger'):
    """
    Log events or errors with detailed context to database and file.
    :param level: Logging level (e.g., logging.ERROR, logging.INFO) - سطح لاگ
    :param message: Log message - پیام لاگ
    :param exception: Exception object, if any - شیء خطا (اختیاری)
    :param request: Django request object, if available - شیء درخواست (اختیاری)
    :param context: Optional context (e.g., instance for class name) - زمینه (اختیاری)
    :param logger_name: Name of the logger - نام لاگر

    مثال::::

    class MyClass:
        def process_data(self, data, request=None):
            try:
                result = 10 / int(data)  # ممکنه خطا بده
                log_event(logging.INFO, "Data processed successfully", context=self, request=request)
                return result
            except Exception as e:
                log_event(logging.ERROR, f"Error processing data: {str(e)}", exception=e, context=self, request=request)
                raise

    def index(data):
        try:
            result = 10 / 0  # ممکنه خطا بده
            log_event(logging.INFO, "Function executed successfully")
            return result
        except Exception as e:
            log_event(logging.ERROR, f"Error in function: {str(e)}", exception=e)
            raise

    def test_view(request):
        try:
            result = MyClass().process_data(request.GET.get('number', 1), request)
            return HttpResponse(f"Result: {result}")
        except Exception as e:
            log_event(logging.ERROR, f"View error: {str(e)}", exception=e, request=request)
            raise
    """
    # گرفتن اطلاعات caller
    stack = inspect.stack()  # گرفتن stack trace
    frame = stack[1]  # فریم caller
    module_name = inspect.getmodule(frame[0]).__name__ if frame[0] else 'unknown'  # نام ماژول
    file_name = frame[0].f_code.co_filename if frame[0] else 'unknown'  # نام فایل
    line_number = frame[0].f_lineno if frame[0] else None  # شماره خط

    # گرفتن نام کلاس
    class_name = None  # مقدار اولیه
    if context and hasattr(context, '__class__'):  # اگر context داده شده
        class_name = context.__class__.__name__  # نام کلاس
    elif frame[0].f_locals.get('self'):  # اگر توی متد کلاسی هستیم
        class_name = frame[0].f_locals['self'].__class__.__name__

    # جمع‌آوری اطلاعات اضافی
    extra_data = {  # دیکشنری اطلاعات
        'module': module_name,  # نام ماژول
        'class': class_name or 'N/A',  # نام کلاس
        'file': file_name,  # نام فایل
        'line': line_number  # شماره خط
    }
    user = None  # مقدار اولیه کاربر
    context_info = None  # مقدار اولیه زمینه

    if request:  # اگر درخواست Django وجود داره
        extra_data.update({  # اضافه کردن اطلاعات درخواست
            'url': request.build_absolute_uri(),  # URL
            'method': request.method,  # متد HTTP
            'ip': request.META.get('REMOTE_ADDR', 'unknown'),  # IP
            'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown'),  # مرورگر
            'user': str(request.user) if request.user.is_authenticated else 'Anonymous'  # کاربر
        })
        user = str(request.user) if request.user.is_authenticated else 'Anonymous'

    if exception:  # اگر خطا وجود داره
        extra_data.update({  # اضافه کردن اطلاعات خطا
            'exception_type': exception.__class__.__name__,  # نوع خطا
            'exception_message': str(exception),  # پیام خطا
            'stack_trace': ''.join(traceback.format_tb(exception.__traceback__))  # stack trace
        })
        context_info = f"{exception.__class__.__name__} in {module_name}"

    # لاگ توی فایل
    logger.log(level, message, extra={'extra_data': extra_data})  # نوشتن در فایل

    # لاگ توی دیتابیس
    try:
        LogEntry.objects.create(  # ایجاد رکورد
            level=logging.getLevelName(level),  # سطح لاگ
            logger_name=logger_name,  # نام لاگر
            message=message,  # پیام
            extra_data=extra_data,  # اطلاعات اضافی
            module_name=module_name,  # ماژول
            class_name=class_name,  # کلاس
            user=user,  # کاربر
            file_name=file_name,  # فایل
            line_number=line_number,  # خط
            context=context_info or f"{module_name}.{class_name or 'function'}"  # زمینه
        )
    except Exception as db_error:  # در صورت خطای دیتابیس
        logger.error(f"DB log failed: {db_error}")  # لاگ خطای دیتابیس