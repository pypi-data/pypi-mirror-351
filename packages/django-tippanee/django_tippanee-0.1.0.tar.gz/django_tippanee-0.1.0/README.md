# Django Tippanee

A reusable Django app for a generic comment system with DRF API support, using `GenericForeignKey` to attach comments to any model.

## Installation

```bash
pip install django-tippanee  # after uploading to pypi

pip install git+https://github.com/urwithajit9/django-tippanee.git
```

## Usage

- Add to INSTALLED_APPS:

```python

INSTALLED_APPS = [
    ...
    'django_tippanee',
]
```

- Include URLs:

```python
urlpatterns = [
    path('api/comments/', include('django_tippanee.urls')),
]

```

- Run migrations

```python
python manage.py migrate
```

## API Endpoints

- GET /api/comments/: List comments (filter by content_type, object_id).

- POST /api/comments/: Create a comment.
