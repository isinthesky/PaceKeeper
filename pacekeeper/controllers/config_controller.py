# controllers/config_controller.py
from enum import Enum
from dataclasses import dataclass
from pacekeeper.models.setting_model import SettingsModel
from pacekeeper.models.data_model import DataModel
from pacekeeper.consts.labels import load_language_resource

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
        self.data_model = DataModel()
        self.data_model.init_db()

        self._status = AppStatus.WAIT
        self.is_running = False
        self.current_cycle = 1

        self.__initialized = True

    # --- 설정 접근/수정 ---
    def get_setting(self, key: str, default=None):
        return self.settings_model.settings.get(key, default)

    def update_settings(self, new_settings: dict):
        self.settings_model.update_settings(new_settings)

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

    def get_cycle(self):
        return self.current_cycle
