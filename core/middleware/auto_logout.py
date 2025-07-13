import datetime
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin

class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        current_datetime = datetime.datetime.now()
        last_activity = request.session.get('last_activity')

        if last_activity:
            last_activity_time = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S.%f')
            elapsed = (current_datetime - last_activity_time).total_seconds()

            if elapsed > 3600:  # 3600 ثانیه = 1 ساعت
                logout(request)
                # پاک کردن سشن
                request.session.flush()
                return

        # بروزرسانی زمان آخرین فعالیت
        request.session['last_activity'] = str(current_datetime)
