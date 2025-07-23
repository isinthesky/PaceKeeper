# utils.py
import os
import re
import sys


def resource_path(relative_path: str) -> str:
    """
    PyInstaller 환경 등에서 리소스 절대 경로를 반환
    """
    try:
        base_path = sys._MEIPASS  # PyInstaller 임시 폴더
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def extract_tags(message: str) -> list[str]:
    """
    message에서 태그 추출
    """
    tags = re.findall(r'#(\w+)', message)
    return tags
