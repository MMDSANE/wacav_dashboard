from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('home/', views.student_dashboard, name='student_dashboard'),
    path('videos/', views.videos_dashboard, name='videos_dashboard'),
    path('resources/', views.resources_dashboard, name='resources_dashboard'),
    path('assignments/', views.assignments_dashboard, name='assignments_dashboard'),
    path('support/', views.support_dashboard, name='support_dashboard'),
    path('notifications/', views.notifications_dashboard, name='notifications_dashboard'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('assignments/', views.assignments_dashboard, name='assignments_dashboard'),
    path('logout/', views.logout_view, name='logout_view'),

]
