import random
from collections import defaultdict
from apps.practice.models import UserQuestionStatus


def evaluate_algorithm(algorithm, users, k=5):
    """
    评估推荐算法（留一法 + 多次采样取平均）
    对每个用户，随机隐藏一道做过的题，看推荐能否命中
    重复多轮取平均，结果更稳定
    """
    from apps.questions.models import Question
    total_questions = Question.objects.count()
    all_recommended = set()

    rounds = 5  # 重复5轮
    hit_count = 0
    total_tests = 0
    rec_count = 0
    valid_users = 0

    for user in users:
        # 用户做过且得分>=60的题
        liked_ids = list(
            UserQuestionStatus.objects.filter(user=user, best_score__gte=60)
            .values_list('question_id', flat=True)
        )

        if len(liked_ids) < 3:
            continue

        all_done_ids = set(
            UserQuestionStatus.objects.filter(user=user)
            .values_list('question_id', flat=True)
        )

        user_hits = 0
        user_tests = 0
        user_recs = 0

        for _ in range(rounds):
            # 留一法：随机隐藏一道喜欢的题
            hidden = random.choice(liked_ids)
            exclude_ids = all_done_ids - {hidden}

            try:
                recommendations = algorithm.recommend(user, n=k, exclude_ids=exclude_ids)
            except Exception:
                continue

            if not recommendations:
                continue

            rec_ids = set(qid for qid, _ in recommendations)
            all_recommended.update(rec_ids)

            if hidden in rec_ids:
                user_hits += 1

            user_tests += 1
            user_recs += len(rec_ids)

        if user_tests > 0:
            hit_count += user_hits
            total_tests += user_tests
            rec_count += user_recs
            valid_users += 1

    if total_tests == 0 or valid_users == 0:
        return {
            'precision': 0, 'recall': 0, 'f1': 0,
            'hit_rate': 0, 'coverage': 0, 'valid_users': 0,
        }

    # Hit Rate = 命中次数 / 总测试次数
    hit_rate = round(hit_count / total_tests, 4)

    # Precision = 命中次数 / 总推荐数
    precision = round(hit_count / rec_count, 4) if rec_count > 0 else 0

    # Recall = Hit Rate（留一法中 recall = hit_rate）
    recall = hit_rate

    f1 = round(2 * precision * recall / (precision + recall), 4) if (precision + recall) > 0 else 0
    coverage = round(len(all_recommended) / total_questions * 100, 2) if total_questions > 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'hit_rate': hit_rate,
        'coverage': coverage,
        'valid_users': valid_users,
    }