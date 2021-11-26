from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from blog.models import Post

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username="trump", password="somepassword")

    def test_landing(self):
        post_001 = Post.objects.create(
            title = '첫 번째 포스트입니다.',
            content = 'Hello World!!! We are the world...',
            author = self.user_trump
        )
        post_002 = Post.objects.create(
            title = '두 번째 포스트입니다.',
            content = '1등이 전부가 아니잖아요',
            author = self.user_trump
        )
        post_003 = Post.objects.create(
            title = '세 번째 파이썬 포스트입니다.',
            content = '세 번째 포스트입니다.',
            author = self.user_trump
        )
        post_004 = Post.objects.create(
            title = '네 번째 파이썬 포스트입니다.',
            content = '네 번째 포스트입니다.',
            author = self.user_trump
        )

        response = self.client.get('') #landing 페이지 url(IP 주소)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body #body 태그는 하나이므로 굳이 find를 통해서 태그를 찾을 필요 없이 해당되는 태그의 이름을 그대로 쓴다
        self.assertNotIn(post_001.title, body.text)
        self.assertIn(post_002.title, body.text)
        self.assertIn(post_003.title, body.text)
        self.assertIn(post_004.title, body.text)
