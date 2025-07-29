# django-vendor-images

A reusable Django app for handling vendor/shop images.

## Features

- Upload and manage vendor images (logos, banners, etc.)
- Automatically organize images by vendor and date
- Easy integration with Django projects
- Supports image resizing and optimization using Pillow

## Installation

```bash
pip install django-vendor-images

Add "vendor_images" to your INSTALLED_APPS in settings.py.
INSTALLED_APPS = [
    ...
    'vendor_images',
]

Run migrations:
python manage.py migrate vendor_images


Use the models and utilities to handle vendor images in your project.
