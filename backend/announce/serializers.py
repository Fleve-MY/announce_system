# api/serializers.py (最终修复版)

from rest_framework import serializers
from .models import User, Announcement, Feedback


class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(source='is_superuser', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'is_admin']


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'is_superuser']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            is_superuser=validated_data.get('is_superuser', False)
        )
        return user


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    # 这一行保持不变，用于读取时显示用户名
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Feedback
        # 确保 'user' 字段在列表中
        fields = ['id', 'user', 'user_name', 'message', 'date']