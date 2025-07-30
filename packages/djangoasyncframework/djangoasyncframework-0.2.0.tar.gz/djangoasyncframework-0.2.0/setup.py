from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="djangoasyncframework",
    version="0.2.0",
    packages=find_packages(),
    description="Django Async Framework provides an async-first approach to Django, enabling non-blocking ORM, views, serializers, and background tasks for improved performance.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="mouhamaddev",
    author_email="mouhamaddev04@gmail.com",
    url="https://github.com/mouhamaddev/django-async-framework",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True   
)
