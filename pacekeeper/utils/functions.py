# utils.py
import os
import sys
import re

def resource_path(relative_path: str) -> str:
    """
    PyInstaller 환경 등에서 리소스 절대 경로를 반환
    """
    try:
        # PyInstaller 환경에서는 _MEIPASS 사용
        base_path = sys._MEIPASS
    except Exception:
        # 개발 환경에서는 현재 디렉토리 사용
        base_path = os.path.abspath(".")
    
    # 파일이 존재하는지 확인하고, 존재하지 않으면 사용자 데이터 디렉토리에 생성
    full_path = os.path.join(base_path, relative_path)
    
    # 데이터베이스나 설정 파일인 경우 사용자 데이터 디렉토리에 저장
    if relative_path.endswith('.db') or relative_path == 'config.json':
        # 사용자 데이터 디렉토리 (OS에 따라 다름)
        if sys.platform == 'win32':
            user_data_dir = os.path.join(os.environ['APPDATA'], 'PaceKeeper')
        elif sys.platform == 'darwin':  # macOS
            user_data_dir = os.path.expanduser('~/Library/Application Support/PaceKeeper')
        else:  # Linux 및 기타
            user_data_dir = os.path.expanduser('~/.pacekeeper')
        
        # 디렉토리가 없으면 생성
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        
        # 사용자 데이터 디렉토리에 파일 경로 설정
        user_file_path = os.path.join(user_data_dir, os.path.basename(relative_path))
        
        # 개발 모드에서는 기존 경로 사용
        if os.environ.get('PACEKEEPER_DEV_MODE') == '1':
            return full_path
        
        return user_file_path
    
    return full_path


def extract_tags(message: str) -> list[str]:
    """
    message에서 태그 추출
    """
    tags = re.findall(r'#(\w+)', message)
    return tags
