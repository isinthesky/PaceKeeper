"""데이터베이스 설정 모듈"""
import os
import sys
from pathlib import Path

from pacekeeper.consts.settings import DB_FILE


def get_db_path():
    """앱 실행 환경에 따른 데이터베이스 경로 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 경우
        # macOS의 경우 Application Support 디렉토리 사용
        if sys.platform == 'darwin':
            app_support = os.path.expanduser('~/Library/Application Support/PaceKeeper')
        else:
            app_support = os.path.expanduser('~/.pacekeeper')
        
        # 디렉토리가 없으면 생성
        os.makedirs(app_support, exist_ok=True)
        db_path = os.path.join(app_support, DB_FILE)
    else:
        # 개발 환경
        # 프로젝트 루트에서 한 단계 위의 pacekeeper 디렉토리에 생성
        base_dir = Path(__file__).parent.parent
        db_path = os.path.join(base_dir, DB_FILE)
    
    return db_path


# 데이터베이스 URI
DATABASE_URI = f"sqlite:///{get_db_path()}"