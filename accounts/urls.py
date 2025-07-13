# accounts/urls.py
from django.urls import path
from .views import student_login, student_logout

app_name = 'accounts'


urlpatterns = [
    path('login/', student_login, name='student_login'),
    path('logout/', student_logout, name='student_logout'),

]
