from django.shortcuts import render
from django.views.generic import ListView, DetailView

from . models import Post, Category

# Create your views here.
class PostList(ListView) :
    model = Post
    ordering = '-pk'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data() #부모가 가지고 있는 것을 상속받는다
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

#    template_name = 'blog/index.html'
# post_list.html  #(index.html 이름을 post_list.html로 수정)  #template_name을 선언 안 해 주는 방법

class PostDetail(DetailView) :
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data() #상위에 있는 get_context_data를 가지고 와서 사용하겠다
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

# post_detail.html  #(single_post_page.html 이름을 post_detail.html로 수정)


# def index(request) :
#     posts = Post.objects.all().order_by('-pk') #pk의 역순으로 정렬
#
#     return render(request, 'blog/index.html',
#                   {
#                       'posts' : posts  #오른쪽의 posts가 위에서 정의한 posts를 의미
#                   }
#                   )

# def single_post_page(request, pk) :
#     post = Post.objects.get(pk=pk)  #= 중심으로 왼쪽은 Post 모델의 field 이름, 오른쪽은 그 field에 넣어 줄 해당되는 값(파라미터로 전달 받은 pk)
#
#     return render(request, 'blog/single_post_page.html',
#                   {
#                       'post' : post
#                   }
#                   )