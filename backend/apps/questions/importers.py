import openpyxl
from .models import Category, SubCategory, Question, TextQuestionDetail, CodeQuestionDetail


def import_questions_from_excel(file):
    """从Excel导入题目"""
    wb = openpyxl.load_workbook(file, read_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(min_row=2, values_only=True))
    success = 0
    failed = 0
    errors = []

    for idx, row in enumerate(rows, start=2):
        try:
            if not row or not row[0]:
                continue

            title = str(row[0]).strip()
            question_type = str(row[1]).strip().lower() if row[1] else ''
            category_name = str(row[2]).strip() if row[2] else ''
            sub_category_name = str(row[3]).strip() if row[3] else ''
            difficulty = str(row[4]).strip().lower() if row[4] else 'medium'

            # 查找或创建分类
            category, _ = Category.objects.get_or_create(name=category_name)
            sub_category = None
            if sub_category_name:
                sub_category, _ = SubCategory.objects.get_or_create(
                    category=category, name=sub_category_name
                )

            # 映射难度
            diff_map = {'简单': 'easy', '中等': 'medium', '困难': 'hard', 'easy': 'easy', 'medium': 'medium', 'hard': 'hard'}
            difficulty = diff_map.get(difficulty, 'medium')

            # 创建题目
            question = Question.objects.create(
                question_type=question_type if question_type in ('text', 'code') else 'text',
                title=title,
                category=category,
                sub_category=sub_category,
                difficulty=difficulty,
            )

            if question.question_type == 'text':
                content = str(row[5]).strip() if len(row) > 5 and row[5] else ''
                standard_answer = str(row[6]).strip() if len(row) > 6 and row[6] else ''
                explanation = str(row[7]).strip() if len(row) > 7 and row[7] else ''
                TextQuestionDetail.objects.create(
                    question=question,
                    content=content,
                    standard_answer=standard_answer,
                    explanation=explanation,
                )
            elif question.question_type == 'code':
                import json
                description = str(row[5]).strip() if len(row) > 5 and row[5] else ''
                test_cases_raw = str(row[6]).strip() if len(row) > 6 and row[6] else '[]'
                reference_code = str(row[7]).strip() if len(row) > 7 and row[7] else ''
                try:
                    test_cases = json.loads(test_cases_raw)
                except json.JSONDecodeError:
                    test_cases = []
                CodeQuestionDetail.objects.create(
                    question=question,
                    description=description,
                    test_cases=test_cases,
                    reference_code=reference_code,
                )

            success += 1
        except Exception as e:
            failed += 1
            errors.append(f'第{idx}行: {str(e)}')

    return {
        'success': success,
        'failed': failed,
        'errors': errors[:20],  # 最多返回20条错误
    }