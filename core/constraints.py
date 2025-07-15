# -----------------------------------
# محدودیت‌ها برای فیلدهای عمومی کاربران
# -----------------------------------

# حداکثر طول ID برای هر یوزر
MAX_USER_ID_LENGTH = 50

# حداکثر طول برای کلید خارجی
MAX_FOREIGNKEY_LENGTH = 50

# حداکثر طول شماره تلفن (شامل کد کشور)
MAX_PHONE_NUMBER_LENGTH = 15

# حداکثر طول آدرس ایمیل
MAX_EMAIL_LENGTH = 255

# حداکثر طول نام کاربری
MAX_USERNAME_LENGTH = 150

# حداقل طول رمز عبور
MIN_PASSWORD_LENGTH = 8

# حداکثر طول رمز عبور
MAX_PASSWORD_LENGTH = 128

# حداکثر طول آدرس محل سکونت کاربر
MAX_ADDRESS_LENGTH = 300

# کوپن تخفیف
MAX_LENGTH_VOUCHER_CODE = 50

# انقضای کد یک‌بار مصرف (OTP) بر حسب ثانیه – معادل ۳ دقیقه
OTP_EXPIRATION_SECONDS = 180

# تعداد اعداد در OTP
OTP_LENGTH = 6

# اندازه یا ماکسیمم تعداد اعداد صحیح
MAX_INTEGER_DIGITS = 50

# اندازه یا ماکسیمم تعداد اعداد اعشاری
MAX_DECIMAL_PLACES = 2

# کاراکتر‌های خاص برای استفاده در پسورد
SPECIAL_CHARACTERS = "!@#$%^&*()-_=+[]{}|;:,.<>?/~"

# ------------------------------------------
# تنظیمات مربوط به اندازه‌ی تصاویر ####
# ------------------------------------------

# تصویر پروفایل کاربر - مربع (نمایش در آواتار، هدر و ...):
PROFILE_IMAGE_SIZE = (400, 400)

# لوگو شرکت یا فروشگاه - کمی مستطیل:
LOGO_IMAGE_SIZE = (400, 300)

# بنر اصلی یا هدر سایت/اپ - عریض:
HEADER_BANNER_SIZE = (1200, 400)

# تصاویر محصولات در فروشگاه یا گالری - مربع:
PRODUCT_IMAGE_SIZE = (800, 800)

# تصاویر کوچک (thumbnail) - برای لیست‌ها و کارت‌ها:
THUMBNAIL_IMAGE_SIZE = (150, 150)

# تصاویر اسلایدر - کمی عریض:
SLIDER_IMAGE_SIZE = (1000, 500)

# تصویر پس‌زمینه پروفایل یا کاور پیج:
COVER_IMAGE_SIZE = (1200, 600)

# ------------------------------------------
### تنظیمات و زمانبندی مربوط به دسترسی #
# ------------------------------------------

# زمان استراحت کاربر بعد از درخواست ( مثل پیامک یا ایمیل )
USER_LIMIT_COOLDOWN = 120

# تعداد درخواست مجاز هر کاربر در بازه زمانی مشخص شده مثلا ۳۶۰۰ ثانیه یا یکساعت
IP_LIMIT = 15000000000

# بازه زمانی ارسال تعداد درخواست‌های مشخص شده هر IP
IP_WINDOW_SECONDS = 3600

# -----------------------------------
# مدت اعتبار توکن تأیید ایمیل (بر حسب ثانیه)
# -----------------------------------

EMAIL_VERIFICATION_TOKEN_EXPIRATION_SECONDS = 900  # معادل 15 دقیقه

###################
#### models.py ####

# حداکثر طول برای نام
MAX_FIRST_NAME_LENGTH = 100

# حداکثر طول برای نام خانوادگی
MAX_LAST_NAME_LENGTH = 100

# حداکثر طول slug
MAX_LENGTH_SLUG = 300

# حداکثر طول Status
MAX_LENGTH_STATUS = 2

# حداکثر طول title
MAX_LENGTH_TITLE = 250

# حداکثر طول description
MAX_LENGTH_DESCRIPTION = 200

# حداکثر طول subject
MAX_LENGTH_SUBJECT = 200

# برای بخش نمره دهی
MIN_VALUE_SCORE = 1
MAX_VALUE_SCORE = 100

# # حداکثر تعداد درخواست هر کاربر روی هر URL در یک دوره زمانی
# USER_LIMIT_PER_URL = 100
#
# # دوره زمانی به ثانیه (30 دقیقه = 1800 ثانیه)
# TIME_WINDOW_SECONDS = 30 * 60  # 1800 ثانیه

# برای تست می‌تونید مقادیر کمتری استفاده کنید:
USER_LIMIT_PER_URL = 5
TIME_WINDOW_SECONDS = 60  # 1 دقیقه

###################

# -----------------------------------
# محدودیت‌ها برای برنامه وفاداری (Loyalty)
# -----------------------------------

# حداکثر تعداد ارقام عددی در امتیاز
MAX_POINTS_DECIMAL_DIGITS = 10

# حداکثر تعداد رقم اعشار در امتیاز
MAX_POINTS_DECIMAL_PLACES = 2

# -----------------------------------
# انواع قوانین دریافت امتیاز در برنامه وفاداری
# (برای استفاده مشترک در اپ loyalty)
# -----------------------------------

# قانون دریافت امتیاز از طریق خرید
LOYALTY_RULE_TYPE_PURCHASE = ('purchase','دریافت امتیاز از طریق خرید')

# قانون دریافت امتیاز با ثبت‌نام کاربر
LOYALTY_RULE_TYPE_SIGNUP = ('signup','دریافت امتیاز با ثبت‌نام کاربر')

# قانون دریافت امتیاز با معرفی دیگران
LOYALTY_RULE_TYPE_REFERRAL = ('referral','دریافت امتیاز با معرفی دیگران')

# قانون دریافت امتیاز در اولین خرید
LOYALTY_RULE_TYPE_FIRST_PURCHASE = ('first_purchase','دریافت امتیاز در اولین خرید')

# قانون دریافت امتیاز در صورت خرید بالای مقدار مشخص
LOYALTY_RULE_TYPE_HIGH_VALUE_PURCHASE = ('high_value_purchase','دریافت امتیاز در صورت خرید بالای مقدار مشخص')

# قانون دریافت امتیاز به ازای نظر دادن یا امتیاز دادن به محصولات
LOYALTY_RULE_TYPE_REVIEW = ('review','دریافت امتیاز به ازای نظر دادن یا امتیاز دادن به محصولات')

# قانون دریافت امتیاز به ازای تاریخ تولد
RULE_TYPE_BIRTHDAY = ('birthday','دریافت امتیاز به ازای تاریخ تولد')

# قانون دریافت امتیاز به ازای شرکت در کمپین‌ها
RULE_TYPE_SPECIAL_CAMPAIGN = ('special_campaign','دریافت امتیاز به ازای شرکت در کمپین‌ها')

# قانون دریافت امتیاز برای تکمیل پروفایل کاربری
LOYALTY_RULE_TYPE_PROFILE_COMPLETION = ('profile_completion','دریافت امتیاز برای تکمیل پروفایل کاربری')

# قانون دریافت امتیاز به ازای فعالیت روزانه (Daily login)
LOYALTY_RULE_TYPE_DAILY_LOGIN = ('daily_login','دریافت امتیاز به ازای فعالیت روزانه')

# قانون دریافت امتیاز در تاریخ‌های خاص (مثل مناسبت‌ها)
LOYALTY_RULE_TYPE_SPECIAL_DATE = ('special_date','دریافت امتیاز در تاریخ‌های خاص (مثل مناسبت‌ها)')

# قانون دریافت امتیاز در صورت عدم بازگشت طولانی و بازگشت مجدد کاربر
LOYALTY_RULE_TYPE_COMEBACK = ('comeback','دریافت امتیاز در صورت عدم بازگشت طولانی و بازگشت مجدد کاربر')

# لیست انواع معتبر قوانین دریافت امتیاز (برای استفاده در choices و اعتبارسنجی‌ها)
VALID_LOYALTY_RULE_TYPES = (
    LOYALTY_RULE_TYPE_PURCHASE,
    LOYALTY_RULE_TYPE_SIGNUP,
    LOYALTY_RULE_TYPE_REFERRAL,
    LOYALTY_RULE_TYPE_FIRST_PURCHASE,
    LOYALTY_RULE_TYPE_HIGH_VALUE_PURCHASE,
    LOYALTY_RULE_TYPE_REVIEW,
    LOYALTY_RULE_TYPE_PROFILE_COMPLETION,
    LOYALTY_RULE_TYPE_DAILY_LOGIN,
    LOYALTY_RULE_TYPE_SPECIAL_DATE,
    LOYALTY_RULE_TYPE_COMEBACK,
)

# انواع پاداش (Reward Types)
REWARD_TYPE_DISCOUNT_AMOUNT = ('discount_amount',' تخفیف مبلغی')
REWARD_TYPE_DISCOUNT_PERCENTAGE = ('discount_percentage','تخفیف درصدی')
REWARD_TYPE_FREE_PRODUCT = ('free_product','محصول رایگان')
REWARD_TYPE_SPECIAL_SERVICE = ('special_service','خدمات ویژه')

# اعتبار سنجی برای دریافت پاداش
VALID_REWARD_TYPES = (
    REWARD_TYPE_DISCOUNT_AMOUNT,
    REWARD_TYPE_DISCOUNT_PERCENTAGE,
    REWARD_TYPE_FREE_PRODUCT,
    REWARD_TYPE_SPECIAL_SERVICE,
)

# انواع تغییر امتیاز (Point History Change Types)
POINT_CHANGE_EARNED = 'Earned'
POINT_CHANGE_REDEEMED = 'Redeemed'
POINT_CHANGE_EXPIRED = 'Expired'
POINT_CHANGE_ADJUSTED = 'Adjusted'

VALID_POINT_CHANGE = (
    POINT_CHANGE_EARNED,
    POINT_CHANGE_REDEEMED,
    POINT_CHANGE_EXPIRED,
    POINT_CHANGE_ADJUSTED,
)

# --- API & Integration Constants ---
# کدهای وضعیت API (اگر خارج از HTTP استاندارد باشند)
API_STATUS_SUCCESS = 'success'
API_STATUS_FAILED = 'failed'

# --- Other General Settings ---
DEFAULT_POINTS_FOR_NEW_SIGNUP = 0
REFERRAL_POINTS_FOR_REFERRER = 50
REFERRAL_POINTS_FOR_NEW_CUSTOMER = 20

# برای مدیران فروشگاه که مبلغ ثابت باشه یا با تخفیف
VALUE_TYPE_CHOICES = (
    ('amount', 'مبلغ ثابت'),
    ('percentage', 'درصد تخفیف'),
)

CHANGE_TYPE_CHOICES = (
    ('Earned', 'کسب شده'),
    ('Redeemed', 'مصرف شده'),
    ('Expired', 'منقضی شده'),
    ('Adjusted', 'تنظیم دستی'),
)

# -----------------------------------
# نام‌های پیش‌فرض سطوح وفاداری (Tier)
# -----------------------------------

DEFAULT_TIER_NAME = (
    ('bronze', 'برنز'),
    ('silver', 'نقره‌ای'),
    ('gold', 'طلایی'),
    ('platinum', 'پلاتینیوم'),
    ('diamond', 'الماسی'),
)

# استفاده مستقیم از کلیدها
TIER_KEYS = tuple(key for key, _ in DEFAULT_TIER_NAME)

# -----------------------------------
# انواع پیش‌فرض کمپین‌ها
# -----------------------------------

DEFAULT_CAMPAIGN_TYPE = (
    ('seasonal', 'فصلی'),
    ('birthday', 'تولد'),
    ('welcome', 'خوش‌آمدگویی'),
    ('special_offer', 'پیشنهاد ویژه'),
    ('flash_sale', 'فروش فوری'),
)

##### for settings.py ######
# تعداد آیتم‌هایی که در هر صفحه هنگام صفحه‌بندی نمایش داده می‌شود
PAGE_SIZE_PAGINATION = 12
