#!/usr/bin/env python3
"""리소스 경로 처리 유틸리티"""
import os
import sys

def resource_path(relative_path):
    """PyInstaller로 빌드된 앱에서 리소스 경로를 올바르게 반환합니다."""
    try:
        # PyInstaller가 생성한 임시 폴더
        base_path = sys._MEIPASS
    except AttributeError:
        # 개발 환경에서 실행 중
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    except Exception as e:
        print(f"Resource path error: {e}")
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 전체 경로 생성
    full_path = os.path.join(base_path, relative_path)
    
    # 디버그 출력
    print(f"Resource path: {relative_path} -> {full_path}")
    
    return full_path

def get_asset_path(filename):
    """assets 디렉토리의 파일 경로를 반환합니다."""
    return resource_path(os.path.join('assets', filename))

def get_icon_path(filename):
    """아이콘 파일 경로를 반환합니다."""
    return resource_path(os.path.join('assets', 'icons', filename))

def get_sound_path(filename):
    """사운드 파일 경로를 반환합니다."""
    return resource_path(os.path.join('assets', 'sounds', filename))

def get_config_path():
    """config.json 파일 경로를 반환합니다."""
    return resource_path('config.json')