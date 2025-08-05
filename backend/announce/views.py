from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Announcement, Feedback
from .serializers import UserSerializer, UserCreateSerializer, AnnouncementSerializer, FeedbackSerializer
from .permissions import IsAdminUser
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all().order_by('-date')
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by('-date')
    serializer_class = FeedbackSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class ImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # 确保只有登录用户可以上传

    def post(self, request, *args, **kwargs):
        file_obj = request.data.get('upload')
        if not file_obj:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # 保存文件
        path = default_storage.save(file_obj.name, ContentFile(file_obj.read()))
        url = os.path.join(settings.MEDIA_URL, path)
        return Response({'url': request.build_absolute_uri(url)}, status=status.HTTP_201_CREATED)
