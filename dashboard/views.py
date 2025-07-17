from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .models import *
from django.urls import reverse
from django.contrib.auth import logout
import logging, json
from django.http import FileResponse, JsonResponse, Http404
from core.utils import create_course_notification
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
import mimetypes, os
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta



# تابع برای ساخت نوتیفیکیشن
def create_notification(course, message_type, item_title=None, item_id=None):
    """
    تابع برای ساخت نوتیفیکیشن جدید
    course: کلاس مربوطه
    message_type: نوع پیام (video, assignment, resource, etc.)
    item_title: عنوان آیتم جدید
    item_id: آیدی آیتم جدید
    """
    messages = {
        'video': f'ویدیو جدید "{item_title}" به کلاس {course.title} اضافه شد',
        'assignment': f'تکلیف جدید "{item_title}" به کلاس {course.title} اضافه شد',
        'resource': f'منبع جدید "{item_title}" به کلاس {course.title} اضافه شد',
        'roadmap': f'مرحله جدید "{item_title}" به نقشه راه کلاس {course.title} اضافه شد',
        'general': f'اطلاعیه جدید در کلاس {course.title}',
    }

    message = messages.get(message_type, f'بروزرسانی جدید در کلاس {course.title}')

    # ایجاد نوتیفیکیشن
    notification = Notification.objects.create(
        course=course,
        message=message,
        created_at=timezone.now(),
        is_read=False
    )

    return notification



def update_notifications_for_user(user):
    """
    برای همه‌ی دوره‌هایی که کاربر عضو است، بررسی می‌کنه
    و اگر آیتم جدید اومده ولی براش نوتیفیکیشن ساخته نشده، می‌سازه.
    """
    user_courses = Course.objects.filter(students=user)

    # ویدیوهای جدید
    videos = VideoItem.objects.filter(course__in=user_courses)
    for video in videos:
        message = f"ویدیوی جدید اضافه شد: {video.title}"
        if not Notification.objects.filter(course=video.course, message=message).exists():
            Notification.objects.create(course=video.course, message=message)

    # تکالیف جدید
    assignments = Assignment.objects.filter(course__in=user_courses)
    for assignment in assignments:
        message = f"تکلیف یا آزمون جدید اضافه شد: {assignment.title}"
        if not Notification.objects.filter(course=assignment.course, message=message).exists():
            Notification.objects.create(course=assignment.course, message=message)

    # منابع جدید
    sections = ResourceSection.objects.filter(course__in=user_courses).prefetch_related('links')
    for section in sections:
        for link in section.links.all():
            message = f"منبع جدید اضافه شد: {link.title}"
            if not Notification.objects.filter(course=section.course, message=message).exists():
                Notification.objects.create(course=section.course, message=message)

    # استپ‌های جدید نقشه راه
    roadmap_steps = RoadmapStep.objects.filter(course__in=user_courses)
    for step in roadmap_steps:
        message = f"مرحله جدید اضافه شد: {step.title}"
        if not Notification.objects.filter(course=step.course, message=message).exists():
            Notification.objects.create(course=step.course, message=message)



# ========================= DASHBOARD VIEWS =========================

@login_required(login_url='/login/')
def student_dashboard(request):
    user = request.user

    # فرض می‌کنیم کاربر از مدل Student باشه یا ارتباط داشته باشه
    # اگر مستقیماً از settings.AUTH_USER_MODEL استفاده کردی و پرچم student داری، می‌تونی فیلتر کنی
    student_courses = Course.objects.filter(students=user)

    # به‌روزرسانی نوتیفیکیشن‌ها
    update_notifications_for_user(user)

    # ویدیوها، منابع و تکالیف همه کلاس‌های دانشجو
    videos = VideoItem.objects.filter(course__in=student_courses).order_by('order')
    assignments = Assignment.objects.filter(course__in=student_courses).order_by('-created_at')

    # نوتیفیکیشن‌های مربوط به کلاس‌هایی که دانشجو عضو هست
    notifications = Notification.objects.filter(course__in=student_courses).order_by('-created_at')

    new_notifications_count = Notification.objects.filter(course__in=student_courses, is_read=False).count()

    # تیکت‌های ارسال شده توسط این دانشجو
    tickets = Ticket.objects.filter(student=user)

    # نقشه راه هر کلاس
    road_map_step = RoadmapStep.objects.filter(course__in=student_courses).order_by('order')

    # نمره دانشجو در هر کلاس
    # دیکشنری: course.id => CourseStudent object
    course_students_map = {
        cs.course_id: cs
        for cs in CourseStudent.objects.filter(student=user, course__in=student_courses)
    }

    # برای هر کورس استپ‌هاش رو بیار
    course_roadmaps = {}
    for course in student_courses:
        steps = RoadmapStep.objects.filter(course=course).order_by('order')
        course_roadmaps[course.id] = steps

    context = {
        'user': user,
        'courses': student_courses,
        'videos': videos,
        'assignments': assignments,
        'notifications': notifications,
        'new_notifications_count': new_notifications_count,
        'tickets': tickets,
        'road_map_step': road_map_step,
        'course_students_map': course_students_map,
        'course_roadmaps': course_roadmaps,
    }

    return render(request, 'dashboard/index.html', context)


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'dashboard/course_detail.html', {'course': course})


# ========================= VIDEO VIEWS =========================

@login_required
def videos_dashboard(request):
    user = request.user

    # فقط دوره‌هایی که دانشجو عضو است
    user_courses = Course.objects.filter(students=user)

    # به‌روزرسانی نوتیفیکیشن‌ها
    update_notifications_for_user(user)

    # فقط ویدیوهای مربوط به این دوره‌ها
    videos = VideoItem.objects.filter(course__in=user_courses).order_by('order')

    # شمارش نوتیفیکیشن‌های جدید
    new_notifications_count = Notification.objects.filter(course__in=user_courses, is_read=False).count()

    # بررسی و ایجاد نوتیفیکیشن برای ویدیوهای جدید (فقط اگر نوتیفیکیشنی برای این ویدیو ندارند)
    for video in videos:
        message = f"ویدیوی جدید اضافه شد: {video.title}"
        exists = Notification.objects.filter(course=video.course, message=message).exists()
        if not exists:
            Notification.objects.create(course=video.course, message=message)

    context = {
        'videos': videos,
        'new_notifications_count': new_notifications_count,
    }
    return render(request, 'dashboard/videos.html', context)



@login_required(login_url='/login/')
def download_video(request, video_id):
    video = get_object_or_404(VideoItem, id=video_id)
    file_path = video.src.path  # تغییر از video_file به src
    with open(file_path, 'rb') as file:
        response = FileResponse(file, content_type='video/mp4')
        response['Content-Disposition'] = f'attachment; filename="{video.src.name.split("/")[-1]}"'
        return response


# ========================= RESOURCE VIEWS =========================

@login_required
def resources_dashboard(request):
    user = request.user
    # فقط دوره‌هایی که کاربر در آنها عضو است
    user_courses = Course.objects.filter(students=user)

    # به‌روزرسانی نوتیفیکیشن‌ها
    update_notifications_for_user(user)

    # فقط بخش‌هایی که متعلق به این دوره‌ها هستند
    sections = ResourceSection.objects.filter(course__in=user_courses).prefetch_related('links').order_by('order')

    # شمارش نوتیفیکیشن‌های جدید
    new_notifications_count = Notification.objects.filter(course__in=user_courses, is_read=False).count()

    # بررسی و ایجاد نوتیفیکیشن برای لینک‌های جدید منابع
    for section in sections:
        for link in section.links.all():
            message = f"منبع جدید اضافه شد: {link.title}"
            exists = Notification.objects.filter(course=section.course, message=message).exists()
            if not exists:
                Notification.objects.create(course=section.course, message=message)

    context = {
        'sections': sections,
        'new_notifications_count': new_notifications_count,
    }
    return render(request, 'dashboard/resources.html', context)


# ========================= ASSIGNMENT VIEWS =========================

# تنظیم لاگر برای دیباگ
logger = logging.getLogger(__name__)


@login_required(login_url='/login/')
def assignments_dashboard(request):
    user = request.user

    # فقط دوره‌هایی که کاربر در آنها عضو است
    courses = Course.objects.filter(students=user)

    # به‌روزرسانی نوتیفیکیشن‌ها
    update_notifications_for_user(user)

    # تکالیف را برای هر دوره دسته‌بندی می‌کنیم
    assignments_by_course = {}
    for course in courses:
        assignments = course.assignments.all().order_by('-created_at')
        assignments_by_course[course.id] = assignments

        # بررسی و ایجاد نوتیفیکیشن برای تکالیف جدید
        for assignment in assignments:
            message = f"تکلیف یا آزمون جدید اضافه شد: {assignment.title}"
            exists = Notification.objects.filter(course=course, message=message).exists()
            if not exists:
                Notification.objects.create(course=course, message=message)

    # همه‌ی ارسال‌های دانشجو
    submissions = AssignmentSubmission.objects.filter(student=user)
    submissions_map = {s.assignment_id: s for s in submissions}

    # نوتیفیکیشن‌های جدید برای دوره‌های کاربر
    student_courses = Course.objects.filter(students=user)
    new_notifications = Notification.objects.filter(
        course__in=student_courses,
        is_read=False
    ).order_by('-created_at')
    new_notifications_count = new_notifications.count()

    # لاگ برای دیباگ
    logger.debug(f"User: {user.username}, New notifications count: {new_notifications_count}")

    if request.method == 'POST':
        assignment_id = request.POST.get('assignment_id')
        github_link = request.POST.get('github_link')
        assignment = get_object_or_404(Assignment, id=assignment_id, course__in=courses)

        submission, created = AssignmentSubmission.objects.get_or_create(
            assignment=assignment,
            student=user
        )
        submission.github_link = github_link
        submission.status = AssignmentSubmission.Status.SUBMITTED
        submission.save()

        return redirect(reverse('dashboard:assignments_dashboard'))

    context = {
        'now': timezone.now(),
        'courses': courses,
        'assignments_by_course': assignments_by_course,
        'submissions_map': submissions_map,
        'new_notifications_count': new_notifications_count,
        'new_notifications': new_notifications,  # برای دیباگ اضافه شده
    }

    return render(request, 'dashboard/assignments.html', context)



@login_required(login_url='/login/')
def download_file(request, file_id):
    """
    دانلود هر فایلی که در مدل Assignment ذخیره شده.
    """
    try:
        assignment = get_object_or_404(Assignment, id=file_id)
        file_field = assignment.file  # فرض بر این است که فیلد فایل در مدل Assignment با نام file است
        if not file_field:
            raise Http404("فایل موجود نیست.")
        file_path = file_field.path
        file_name = os.path.basename(file_path)

        response = FileResponse(open(file_path, 'rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise Http404("مشکلی در دانلود فایل پیش آمد.")

# ========================= SUPPORT VIEWS =========================

@login_required
def support_dashboard(request):
    user = request.user

    # فقط دورههایی که دانشجو عضو است
    user_courses = Course.objects.filter(students=user)

    # بهروزرسانی نوتیفیکیشنها
    update_notifications_for_user(user)

    # تیکتهای این کاربر (پایه)
    tickets = Ticket.objects.filter(student=user).select_related('student')

    # پارامترهای سرچ
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date_filter', '')
    sort_by = request.GET.get('sort', '-created_at')

    # سرچ سریع در موضوع، پیام و پاسخ
    if search_query:
        tickets = tickets.filter(
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query) |
            Q(feedback__icontains=search_query)
        )

    # فیلتر بر اساس وضعیت
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    # فیلتر بر اساس تاریخ
    if date_filter:
        today = timezone.now().date()
        if date_filter == 'today':
            tickets = tickets.filter(created_at__date=today)
        elif date_filter == 'week':
            week_ago = today - timedelta(days=7)
            tickets = tickets.filter(created_at__date__gte=week_ago)
        elif date_filter == 'month':
            month_ago = today - timedelta(days=30)
            tickets = tickets.filter(created_at__date__gte=month_ago)
    # مرتب‌سازی
    valid_sort_fields = ['-created_at', 'created_at', '-updated_at', 'updated_at', 'subject', '-subject', 'status']
    if sort_by in valid_sort_fields:
        tickets = tickets.order_by(sort_by)
    else:
        tickets = tickets.order_by('-created_at')

    # صفحه‌بندی
    paginator = Paginator(tickets, 6)  # 10 تیکت در هر صفحه
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # شمارش نوتیفیکیشنهای جدید
    new_notifications_count = Notification.objects.filter(
        course__in=user_courses,
        is_read=False
    ).count()

    # آمار سریع
    total_tickets = tickets.count()
    open_tickets = tickets.filter(status__in=['NE', 'IP']).count()
    closed_tickets = tickets.filter(status='CL').count()

    context = {
        'page_obj': page_obj,
        'tickets': page_obj,  # برای سازگاری با تمپلیت قدیمی
        'new_notifications_count': new_notifications_count,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'sort_by': sort_by,
        'status_choices': Ticket.Status.choices,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'closed_tickets': closed_tickets,
    }
    return render(request, 'dashboard/support.html', context)


@login_required(login_url='/login/')
def submit_ticket(request):
    if request.method == 'POST':
        try:
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            user = request.user

            if not subject or not message:
                logger.warning("Subject or message missing")
                return JsonResponse({'success': False, 'error': 'موضوع و پیام الزامی است'}, status=400)

            ticket = Ticket.objects.create(
                student=user,
                subject=subject,
                message=message,
                status='NE'
            )
            logger.info(f"Ticket created: {ticket.id} by {user.username}")
            return JsonResponse({'success': True})

        except Exception as e:
            logger.error(f"Error in submit_ticket: {str(e)}")
            return JsonResponse({'success': False, 'error': f'خطای سرور: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'}, status=400)


# ========================= NOTIFICATION VIEWS =========================

@login_required
def notifications_dashboard(request):
    user = request.user

    # فقط دوره‌هایی که کاربر در آنها عضو است
    user_courses = Course.objects.filter(students=user)

    # به‌روزرسانی نوتیفیکیشن‌ها
    update_notifications_for_user(user)

    # نوتیفیکیشن‌های مربوط به این دوره‌ها
    notifications = Notification.objects.filter(
        course__in=user_courses
    ).select_related('course').order_by('-created_at')

    # شمارش نوتیفیکیشن‌های جدید (خوانده نشده)
    new_notifications_count = notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications,
        'new_notifications_count': new_notifications_count,
    }
    return render(request, 'dashboard/notifications.html', context)



@login_required(login_url='/login/')
def mark_notification_read(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            notification_id = data.get('notification_id')

            if not notification_id:
                return JsonResponse({'success': False, 'error': 'آیدی نوتیفیکیشن مشخص نشده'}, status=400)

            # بررسی دسترسی کاربر به نوتیفیکیشن
            notification = get_object_or_404(
                Notification,
                id=notification_id,
                course__students=request.user
            )

            notification.is_read = True
            notification.save()

            logger.info(f"Notification {notification_id} marked as read by {request.user.username}")
            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'فرمت JSON نامعتبر'}, status=400)
        except Exception as e:
            logger.error(f"Error in mark_notification_read: {str(e)}")
            return JsonResponse({'success': False, 'error': f'خطای سرور: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'}, status=405)


@login_required(login_url='/login/')
def mark_all_notifications_read(request):
    if request.method == 'POST':
        try:
            # دوره‌هایی که کاربر عضو آنهاست
            user_courses = Course.objects.filter(students=request.user)

            # تمام نوتیفیکیشن‌های خوانده نشده کاربر
            notifications = Notification.objects.filter(
                course__in=user_courses,
                is_read=False
            )

            # تعداد نوتیفیکیشن‌های به‌روزرسانی شده
            count = notifications.update(is_read=True)

            logger.info(f"{count} notifications marked as read by {request.user.username}")
            return JsonResponse({'success': True, 'count': count})

        except Exception as e:
            logger.error(f"Error in mark_all_notifications_read: {str(e)}")
            return JsonResponse({'success': False, 'error': f'خطای سرور: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'}, status=405)


# ========================= AUTH VIEWS =========================

def logout_view(request):
    logout(request)
    return redirect(reverse('accounts:student_login'))


# ========================= UTILITY FUNCTIONS FOR ADMIN =========================

def create_video_notification(video_instance):
    """
    برای استفاده در admin panel یا signals
    """
    return create_notification(
        course=video_instance.course,
        message_type='video',
        item_title=video_instance.title,
        item_id=video_instance.id
    )


def create_assignment_notification(assignment_instance):
    """
    برای استفاده در admin panel یا signals
    """
    return create_notification(
        course=assignment_instance.course,
        message_type='assignment',
        item_title=assignment_instance.title,
        item_id=assignment_instance.id
    )


def create_resource_notification(resource_instance):
    """
    برای استفاده در admin panel یا signals
    """
    return create_notification(
        course=resource_instance.section.course,
        message_type='resource',
        item_title=resource_instance.title,
        item_id=resource_instance.id
    )


def create_roadmap_notification(roadmap_instance):
    """
    برای استفاده در admin panel یا signals
    """
    return create_notification(
        course=roadmap_instance.course,
        message_type='roadmap',
        item_title=roadmap_instance.title,
        item_id=roadmap_instance.id
    )