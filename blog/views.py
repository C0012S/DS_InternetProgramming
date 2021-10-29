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

def category_page(request, slug):
    if slug == 'no_category' :
        category = '미분류' #Category 모델에서 찾지 않고 '미분류' 라는 이름을 전달
        post_list = Post.objects.filter(category=None)
    else :
        category = Category.objects.get(slug=slug) #두 번째에 있는 slug가 함수 인자에서 전달받은 slug / 앞에 있는 것은 (카테고리가 가지고 있는?) field명 #slug와 일치하는 slug에 해당하는 카테고리를 가지고 온다
        post_list = Post.objects.filter(category=category)

    return render(request, 'blog/post_list.html',
                  {
                      'post_list' : post_list, #post_list 변수를 post_list라는 키를 통해서 전달  <-  #Post.objects.filter(category=category), #포스트 중에서 category라는 값이 위에서 선언해 놓은 category(두 번째에 오는 category이다) 값과 같은 포스트만 가지고 와서 포스트에 대한 리스트로 만들어 준다
                      'categories' : Category.objects.all(), #모든 카테고리에 대한 정보 전달
                      'no_category_post_count' : Post.objects.filter(category=None).count(), #카테고리가 없는, 미분류되어져 있는 포스트 개수가 몇 개 있는지 값을 저장
                      'category' : category #현재 카테고리는 무엇인가
                  }
                  )


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