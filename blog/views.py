from django.shortcuts import render
from . models import Post

# Create your views here.
def index(request) :
    posts = Post.objects.all().order_by('-pk') #pk의 역순으로 정렬

    return render(request, 'blog/index.html',
                  {
                      'posts' : posts  #오른쪽의 posts가 위에서 정의한 posts를 의미
                  }
                  )

def single_post_page(request, pk) :
    post = Post.objects.get(pk=pk)  #= 중심으로 왼쪽은 Post 모델의 field 이름, 오른쪽은 그 field에 넣어 줄 해당되는 값(파라미터로 전달 받은 pk)

    return render(request, 'blog/single_post_page.html',
                  {
                      'post' : post
                  }
                  )