from django.shortcuts import render
from blog.models import Post

# Create your views here.
def langing(request):
    recent_posts = Post.objects.order_by('-pk')[:3] #최신 포스트 #[:3] - 맨 앞에서부터 최대 3 개까지 가져온다
    return render(request, 'single_pages/landing.html',
                  {'recent_posts' : recent_posts}) #recent_posts를 전달하는 key : 'recent_posts'(보통 변수 이름과 동일하다)  #변수 recent_posts는 : 오른쪽

def about_me(request):
    return render(request, 'single_pages/about_me.html')