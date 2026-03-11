from abc import ABC, abstractmethod
import jieba
import re
from collections import Counter

# 评分权重配置
F1_SCORE_WEIGHT = 85
RECALL_WEIGHT = 15
MAX_SCORE = 100

# 评分等级阈值
EXCELLENT_THRESHOLD = 80
GOOD_THRESHOLD = 60
BASIC_THRESHOLD = 30

# 反馈配置
MAX_MISSED_WORDS_HINT = 5  # 最多提示的遗漏关键词数量

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
        if not user_answer or not user_answer.strip():
            return 0, '答案为空'

        if not standard_answer or not standard_answer.strip():
            return 0, '无法评分，标准答案为空'

        # 中文分词 + 去停用词
        standard_counter = self._tokenize(standard_answer)
        user_counter = self._tokenize(user_answer)

        if not standard_counter:
            return 0, '无法评分，标准答案无效'
            
        if not user_counter:
            return 0, '无法评分，用户答案无效'

        # 计算加权重叠词数（考虑词频）
        # 计算两个 Counter 的交集（词频取最小值）
        intersection = standard_counter & user_counter
        overlap_count = sum(intersection.values())

        # 总词数（用于计算比率）
        total_standard_words = sum(standard_counter.values())
        total_user_words = sum(user_counter.values())

        # 召回率：用户答案覆盖了标准答案的多少内容
        recall = overlap_count / total_standard_words if total_standard_words > 0 else 0

        # 精确率：用户答案中有多少是有效内容
        precision = overlap_count / total_user_words if total_user_words > 0 else 0

        # F1 Score
        if precision + recall == 0:
            f1_score = 0
        else:
            f1_score = 2 * (precision * recall) / (precision + recall)
            
        # 综合评分：召回率权重更高（覆盖率更重要）
        # score = F1 * 0.5 + Recall * 0.5 * 100
        score = (f1_score * 0.6 + recall * 0.4) * 100
        score = min(100, max(0, score))

        # 生成评语
        # 获取遗漏的关键词（在标准答案中出现频率高但在用户答案中缺失的）
        missed_words = []
        for word, count in standard_counter.most_common():
            if word not in user_counter:
                missed_words.append(word)
                if len(missed_words) >= 5:
                    break
                    
        feedback = self._generate_feedback(score, missed_words)

        return round(score, 2), feedback
        
    def _generate_feedback(self, score, missed_words):
        """生成评语"""
        if score >= 90:
            return "回答非常完美！涵盖了所有关键点。"
        elif score >= 60:
            feedback = "回答基本正确。"
            if missed_words:
                feedback += f" 建议补充以下关键词：{', '.join(missed_words)}。"
            return feedback
        else:
            feedback = "回答还有待完善。"
            if missed_words:
                feedback += f" 关键点缺失较多，请注意包含：{', '.join(missed_words)}。"
            return feedback

    def _tokenize(self, text):
        """中文分词 + 去停用词 + 文本清洗（返回 Counter 保留词频）"""
        if not text or not text.strip():
            return Counter()

        # 转小写并去除首尾空格
        text = text.lower().strip()

        # 移除特殊符号和标点（保留中英文、数字、字母）
        text = re.sub(r'[^\w\u4e00-\u9fff]+', '', text)

        # 移除纯数字（除非是重要术语）
        text = re.sub(r'\b\d+\b', '', text)

        # 中文分词
        words = jieba.cut(text)

        # 过滤：去除单字、停用词、空字符串，返回 Counter
        filtered_words = [
            w.strip() for w in words
            if len(w.strip()) > 1 and w.strip() not in self.STOP_WORDS
        ]

        return Counter(filtered_words)