# api/models.py (正确版本)

from django.db import models
from django.contrib.auth.models import AbstractUser

# User 模型现在只是一个简单的继承，没有任何自定义字段
class User(AbstractUser):
    pass # 我们不再需要自定义 is_admin 字段

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback from {self.user.username}'