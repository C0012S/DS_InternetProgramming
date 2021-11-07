from django.urls import path
from . import views

urlpatterns = [ # 서버IP/blog/
#    path('<int:pk>/', views.single_post_page), #view에 있는 함수 호출
#    path('', views.index),     # 서버IP/blog

    path('update_post/<int:pk>/', views.PostUpdate.as_view()), #수정 페이지인 경우 post를 특정해 줘야 한다
    path('create_post/', views.PostCreate.as_view()),
    path('tag/<str:slug>', views.tag_page),
    path('category/<str:slug>', views.category_page), # 서버IP/blog/category/slug
    path('<int:pk>/', views.PostDetail.as_view()),
    path('', views.PostList.as_view()), #함수 대신 클래스 호출
]