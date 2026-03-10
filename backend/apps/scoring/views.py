from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from common.response import success_response, error_response
from apps.questions.models import Question


class ScorePreviewView(APIView):
    """评分预览（不保存记录，仅返回评分结果）"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question_id = request.data.get('question_id')
        user_answer = request.data.get('user_answer', '')
        scoring_method = request.data.get('scoring_method', 'model')

        if not question_id or not user_answer.strip():
            return error_response(message='缺少题目ID或答案')

        try:
            question = Question.objects.select_related('text_detail').get(
                pk=question_id, question_type='text'
            )
        except Question.DoesNotExist:
            return error_response(message='题目不存在')

        from apps.scoring.engines.base import SimpleScorer
        from apps.scoring.engines.deepseek import DeepSeekScorer

        if scoring_method == 'deepseek':
            scorer = DeepSeekScorer()
        else:
            scorer = SimpleScorer()

        score, feedback = scorer.score(
            question_title=question.title,
            standard_answer=question.text_detail.standard_answer,
            user_answer=user_answer,
        )

        return success_response(data={
            'score': score,
            'feedback': feedback,
            'scoring_method': scoring_method,
            'engine': scorer.get_name(),
        })