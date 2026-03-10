from abc import ABC, abstractmethod
import jieba


class BaseScorer(ABC):
    """评分引擎基类"""

    @abstractmethod
    def score(self, question_title, standard_answer, user_answer):
        pass

    @abstractmethod
    def get_name(self):
        pass


class SimpleScorer(BaseScorer):
    """基于中文分词的关键词匹配评分"""

    # 停用词（常见无意义词汇）
    STOP_WORDS = {
        '的', '了', '是', '在', '和', '与', '及', '等', '有', '对',
        '也', '都', '而', '或', '被', '从', '到', '把', '可以', '进行',
        '通过', '使用', '其', '这', '那', '一个', '一种', '用于', '可',
        '会', '能', '就', '不', '要', '为', '以', '将', '所', '由',
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but',
        'with', 'that', 'this', 'it', 'as', 'by', 'from',
    }

    def get_name(self):
        return 'simple'

    def score(self, question_title, standard_answer, user_answer):
        if not user_answer.strip():
            return 0, '答案为空'

        if not standard_answer.strip():
            return 50, '无法评分，标准答案为空'

        # 中文分词 + 去停用词
        standard_words = self._tokenize(standard_answer)
        user_words = self._tokenize(user_answer)

        if not standard_words:
            return 50, '无法评分'

        # 关键词命中率
        overlap = standard_words & user_words
        recall = len(overlap) / len(standard_words)  # 覆盖了多少标准答案的关键词

        # 精确度（用户答案中有多少是有效关键词）
        precision = len(overlap) / len(user_words) if user_words else 0

        # 综合评分：recall权重更高（覆盖率更重要）
        if recall == 0 and precision == 0:
            score = 0
        else:
            f_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            score = round(f_score * 85 + recall * 15, 2)  # 最高100分

        score = min(100, max(0, score))

        # 生成评语
        feedback = self._generate_feedback(score, overlap, standard_words - overlap)

        return round(score, 2), feedback

    def _tokenize(self, text):
        """中文分词 + 去停用词 + 去单字"""
        text = text.lower().strip()
        words = jieba.cut(text)
        return {
            w.strip() for w in words
            if len(w.strip()) > 1 and w.strip() not in self.STOP_WORDS
        }

    def _generate_feedback(self, score, hit_words, missed_words):
        """生成评语"""
        if score >= 80:
            feedback = '回答非常好，覆盖了大部分核心知识点。'
        elif score >= 60:
            feedback = '回答基本正确，但可以更加完善。'
        elif score >= 30:
            feedback = '回答涉及了部分内容，但遗漏较多关键点。'
        elif score > 0:
            feedback = '回答与标准答案差距较大，建议重新学习该知识点。'
        else:
            feedback = '未检测到相关知识点，请认真作答。'

        # 补充遗漏关键词提示（最多提示5个）
        if missed_words and score < 80:
            missed_sample = list(missed_words)[:5]
            feedback += f' 建议补充以下关键点：{"、".join(missed_sample)}。'

        return feedback