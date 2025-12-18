import random
import string

def generate_random_nickname(prefix: str = "用户") -> str:
    """
    生成随机昵称
    格式: 前缀_随机字符串(6位)
    """
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"{prefix}_{suffix}"
