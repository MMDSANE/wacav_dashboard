import logging
from rest_framework.permissions import BasePermission  # ایمپورت کلاس پایه پرمیشن از DRF
from .utils import error_log
# ایجاد logger اختصاصی برای این فایل (نامش همان نام فایل خواهد بود)

"""
این فایل برای مدیریت سطح دسترسی (Permissions) کاربران در پروژه است.
در اولین فرصت می‌توان پرمیشن‌های بیشتری را اضافه یا کامل کرد.
"""

class IsAdminGroup(BasePermission):
    """
    این پرمیشن اجازه دسترسی می‌دهد فقط به:
    - کاربران گروه‌های 'Admin' یا 'HeadAdmin'
    - یا ابرمدیر (is_superuser=True)
    """
    def has_permission(self, request, view):
        try:
            user = getattr(request, 'user', None)  # گرفتن شی user از request به صورت ایمن
            if not user or not user.is_authenticated:  # بررسی اینکه کاربر وجود دارد و لاگین کرده است
                return False
            if getattr(user, 'is_superuser', False):  # اگر کاربر ابرمدیر باشد
                return True
            if getattr(user, 'rule', None) in ["Admin", "HeadAdmin"]:  # اگر نقش کاربر Admin یا HeadAdmin باشد
                return True
            return False  # در غیر این صورت دسترسی ندارد
        except Exception as e:  # اگر هر خطایی پیش آمد
            error_log(logging.ERROR, f"Error in function: {str(e)}", exception=e)
            return False  # باز هم دسترسی نده تا ایمن باشد


class IsSelfOrAdmin(BasePermission):
    """
    اجازه دسترسی به:
    - خود کاربر (id کاربر و id آبجکت یکی باشد)
    - کاربران Admin و HeadAdmin
    - یا ابرمدیر
    """
    def has_object_permission(self, request, view, obj):
        try:
            user = getattr(request, 'user', None)  # گرفتن کاربر از request
            if not user or not user.is_authenticated:  # بررسی لاگین بودن کاربر
                return False

            # تلاش برای به‌دست‌آوردن id از شیء obj
            user_id = getattr(obj, "id", None)
            if user_id is None and hasattr(obj, "user"):
                user_id = getattr(obj.user, "id", None)  # اگر obj فیلد user داشته باشد، id آن را بگیر

            if getattr(user, 'is_superuser', False):  # اگر کاربر ابرمدیر است
                return True
            if getattr(user, 'rule', None) in ["Admin", "HeadAdmin"]:  # اگر نقش کاربر Admin یا HeadAdmin است
                return True
            if user.id == user_id:  # اگر کاربر صاحب همان آبجکت باشد
                return True

            return False  # در غیر این صورت اجازه ندارد
        except Exception as e:  # در صورت بروز هر خطا
            error_log(logging.ERROR, f"Error in function: {str(e)}", exception=e)
            return False


class IsCustomer(BasePermission):
    """
    این پرمیشن فقط به کاربری اجازه می‌دهد که rule او 'Customer' باشد.
    """
    def has_permission(self, request, view):
        try:
            user = getattr(request, 'user', None)  # گرفتن user ایمن
            if not user or not user.is_authenticated:  # بررسی احراز هویت
                return False
            return getattr(user, 'rule', None) == "Customer"  # اگر نقش کاربر Customer بود، اجازه بده
        except Exception as e:
            error_log(logging.ERROR, f"Error in function: {str(e)}", exception=e)
            return False


class IsSeller(BasePermission):
    """
    این پرمیشن فقط به کاربری اجازه می‌دهد که rule او 'Seller' باشد.
    """
    def has_permission(self, request, view):
        try:
            user = getattr(request, 'user', None)  # گرفتن user
            if not user or not user.is_authenticated:  # بررسی لاگین بودن
                return False
            return getattr(user, 'rule', None) == "Seller"  # اگر نقش Seller بود اجازه بده
        except Exception as e:
            error_log(logging.ERROR, f"Error in function: {str(e)}", exception=e)
            return False


class IsHeadAdmin(BasePermission):
    """
    این پرمیشن فقط به کاربری اجازه می‌دهد که rule او 'HeadAdmin' باشد.
    """
    def has_permission(self, request, view):
        try:
            user = getattr(request, 'user', None)  # گرفتن user
            if not user or not user.is_authenticated:  # بررسی احراز هویت
                return False
            return getattr(user, 'rule', None) == "HeadAdmin"  # اگر نقش HeadAdmin بود، اجازه بده
        except Exception as e:
            error_log(logging.ERROR, "Function Failed", exception=e)
            return False
