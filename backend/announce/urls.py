# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AnnouncementViewSet, FeedbackViewSet, ImageUploadView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'announcements', AnnouncementViewSet)
router.register(r'feedback', FeedbackViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upload/image/', ImageUploadView.as_view(), name='image_upload'),
]