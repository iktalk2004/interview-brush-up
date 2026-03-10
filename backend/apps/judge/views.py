from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from common.response import success_response, error_response
from apps.questions.models import Question
from apps.practice.services import create_submission_and_update_status
from .models import JudgeTask
from .serializers import SubmitCodeSerializer, JudgeTaskSerializer
from .client import Judge0Client


class SubmitCodeView(APIView):
    """提交代码判题"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SubmitCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message=serializer.errors)

        data = serializer.validated_data
        try:
            question = Question.objects.select_related('code_detail').get(
                pk=data['question_id'], question_type='code'
            )
        except Question.DoesNotExist:
            return error_response(message='代码题不存在')

        code_detail = question.code_detail
        if not code_detail:
            return error_response(message='题目缺少代码详情')

        test_cases = code_detail.test_cases or []
        if not test_cases:
            return error_response(message='题目没有测试用例')

        language = data['language']
        source_code = data['source_code']
        time_spent = data.get('time_spent', 0)

        # 创建判题任务
        task = JudgeTask.objects.create(
            user=request.user,
            question=question,
            language=language,
            source_code=source_code,
            status=JudgeTask.Status.RUNNING,
            total_count=len(test_cases),
        )

        # 逐个测试用例判题
        client = Judge0Client()
        passed = 0
        max_time = 0
        max_memory = 0
        details = []
        first_error = ''

        for idx, tc in enumerate(test_cases):
            stdin = tc.get('input', '')
            expected = tc.get('output', '').strip()

            try:
                result = client.submit_and_wait(
                    source_code=source_code,
                    language=language,
                    stdin=stdin,
                    expected_output=expected,
                    time_limit=code_detail.time_limit,
                    memory_limit=code_detail.memory_limit,
                    max_wait=30,
                )

                status_id = result['status_id']
                stdout = result['stdout'].strip()
                stderr = result['stderr']
                compile_output = result['compile_output']
                time_ms = round(result['time'] * 1000, 2)
                memory_kb = result['memory']

                is_pass = (status_id == 3)  # Accepted
                if is_pass:
                    passed += 1

                max_time = max(max_time, time_ms)
                max_memory = max(max_memory, memory_kb)

                case_detail = {
                    'index': idx + 1,
                    'passed': is_pass,
                    'status': result['status_desc'],
                    'time': time_ms,
                    'memory': memory_kb,
                    'input': stdin[:200],
                    'expected': expected[:200],
                    'actual': stdout[:200],
                    'stderr': result['stderr'][:300] if result['stderr'] else '',
                    'compile_output': result['compile_output'][:300] if result['compile_output'] else '',
                }

                if not is_pass and not first_error:
                    if compile_output:
                        first_error = f'编译错误: {compile_output[:300]}'
                    elif stderr:
                        first_error = f'运行错误: {stderr[:300]}'
                    else:
                        first_error = f'测试用例{idx+1}未通过: 期望输出 "{expected[:100]}"，实际输出 "{stdout[:100]}"'

                details.append(case_detail)

            except Exception as e:
                details.append({
                    'index': idx + 1,
                    'passed': False,
                    'status': 'System Error',
                    'error': str(e)[:200],
                })
                if not first_error:
                    first_error = f'系统错误: {str(e)[:200]}'

        # 更新任务状态
        all_passed = (passed == len(test_cases))
        if all_passed:
            task.status = JudgeTask.Status.ACCEPTED
        elif first_error.startswith('编译错误'):
            task.status = JudgeTask.Status.COMPILE_ERROR
        elif first_error.startswith('运行错误'):
            task.status = JudgeTask.Status.RUNTIME_ERROR
        else:
            task.status = JudgeTask.Status.WRONG_ANSWER

        task.passed_count = passed
        task.time_used = max_time
        task.memory_used = max_memory
        task.error_message = first_error
        task.detail = details
        task.finished_at = timezone.now()
        task.save()

        # 同步到答题记录
        score = round(passed / len(test_cases) * 100, 2) if test_cases else 0
        feedback = f'通过 {passed}/{len(test_cases)} 个测试用例'
        if all_passed:
            feedback += '，恭喜！'
        elif first_error:
            feedback += f'。{first_error}'

        create_submission_and_update_status(
            user=request.user,
            question=question,
            user_answer=source_code,
            score=score,
            is_correct=all_passed,
            scoring_method='judge',
            time_spent=time_spent,
            ai_feedback=feedback,
            language=language,
        )

        return success_response(data=JudgeTaskSerializer(task).data, message='判题完成')


class JudgeTaskDetailView(APIView):
    """查询判题结果"""
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        try:
            task = JudgeTask.objects.get(pk=task_id, user=request.user)
        except JudgeTask.DoesNotExist:
            return error_response(message='任务不存在')

        return success_response(data=JudgeTaskSerializer(task).data)


class JudgeHistoryView(APIView):
    """某题的判题历史"""
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        tasks = JudgeTask.objects.filter(
            user=request.user, question_id=question_id
        ).order_by('-created_at')[:20]

        serializer = JudgeTaskSerializer(tasks, many=True)
        return success_response(data=serializer.data)