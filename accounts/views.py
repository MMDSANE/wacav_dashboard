import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.http import HttpResponse
from django.contrib.auth import get_user_model
User = get_user_model()

logger = logging.getLogger(__name__)  # لاگر برای ثبت خطاها و رویدادها

MAX_ATTEMPTS = 60
BLOCK_DURATION = 120  # به ثانیه (۲ دقیقه)

def student_login(request):
    context = {
        'error': None,
        'blocked': False
    }

    try:
        if request.method == 'POST':
            raw_username = request.POST.get('user') or ''
            raw_password = request.POST.get('password') or ''

            username = raw_username.strip()
            password = raw_password.strip()

            ip = request.META.get('REMOTE_ADDR', '')
            cache_key = f'login_attempts_{ip}'

            attempts = cache.get(cache_key, 0)

            if attempts >= MAX_ATTEMPTS:
                context['blocked'] = True
                context['error'] = 'به دلیل تلاش‌های مکرر، دسترسی شما برای ۲ دقیقه مسدود شده است.'
                logger.warning(f'IP blocked due to too many login attempts: {ip}')
            else:
                try:
                    # پیدا کردن یوزری که یوزرنیمش (با فاصله) ذخیره شده
                    matched_user = User.objects.get(username__iexact=username)
                    real_username = matched_user.username  # دقیقاً همون چیزی که در DB هست
                except User.DoesNotExist:
                    real_username = username  # فیک، تا لاگین fail بشه

                user = authenticate(request, username=real_username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        cache.delete(cache_key)
                        logger.info(f'User logged in successfully: {real_username}')
                        return redirect('dashboard:student_dashboard')
                    else:
                        context['error'] = 'حساب کاربری شما غیرفعال است.'
                        logger.warning(f'Inactive account login attempt: {real_username}')
                else:
                    attempts += 1
                    cache.set(cache_key, attempts, timeout=BLOCK_DURATION)
                    context['error'] = 'نام کاربری یا رمز عبور اشتباه است.'
                    logger.info(f'Failed login attempt {attempts} for IP {ip} and username: {username}')
    except Exception as e:
        logger.error(f'Unexpected error in student_login: {e}')
        context['error'] = 'خطایی رخ داد، لطفاً دوباره تلاش کنید.'

    return render(request, 'forms/login.html', context)


def student_logout(request):
    logout(request)
    return redirect('student_login')
