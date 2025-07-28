#!/usr/bin/env python3
"""애플리케이션 경로 관리 유틸리티"""
import os
import sys
from pathlib import Path

from pacekeeper.consts.settings import CONFIG_FILE, DB_FILE


def get_app_data_dir():
    """
    애플리케이션 데이터 디렉토리 반환
    
    개발 환경과 프로덕션 환경에서 통일된 데이터 디렉토리를 제공합니다.
    
    Returns:
        str: 애플리케이션 데이터 디렉토리 경로
    """
    if getattr(sys, 'frozen', False):
        # 프로덕션 환경 (PyInstaller)
        if sys.platform == 'darwin':
            # macOS: Application Support 디렉토리
            app_dir = os.path.expanduser('~/Library/Application Support/PaceKeeper')
        elif sys.platform == 'win32':
            # Windows: AppData Roaming 디렉토리
            app_dir = os.path.expanduser('~/AppData/Roaming/PaceKeeper')
        else:
            # Linux: 숨김 디렉토리
            app_dir = os.path.expanduser('~/.pacekeeper')
    else:
        # 개발 환경
        # 프로젝트 루트/data 디렉토리 사용 (기존 pacekeeper/ 대신)
        base_dir = Path(__file__).parent.parent.parent
        app_dir = os.path.join(base_dir, 'data')

    # 디렉토리가 없으면 생성
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def get_config_path():
    """
    설정 파일 경로 반환
    
    Returns:
        str: config.json 파일의 전체 경로
    """
    return os.path.join(get_app_data_dir(), CONFIG_FILE)


def get_database_path():
    """
    데이터베이스 파일 경로 반환
    
    Returns:
        str: 데이터베이스 파일의 전체 경로
    """
    return os.path.join(get_app_data_dir(), DB_FILE)


def get_log_dir():
    """
    로그 디렉토리 경로 반환
    
    Returns:
        str: 로그 디렉토리 경로
    """
    log_dir = os.path.join(get_app_data_dir(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def get_backup_dir():
    """
    백업 디렉토리 경로 반환
    
    Returns:
        str: 백업 디렉토리 경로
    """
    backup_dir = os.path.join(get_app_data_dir(), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def get_legacy_paths():
    """
    기존 개발 환경에서 사용하던 경로들 반환
    
    마이그레이션 목적으로 사용됩니다.
    
    Returns:
        dict: 기존 경로들의 딕셔너리
    """
    project_root = Path(__file__).parent.parent.parent

    return {
        'database': os.path.join(project_root, 'pacekeeper', DB_FILE),
        'config': os.path.join(project_root, 'pacekeeper', CONFIG_FILE),
        'project_root': str(project_root)
    }


def ensure_data_directory():
    """
    데이터 디렉토리와 필요한 하위 디렉토리들을 생성합니다.
    
    Returns:
        bool: 성공 여부
    """
    try:
        get_app_data_dir()  # 메인 데이터 디렉토리
        get_log_dir()       # 로그 디렉토리
        get_backup_dir()    # 백업 디렉토리
        return True
    except Exception as e:
        print(f"데이터 디렉토리 생성 실패: {e}")
        return False


