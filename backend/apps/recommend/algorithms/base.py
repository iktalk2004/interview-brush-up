from abc import ABC, abstractmethod


class BaseRecommender(ABC):
    """推荐算法基类"""

    @abstractmethod
    def recommend(self, user, n=5, exclude_ids=None):
        """
        为用户生成推荐列表
        :param user: 用户对象
        :param n: 推荐数量
        :param exclude_ids: 需排除的题目ID集合
        :return: [(question_id, score), ...]
        """
        pass

    @abstractmethod
    def get_name(self):
        """算法名称"""
        pass