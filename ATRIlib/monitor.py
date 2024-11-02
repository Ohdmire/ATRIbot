from ATRIlib.DB.pipeline_monitor import monitor_pipeline
from difflib import SequenceMatcher

def calculate_similarity(str1, str2):
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, str1, str2).ratio()

def monitor_profile(group_id):
    # 获取监控数据
    raw = monitor_pipeline(group_id)

    if len(raw) == 0:
        return []
    
    # 计算差异度并排序
    diff_results = []
    for item in raw:
        try:
            new_page = item.get('new_page_raw')
            old_page = item.get('old_page_raw')
        except:
            continue
        
        # 计算相似度
        similarity = calculate_similarity(new_page, old_page)
        diff_score = 1 - similarity  # 转换为差异度
        
        diff_results.append({
            'user_id': item.get('user_id'),
            'username': item.get('username'),
            'diff_score': diff_score,
        })
    
    # 按差异度降序排序
    sorted_results = sorted(diff_results, key=lambda x: x['diff_score'], reverse=True)
    
    return sorted_results
