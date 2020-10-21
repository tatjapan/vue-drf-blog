# vue-drf-blog

Blog app w/ Django REST framework & Vue.js

## How to Install

### Try it right now

```
git clone https://github.com/tatjapan/vue-drf-blog
cd vue-drf-blog/backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Access tp `http://127.0.0.1:8000/blog/`, and enjoy it!

### Install to your project

```
pip install https://github.com/tatjapan/vue-drf-blog/archive/master.tar.gz
```

Add following settings to `settings.py`

```python
INSTALLED_APPS = [
    'blog.apps.BlogConfig',  # ADD
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework'  # ADD
]
```

e.x. Settings about media files

```python
# Settings about upload files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

`urls.py`

```python
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
]


# Settings for development
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
```


Migrate and create superuser

```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```