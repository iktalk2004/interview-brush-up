from rest_framework import serializers
from .models import Category, SubCategory, Question, TextQuestionDetail, CodeQuestionDetail


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'description', 'sort_order']


class CategorySerializer(serializers.ModelSerializer):
    sub_categories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'sort_order', 'sub_categories']


class CategorySimpleSerializer(serializers.ModelSerializer):
    """分类简要信息（用于题目列表展示）"""
    class Meta:
        model = Category
        fields = ['id', 'name']


class SubCategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name']


# ============================================================
# 题目详情序列化器
# ============================================================

class TextQuestionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextQuestionDetail
        fields = ['content', 'standard_answer', 'explanation']


class CodeQuestionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeQuestionDetail
        fields = ['description', 'test_cases', 'reference_code', 'code_template', 'time_limit', 'memory_limit']


# ============================================================
# 题目序列化器
# ============================================================

class QuestionListSerializer(serializers.ModelSerializer):
    """题目列表序列化器"""
    category = CategorySimpleSerializer(read_only=True)
    sub_category = SubCategorySimpleSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_type', 'title', 'category', 'sub_category', 'difficulty', 'created_at']


class QuestionDetailSerializer(serializers.ModelSerializer):
    """题目详情序列化器（自动关联扩展表）"""
    category = CategorySimpleSerializer(read_only=True)
    sub_category = SubCategorySimpleSerializer(read_only=True)
    text_detail = TextQuestionDetailSerializer(read_only=True)
    code_detail = CodeQuestionDetailSerializer(read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'question_type', 'title', 'category', 'sub_category',
            'difficulty', 'created_at', 'updated_at',
            'text_detail', 'code_detail',
        ]


# ============================================================
# 管理员创建/编辑序列化器
# ============================================================

class AdminTextQuestionSerializer(serializers.Serializer):
    """管理员创建/编辑简答题"""
    title = serializers.CharField(max_length=255)
    category_id = serializers.IntegerField()
    sub_category_id = serializers.IntegerField(required=False, allow_null=True)
    difficulty = serializers.ChoiceField(choices=Question.Difficulty.choices)
    content = serializers.CharField(required=False, allow_blank=True, default='')
    standard_answer = serializers.CharField()
    explanation = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_category_id(self, value):
        if not Category.objects.filter(pk=value).exists():
            raise serializers.ValidationError('分类不存在')
        return value

    def create(self, validated_data):
        question = Question.objects.create(
            question_type='text',
            title=validated_data['title'],
            category_id=validated_data['category_id'],
            sub_category_id=validated_data.get('sub_category_id'),
            difficulty=validated_data['difficulty'],
        )
        TextQuestionDetail.objects.create(
            question=question,
            content=validated_data.get('content', ''),
            standard_answer=validated_data['standard_answer'],
            explanation=validated_data.get('explanation', ''),
        )
        return question

    def update(self, instance, validated_data):
        instance.title = validated_data['title']
        instance.category_id = validated_data['category_id']
        instance.sub_category_id = validated_data.get('sub_category_id')
        instance.difficulty = validated_data['difficulty']
        instance.save()

        detail = instance.text_detail
        detail.content = validated_data.get('content', '')
        detail.standard_answer = validated_data['standard_answer']
        detail.explanation = validated_data.get('explanation', '')
        detail.save()
        return instance


class AdminCodeQuestionSerializer(serializers.Serializer):
    """管理员创建/编辑代码题"""
    title = serializers.CharField(max_length=255)
    category_id = serializers.IntegerField()
    sub_category_id = serializers.IntegerField(required=False, allow_null=True)
    difficulty = serializers.ChoiceField(choices=Question.Difficulty.choices)
    description = serializers.CharField()
    test_cases = serializers.JSONField()
    reference_code = serializers.CharField(required=False, allow_blank=True, default='')
    code_template = serializers.JSONField(required=False, default=dict)
    time_limit = serializers.IntegerField(default=1000)
    memory_limit = serializers.IntegerField(default=256)

    def validate_category_id(self, value):
        if not Category.objects.filter(pk=value).exists():
            raise serializers.ValidationError('分类不存在')
        return value

    def create(self, validated_data):
        question = Question.objects.create(
            question_type='code',
            title=validated_data['title'],
            category_id=validated_data['category_id'],
            sub_category_id=validated_data.get('sub_category_id'),
            difficulty=validated_data['difficulty'],
        )
        CodeQuestionDetail.objects.create(
            question=question,
            description=validated_data['description'],
            test_cases=validated_data['test_cases'],
            reference_code=validated_data.get('reference_code', ''),
            code_template=validated_data.get('code_template', {}),
            time_limit=validated_data.get('time_limit', 1000),
            memory_limit=validated_data.get('memory_limit', 256),
        )
        return question

    def update(self, instance, validated_data):
        instance.title = validated_data['title']
        instance.category_id = validated_data['category_id']
        instance.sub_category_id = validated_data.get('sub_category_id')
        instance.difficulty = validated_data['difficulty']
        instance.save()

        detail = instance.code_detail
        detail.description = validated_data['description']
        detail.test_cases = validated_data['test_cases']
        detail.reference_code = validated_data.get('reference_code', '')
        detail.code_template = validated_data.get('code_template', {})
        detail.time_limit = validated_data.get('time_limit', 1000)
        detail.memory_limit = validated_data.get('memory_limit', 256)
        detail.save()
        return instance


class AdminCategoryCreateSerializer(serializers.ModelSerializer):
    """管理员创建/编辑一级分类"""
    class Meta:
        model = Category
        fields = ['name', 'description', 'sort_order']


class AdminSubCategoryCreateSerializer(serializers.ModelSerializer):
    """管理员创建/编辑二级分类"""
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'description', 'sort_order']