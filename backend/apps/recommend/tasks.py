from celery import shared_task
from .algorithms.user_cf import UserBasedCF
from .algorithms.item_cf import ItemBasedCF

@shared_task
def update_user_similarity():
    """定期更新用户相似度矩阵"""
    try:
        count = UserBasedCF.compute_and_save_all()
        return f"Successfully updated {count} user similarity pairs."
    except Exception as e:
        return f"Failed to update user similarity: {str(e)}"

@shared_task
def update_item_similarity():
    """定期更新题目相似度矩阵"""
    try:
        count = ItemBasedCF.compute_and_save_all()
        return f"Successfully updated {count} item similarity pairs."
    except Exception as e:
        return f"Failed to update item similarity: {str(e)}"
