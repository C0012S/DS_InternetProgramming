from django.db import models
from django.contrib.auth.models import User #장고가 제공해 주고 있는 User 모델
import os

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True) #python -m pip install Pillow 또는 pip install Pillow -> pip list로 확인
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL) #User가 삭제되었을 때 Post의 author를 NULL 처리 -> author가 NULL이 허용된다는 설정 필요 : null=True  #on_delete=models.CASCADE : User가 삭제되었을 때 Post의 내용도 같이 삭제

    def __str__(self):
        #return f'[{self.pk}]{self.title}'
        return f'[{self.pk}]{self.title} :: {self.author}'

    def get_absolute_url(self): #self는 레코드 자기 자신을 의미하는 것
        return f'/blog/{self.pk}'

    def get_file_name(self): #file 이름에 대한 부분 return
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self): #확장자 가져오는 함수
        return self.get_file_name().split('.')[-1] #[-1]은 배열의 마지막 원소를 의미
