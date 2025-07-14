from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('home/', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.logout_view, name='logout_view'),

    path('videos/', views.videos_dashboard, name='videos_dashboard'),
    path('videos/download/<int:video_id>/', views.download_video, name='download_video'),

    path('resources/', views.resources_dashboard, name='resources_dashboard'),

    path('assignments/', views.assignments_dashboard, name='assignments_dashboard'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),

    path('support/', views.support_dashboard, name='support_dashboard'),
    path('support/submit/', views.submit_ticket, name='submit_ticket'),

    path('notifications/', views.notifications_dashboard, name='notifications_dashboard'),
    path('notifications/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
]
