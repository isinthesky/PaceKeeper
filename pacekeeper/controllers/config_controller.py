# controllers/config_controller.py

from typing import Dict, Any, Optional

from pacekeeper.services.app_state_manager import AppStatus, AppStateManager
from pacekeeper.services.settings_manager import SettingsManager
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import SET_LANGUAGE

# 언어 리소스 로드
lang_res = load_language_resource()

class ConfigController:
    """
    앱의 설정 및 상태를 통합 관리하는 컨트롤러
    
    설정 관리와 앱 상태 관리를 조합하여 애플리케이션 전체 구성을 제어합니다.
    """
    _instance = None

    def __new__(cls, settings_manager: Optional[SettingsManager] = None, app_state_manager: Optional[AppStateManager] = None):
        """
        싱글톤 패턴 구현 또는 의존성 주입을 통한 인스턴스 생성
        
        Args:
            settings_manager: 설정 관리자 인스턴스 (None이면 새로 생성)
            app_state_manager: 앱 상태 관리자 인스턴스 (None이면 새로 생성)
        
        Returns:
            ConfigController 인스턴스
        """
        if settings_manager is not None or app_state_manager is not None:
            # 의존성 주입 모드: 새 인스턴스 생성
            return super().__new__(cls)
        
        # 싱글톤 모드: 기존 인스턴스 반환 또는 새 인스턴스 생성
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, settings_manager: Optional[SettingsManager] = None, app_state_manager: Optional[AppStateManager] = None):
        """
        ConfigController 초기화
        
        Args:
            settings_manager: 설정 관리자 인스턴스 (None이면 새로 생성)
            app_state_manager: 앱 상태 관리자 인스턴스 (None이면 새로 생성)
        """
        # 싱글톤 모드에서 중복 초기화 방지
        if hasattr(self, "__initialized") and self.__initialized:
            return
            
        # 의존성 주입 또는 새 인스턴스 생성
        self.settings_manager = settings_manager or SettingsManager()
        self.app_state_manager = app_state_manager or AppStateManager()
        
        self.__initialized = True

    # --- 설정 관련 메서드 (SettingsManager에 위임) ---
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        설정 값 반환
        
        Args:
            key: 설정 키
            default: 설정이 존재하지 않을 경우 반환할 기본값
        
        Returns:
            설정 값 또는 기본값
        """
        return self.settings_manager.get_setting(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """
        설정 값 설정
        
        Args:
            key: 설정 키
            value: 설정 값
        """
        self.settings_manager.set_setting(key, value)
        
    def save_settings(self) -> bool:
        """
        현재 설정을 파일에 저장
        
        Returns:
            저장 성공 여부
        """
        return self.settings_manager.save_settings()

    def update_settings(self, new_settings: Dict[str, Any]) -> Dict[str, str]:
        """
        여러 설정 값 업데이트 및 저장
        
        Args:
            new_settings: 업데이트할 설정 딕셔너리
        
        Returns:
            유효성 검사 오류 메시지 딕셔너리 (키: 설정 키, 값: 오류 메시지)
        """
        return self.settings_manager.update_settings(new_settings)

    def get_language(self) -> str:
        """
        현재 설정된 언어 코드 반환
        
        Returns:
            언어 코드 (기본값: "ko")
        """
        return self.settings_manager.get_language()

    def set_language(self, lang: str) -> None:
        """
        언어 코드 설정
        
        Args:
            lang: 언어 코드 ("ko" 또는 "en")
        """
        self.settings_manager.set_language(lang)

    # --- 상태 관련 메서드 (AppStateManager에 위임) ---
    def get_status(self) -> AppStatus:
        """
        현재 애플리케이션 상태 반환
        
        Returns:
            현재 AppStatus
        """
        return self.app_state_manager.get_status()

    def set_status(self, status: AppStatus) -> None:
        """
        애플리케이션 상태 설정
        
        Args:
            status: 새 애플리케이션 상태
        """
        self.app_state_manager.set_status(status)

    @property
    def is_running(self) -> bool:
        """애플리케이션 실행 상태 반환"""
        return self.app_state_manager.is_running()
    
    @is_running.setter
    def is_running(self, running: bool) -> None:
        """애플리케이션 실행 상태 설정"""
        self.app_state_manager.set_running(running)

    def start_app(self) -> None:
        """애플리케이션 시작 및 상태 변경"""
        self.app_state_manager.start_app()

    def stop_app(self) -> None:
        """애플리케이션 중지 및 상태 초기화"""
        self.app_state_manager.stop_app()

    def increment_cycle(self) -> int:
        """
        사이클 수 증가
        
        Returns:
            증가된 사이클 수
        """
        return self.app_state_manager.increment_cycle()

    def get_cycle(self) -> int:
        """
        현재 사이클 수 반환
        
        Returns:
            현재 사이클 수
        """
        return self.app_state_manager.get_cycle()