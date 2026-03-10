import json
import re
import requests
from django.conf import settings

from .base import BaseScorer, SimpleScorer


class DeepSeekScorer(BaseScorer):
    """DeepSeek AI 评分引擎"""

    SYSTEM_PROMPT = """你是一个专业的技术面试评分官。请根据以下信息对用户的回答进行评分：

评分规则：
1. 满分100分
2. 从以下维度评分：
   - 核心概念准确性（40分）：回答是否涵盖了标准答案中的核心知识点
   - 完整性（30分）：回答是否全面，是否有重要遗漏
   - 表述清晰度（20分）：回答是否条理清晰、逻辑通顺
   - 额外加分（10分）：是否有标准答案以外的正确补充

请严格按照以下JSON格式回复，不要输出任何其他内容：
{"score": 数字, "feedback": "评语文字"}

评语要求：
- 简洁明了，2-4句话
- 指出答对了哪些要点
- 指出遗漏或错误的地方
- 给出改进建议"""

    def get_name(self):
        return 'deepseek'

    def score(self, question_title, standard_answer, user_answer):
        api_key = settings.DEEPSEEK_API_KEY
        if not api_key:
            fallback = SimpleScorer()
            score, feedback = fallback.score(question_title, standard_answer, user_answer)
            return score, f'[DeepSeek未配置，使用关键词匹配] {feedback}'

        user_prompt = f"""题目：{question_title}

标准答案：{standard_answer}

用户回答：{user_answer}

请评分并给出评语。"""

        try:
            response = requests.post(
                f"{settings.DEEPSEEK_BASE_URL}/v1/chat/completions",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}',
                },
                json={
                    'model': settings.DEEPSEEK_MODEL,
                    'messages': [
                        {'role': 'system', 'content': self.SYSTEM_PROMPT},
                        {'role': 'user', 'content': user_prompt},
                    ],
                    'temperature': 0.3,
                    'max_tokens': 300,
                },
                timeout=30,
            )

            if response.status_code != 200:
                raise Exception(f'API返回状态码: {response.status_code}, 内容: {response.text[:200]}')

            data = response.json()
            content = data['choices'][0]['message']['content'].strip()

            # 处理可能包含markdown代码块的情况
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)
            score = float(result.get('score', 0))
            score = max(0, min(100, score))
            feedback = result.get('feedback', '评分完成')

            return round(score, 2), feedback

        except json.JSONDecodeError:
            # JSON解析失败，尝试从文本中提取分数
            try:
                score_match = re.search(r'"score"\s*:\s*(\d+(?:\.\d+)?)', content)
                if score_match:
                    score = float(score_match.group(1))
                    return round(min(100, score), 2), 'AI评分完成（响应格式异常，已提取分数）'
            except Exception:
                pass
            fallback = SimpleScorer()
            return fallback.score(question_title, standard_answer, user_answer)

        except Exception as e:
            fallback = SimpleScorer()
            score, feedback = fallback.score(question_title, standard_answer, user_answer)
            return score, f'[AI评分不可用: {str(e)[:50]}，使用关键词匹配] {feedback}'