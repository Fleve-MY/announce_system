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
import requests
import time
import logging

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create': return UserCreateSerializer
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
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_obj = request.data.get('upload')
        if not file_obj: return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        path = default_storage.save(file_obj.name, ContentFile(file_obj.read()))
        url = os.path.join(settings.MEDIA_URL, path)
        return Response({'url': request.build_absolute_uri(url)}, status=status.HTTP_201_CREATED)


# 飞书连接相关
feishu_token_cache = {'token': None, 'expiry_time': 0}


def get_feishu_tenant_access_token():
    global feishu_token_cache
    if feishu_token_cache['token'] and time.time() < feishu_token_cache['expiry_time'] - 60:
        return feishu_token_cache['token']
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    data = {'app_id': settings.FEISHU_APP_ID, 'app_secret': settings.FEISHU_APP_SECRET}
    try:
        logger.info("正在尝试从飞书获取新的 Tenant Access Token...")
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        if result.get('code') == 0:
            feishu_token_cache['token'] = result['tenant_access_token']
            feishu_token_cache['expiry_time'] = time.time() + result['expire']
            logger.info("成功获取飞书 Token。")
            return feishu_token_cache['token']
        else:
            logger.error(f"获取飞书 Token 失败: {result.get('msg')}")
            return None
    except requests.RequestException as e:
        logger.error(f"请求飞书 Token 时发生网络错误: {e}")
        return None


class FeishuLogView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logger.info("FeishuLogView: 开始处理 GET 请求...")
        token = get_feishu_tenant_access_token()
        if not token:
            return Response({"error": "无法获取飞书访问凭证"},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE
                            )

        spreadsheet_token = settings.FEISHU_SPREADSHEET_TOKEN
        headers = {'Authorization': f'Bearer {token}'}

        try:
            meta_url = f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query'
            meta_response = requests.get(meta_url, headers=headers, timeout=10)
            meta_response.raise_for_status()
            meta_result = meta_response.json()

            if meta_result.get('code') != 0 or not meta_result.get('data', {}).get('sheets'):
                error_msg = f"获取表格元数据失败: {meta_result.get('msg', '没有找到任何 sheet')}"
                return Response({"error": error_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            first_sheet_id = meta_result['data']['sheets'][0]['sheet_id']

        except requests.RequestException as e:
            return Response({"error": "请求表格元数据失败，请检查后端日志。"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            range_str = f'{first_sheet_id}!A2:L1000'
            sheets_url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_str}'

            response = requests.get(sheets_url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as e:
            return Response({"error": "请求飞书表格数据时发生网络错误，请检查后端日志。"},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if result.get('code') != 0:
            return Response({"error": f"飞书API错误: {result.get('msg')}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_logs = []
        current_user = request.user
        all_rows = result.get('data', {}).get('valueRange', {}).get('values', [])

        logger.info(
            f"FeishuLogView: 开始为用户 '{current_user.username}' (is_admin: {current_user.is_superuser}) 筛选数据...")

        for row in all_rows:
            # 行结构: [B, C, D, E, F, G, H, I, J, K]
            # 过滤条件：如果 E 列（用户名）为空，则跳过此行
            if len(row) >= 10 and row[4]:
                row_username = row[4]

                # 如果当前用户是管理员，或者当前行数据的用户名与登录用户名一致
                if current_user.is_superuser or row_username == current_user.username:
                    user_logs.append({
                        'username': row_username,
                        'a_col': row[0],  # A 列 - 流水号
                        'b_col': row[1],  # B 列 - 日期
                        'c_col': row[2],  # c 列 - 店铺中文名称
                        'd_col': row[3],  # d 列 - 店铺编号
                        'h_col': row[7],  # H 列 - 数量
                        'f_col': row[5],  # F 列 - 关键字
                        'g_col': row[6],  # G 列 - oss上传路径
                        'i_col': row[8],  # I 列 - 上传状态
                        'j_col': row[9],  # J 列 - 编码
                        'k_col': row[10] if row[10] else "未完成",  # K 列 - 状态
                        'l_col': row[11], # L列 - 识别结果路径
                    })

        logger.info(f"FeishuLogView: 筛选完成，找到 {len(user_logs)} 条记录。")
        print(user_logs)
        return Response(user_logs, status=status.HTTP_200_OK)
