from django.db import models

class ActiveObjectsManager(models.Manager):
    """
    ⚙️ این Manager سفارشی فقط آبجکت‌هایی را برمی‌گرداند که status آنها برابر با DELETED نباشد.

    چرا استفاده می‌کنیم؟
    - در اکثر پروژه‌های واقعی، ما آبجکت‌ها را به‌صورت soft-delete حذف می‌کنیم (با تغییر وضعیت status به 'DELETED')
    - نمی‌خواهیم آبجکت‌های حذف شده در کوئری‌های معمولی دیده شوند
    - با این Manager می‌توانیم در مدل اصلی، به‌صورت پیش‌فرض فقط آبجکت‌های «فعال» یا «غیرفعال» (ولی حذف‌نشده) را داشته باشیم

    نحوه‌ی استفاده:
    - در مدل اصلی اضافه می‌کنیم:
        objects = ActiveObjectsManager()  # فقط آبجکت‌های حذف نشده
        all_objects = models.Manager()    # همه‌ی آبجکت‌ها (حتی حذف شده‌ها)

    مثال:
        MyModel.objects.all()      --> فقط حذف نشده‌ها
        MyModel.all_objects.all()  --> همه‌ی رکوردها شامل حذف شده‌ها

    ⚠️ توجه:
    - این کار کوئری‌های پیش‌فرض را امن‌تر می‌کند
    - برای دسترسی به آبجکت‌های حذف شده، باید از all_objects استفاده کنیم
    """

    def get_queryset(self):
        # فقط رکوردهایی که status != DELETED دارند
        return super().get_queryset().exclude(status=self.model.Status.FINISHED)
