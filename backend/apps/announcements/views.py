from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.paginator import Paginator

from common.response import success_response, error_response, created_response
from apps.users.permissions import IsAdmin
from .models import Announcement
from .serializers import AnnouncementListSerializer, AnnouncementCreateSerializer


class AnnouncementPublicListView(APIView):
    """前台公告列表（只显示已发布）"""
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = Announcement.objects.filter(is_published=True).select_related('author')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = AnnouncementListSerializer(page_obj.object_list, many=True)
        return success_response(data={
            'results': serializer.data,
            'count': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages,
        })


class AdminAnnouncementListView(APIView):
    """管理员 - 公告列表与创建"""
    permission_classes = [IsAdmin]

    def get(self, request):
        queryset = Announcement.objects.select_related('author').all()
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = AnnouncementListSerializer(page_obj.object_list, many=True)
        return success_response(data={
            'results': serializer.data,
            'count': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages,
        })

    def post(self, request):
        serializer = AnnouncementCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)
        serializer.save(author=request.user)
        return created_response(data=serializer.data, message='公告创建成功')


class AdminAnnouncementDetailView(APIView):
    """管理员 - 公告编辑与删除"""
    permission_classes = [IsAdmin]

    def put(self, request, announcement_id):
        try:
            obj = Announcement.objects.get(pk=announcement_id)
        except Announcement.DoesNotExist:
            return error_response(message='公告不存在', code=404)

        serializer = AnnouncementCreateSerializer(obj, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)
        serializer.save()
        return success_response(data=AnnouncementListSerializer(obj).data, message='公告更新成功')

    def delete(self, request, announcement_id):
        try:
            obj = Announcement.objects.get(pk=announcement_id)
        except Announcement.DoesNotExist:
            return error_response(message='公告不存在', code=404)
        obj.delete()
        return success_response(message='公告已删除')