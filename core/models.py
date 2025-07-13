from django.db import models
from django.conf import settings
from .constraints import *
from core.middleware.current_user import get_current_user, get_current_request
from .managers import ActiveObjectsManager



class BaseModel(models.Model):
    """
    مدل پایه انتزاعی که شامل فیلدهای تاریخ ایجاد و به‌روزرسانی و کاربر ایجادکننده و ویرایشگر است.
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    created_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_%(class)s_set',
        verbose_name="کاربر ایجادکننده"
    )

    updated_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='updated_%(class)s_set',
        verbose_name="کاربر آخرین ویرایش"
    )

    class Status(models.TextChoices):
        ACTIVE = 'AC', 'Active'
        DEACTIVE = 'DAC', 'Deactive'
        DELETED = 'DEL', 'Deleted'

    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name='وضعیت'
    )

    objects = ActiveObjectsManager()

    class Meta:
        abstract = True  # مدل انتزاعی، جدول جداگانه ایجاد نمی‌شود
        ordering = ['-created_at']  # مرتب‌سازی پیش‌فرض بر اساس تاریخ ایجاد نزولی

    def save(self, *args, **kwargs):
        user = get_current_user()
        request = get_current_request()

        if not self.pk and user and not self.created_user:
            self.created_user = user
            self.updated_user = user

        if user and request and request.method in ['PUT', 'PATCH']:
            self.updated_user = user

        super().save(*args, **kwargs)


# مدل برای ذخیره تمامی لاگ‌ها در دیتابیس
class LogEntry(models.Model):
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    timestamp = models.DateTimeField(auto_now_add=True)  # زمان لاگ (خودکار)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)  # سطح لاگ
    logger_name = models.CharField(max_length=100)  # نام لاگر
    message = models.TextField()  # پیام لاگ
    extra_data = models.JSONField(null=True, blank=True)  # اطلاعات اضافی
    module_name = models.CharField(max_length=100, blank=True, null=True)  # نام ماژول
    class_name = models.CharField(max_length=100, blank=True, null=True)  # نام کلاس
    user = models.CharField(max_length=100, blank=True, null=True)  # کاربر
    file_name = models.CharField(max_length=255, blank=True, null=True)  # نام فایل
    line_number = models.IntegerField(blank=True, null=True)  # شماره خط
    context = models.CharField(max_length=255, blank=True, null=True)  # زمینه (برای توابع غیر-view)

    def __str__(self):
        return f"[{self.timestamp}] {self.level} - {self.logger_name} ({self.class_name or 'No Class'})"