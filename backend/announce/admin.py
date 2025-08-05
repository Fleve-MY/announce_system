from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Announcement, Feedback

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'groups', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title', 'content')
    list_filter = ('date',)
    ordering = ('-date',)

    fields = ('title', 'content')

# 3. 优化用户反馈界面
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_message', 'date')
    search_fields = ('user__username', 'message')
    list_filter = ('date',)
    ordering = ('-date',)
    readonly_fields = ('user', 'message', 'date')

    @admin.display(description='反馈内容')
    def short_message(self, obj):
        return f'{obj.message}'