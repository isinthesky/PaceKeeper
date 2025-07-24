#!/usr/bin/env python3
"""리소스 경로 처리 유틸리티"""
import logging
import os
import sys

logger = logging.getLogger(__name__)

def resource_path(relative_path):
    """PyInstaller로 빌드된 앱에서 리소스 경로를 올바르게 반환합니다."""
    if getattr(sys, 'frozen', False):
        # PyInstaller 환경: sys._MEIPASS 사용
        base_path = sys._MEIPASS
    else:
        # 개발 환경: 프로젝트 루트 디렉토리 사용
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # 상대 경로 처리
    if relative_path.startswith('pacekeeper/'):
        # 개발 환경에서의 전체 경로
        if not getattr(sys, 'frozen', False):
            full_path = os.path.join(base_path, relative_path)
        else:
            # PyInstaller 환경에서는 pacekeeper/ 접두사 제거
            relative_path = relative_path.replace('pacekeeper/', '')
            full_path = os.path.join(base_path, relative_path)
    else:
        full_path = os.path.join(base_path, relative_path)

    # 디버그 로깅
    logger.debug(f"Resource path: {relative_path} -> {full_path}")
    logger.debug(f"File exists: {os.path.exists(full_path)}")

    return full_path

# get_asset_path 함수 제거됨 - 현재 사용되지 않음
# def get_asset_path(filename):
#     """assets 디렉토리의 파일 경로를 반환합니다."""
#     return resource_path(os.path.join('assets', filename))

# get_icon_path 함수 제거됨 - 현재 사용되지 않음
# def get_icon_path(filename):
#     """아이콘 파일 경로를 반환합니다."""
#     return resource_path(os.path.join('assets', 'icons', filename))

# get_sound_path 함수 제거됨 - 현재 사용되지 않음
# def get_sound_path(filename):
#     """사운드 파일 경로를 반환합니다."""
#     return resource_path(os.path.join('assets', 'sounds', filename))

# get_config_path 함수 제거됨 - 현재 사용되지 않음
# def get_config_path():
#     """config.json 파일 경로를 반환합니다."""
#     return resource_path('config.json')
