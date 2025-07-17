from django.db import models
from accounts.models import Student
from django_jalali.db import models as jmodels
from django.utils.text import slugify
from uuid import uuid4
from core.constraints import *
from core.managers import ActiveObjectsManager
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator




class Course(models.Model):
    title = models.CharField(max_length=MAX_LENGTH_TITLE, verbose_name="عنوان کلاس")
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات کلاس")
    students = models.ManyToManyField(Student, related_name='courses', verbose_name="دانشجویان")
    slug = models.SlugField(max_length=MAX_LENGTH_SLUG, unique=True, blank=True, verbose_name="اسلاگ")
    manual_progress = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="درصد پیشرفت دستی",
        help_text="اگر مقدار بزرگ‌تر از ۰ باشد، این مقدار به عنوان درصد پیشرفت استفاده می‌شود."
    )

    created_at = jmodels.jDateTimeField(auto_now_add=True)

    class Status(models.TextChoices):
        STARTED = 'ST', 'Started'
        SUSPENDED = 'SU', 'Suspended'
        FINISHED = 'FI', 'Finished'

    status = models.CharField(max_length=MAX_LENGTH_STATUS, choices=Status, default=Status.SUSPENDED, verbose_name='وضعیت')
    objects = ActiveObjectsManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            unique_slug = f"{base_slug}-{uuid4().hex[:6]}"
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def student_count(self):
        return self.students.count()
    student_count.short_description = "تعداد دانشجویان"

    def progress_percent(self):
        if self.manual_progress > 0:
            # اگر درصد دستی تنظیم شده بود، همون رو برگردون
            return min(max(self.manual_progress, 0), 100)  # مطمئن می‌شه بین 0 و 100 باشه
        total_steps = self.roadmap_steps.count()
        completed_steps = self.roadmap_steps.filter(status='completed').count()
        if total_steps == 0:
            return 0
        return int((completed_steps / total_steps) * 100)
    progress_percent.short_description = "درصد پیشرفت دوره"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "کلاس"
        verbose_name_plural = "کلاس‌ها"
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
        ]


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments', verbose_name="کلاس مربوطه")
    title = models.CharField(max_length=MAX_LENGTH_TITLE, verbose_name="عنوان تکلیف")
    description = models.TextField(blank=True, verbose_name="توضیحات تکلیف")
    file = models.FileField(upload_to='assignments/', null=True, blank=True, verbose_name="فایل تکلیف")
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    due_date = jmodels.jDateTimeField(default=timezone.now, null=True, blank=True, verbose_name="مهلت ارسال")
    slug = models.SlugField(max_length=MAX_LENGTH_SLUG, unique=True, blank=True, verbose_name="اسلاگ")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            unique_slug = f"{base_slug}-{uuid4().hex[:6]}"
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.course.title}"

    class Meta:
        verbose_name = "تکلیف"
        verbose_name_plural = "تکالیف"
        ordering = ['-created_at']


class AssignmentSubmission(models.Model):
    class Status(models.TextChoices):
        NOT_SUBMITTED = 'not_submitted', ('ارسال نشده')
        SUBMITTED = 'submitted', ('ارسال شده')

    assignment = models.ForeignKey(
        'Assignment',
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name="تکلیف مربوطه"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name="دانشجو"
    )
    github_link = models.URLField(
        verbose_name="لینک گیت‌هاب",
        blank=True,
        null=True
    )
    submitted_at = jmodels.jDateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ارسال"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_SUBMITTED,
        verbose_name="وضعیت ارسال"
    )
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="نمره"
    )
    feedback = models.TextField(
        blank=True,
        null=True,
        verbose_name="بازخورد"
    )

    class Meta:
        verbose_name = "تکلیف ارسالی"
        verbose_name_plural = "تکالیف ارسالی"
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"



class Ticket(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='دانشجو'
    )
    subject = models.CharField(max_length=MAX_LENGTH_SUBJECT, verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')

    class Status(models.TextChoices):
        NEW = 'NE', 'جدید'
        IN_PROGRESS = 'IP', 'در حال بررسی'
        ANSWERED = 'AN', 'پاسخ داده شده'
        CLOSED = 'CL', 'بسته شده'

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='وضعیت'
    )

    # feedback = models.TextField(
    #     blank=True,
    #     null=True,
    #     verbose_name="پاسخ ادمین"
    # )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    def __str__(self):
        return f"{self.subject} - {self.student.username}"

    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت‌ها'
        ordering = ['-created_at']
        # اضافه کردن ایندکس برای بهبود سرچ
        indexes = [
            models.Index(fields=['subject']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]


class RoadmapStep(models.Model):
    STATUS_CHOICES = [
        ('completed', 'تکمیل شده'),
        ('current', 'در حال انجام'),
        ('pending', 'در انتظار'),
    ]

    course = models.ForeignKey(Course, related_name='roadmap_steps', on_delete=models.CASCADE, verbose_name='کلاس')
    title = models.CharField(max_length=MAX_LENGTH_TITLE, verbose_name='عنوان مرحله')
    description = models.CharField(max_length=MAX_LENGTH_DESCRIPTION, verbose_name='توضیح کوتاه')
    details = models.TextField(blank=True, verbose_name='توضیحات کامل')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    slug = models.SlugField(max_length=MAX_LENGTH_SLUG, unique=True, blank=True, verbose_name='اسلاگ')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        verbose_name = 'مرحله نقشه راه'
        verbose_name_plural = 'مراحل نقشه راه'
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            self.slug = f"{base_slug}-{uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class VideoItem(models.Model):
    course = models.ForeignKey(Course, related_name='videos', on_delete=models.CASCADE, verbose_name='کلاس')
    title = models.CharField(max_length=MAX_LENGTH_TITLE, verbose_name='عنوان ویدیو')
    description = models.CharField(max_length=MAX_LENGTH_DESCRIPTION, verbose_name='توضیح کوتاه')
    duration = models.CharField(max_length=20, verbose_name='مدت زمان')
    src = models.FileField(upload_to='videos/', verbose_name='فایل ویدیو')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    slug = models.SlugField(max_length=MAX_LENGTH_SLUG, unique=True, blank=True, verbose_name='اسلاگ')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        verbose_name = 'ویدیو'
        verbose_name_plural = 'ویدیوها'
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            self.slug = f"{base_slug}-{uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class ResourceSection(models.Model):
    course = models.ForeignKey(Course, related_name='resource_sections', on_delete=models.CASCADE, verbose_name='کلاس')
    session = models.CharField(max_length=MAX_LENGTH_TITLE, verbose_name='جلسه')
    chapter = models.CharField(max_length=MAX_LENGTH_TITLE, verbose_name='فصل')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')

    class Meta:
        verbose_name = 'بخش منابع'
        verbose_name_plural = 'بخش‌های منابع'
        ordering = ['order']

    def __str__(self):
        return f"{self.session} - {self.chapter} ({self.course.title})"


class ResourceLink(models.Model):
    section = models.ForeignKey(ResourceSection, related_name='links', on_delete=models.CASCADE, verbose_name='بخش')
    title = models.CharField(max_length=MAX_LENGTH_TITLE, verbose_name='عنوان لینک')
    url = models.URLField(verbose_name='آدرس',null=True, blank=True)

    class Meta:
        verbose_name = 'لینک منبع'
        verbose_name_plural = 'لینک‌های منابع'

    def __str__(self):
        return self.title



class Notification(models.Model):
    course = models.ForeignKey(Course, related_name='notifications', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.message} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"




class CourseStudent(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_students',
        verbose_name='کلاس'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='student_courses',
        verbose_name='دانشجو'
    )
    score = models.DecimalField(
        max_digits=MAX_INTEGER_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
        validators=[MinValueValidator(MIN_VALUE_SCORE), MaxValueValidator(MAX_VALUE_SCORE)],
        null=True,
        blank=True,
        verbose_name='نمره دانشجو در این کلاس'
    )
    registered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت‌نام'
    )

    class Meta:
        verbose_name = 'نمره دانشجو در کلاس'
        verbose_name_plural = 'نمرات دانشجو در کلاس‌ها'
        unique_together = ('course', 'student')

    def __str__(self):
        return f"{self.student} در {self.course} - نمره: {self.score}"
