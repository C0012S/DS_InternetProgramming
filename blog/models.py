from django.db import models

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #author

    def __str__(self):
        return f'[{self.pk}]{self.title}'

    def get_absolute_url(self): #self는 레코드 자기 자신을 의미하는 것
        return f'/blog/{self.pk}'
