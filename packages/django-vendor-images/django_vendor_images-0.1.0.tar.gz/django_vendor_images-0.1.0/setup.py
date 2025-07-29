from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-vendor-images",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django>=3.2",
        "Pillow>=9.0"
    ],
    license="MIT",
    description="Reusable Django app for handling vendor/shop images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mehran-jafari/django-vendor-images",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 5.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    author="Mehran Jafari",
    author_email="eng.mehranjafarii@gmail.com",
)
