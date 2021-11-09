"""myInternetPrj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

#    venv\Scripts\activate.bat  -> 가상환경 실행

#    django-admin startproject myInternetPrj .  -> 여기서 manage.py, Prj 생성

#    python manage.py runserver  -> 서버

#    python manage.py migrate -> 데이터베이스 마이그레이션
#    python manage.py createsuperuser  -> 관리자 계정 생성

#    python manage.py startapp blog  -> blog 앱 생성
#    python manage.py startapp single_pages  -> single_pages 앱 생성

#    blog>models.py>Post class 작성 후 반영하기 위해
#    myInternetPrj>settings.py의 INSTALLED_APPS에 'blog', 'single_pages' 추가
#    python manage.py makemigrations  -> create model
#    python manage.py migrate  -> 데이터베이스에 반영
#    blog>admin.py에 admin.site.register(Post) 등록해야 admin에 model 등록됨
"""
from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('blog/', include('blog.urls')),     # 서버IP/blog #blog app에 urls.py 생성
    path('admin/', admin.site.urls),    # 서버IP/admin
    path('', include('single_pages.urls')),     # 서버IP/
    path('markdownx/', include('markdownx.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)     # 서버IP/media/  #head_image 사용을 위해 추가 #myInternetPrj/settings.py에 import os, MEDIA_URL = '/media/', MEDIA_ROOT = os.path.join(BASE_DIR, '_media') 추가
