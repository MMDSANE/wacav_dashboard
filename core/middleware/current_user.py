import threading

_user = threading.local()
_request = threading.local()

def get_current_user():
    return getattr(_user, 'value', None)

def get_current_request():
    return getattr(_request, 'value', None)

class CurrentUserMiddleware:
    """
    ذخیره‌ی کاربر و درخواست جاری برای استفاده در لایه‌های پایین‌تر مثل مدل‌ها.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = getattr(request, 'user', None)
        _request.value = request
        response = self.get_response(request)
        return response
