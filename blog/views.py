from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from . models import Post, Category, Tag
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .forms import CommentForm
from django.shortcuts import get_object_or_404
from django.db.models import Q

# Create your views here.
def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk) #Primary Key가 파라미터로 전달받은 pk와 일치하는 데이터를 가지고 온다 #옳지 않은 pk면 404
        if request.method == 'POST' : #request가 POST 방식으로 들어왔는지 확인 #comment에 대한 url에 접근하는 것이 계수로도 접근할 수 있고, POST로도 접근할 수 있는데, 새로운 comment를 입력한 다음에 그 입력된 comment를 가지고 접근하는 경우는 POST로 접근한다
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid() :
                comment = comment_form.save(commit=False) #만들어지고 있는 form이 바로 모델에 등록돼서 저장되는 걸 막기 위해 commit=False
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else :
            return redirect(post.get_absolute_url()) #comment는 안 붙고 상세 페이지를 보여 준다
    else :
        raise PermissionDenied #예외 발생

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category'] #, 'tags'] #field 부분에 있는 내용들은 form에서 가지고 와서 쓰겠다고 하는 내용 -> 더 이상 Django가 제공해 주고 있는 form 형태로 tags를 쓰지 않고 재정의할 것이므로 tags를 지운다

    def test_func(self): #Ture or False 값을 return
        return self.request.user.is_superuser or self.request.user.is_staff #superuser이거나 staff이면 True -> 이 지금 클래스에 접근할 수 있게끔 하는 함수

    def form_valid(self, form): #장고에서 제공해 주는 함수 재정의 #user에 해당되는 author에 대한 부분을 로그인한 author에 username으로 자동으로 입력되게 한다 #form_valid : form을 처리해 주는 함수 #PostCreate의 form_valid에서는 User에 대해서 권한을 체크해 준다
        current_user = self.request.user #이 form을 요청하는 user가 누구인지 확인 #이 클래스에 대해서 request 하고 있는 user가 누군지 파악
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser) : #로그인되어져 있고, 동시에 superuser 아니면 staff user를 만족해야 한다  #if current_user.is_authenticated : #허락받은 사용자(user)인지
            form.instance.author = current_user #비어있는 author field에 지금 로그인한 current_user의 아이디로 로그인한다
            response = super(PostCreate, self).form_valid(form) #return super(PostCreate, self).form_valid(form)
            tags_str = self.request.POST.get('tags_str') #직접 입력한 태그들에 대한 문자열 데이터
            if tags_str : #태그 값이 입력되어 태그 값이 있는 경우
                tags_str = tags_str.strip() #strip : 불필요한 공백 제거해 주는 문자열 함수
                tags_str = tags_str.replace(',', ';') #,로 되어져 있는 거를 ;으로 바꾼다 -> 모든 태그들은 , 없이 ;으로 구분된다
                tags_list = tags_str.split(';') #;을 기준으로 split 한다
                for t in tags_list :
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created :
                        tag.slug = slugify(t, allow_unicode=True) #allow_unicode=True : 한글에 대한 태그도 받고, 한글에 대한 slug도 만들 수 있다
                        tag.save() #기존에 있던 태그의 slug에 대한 부분이 추가되었으니, 변경된 태그에 대한 내용을 저장
                    self.object.tags.add(tag) #tags라는 field에 tag를 추가
            return response #input에 입력한 여러 개의 태그들에 대해서 각각 분리를 해서, 새로 만들어 준 POST의 tags에 추가를 해 줄 수 있고, 만약에 새로운 태그가 있다면 Tag 모델에 등록할 뿐만 아니라 slug도 같이 만들어 준다
        else : #허가된 로그인한 유저가 아니라면, 이 create_post라고 하는 url을 통해서 접근할 수 없다 #그러면 create_post라고 하는 곳에 접근하지 못하게 해 주려면, 그걸 대신해 줄 수 있는 페이지가 보여져야 한다
            return redirect('/blog/') #디폴트로 포스트 목록 항목을 보여 준다 #다른 페이지에 대한 내용을 전달하므로 redirect 함수를 이용

class PostUpdate(LoginRequiredMixin, UpdateView): # 모델명_form #으로 되어져 있는 템플릿 이름을 사용 -> 작성 페이지 템플릿과 이름이 동일하기 때문에 자동으로 설정되고 있는 템플릿 이름을 사용할 수 없다 -> 템플릿을 별도로 선언해 줘야 한다  #로그인한 User만 접근할 수 있는 페이지이기 때문에 파라미터 LoginRequiredMixin 추가
    model = Post #모델 선언
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category'] #, 'tags']

    template_name = 'blog/post_update_form.html'

    def dispatch(self, request, *args, **kwargs): #dispatch : 장고에서 get으로 접근했는지, post로 접근했는지 구별해 주는 함수 제공
        if request.user.is_authenticated and request.user == self.get_object().author : #작성자가 접근해야지만 접근 가능 #로그인되어져 있고 실제 작성자에 해당되는 author 하고 같은 User가 request 했다면
            return super(PostUpdate, self).dispatch(request, *args, **kwargs) #작성자가 요구하는 경우에만 dispatch를 통해서 PostUpdate에 접근
        else :
            raise PermissionDenied #예외 상황 발생

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists() :
            tags_str_list = list()
            for t in self.object.tags.all() :
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)
        return context

    def form_valid(self, form): #PostUpdate의 form_valid에서는 dispatch라는 곳에서 GET, POST 구별해 주는 과정에서 request 하고 있는 User의 권한을 체크하고 있기 때문에 굳이 form_valid 함수에서 다시 User에 대한 권한 체크를 할 필요가 없다
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear() #object : 현재의 포스트를 의미 #현재 포스트에 포함되어져 있는 모든 태그들을 가지고 와서 지운다 #이 포스트는 태그를 지우고 Update에 들어가 있는 태그들로 다시 태그가 만들어진다
        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')
            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)
        return response

class PostList(ListView) :
    model = Post
    ordering = '-pk'
    paginate_by = 5 #페이지네이션 하고 싶은 개수

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
        context['comment_form'] = CommentForm #CommentForm 내용을 사용할 수 있다
        return context

# post_detail.html  #(single_post_page.html 이름을 post_detail.html로 수정)

class PostSearch(PostList) :
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q'] #검색어를 가져온다
        post_list = Post.objects.filter( #검색된 결과 저장
            Q(title__contains=q) | Q(tags__name__contains=q) #해당되는 Query를 가지고서 db에서 내가 원하는 데이터를 찾는다
        ).distinct() #검색어인 경우 title과 tag에 대한 내용만 추가 #distinct : 중복 제거하고 하나만 사용
        return post_list

    def get_context_data(self, **kwargs):
        context = super(PostSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search : {q}({self.get_queryset().count()})' #서치된 결과를 넣어 준다

        return context

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

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug) #오른쪽 slug는 url을 통해서 tag 뒤에 오는 slug, url 주소를 통해서 전달받은 slug 값, tag 페이지에 해당되는 파라미터로 전달된 값 #앞에 있는 slug는 Tag 모델 안에 있는 field
    post_list = tag.post_set.all() # Post.objects.filter(tags=tag) #카테고리는 하나의 값을 가지고 있다 #태그는 카테고리와 달리 다대다 관계이므로 태그에 있는 값이 포스트 안에 다대다 관계로, ManyToMany 형태로 연결되어져 있어서 포스트에 있는 tags라는 field는 하나의 태그가 아니라 여러 개의 태그를 가질 수 있다 -> filter(tags=tag) 통과 불가

    return render(request, 'blog/post_list.html',
                  {
                      'post_list' : post_list,
                      'categories' : Category.objects.all(),
                      'no_category_post_count' : Post.objects.filter(category=None).count(),
                      'tag' : tag
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