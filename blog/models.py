from django.db import models
from django.contrib.auth.models import User #장고가 제공해 주고 있는 User 모델
import os
from markdownx.models import MarkdownxField
from markdownx.utils import markdown

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}'

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True) #Post 같은 경우는 Primary Key로 구분, Category에는 slug로 구분

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}'

    class Meta:
        verbose_name_plural = 'Categories'

class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = MarkdownxField() #models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True) #python -m pip install Pillow 또는 pip install Pillow -> pip list로 확인
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL) #User가 삭제되었을 때 Post의 author를 NULL 처리 -> author가 NULL이 허용된다는 설정 필요 : null=True  #on_delete=models.CASCADE : User가 삭제되었을 때 Post의 내용도 같이 삭제

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL) #blank=True : 처음부터 NULL 값을 넣거나 값을 안 넣게 해 준다

    tags = models.ManyToManyField(Tag, blank=True) #blank=True : null=True처럼 해당되는 값이 없는 걸 나타내는 건 비슷하지만, admin 페이지에서 해당되는 tags라는 폼 자체에 빈 값으로 저장하는 것이 가능하다는 걸 허용해 주는 내용

    def __str__(self):
        #return f'[{self.pk}]{self.title}'
        return f'[{self.pk}]{self.title} :: {self.author}'

    def get_absolute_url(self): #self는 레코드 자기 자신을 의미하는 것
        return f'/blog/{self.pk}'

    def get_file_name(self): #file 이름에 대한 부분 return
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self): #확장자 가져오는 함수
        return self.get_file_name().split('.')[-1] #[-1]은 배열의 마지막 원소를 의미

    def get_content_markdown(self):
        return markdown(self.content) #마크다운으로 변환 #기존의 작성해 준 텍스트를 html 문서로 바꿔 주는 과정을 거침

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE) #하나의 포스트에 여러 개의 댓글 : 다대일 관계
    author = models.ForeignKey(User, on_delete=models.CASCADE) #한 명의 User가 여러 개의 Comment를 넣을 수 있는 다대일 관계
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) #작성 시간

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self): #Comment 모델에 대해서 값을 요구했을 때, 그 값을 요구할 수 있는 url에 대한 정의
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'
