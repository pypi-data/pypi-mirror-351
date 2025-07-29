from django.db import models
from datetime import datetime
from django.utils.translation import gettext_lazy as _
import uuid



def vendor_image_upload_to(instance, filename):
    if instance.vendor.id is None:
        raise ValueError("ابتدا باید فروشنده ذخیره شود تا تصویر به مسیر مشخصی آپلود شود.")

    now = datetime.now()
    ext = filename.split('.')[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    return f'vendors/{instance.vendor.id}/{now.year}/{now.month}/{unique_name}'



class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)

    class Meta:
        abstract = True  # این مدل فقط برای ارث‌بری است و جدول مستقلی ایجاد نمی‌کند
