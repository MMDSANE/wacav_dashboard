from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Student
from .forms import StudentCreationForm, StudentChangeForm

# شخصی‌سازی ظاهر کلی پنل
admin.site.site_header = '🎓 پنل مدیریت دانشجویان'
admin.site.site_title = 'داشبورد مدیریت'
admin.site.index_title = 'خوش آمدید به داشبورد مدیریت سایت'

@admin.register(Student)
class StudentAdmin(UserAdmin):
    model = Student
    add_form = StudentCreationForm
    form = StudentChangeForm

    list_display = ('colored_username', 'student_id', 'full_name', 'phone_number', 'status_badge', 'is_active', 'is_staff')
    list_display_links = ('colored_username', 'student_id')

    search_fields = ('username', 'student_id', 'first_name', 'last_name', 'phone_number')

    list_filter = ('is_active', 'is_staff', 'is_superuser', 'status')

    ordering = ('student_id',)

    readonly_fields = ('student_id', 'last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'phone_number', 'status')}),
        ('مجوزها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('اطلاعات مهم', {'fields': ('student_id',)}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2',
                'first_name', 'last_name', 'phone_number', 'score', 'status',
                'is_active', 'is_staff'
            )}
        ),
    )

    def full_name(self, obj):
        return obj.full_name()
    full_name.short_description = 'نام کامل دانشجو'

    def colored_username(self, obj):
        return format_html('<span style="color: #2e86de; font-weight:bold;">{}</span>', obj.username)
    colored_username.short_description = 'نام کاربری'

    def status_badge(self, obj):
        color = 'green' if obj.status == obj.Status.REGISTERED else 'gray'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'وضعیت'

    # می‌تونی این متد رو بسازی اگر میخوای رنگی یا قالب خاص برای نمره داشته باشی، مثلا:
    def colored_score(self, obj):
        if obj.score >= 85:
            color = 'green'
        elif obj.score >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.score)
    colored_score.short_description = 'نمره'

    # اگر خواستی بجای 'score' از 'colored_score' در list_display استفاده کنی:
    # list_display = ('colored_username', 'student_id', 'full_name', 'phone_number', 'colored_score', 'status_badge', 'is_active', 'is_staff')

    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "فعال‌سازی دانشجویان انتخاب‌شده"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "غیرفعال‌سازی دانشجویان انتخاب‌شده"
