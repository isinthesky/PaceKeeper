"""데이터베이스 설정 모듈"""
from pacekeeper.utils.app_paths import get_database_path


def get_db_path():
    """앱 실행 환경에 따른 데이터베이스 경로 반환"""
    return get_database_path()


# 데이터베이스 URI
DATABASE_URI = f"sqlite:///{get_db_path()}"
