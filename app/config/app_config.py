"""
PaceKeeper Qt - 애플리케이션 설정 관리
설정 값 로드, 저장 및 기본값 관리
"""

import os
import json
from PyQt6.QtCore import QObject, pyqtSignal


class AppConfig(QObject):
    """애플리케이션 설정 관리 클래스"""
    
    # 설정 변경 시 발생하는 시그널
    settingChanged = pyqtSignal(str, object)
    
    def __init__(self, config_file=None):
        super().__init__()
        
        # 설정 파일 경로 결정
        if config_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.config_file = os.path.join(base_dir, "config.json")
        else:
            self.config_file = config_file
        
        # 기본 설정값
        self.default_settings = {
            # 일반 설정
            "theme": "default",
            "language": "ko",
            
            # 타이머 설정
            "study_time": 25,  # 분 단위
            "break_time": 5,   # 분 단위
            "long_break_time": 15,  # 분 단위
            "long_break_interval": 4,  # 세션 수
            "auto_start_breaks": True,
            "auto_start_pomodoros": False,
            
            # 소리 설정
            "sound_enabled": True,
            "timer_end_sound": "bell.wav",
            "break_end_sound": "bell.wav",
            
            # UI 설정
            "main_dlg_width": 800,
            "main_dlg_height": 500,
            "show_seconds": True,
            "minimize_to_tray": True,
            
            # 알림 설정
            "notifications_enabled": True,
            "notification_sound": True,
        }
        
        # 설정 로드
        self.settings = self.default_settings.copy()
        self.load_settings()
    
    def load_settings(self):
        """설정 파일에서 설정 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # 로드된 설정을 기본 설정과 병합
                    self.settings.update(loaded_settings)
        except Exception as e:
            print(f"설정 로드 중 오류 발생: {e}")
    
    def save_settings(self):
        """설정을 파일에 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"설정 저장 중 오류 발생: {e}")
    
    def get(self, key, default=None):
        """설정값 가져오기"""
        return self.settings.get(key, default if default is not None else self.default_settings.get(key))
    
    def set(self, key, value):
        """설정값 설정"""
        if key in self.settings and self.settings[key] == value:
            return False  # 변경 없음
        
        self.settings[key] = value
        self.settingChanged.emit(key, value)
        return True
    
    def reset(self, key=None):
        """설정값 초기화"""
        if key is None:
            # 모든 설정 초기화
            self.settings = self.default_settings.copy()
            for key, value in self.settings.items():
                self.settingChanged.emit(key, value)
        elif key in self.default_settings:
            # 특정 설정만 초기화
            self.settings[key] = self.default_settings[key]
            self.settingChanged.emit(key, self.default_settings[key])
