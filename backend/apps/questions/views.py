from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.paginator import Paginator
from django.db.models import Q

from common.response import success_response, error_response, created_response
from apps.users.permissions import IsAdmin
from .models import Category, SubCategory, Question
from .serializers import (
    CategorySerializer, QuestionListSerializer, QuestionDetailSerializer,
    AdminTextQuestionSerializer, AdminCodeQuestionSerializer,
    AdminCategoryCreateSerializer, AdminSubCategoryCreateSerializer,
    SubCategorySerializer,
)


# ============================================================
# 前台接口
# ============================================================

class CategoryListView(APIView):
    """分类树查询"""
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.prefetch_related('sub_categories').all()
        serializer = CategorySerializer(categories, many=True)
        return success_response(data=serializer.data)


class QuestionListView(APIView):
    """题目列表（分页、筛选、搜索）"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.practice.models import UserQuestionStatus

        queryset = Question.objects.select_related('category', 'sub_category').all()

        # 筛选
        category = request.query_params.get('category')
        sub_category = request.query_params.get('sub_category')
        difficulty = request.query_params.get('difficulty')
        question_type = request.query_params.get('question_type')
        search = request.query_params.get('search', '')

        if category:
            queryset = queryset.filter(category_id=category)
        if sub_category:
            queryset = queryset.filter(sub_category_id=sub_category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if question_type:
            queryset = queryset.filter(question_type=question_type)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(text_detail__content__icontains=search)
            )

        # 排序
        ordering = request.query_params.get('ordering', 'id')
        queryset = queryset.order_by(ordering)

        # 分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = QuestionListSerializer(page_obj.object_list, many=True)
        question_ids = [q.id for q in page_obj.object_list]
        status_map = dict(
            UserQuestionStatus.objects.filter(
                user=request.user, question_id__in=question_ids
            ).values_list('question_id', 'best_score')
        )
        results = serializer.data
        for item in results:
            item['is_done'] = item['id'] in status_map
            item['best_score'] = status_map.get(item['id'])

        return success_response(data={
            'results': results,
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
        })


class QuestionDetailView(APIView):
    """题目详情"""
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        try:
            question = Question.objects.select_related(
                'category', 'sub_category', 'text_detail', 'code_detail'
            ).get(pk=question_id)
        except Question.DoesNotExist:
            return error_response(message='题目不存在', code=404)

        serializer = QuestionDetailSerializer(question)
        return success_response(data=serializer.data)


# ============================================================
# 管理员 - 分类管理
# ============================================================

class AdminCategoryListView(APIView):
    """管理员 - 分类列表和创建"""
    permission_classes = [IsAdmin]

    def get(self, request):
        categories = Category.objects.prefetch_related('sub_categories').all()
        serializer = CategorySerializer(categories, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        serializer = AdminCategoryCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)
        serializer.save()
        return created_response(data=serializer.data, message='分类创建成功')


class AdminCategoryDetailView(APIView):
    """管理员 - 分类编辑和删除"""
    permission_classes = [IsAdmin]

    def put(self, request, category_id):
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return error_response(message='分类不存在', code=404)

        serializer = AdminCategoryCreateSerializer(category, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)
        serializer.save()
        return success_response(data=serializer.data, message='分类更新成功')

    def delete(self, request, category_id):
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return error_response(message='分类不存在', code=404)

        if category.questions.exists():
            return error_response(message='该分类下存在题目，无法删除')
        category.delete()
        return success_response(message='分类删除成功')


class AdminSubCategoryListView(APIView):
    """管理员 - 二级分类创建"""
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = AdminSubCategoryCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)
        serializer.save()
        return created_response(data=serializer.data, message='子分类创建成功')


class AdminSubCategoryDetailView(APIView):
    """管理员 - 二级分类编辑和删除"""
    permission_classes = [IsAdmin]

    def put(self, request, sub_category_id):
        try:
            sub = SubCategory.objects.get(pk=sub_category_id)
        except SubCategory.DoesNotExist:
            return error_response(message='子分类不存在', code=404)

        serializer = AdminSubCategoryCreateSerializer(sub, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)
        serializer.save()
        return success_response(data=serializer.data, message='子分类更新成功')

    def delete(self, request, sub_category_id):
        try:
            sub = SubCategory.objects.get(pk=sub_category_id)
        except SubCategory.DoesNotExist:
            return error_response(message='子分类不存在', code=404)

        if sub.questions.exists():
            return error_response(message='该子分类下存在题目，无法删除')
        sub.delete()
        return success_response(message='子分类删除成功')


# ============================================================
# 管理员 - 题目管理
# ============================================================

class AdminQuestionListView(APIView):
    """管理员 - 题目列表和创建"""
    permission_classes = [IsAdmin]

    def get(self, request):
        queryset = Question.objects.select_related('category', 'sub_category').all()

        search = request.query_params.get('search', '')
        category = request.query_params.get('category')
        difficulty = request.query_params.get('difficulty')
        question_type = request.query_params.get('question_type')

        if search:
            queryset = queryset.filter(title__icontains=search)
        if category:
            queryset = queryset.filter(category_id=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if question_type:
            queryset = queryset.filter(question_type=question_type)

        # 排序：默认按 ID 升序
        ordering = request.query_params.get('ordering', 'id')
        queryset = queryset.order_by(ordering)

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = QuestionListSerializer(page_obj.object_list, many=True)
        return success_response(data={
            'results': serializer.data,
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
        })

    def post(self, request):
        question_type = request.data.get('question_type')

        if question_type == 'text':
            serializer = AdminTextQuestionSerializer(data=request.data)
        elif question_type == 'code':
            serializer = AdminCodeQuestionSerializer(data=request.data)
        else:
            return error_response(message='题目类型无效，必须为 text 或 code')

        if not serializer.is_valid():
            return error_response(message=serializer.errors)

        question = serializer.save()
        detail_serializer = QuestionDetailSerializer(question)
        return created_response(data=detail_serializer.data, message='题目创建成功')


class AdminQuestionDetailView(APIView):
    """管理员 - 题目编辑和删除"""
    permission_classes = [IsAdmin]

    def get(self, request, question_id):
        try:
            question = Question.objects.select_related(
                'category', 'sub_category', 'text_detail', 'code_detail'
            ).get(pk=question_id)
        except Question.DoesNotExist:
            return error_response(message='题目不存在', code=404)

        serializer = QuestionDetailSerializer(question)
        return success_response(data=serializer.data)

    def put(self, request, question_id):
        try:
            question = Question.objects.select_related('text_detail', 'code_detail').get(pk=question_id)
        except Question.DoesNotExist:
            return error_response(message='题目不存在', code=404)

        if question.question_type == 'text':
            serializer = AdminTextQuestionSerializer(question, data=request.data)
        else:
            serializer = AdminCodeQuestionSerializer(question, data=request.data)

        if not serializer.is_valid():
            return error_response(message=serializer.errors)

        serializer.update(question, serializer.validated_data)
        detail_serializer = QuestionDetailSerializer(question)
        return success_response(data=detail_serializer.data, message='题目更新成功')

    def delete(self, request, question_id):
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return error_response(message='题目不存在', code=404)

        question.delete()
        return success_response(message='题目删除成功')


class AdminQuestionImportView(APIView):
    """管理员 - Excel批量导入"""
    permission_classes = [IsAdmin]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return error_response(message='请上传文件')

        if not file.name.endswith(('.xlsx', '.xls')):
            return error_response(message='仅支持 xlsx/xls 格式')

        from .importers import import_questions_from_excel
        result = import_questions_from_excel(file)
        return success_response(data=result, message=f"导入完成：成功 {result['success']} 条，失败 {result['failed']} 条")
