from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Student

class StudentCreationForm(UserCreationForm):
    class Meta:
        model = Student
        fields = ('username', 'password')

    def clean_username(self):
        username = self.cleaned_data['username']
        # اینجا می‌تونی هرچی دلت می‌خواد اجازه بدی؛ مثلاً فارسی و فاصله
        return username

class StudentChangeForm(UserChangeForm):
    class Meta:
        model = Student
        fields = ('username', 'password')



class StudentLoginForm(forms.Form):
    username = forms.CharField(
        label="نام کاربری",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کاربری'})
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'رمز عبور'})
    )

