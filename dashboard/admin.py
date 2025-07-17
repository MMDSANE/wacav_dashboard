from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import slugify
from .models import *
from django_jalali.admin.filters import JDateFieldListFilter

# شخصی‌سازی هدر و تایتل کلی
admin.site.site_header = '🎓 پنل مدیریت کلاس‌ها و تکالیف'
admin.site.site_title = 'داشبورد مدیریت'
admin.site.index_title = 'پنل ادمین اپلیکیشن'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }
        js = ('js/custom_admin.js',)

    list_display = ('title', 'colored_status', 'student_count', 'progress_display')
    search_fields = ('title',)
    ordering = ('title',)
    filter_horizontal = ('students',)

    def student_count(self, obj):
        return obj.student_count()
    student_count.short_description = 'تعداد دانشجویان'

    def colored_status(self, obj):
        color = {
            'ST': 'green',
            'SU': 'orange',
            'FI': 'gray'
        }.get(obj.status, 'black')
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, obj.get_status_display())
    colored_status.short_description = 'وضعیت'

    def progress_display(self, obj):
        percent = obj.progress_percent()
        color = "green" if percent == 100 else "orange" if percent > 0 else "gray"
        return format_html(
            '<div style="width: 100px; border: 1px solid #ccc; border-radius: 5px;">'
            '<div style="background-color: {}; width: {}%; height: 16px; border-radius: 5px;"></div>'
            '</div>'
            '<span style="margin-left: 5px;">{}%</span>',
            color,
            percent,
            percent
        )
    progress_display.short_description = 'درصد پیشرفت دوره'

    actions = ['set_started', 'set_suspended', 'set_finished']

    def set_started(self, request, queryset):
        queryset.update(status='ST')
    set_started.short_description = "تغییر وضعیت به Started"

    def set_suspended(self, request, queryset):
        queryset.update(status='SU')
    set_suspended.short_description = "تغییر وضعیت به Suspended"

    def set_finished(self, request, queryset):
        queryset.update(status='FI')
    set_finished.short_description = "تغییر وضعیت به Finished"

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/custom_admin.css',)}
        js = ('js/custom_admin.js',)

    list_display = ('title', 'course', 'created_at', 'due_date')
    list_filter = ('course', 'created_at', 'due_date')
    search_fields = ('title', 'course__title')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    autocomplete_fields = ('course',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {'fields': ('course', 'title', 'description', 'file', 'due_date')}),
        ('اطلاعات سیستمی', {'fields': ('slug',)}),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        if 'title' in form.changed_data or not obj.slug:
            title = obj.title
            slug = slugify(title, allow_unicode=True)
            slug = slug[:100].rstrip('-')
            base_slug = slug
            counter = 1
            while Assignment.objects.filter(slug=slug).exclude(id=obj.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            obj.slug = slug
        super().save_model(request, obj, form, change)

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/custom_admin.css',)}
        js = ('js/custom_admin.js',)

    list_display = ('assignment', 'student', 'submitted_at', 'grade_display')
    list_filter = ('assignment', 'submitted_at', 'grade')
    search_fields = ('assignment__title', 'student__username', 'student__student_id')
    ordering = ('-submitted_at',)
    autocomplete_fields = ('assignment', 'student')
    readonly_fields = ('submitted_at',)

    fieldsets = (
        (None, {'fields': ('assignment', 'student', 'github_link')}),
        ('ارزیابی', {'fields': ('grade', 'feedback')}),
        ('اطلاعات تکمیلی', {'fields': ('submitted_at',)}),
    )

    def grade_display(self, obj):
        if obj.grade is not None:
            return format_html('<span style="color: darkblue; font-weight:bold;">{}</span>', obj.grade)
        return '-'
    grade_display.short_description = 'نمره'

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/custom_admin.css',)}
        js = ('js/custom_admin.js',)

    list_display = ('subject', 'student', 'colored_status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'message', 'student__username', 'student__first_name', 'student__last_name')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('student', 'subject', 'message', 'feedback_ticket')}),
        ('وضعیت و تاریخ‌ها', {'fields': ('status', 'created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')

    def colored_status(self, obj):
        color = 'green' if obj.status == 'باز' else 'gray'
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, obj.status)
    colored_status.short_description = 'وضعیت'

    actions = ['mark_as_closed', 'mark_as_open']

    def mark_as_closed(self, request, queryset):
        queryset.update(status='بسته')
    mark_as_closed.short_description = "بستن تیکت‌های انتخاب‌شده"

    def mark_as_open(self, request, queryset):
        queryset.update(status='باز')
    mark_as_open.short_description = "باز کردن تیکت‌های انتخاب‌شده"

@admin.register(RoadmapStep)
class RoadmapStepAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/custom_admin.css',)}
        js = ('js/custom_admin.js',)

    list_display = ('title', 'course', 'status', 'order', 'created_at')
    list_filter = ('course', 'status', 'created_at')
    search_fields = ('title', 'description', 'course__title')
    ordering = ('course', 'order')
    autocomplete_fields = ('course',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('course', 'title', 'description', 'details', 'status', 'order')}),
        ('اطلاعات سیستمی', {'fields': ('slug', 'created_at', 'updated_at')}),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        if 'title' in form.changed_data or not obj.slug:
            title = obj.title
            slug = slugify(title, allow_unicode=True)
            slug = slug[:100].rstrip('-')
            base_slug = slug
            counter = 1
            while RoadmapStep.objects.filter(slug=slug).exclude(id=obj.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            obj.slug = slug
        super().save_model(request, obj, form, change)

@admin.register(VideoItem)
class VideoItemAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/custom_admin.css',)}
        js = ('js/custom_admin.js',)

    list_display = ('title', 'course', 'duration', 'order', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'description', 'course__title')
    ordering = ('course', 'order')
    autocomplete_fields = ('course',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('course', 'title', 'description', 'duration', 'src', 'order')}),
        ('اطلاعات سیستمی', {'fields': ('slug', 'created_at', 'updated_at')}),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        if 'title' in form.changed_data or not obj.slug:
            title = obj.title
            slug = slugify(title, allow_unicode=True)
            slug = slug[:100].rstrip('-')
            base_slug = slug
            counter = 1
            while VideoItem.objects.filter(slug=slug).exclude(id=obj.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            obj.slug = slug
        super().save_model(request, obj, form, change)

@admin.register(ResourceSection)
class ResourceSectionAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/custom_admin.css',)}
        js = ('js/custom_admin.js',)

    list_display = ('session', 'chapter', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('session', 'chapter', 'course__title')
    ordering = ('course', 'order')
    autocomplete_fields = ('course',)

@admin.register(ResourceLink)
class ResourceLinkAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/custom_admin.css',)}
        js = ('js/custom_admin.js',)
    list_display = ('title', 'course_title')
    search_fields = ('title', 'url',)

    def course_title(self, obj):
        return obj.section.course.title
    course_title.short_description = 'کلاس'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/custom_admin.css',)}
        js = ('js/custom_admin.js',)
    list_display = ('course', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at', 'course')
    search_fields = ('message', 'course__title')
    readonly_fields = ('course', 'message', 'created_at')

    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} نوتیفیکیشن علامت‌گذاری شد به عنوان خوانده شده.")
    mark_as_read.short_description = "علامت‌گذاری نوتیفیکیشن‌ها به عنوان خوانده شده"

@admin.register(CourseStudent)
class CourseStudentAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/custom_admin.css',)}
        js = ('js/custom_admin.js',)

    list_display = ('student', 'course', 'score_display', 'registered_at')
    list_filter = ('course', 'registered_at')
    search_fields = (
        'student__username',
        'student__student_id',
        'student__first_name',
        'student__last_name',
        'course__title'
    )
    ordering = ('-registered_at',)
    autocomplete_fields = ('student', 'course')
    readonly_fields = ('registered_at',)

    fieldsets = (
        (None, {'fields': ('student', 'course')}),
        ('اطلاعات تکمیلی', {'fields': ('score', 'registered_at')}),
    )

    def score_display(self, obj):
        if obj.score is not None:
            return format_html('<span style="color: darkblue; font-weight:bold;">{}</span>', obj.score)
        return '-'
    score_display.short_description = 'نمره'