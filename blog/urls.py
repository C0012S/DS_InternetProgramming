from django.urls import path
from . import views

urlpatterns = [ # 서버IP/blog/
#    path('<int:pk>/', views.single_post_page), #view에 있는 함수 호출
#    path('', views.index),     # 서버IP/blog

    path('category/<str:slug>', views.category_page),
    path('<int:pk>/', views.PostDetail.as_view()),
    path('', views.PostList.as_view()), #함수 대신 클래스 호출
]