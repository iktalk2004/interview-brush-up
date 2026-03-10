def normalize_score(score, min_val=0, max_val=100):
    """评分归一化，统一映射到0-100"""
    score = max(min_val, min(max_val, score))
    return round(score, 2)