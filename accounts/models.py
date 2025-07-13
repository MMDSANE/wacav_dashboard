from django.db import models
from django.contrib.auth.models import AbstractUser
from django_jalali.db import models as jmodels
from core.constraints import *


class Student(AbstractUser):
    """
    مدل دانشجو که از AbstractUser ارث‌بری می‌کند.
    شامل شماره دانشجویی، شماره تماس، وضعیت و تاریخ ثبت‌نام.
    """

    student_id = models.PositiveIntegerField(
        unique=True,
        editable=False,
        null=True,
        blank=True,
        verbose_name="شماره دانشجویی"
    )

    phone_number = models.CharField(
        max_length=MAX_PHONE_NUMBER_LENGTH,
        blank=True,
        null=True,
        verbose_name="شماره تماس"
    )

    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        help_text='نام کاربری می‌تواند شامل فاصله و حروف فارسی باشد.',
        error_messages={
            'unique': "یک کاربر با این نام کاربری وجود دارد.",
        },
        verbose_name="نام کاربری"
    )

    first_name = models.CharField(
        max_length=MAX_FIRST_NAME_LENGTH,
        blank=True,
        null=True,
        verbose_name="نام"
    )

    last_name = models.CharField(
        max_length=MAX_LAST_NAME_LENGTH,
        blank=True,
        null=True,
        verbose_name="نام خانوادگی"
    )

    created_at = jmodels.jDateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Status(models.TextChoices):
        REGISTERED = 'RE', 'ثبت‌نام شده'
        FINISHED = 'FI', 'اتمام دوره'

    status = models.CharField(
        max_length=MAX_LENGTH_STATUS,
        choices=Status.choices,
        default=Status.REGISTERED,
        verbose_name='وضعیت'
    )

    def save(self, *args, **kwargs):
        """
        به‌صورت خودکار student_id را مقداردهی می‌کند،
        اگر اولین بار ساخته می‌شود.
        """
        if self.student_id is None:
            last_student = Student.objects.order_by('-student_id').first()
            self.student_id = (last_student.student_id + 1) if last_student and last_student.student_id else 100
        super().save(*args, **kwargs)

    def full_name(self):
        """
        نام کامل دانشجو را برمی‌گرداند.
        """
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def __str__(self):
        return f"{self.username} ({self.student_id})"

    class Meta:
        verbose_name = "دانشجو"
        verbose_name_plural = "دانشجویان"
        ordering = ['student_id']
