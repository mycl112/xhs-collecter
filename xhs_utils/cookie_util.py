import time

def trans_cookies(cookies_str):
    """
    将Cookie字符串转换为字典
    :param cookies_str: Cookie字符串
    :return: Cookie字典
    """
    ck = {}
    if not cookies_str:
        return ck
    
    # 分割Cookie字符串
    cookie_pairs = cookies_str.split('; ')
    if len(cookie_pairs) == 1:
        cookie_pairs = cookies_str.split(';')
    
    # 解析每个Cookie对
    for pair in cookie_pairs:
        pair = pair.strip()
        if '=' in pair:
            key, value = pair.split('=', 1)  # 限制只分割一次，避免值中包含=号
            ck[key.strip()] = value.strip()
    
    return ck

def validate_cookie(cookie_dict):
    """
    验证Cookie的有效性
    :param cookie_dict: Cookie字典
    :return: (bool, str) 有效性和错误信息
    """
    if not cookie_dict:
        return False, "Cookie为空"
    
    # 检查必要的Cookie字段
    required_fields = ['a1', 'web_session']
    for field in required_fields:
        if field not in cookie_dict:
            return False, f"缺少必要的Cookie字段: {field}"
    
    return True, "Cookie有效"

def get_cookie_expiry(cookie_dict):
    """
    获取Cookie的过期时间
    :param cookie_dict: Cookie字典
    :return: int 过期时间戳（秒），如果无法获取则返回None
    """
    # 尝试从多个可能的字段获取过期时间
    expiry_fields = ['expires', 'expiry', '__expires']
    for field in expiry_fields:
        if field in cookie_dict:
            try:
                return int(cookie_dict[field])
            except:
                continue
    
    return None

def is_cookie_expired(cookie_dict):
    """
    检查Cookie是否已过期
    :param cookie_dict: Cookie字典
    :return: bool 是否已过期
    """
    expiry = get_cookie_expiry(cookie_dict)
    if not expiry:
        # 如果无法获取过期时间，假设Cookie未过期
        return False
    
    # 检查是否已过期
    return expiry < int(time.time())
