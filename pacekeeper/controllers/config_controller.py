# controllers/config_controller.py

from enum import Enum
from dataclasses import dataclass
from pacekeeper.services.setting_model import SettingsModel
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import SET_LANGUAGE

lang_res = load_language_resource()

@dataclass
class StatusInfo:
    """상태 정보를 담는 데이터 클래스"""
    label: str
    value: int

class AppStatus(Enum):
    WAIT = StatusInfo(label=lang_res.base_labels['WAIT'], value=0)
    STUDY = StatusInfo(label=lang_res.base_labels['STUDY'], value=1)
    SHORT_BREAK = StatusInfo(label=lang_res.base_labels['SHORT_BREAK'], value=2)
    LONG_BREAK = StatusInfo(label=lang_res.base_labels['LONG_BREAK'], value=3)
    PAUSED = StatusInfo(label=lang_res.base_labels['PAUSED'], value=4)

    @property
    def label(self):
        return self.value.label

    @property
    def value_int(self):
        return self.value.value

    @classmethod
    def is_break(cls, status: 'AppStatus') -> bool:
        return status in [cls.SHORT_BREAK, cls.LONG_BREAK]

class ConfigController:
    """
    앱의 전역 상태 및 설정을 관리.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized: 
            return
            
        self.settings_model = SettingsModel()
        self.settings_model.load_settings()

        self._status = AppStatus.WAIT
        self.is_running = False
        self.current_cycle = 1

        self.__initialized = True

    # --- 설정 접근/수정 ---
    def get_setting(self, key: str, default=None):
        return self.settings_model.settings.get(key, default)

    def set_setting(self, key: str, value):
        """설정 값을 업데이트합니다."""
        self.settings_model.settings[key] = value
        
    def save_settings(self):
        """설정을 파일에 저장합니다."""
        self.settings_model.save_settings()

    def update_settings(self, new_settings: dict):
        self.settings_model.update_settings(new_settings)

    # 새로 추가한 언어 설정 접근 메서드
    def get_language(self) -> str:
        """
        현재 설정된 언어 코드를 반환합니다.
        기본값은 'ko'입니다.
        """
        return self.settings_model.settings.get(SET_LANGUAGE, "ko")

    def set_language(self, lang: str):
        """
        언어 코드를 업데이트합니다.
        """
        self.settings_model.settings[SET_LANGUAGE] = lang

    # --- 상태/작업 흐름 ---
    def get_status(self) -> AppStatus:
        return self._status

    def set_status(self, status: AppStatus):
        self._status = status

    def start_app(self):
        self.is_running = True
        self.set_status(AppStatus.STUDY)

    def stop_app(self):
        self.is_running = False
        self.set_status(AppStatus.WAIT)
        self.current_cycle = 1

    def increment_cycle(self):
        self.current_cycle += 1
        return self.current_cycle

    def get_cycle(self):
        return self.current_cycle