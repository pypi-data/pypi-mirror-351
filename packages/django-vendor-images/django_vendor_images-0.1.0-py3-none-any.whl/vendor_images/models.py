from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from .utils import TimeStampedModel, vendor_image_upload_to
import os


class VendorImage(TimeStampedModel):
    """
    Model for vendor images, including different types of images (logo, banner, gallery, etc.).
    Images are optimized before saving and their file size is validated.
    """

    class ImageType(models.TextChoices):
        """
        Different types of vendor images.
        """
        PRODUCT_MAIN = 'product_main', _('Main product image')
        PRODUCT_GALLERY = 'product_gallery', _('Product gallery')
        BANNER = 'banner', _('Banner')
        LOGO = 'logo', _('Logo')
        SLIDER = 'slider', _('Slider')
        CERTIFICATE = 'certificate', _('Certificate')
        OTHER = 'other', _('Other')

    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Vendor')
    )
    image_name = models.CharField(
        _('Image name'),
        max_length=100,
        help_text=_('Descriptive name for easier image identification')
    )
    image = models.ImageField(
        _('Image'),
        upload_to=vendor_image_upload_to,
        height_field='image_height',
        width_field='image_width'
    )
    image_type = models.CharField(
        _('Image type'),
        max_length=20,
        choices=ImageType.choices,
        default=ImageType.PRODUCT_GALLERY
    )
    image_height = models.PositiveIntegerField(
        editable=False,
        null=True,
        help_text=_('Image height is automatically recorded')
    )
    image_width = models.PositiveIntegerField(
        editable=False,
        null=True,
        help_text=_('Image width is automatically recorded')
    )
    size_in_mb = models.DecimalField(
        _('File size (MB)'),
        max_digits=5,
        decimal_places=2,
        editable=False,
        null=True,
        help_text=_('Uploaded file size in megabytes')
    )
    caption = models.CharField(
        _('Image caption'),
        max_length=100,
        blank=True,
        help_text=_('Optional caption for displaying the image')
    )
    alt_text = models.CharField(
        _('Alternative text'),
        max_length=125,
        blank=True,
        help_text=_('Descriptive text for accessibility and SEO')
    )
    order = models.PositiveIntegerField(
        _('Display order'),
        default=0,
        help_text=_('Order of image display in the gallery')
    )

    class Meta:
        verbose_name = _('Vendor image')
        verbose_name_plural = _('Vendor images')
        ordering = ('order', 'created_at')
        constraints = [
            models.UniqueConstraint(
                fields=['vendor', 'image_name'],
                name='unique_image_name_per_vendor'
            )
        ]

    def __str__(self):
        """
        String representation including image name and vendor name.
        """
        return f"{self.image_name} ({self.vendor})"

    def save(self, *args, **kwargs):
        """
        Before saving the image:
        - Optimize the image by converting to JPEG format with quality 90
        - Assign the image file name
        - Calculate the image file size in MB
        """
        if self.image:
            img = Image.open(self.image)

            # Convert to RGB if image mode is different (e.g., PNG with RGBA)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Optimize and compress the image
            output = BytesIO()
            img.save(output, format='JPEG', quality=90)
            output.seek(0)

            # Replace the uploaded file with the optimized version
            filename_root, ext = os.path.splitext(self.image.name)
            self.image = InMemoryUploadedFile(
                output,
                'ImageField',
                f"{filename_root}.jpg",
                'image/jpeg',
                output.getbuffer().nbytes,
                None
            )

        # If image_name is empty, automatically assign the file name
        if not self.image_name and self.image:
            self.image_name = self.image.name.split('/')[-1]

        # Calculate file size in MB for database storage
        if self.image and hasattr(self.image, 'file'):
            self.size_in_mb = round(self.image.file.size / (1024 * 1024), 2)

        super().save(*args, **kwargs)

    def clean(self):
        """
        Validation before saving:
        - Check that the image size does not exceed the allowed max size in settings.
        """
        super().clean()

        # Read max allowed image size from settings, default to 5 MB if not set
        max_size = getattr(settings, 'VENDOR_IMAGE_MAX_SIZE_MB', 5)

        if self.image and hasattr(self.image, 'file'):
            file_size = self.image.file.size
            if file_size > max_size * 1024 * 1024:
                raise ValidationError({
                    'image': _(f"Image size cannot exceed {max_size} MB")
                })

    @property
    def image_url(self):
        """
        URL of the uploaded image.
        """
        return self.image.url if self.image else None

    @property
    def dimensions(self):
        """
        Returns image dimensions as "widthxheight".
        """
        if self.image_width and self.image_height:
            return f"{self.image_width}x{self.image_height}"
        return None
