from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AutoLogoutMiddleware(MiddlewareMixin):
    """
    Middleware برای خروج خودکار کاربران بعد از مدت زمان مشخص عدم فعالیت

    ویژگی‌ها:
    - خروج خودکار کاربران بعد از 1 ساعت عدم فعالیت
    - استفاده از timezone-aware datetime
    - مدیریت خطاهای احتمالی
    - قابلیت تنظیم timeout از settings
    - لاگ کردن خروج‌های خودکار
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        # گرفتن timeout از settings یا استفاده از مقدار پیش‌فرض
        self.timeout_seconds = getattr(settings, 'AUTO_LOGOUT_TIMEOUT', 3600)  # 1 ساعت
        self.session_key = 'last_activity_timestamp'

    def process_request(self, request):
        """بررسی و به‌روزرسانی وضعیت فعالیت کاربر"""

        # فقط برای کاربران وارد شده
        if not request.user.is_authenticated:
            return

        try:
            current_time = timezone.now()
            last_activity = request.session.get(self.session_key)

            if last_activity:
                # تبدیل timestamp به datetime object
                try:
                    if isinstance(last_activity, str):
                        # اگر به صورت string ذخیره شده (compatibility)
                        last_activity_time = timezone.datetime.fromisoformat(last_activity)
                    else:
                        # اگر به صورت timestamp ذخیره شده
                        last_activity_time = timezone.datetime.fromtimestamp(last_activity,
                                                                             tz=timezone.get_current_timezone())
                except (ValueError, TypeError, OSError) as e:
                    # اگر مشکلی در پارس کردن بود، زمان فعلی را به‌عنوان آخرین فعالیت ثبت کن
                    logger.warning(f"Error parsing last_activity for user {request.user.id}: {e}")
                    request.session[self.session_key] = current_time.timestamp()
                    return

                # محاسبه مدت زمان سپری شده
                elapsed_seconds = (current_time - last_activity_time).total_seconds()

                # اگر بیش از حد مجاز زمان گذشته، کاربر را خارج کن
                if elapsed_seconds > self.timeout_seconds:
                    user_id = request.user.id
                    username = getattr(request.user, 'username', 'unknown')

                    # لاگ کردن خروج خودکار
                    logger.info(
                        f"Auto logout user {user_id} ({username}) after {elapsed_seconds:.0f} seconds of inactivity")

                    # خروج کاربر
                    logout(request)

                    # پاک کردن کامل session
                    request.session.flush()

                    return  # به view نرو، درخواست تمام شد

            # به‌روزرسانی زمان آخرین فعالیت
            request.session[self.session_key] = current_time.timestamp()

        except Exception as e:
            # در صورت هر خطای غیرمنتظره، لاگ کن ولی middleware رو خراب نکن
            logger.error(f"Unexpected error in AutoLogoutMiddleware: {e}")
            # در صورت خطا، حداقل session را به‌روزرسانی کن
            try:
                request.session[self.session_key] = timezone.now().timestamp()
            except:
                pass

    def get_remaining_time(self, request):
        """
        محاسبه زمان باقی‌مانده تا خروج خودکار

        Returns:
            int: تعداد ثانیه‌های باقی‌مانده یا None اگر کاربر وارد نشده
        """
        if not request.user.is_authenticated:
            return None

        try:
            last_activity = request.session.get(self.session_key)
            if not last_activity:
                return self.timeout_seconds

            current_time = timezone.now()

            if isinstance(last_activity, str):
                last_activity_time = timezone.datetime.fromisoformat(last_activity)
            else:
                last_activity_time = timezone.datetime.fromtimestamp(last_activity, tz=timezone.get_current_timezone())

            elapsed_seconds = (current_time - last_activity_time).total_seconds()
            remaining = self.timeout_seconds - elapsed_seconds

            return max(0, int(remaining))

        except Exception:
            return self.timeout_seconds

    def extend_session(self, request):
        """
        تمدید دستی session (مثلاً برای عملیات‌های مهم)
        """
        if request.user.is_authenticated:
            request.session[self.session_key] = timezone.now().timestamp()
            return True
        return False