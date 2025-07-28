# utils.py
import re




def extract_tags(message: str) -> list[str]:
    """
    message에서 태그 추출
    """
    tags = re.findall(r'#(\w+)', message)
    return tags
