from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment

# Create your tests here.
class TestView(TestCase): #python manage.py test #pip install beautifulsoup4 #pip list
    def setUp(self):
        self.client = Client()

        self.user_james = User.objects.create_user(username='James', password='somepassword')
        self.user_james.is_staff = True #staff status
        self.user_james.save()
        self.user_trump = User.objects.create_user(username='Trump', password='somepassword')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_culture = Category.objects.create(name='culture', slug='culture')

        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        # 포스트(게시물)이 3개 존재하는 경우
        self.post_001 = Post.objects.create(
            title = '첫 번째 포스트입니다.',
            content = 'Hello World!!! We are the world...',
            author = self.user_james,
            category = self.category_programming
        )
        self.post_001.tags.add(self.tag_hello)
        self.post_002 = Post.objects.create(
            title = '두 번째 포스트입니다.',
            content = '1등이 전부가 아니잖아요',
            author = self.user_trump,
            category = self.category_culture
        )
        self.post_003 = Post.objects.create( #category가 설정이 안 된 Post
            title = '세 번째 파이썬 포스트입니다.',
            content = '세 번째 포스트입니다.',
            author = self.user_trump
        )
        self.post_003.tags.add(self.tag_python)
        self.post_003.tags.add(self.tag_python_kor)

        self.comment_001 = Comment.objects.create(
            post = self.post_001,
            author = self.user_trump,
            content = '첫 번째 댓글입니다.'
        )

    def test_search(self):
        post_004 = Post.objects.create(
            title = "파이썬에 대한 포스트입니다.",
            content = "Hello world...",
            author = self.user_trump
        )

        response = self.client.get('/blog/search/파이썬/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('Search : 파이썬(2)', main_area.text) #Search (2)(-> Search : 파이썬(2))라는 표현이 main_area에 있는 text에 포함되어져 있는지 확인
        self.assertNotIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertIn(self.post_003.title, main_area.text)
        self.assertIn(post_004.title, main_area.text)

    def test_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.post_001.comment_set.count(), 1) #Post의 입장에서 Comment가 추가되어져 있는 역관계를 의미해 주는 그런 관계를 표시해 주기 위해서 모델 뒤에 _set을 붙인다

        # 로그인 하지 않은 상태 #상세 페이지에는 올바르게 접근할 수 있지만, comment form은 존재하지 않고 'Log in and leave a comment'와 같은 안내 문구만 포함하고 있는지 확인
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_area = soup.find('div', id='comment-area')
        self.assertIn('Log in and leave a comment', comment_area.text)
        self.assertFalse(comment_area('form', id='comment-form')) #comment 영역에 comment form이 있다는 것이 거짓이어야 한다 = 없다는 의미

        # 로그인 한 상태
        self.client.login(username='Trump', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('Log in and leave a comment', comment_area.text)
        comment_form = comment_area.find('form', id='comment-form')
        self.assertTrue(comment_form.find('textarea', id='id_content')) #comment_form에서 find한 것(textarea)을 찾는 것이 True라는 건 이 'textarea'라는 태그를 찾았다는 의미

        response = self.client.post( #새로운 comment 추가 #client를 통해서 서버에 접근할 때, 기존의 상세 페이지 접근 방식은 GET 방식 #이제는 comment라는 내용을 가지고서 접근하기 때문에 POST 방식으로 접근
            self.post_001.get_absolute_url() + 'new_comment/', #어떤 사이트에 접근할 것인가에 대한 url 주소가 있어야 한다
            { #추가하는 comment에 대한 부분은, 여기에서는 content에 대한 값만 전달
                'content' : "두 번째 댓글입니다."
            },
            follow=True #client에 접속할 때, 이렇게 데이터 값에 접속할 때는, 하나 더 추가를 하자면 follow에 대한 부분을 True로 설정
        ) #client에 접속 #POST 방식으로 content라고 하는 부분의 값을 가지고 있는 comment를 추가
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

        new_comment = Comment.objects.last() #추가한 comment가 html 문서 안에 잘 나타나고 있는가를 확인 #Comment 모델에서 있는 object들 중에서 가장 마지막에 있는 comment를 가지고 온다
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(new_comment.post.title, soup.title.text) #new_comment가 가지고 있는 post의 title에 대한 내용이 soup으로 되어져 있는 파싱한 문서의 title에 포함되어져 있는가를 text로 확인
        comment_area = soup.find('div', id='comment-area')
        new_comment_div = comment_area.find('div', id=f'comment-{new_comment.pk}')
        self.assertIn('Trump', new_comment_div.text) #작성자 Trump의 이름이 출력되고 있는지 확인 #new_comment_div 태그에 있는 text에 포함되고 있는지 확인
        self.assertIn('두 번째 댓글입니다.', new_comment_div.text)

    def navbar_test(self, soup):
        # 네비게이션바가 있다  # 포스트목록과 같은 네비게이션바가 있는가
        navbar = soup.nav
        # 네비게이션바에 Blog, AboutMe라는 문구가 있다
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo = navbar.find('a', text='Internet Programming')
        self.assertEqual(logo.attrs['href'], '/')
        home = navbar.find('a', text='Home')
        self.assertEqual(home.attrs['href'], '/')
        blog = navbar.find('a', text='Blog')
        self.assertEqual(blog.attrs['href'], '/blog/')
        about = navbar.find('a', text='About Me')
        self.assertEqual(about.attrs['href'], '/about_me/')

    def category_test(self, soup):
        category = soup.find('div', id='categories-card')
        self.assertIn('Categories', category.text) #'Categories' 내용(글자 자체)이 포함(존재)되는지
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', category.text) #f'' : String 표시해 주기 위한 방법 중 하나  #count : category 글이 몇 개가 있는지 출력
        self.assertIn(f'{self.category_culture} ({self.category_culture.post_set.count()})', category.text)
        self.assertIn(f'미분류 (1)', category.text)

    def test_category_page(self):
        # 카테고리 페이지 url로 불러오기
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # beautifulsoup4로 html을 parser하기
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_test(soup)
        # 카테고리 name을 포함하고 있는지
        self.assertIn(self.category_programming.name, soup.h1.text) #soup.h1 : soup 부분 중의 h1 태그로 제한 -> h1.text : h1 태그에 속해 있는 text를 가져와서 비교
        # 카테고리에 포함된 post만 포함하고 있는지
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text) #main-area에도 category_programming에 대한 name을 포함하고 있는가 #soup을 통해서 div 태그를 가져왔기 때문에 soup.main_area.text처럼 앞에 별도로 soup를 붙일 필요가 없다
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        # 카테고리 페이지 url로 불러오기
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # beautifulsoup4로 html을 parser하기
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_test(soup)
        # 카테고리 name을 포함하고 있는지
        self.assertIn(self.tag_hello.name, soup.h1.text)
        # 카테고리에 포함된 post만 포함하고 있는지
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        # 포스트 목록 페이지를 가져온다
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200) #로그인을 하지 않은 상태에서 접근하면, 200이라는 코드를 받으면 안 된다
        self.client.login(username='Trump', password='somepassword') #로그인이 되어야지만 create_post에 접근할 수 있다 #-> 일반 User Trump
        response = self.client.get('/blog/create_post/')
        # 정상적으로 페이지가 로드 #-> Trump는 더 이상 staff에 대한 권한을 가지고 있지 않기 때문에 create_post에 대한 접근을 했을 때, 200이라는 값을 가지면 안 된다
        self.assertNotEqual(response.status_code, 200) #self.assertEqual(response.status_code, 200)

        self.client.login(username='James', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)

        # 페이지 타이틀 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Create Post - Blog')
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str') #tag 입력을 받기 위한 input이 존재하는가 확인 -> 이런 input 태그 있으면 해당되는 input 태그 값을, 없으면 null 값 전달
        self.assertTrue(tag_str_input) #tag_str_input이 True인가, null이 아닌가를 테스트해 봄으로써 input 태그가 있는지 확인

        self.client.post('/blog/create_post/',
                         {
                             'title' : 'Post form 만들기',
                             'content' : "Post form 페이지 만들기",
                             'tags_str' : 'new tag; 한글태그, python' #태그 구별: ;(세미콜론), ,(콤마)
                         })
        last_post = Post.objects.last() #포스트에 있는 마지막 레코드
        self.assertEqual(last_post.title, "Post form 만들기") #create_post에 의해서 submit이 올바르게 됐다면, last_post는 위에서 만든 포스트가 될 것이다
        self.assertEqual(last_post.author.username, 'James') #'Trump') #로그인을 해 둔 username과 동일한 이름으로 마지막 포스트의 author 이름이 들어가 있는지 확인

        self.assertEqual(last_post.tags.count(), 3) #3 개의 태그가 잘 입력되었는지 확인
        self.assertTrue(Tag.objects.get(name='new tag')) #Tag라고 하는 모델의 object에서 get을 이용해 이름이 new tag인 태그를 가지고 있는지 확인 -> 가지고 있으면 True, new tag가 Tag 모델에 등록되지 않았다면 False
        self.assertTrue(Tag.objects.get(name='한글태그')) #python 태그는 이미 Tag라는 모델에 등록되어져 있기 때문에 별도로 있는지 확인하지 않는다(setUp에서 만들어 두었다)
        self.assertEqual(Tag.objects.count(), 5) #Tag 안에 실제로 등록되어져 있는 태그의 개수가 총 5 개인지 확인

    def test_update_post(self): #어떤 User가 update_post에 접근하는지에 따라 3 개로 분리해서 test code 작성 #get, post에 대한 사용을 분리해서 사용
        update_url = f'/blog/update_post/{self.post_003.pk}/' #url 주소 맞지 않으면 403이 아닌 301 오류
        # 로그인하지 않은 경우
        response = self.client.get(update_url) #'/blog/update_post/{self.post_003.pk}')
        self.assertNotEqual(response.status_code, 200) #정상적으로 로드되어지면 안 된다

        # 로그인 했지만 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_james)
        self.client.login(username='James', password='somepassword')
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 403) # 403 : forbidden (접근 권한 금지) #접근이 불가능한 status code : 403

        # 작성자가 로그인해서 접근한 경우  #로그인 했지만 작성자가 접근하는 경우
        self.client.login(username='Trump', password='somepassword')
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200) #정상적으로 접근이 된다

        # 수정 페이지  #제대로 수정 페이지가 보여지고 있는지에 대한 테스트
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Edit Post - Blog')
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text) #main_area에 Edit Post를 담고 있는가의 형태로 수정 페이지가 올바르게 로드되었는가를 확인

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('파이썬 공부; python', tag_str_input.attrs['value']) #기존에 있던 포스트가 가지고 있는 태그 값을 가지고 있는지 확인 #'python, 파이썬 공부' 이 2 개의 내용이 실제 post_003이 가지고 있는 거와 input 태그에 있는 'value' attribute에 들어가 있는 내용과, 2 개의 내용이 지금 포함하고 있는지 확인

        # 실제 수정 후 확인  #-> 수정한 이후에 데이터베이스에 반영했을 때, 그 반영된 내용이 올바르게 수정된 값이 저장되었는가  #수정 페이지에 수정한 내용들이 올바르게 반영되고 있는가
        response = self.client.post(update_url,
                         {
                             'title' : '세 번째 포스트 수정',
                             'content' : '안녕? 우리는 하나/... 반가와요',
                             'category' : self.category_culture.pk, #category_culture만 넣어 주면 안 되고, 이에 대한 Primary Key인 pk를 넣어 줘야 한다
                             'tags_str' : '파이썬 공부; 한글 태그; some tag'
                         }, follow=True) #이렇게 수정된 내용을 전달하고, 그 전달된 값에 대해서 응답을 받을 것이다 #client 입장에서는 이 해당되는 내용을 가지고서 update_url을 따라가서 그 결과를 반영하겠다는 부분이기 때문에 follow는 True로 값을 설정 #정정된 내용을 가지고서, 다시 우리가 해당되는, 반영된, 업데이트로 수정되어져 있는 값에 대해서 처리한 결과를 response로 받는다
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트 수정', main_area.text)
        self.assertIn('안녕? 우리는 하나/... 반가와요', main_area.text)
        self.assertIn(self.category_culture.name, main_area.text) #카테고리에 대한 값을 포함하고 있는가를 봐야 한다 #값을 전달할 때는 뒤에 pk라고 하는 값을 전달하지만, 화면에 출력될 때는 그 pk(Primary Key)에 해당되는 카테고리의 이름이 출력되고 있기 때문에, 출력을 확인할 때는 category_culture.name으로 이름이 출력되고 있는가를 확인
        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('python', main_area.text)

    def test_post_list(self):
        self.assertEqual(Post.objects.count(), 3) #3개의 목록이 있는지 테스트

        # 포스트 목록 페이지를 가져온다
        response = self.client.get('/blog/')
        # 정상적으로 페이지가 로드
        self.assertEqual(response.status_code, 200)
        # 페이지 타이틀 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')

        self.navbar_test(soup)
        self.category_test(soup)

        #포스트 2개 생성 -> setUp에서 생성하도록 변경

        # 목록페이지를 새롭게 불러와서
#        response = self.client.get('/blog/')
#        self.assertEqual(response.status_code, 200)
#        soup = BeautifulSoup(response.content, 'html.parser')    #중복되기 때문에 지운다
        # 포스트(게시물)의 타이틀이 3개 존재하는가
        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text) #category는 string이 아닌 하나의 class이다 -> category가 아닌 category.name과 비교
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        self.assertIn(self.user_james.username.upper(), main_area.text) #포스트에 author로 james와 trump가 잘 입력되어 있는지 확인(upper로 되어진 내용이 main_area 영역의 text에 포함되는지 테스트)
        self.assertIn(self.user_trump.username.upper(), main_area.text)

        # 포스트(게시물)이 하나도 없는 경우
        Post.objects.all().delete() #Post object들을 모두 가지고 와서 지운다
        self.assertEqual(Post.objects.count(), 0)
        # 포스트 목록 페이지를 가져온다
        response = self.client.get('/blog/')
        # 정상적으로 페이지가 로드
        self.assertEqual(response.status_code, 200)
        # 페이지 타이틀 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        # 적절한 안내 문구가 포함되어 있는지
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

    def test_post_detail(self):
        # 포스트 하나 생성 -> setUp에서 생성

        # 이 포스트의 url이 /blog/1  #-> models의 Post에서 f'/blog/{self.pk}'를 f'/blog/{self.pk}/'로 수정 -> /blog/1/
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')
        # url에 의해 정상적으로 상세페이지를 불러오는가
        response = self.client.get('/blog/1/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_test(soup)

        # 포스트의 title은 웹브라우저의 title에 있는가
        self.assertIn(self.post_001.title, soup.title.text)
        # 포스트의 title은 포스트영역에도 있는가
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.post_001.category.name, post_area.text)
        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)
        # 포스트 작성자가 있는가
        # 아직 작성중
        # 포스트의 내용이 있는가
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.user_james.username.upper(), post_area.text)

        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1') #comment-pk #지금 comment는 하나밖에 없으므로 comment_001 같은 경우 pk 값은 1
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text) #댓글 내용이 comment_001_area.text 문구 안에 포함되어져 있는가를 확인 #html 문서 안에, comment 영역 안에 comment가 올바르게 출력되고 있는가를 테스트