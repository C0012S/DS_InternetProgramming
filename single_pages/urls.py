from django.urls import path
from . import views

urlpatterns = [ # 서버IP/
    path('', views.langing),    # 서버IP/
    path('about_me', views.about_me)    # 서버 IP/about_me/
]