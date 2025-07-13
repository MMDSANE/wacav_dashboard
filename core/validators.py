from django.core.exceptions import ValidationError
import re
import uuid
from enum import Enum, auto
from django.core.cache import cache
from .utils import *
from .constraints import *


# اعتبارسنجی جنسیت
def is_valid_gender(gender: str) -> bool:
    """
    اعتبارسنجی جنسیت.
    پشتیبانی از مقادیر رایج: male, female
    بدون حساسیت به حروف بزرگ و کوچک.
    """
    valid_genders = {'male', 'female'}
    return gender.strip().lower() in valid_genders


# اعتبارسنجی شماره‌تلفن
def is_valid_iranian_mobile(phone: str) -> str:
    """
    اعتبارسنجی شماره موبایل ایران بر اساس پیش‌شماره‌های معتبر اپراتورها.
    شماره باید دقیقاً با الگوی تعیین‌شده مطابقت داشته باشد.
    """
    phone_regex = r'^09(0[1-5]|1[0-9]|2[0-2]|3[0-9]|9[0-4])[0-9]{7}$'

    if not re.fullmatch(phone_regex, phone):
        raise ValidationError("شماره همراه معتبر ایران را وارد کنید (مثال: 09361234567)")

    return normalize_phone_number(phone)


def is_valid_email(email: str) -> bool:
    """
    بررسی اعتبار آدرس ایمیل به صورت پیشرفته با استفاده از Regex.
    پشتیبانی از اکثر فرمت‌های معتبر طبق RFC 5322.
    """
    if not email or not isinstance(email, str):
        return False

    email_regex = re.compile(
        r"^(?=.{1,254}$)"              # طول کل ایمیل حداکثر 254 کاراکتر
        r"(?=.{1,64}@)"                # بخش قبل @ حداکثر 64 کاراکتر
        r"[a-zA-Z0-9_.+-]+"            # بخش local (قبل از @)
        r"@"                          
        r"[a-zA-Z0-9-]+\."             # بخش اول دامین (domain name)
        r"[a-zA-Z0-9-.]{2,}$"          # ادامه دامین، حداقل ۲ حرف
    )

    return bool(email_regex.match(email))


def is_valid_iranian_national_code(code: str) -> bool:
    """
    اعتبارسنجی کد ملی ایران (۱۰ رقمی) با بررسی ساختار و رقم کنترل.
    """
    if not re.match(r'^(?!(\d)\1{9})\d{10}$', code):
        raise ValidationError(
            ('کد ملی وارد شده معتبر نیست.'),
            code='invalid_iranian_national_code'
        )

    check = int(code[9])
    s = sum(int(code[i]) * (10 - i) for i in range(9))
    r = s % 11

    if r < 2:
        return check == r
    else:
        return check == (11 - r)


def is_valid_iranian_postal_code(code: str) -> bool:
    """
    اعتبارسنجی کد پستی ایران (۱۰ رقمی).
    بررسی ساختار و جلوگیری از کدهای تکراری مثل 0000000000 یا 1111111111.
    """
    if not re.match(r'^(?!(\d)\1{9})\d{10}$', code):
        raise ValidationError(
            ('کد پستی وارد شده معتبر نیست.'),
            code='invalid_iranian_postal_code'
        )

    # اگر نیاز به بررسی محدوده جغرافیایی بود، می‌توان بر اساس چند رقم اول اینجا چک کرد

    return True


def is_valid_jalali_date(date_str: str, fmt: str = "%Y/%m/%d") -> bool:
    """
    بررسی صحت تاریخ شمسی به فرمت داده‌شده.
    نیازمند نصب jdatetime:
    pip install jdatetime
    """
    try:
        import jdatetime
        jdatetime.datetime.strptime(date_str, fmt)
        return True
    except Exception as e:
        error_log()  # بدون context برای view ساده
        raise


def is_valid_referral_code(code: str) -> bool:
    """
    کد معرف باید ترکیبی از حروف بزرگ و عدد باشد (۶ تا ۱۲ کاراکتر).
    """
    return bool(re.fullmatch(r"[A-Z0-9]{6,12}", code))


def is_strong_password(password: str) -> bool:
    """
    بررسی قدرت رمز عبور:
    - حداقل ۸ کاراکتر
    - حداقل یک حرف بزرگ
    - حداقل یک حرف کوچک
    - حداقل یک رقم
    - حداقل یک نماد از SPECIAL_CHARACTERS
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(f"[{re.escape(SPECIAL_CHARACTERS)}]", password):
        return False
    return True


def is_valid_amount(value: str, MAX_INTEGER_DIGITS: int, MAX_DECIMAL_PLACES: int) -> bool:
    """
    اعتبارسنجی عدد مثبت با تعداد ارقام صحیح و اعشار داینامیک.

    :param value: رشته عددی برای اعتبارسنجی
    :param MAX_INTEGER_DIGITS: حداکثر تعداد ارقام قبل از ممیز
    :param MAX_DECIMAL_PLACES: حداکثر تعداد ارقام بعد از ممیز
    :return: True اگر معتبر باشد، False در غیر این صورت
    مثال: print(is_valid_amount('12.13', 2, 2))---->True
    """
    pattern = rf"^\d{{1,{MAX_INTEGER_DIGITS}}}(\.\d{{1,{MAX_DECIMAL_PLACES}}})?$"
    return bool(re.fullmatch(pattern, value))



def is_valid_iranian_card_number(card_number: str) -> bool:
    """
    شماره کارت باید ۱۶ رقمی باشد و از الگوریتم Luhn تبعیت کند.
    """
    if not re.fullmatch(r"\d{16}", card_number):
        raise ValidationError(
            ('شماره کارت بانکی وارد شده معتبر نیست.'),
            code='invalid_iranian_card_number'
        )
    digits = [int(d) for d in card_number]
    for i in range(0, 16, 2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0


def is_valid_iranian_sheba(sheba: str) -> bool:
    """
    بررسی صحت شماره شبا ایران با الگوریتم MOD-97.
    """
    if not re.fullmatch(r"IR\d{24}", sheba):
        raise ValidationError(
            ('شماره شبا وارد شده معتبر نیست.'),
            code='invalid_iranian_sheba'
        )
    sheba_reordered = sheba[4:] + '1827' + sheba[2:4]
    numeric_str = ''.join(str(int(ch)) if ch.isdigit() else str(ord(ch.upper()) - 55) for ch in sheba_reordered)
    return int(numeric_str) % 97 == 1


def is_valid_url(url: str) -> bool:
    """
    بررسی آدرس اینترنتی (URL یا دامنه ساده) با الگوی معتبر.
    """
    return bool(re.fullmatch(
        r"^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$", url.strip()
    ))


def is_valid_uuid4(value: str) -> bool:
    """
    اعتبارسنجی شناسه یکتا (UUID نسخه 4).
    uuid ایمپورت شود
    بررسی می‌کند که رشته واردشده یک UUID4 معتبر است یا نه.
    """
    try:
        val = uuid.UUID(value, version=4)
    except (ValueError, AttributeError, TypeError):
        raise ValidationError(
            ('شناسه یکتا وارد شده معتبر نیست.'),
            code='invalid_valid_uuid4'
        )
    return str(val) == value.lower()


# اعتبار سنجی کد ارسالی OTP
def is_valid_otp(identifier: str, submitted_code: str) -> bool:
    """
    اعتبارسنجی کد OTP و حذف آن در صورت صحت.

    Args:
        identifier (str): کلید یکتا (مانند شماره موبایل یا ایمیل) برای دسترسی به OTP.
        submitted_code (str): کدی که کاربر وارد کرده است.

    Returns:
        bool: اگر کد درست باشد، True؛ در غیر این صورت، False.
    """
    cached_code = cache.get(identifier) # دریافت کد ثبت شده در کش کاربر
    if cached_code and cached_code == submitted_code: # مقایسه کش کابر با کش وارد شده
        cache.delete(identifier) # برای امنیت؛ چون OTP یک‌بارمصرفه
        return True
    else:
        return False # عدم وجود کش


# اعتبارسنجی روش لاگین (OTP یا Password)
class LoginMethod(str, Enum):
    """
     اعتبارسنجی روش لاگین (OTP یا Password)
     LoginMethod.is_valid('password') نحوه استفاده ----> True
    """
    OTP = "OTP"
    PASSWORD = "PASSWORD"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """
        بررسی اینکه مقدار ورودی در بین روش‌های لاگین تعریف‌شده وجود دارد یا نه.
        """
        if not isinstance(value, str):
            return False
        return value.strip().upper() in cls.__members__


def is_valid_uuid(phone_or_id, url_uuid) -> bool:
    """
    بررسی صحت UUID ارائه شده در URL با UUID ذخیره شده در کش برای کلید مشخص.

    پارامترها:
    - phone_or_id: کلیدی که UUID مرتبط با آن در کش ذخیره شده است.
    - url_uuid: UUID دریافتی از URL برای اعتبارسنجی.

    بازگشت:
    - True اگر UUID ذخیره شده با UUID ارائه شده برابر بود (و سپس حذف UUID از کش)
    - False در غیر این صورت.
    """
    key = phone_or_id
    stored_uuid = cache.get(key)
    if url_uuid and url_uuid == stored_uuid:
        cache.delete(key)
        logger.debug(f'UUID verification success for key: {key}')
        return True
    logger.debug(f'UUID verification failed for key: {key}')
    return False
