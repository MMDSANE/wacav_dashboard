from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'  # یا 'apps.core' اگر در زیرپوشه apps قرار دارد
    verbose_name = "قابلیت‌های اصلی"  # نام نمایشی در پنل ادمین

