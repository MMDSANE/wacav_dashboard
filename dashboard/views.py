from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .models import *
from django.urls import reverse
from django.contrib.auth import logout



@login_required(login_url='/login/')
def student_dashboard(request):
    user = request.user

    # فرض می‌کنیم کاربر از مدل Student باشه یا ارتباط داشته باشه
    # اگر مستقیماً از settings.AUTH_USER_MODEL استفاده کردی و پرچم student داری، می‌تونی فیلتر کنی
    student_courses = Course.objects.filter(students=user)

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

@login_required
def videos_dashboard(request):
    return render(request, 'dashboard/videos.html', context={})

@login_required
def resources_dashboard(request):
    return render(request, 'dashboard/resources.html', context={})


@login_required(login_url='/login/')
def assignments_dashboard(request):
    user = request.user

    courses = Course.objects.filter(students=user)

    # تکالیف را برای هر دوره دسته‌بندی می‌کنیم
    assignments_by_course = {}
    for course in courses:
        assignments_by_course[course.id] = course.assignments.all().order_by('-created_at')

    # همه‌ی ارسال‌های دانشجو
    submissions = AssignmentSubmission.objects.filter(student=user)
    submissions_map = {s.assignment_id: s for s in submissions}

    # نوتیفیکیشن‌های جدید
    student_courses = Course.objects.filter(students=user)
    new_notifications_count = Notification.objects.filter(course__in=student_courses, is_read=False).count()

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
        'courses': courses,
        'assignments_by_course': assignments_by_course,
        'submissions_map': submissions_map,
        'new_notifications_count': new_notifications_count,

    }
    return render(request, 'dashboard/assignments.html', context)


@login_required
def support_dashboard(request):
    return render(request, 'dashboard/support.html', context={})

@login_required
def notifications_dashboard(request):
    return render(request, 'dashboard/notifications.html', context={})



def logout_view(request):
    logout(request)
    return redirect(reverse('accounts:student_login'))
