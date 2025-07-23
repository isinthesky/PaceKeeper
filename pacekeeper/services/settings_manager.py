# services/settings_manager.py

import json
import os
import sys
from typing import Any

from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import CONFIG_FILE, DEFAULT_SETTINGS, SET_LANGUAGE

# 언어 리소스 로드
lang_res = load_language_resource()


class SettingsObserver:
    """설정 변경을 관찰하는 옵저버 인터페이스"""
    def on_settings_changed(self, key: str, old_value: Any, new_value: Any) -> None:
        """
        설정 변경 알림을 받는 메서드

        Args:
            key: 변경된 설정 키
            old_value: 이전 설정 값
            new_value: 새 설정 값
        """
        pass


class SettingsManager:
    """
    애플리케이션 설정 관리 클래스

    설정 파일 로드, 저장 및 설정 값 접근 기능을 제공합니다.
    설정 변경 시 등록된 옵저버에게 알림을 보냅니다.
    """
    def __init__(self, config_file: str = CONFIG_FILE) -> None:
        """
        SettingsManager 초기화

        Args:
            config_file: 설정 파일 이름 (기본값: CONFIG_FILE 상수 사용)
        """
        # PyInstaller로 빌드된 경우
        if getattr(sys, 'frozen', False):
            # 사용자 홈 디렉토리 사용 (설정은 사용자별로 저장)
            self.config_dir: str = os.path.join(os.path.expanduser('~'), '.pacekeeper')
            os.makedirs(self.config_dir, exist_ok=True)
            self.config_file: str = os.path.join(self.config_dir, config_file)
        else:
            # 개발 환경에서는 기존 방식 사용
            self.config_dir: str = os.path.join(os.path.expanduser('~'), '.pacekeeper')
            os.makedirs(self.config_dir, exist_ok=True)
            self.config_file: str = os.path.join(self.config_dir, config_file)

        self.default_settings: dict[str, Any] = dict(DEFAULT_SETTINGS)
        self.settings: dict[str, Any] = dict(self.default_settings)

        # 옵저버 목록 초기화
        self._observers: list[SettingsObserver] = []

        # 설정 로드
        self.load_settings()

    def add_observer(self, observer: SettingsObserver) -> None:
        """
        설정 변경을 관찰할 옵저버 추가

        Args:
            observer: 설정 변경을 관찰할 SettingsObserver 인스턴스
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: SettingsObserver) -> None:
        """
        등록된 옵저버 제거

        Args:
            observer: 제거할 SettingsObserver 인스턴스
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, key: str, old_value: Any, new_value: Any) -> None:
        """
        등록된 모든 옵저버에게 설정 변경 알림

        Args:
            key: 변경된 설정 키
            old_value: 이전 설정 값
            new_value: 새 설정 값
        """
        for observer in self._observers:
            observer.on_settings_changed(key, old_value, new_value)

    def load_settings(self) -> dict[str, Any]:
        """
        설정 파일에서 설정 로드

        설정 파일이 존재하지 않거나 로드 실패 시 기본 설정을 사용합니다.

        Returns:
            로드된 설정 딕셔너리
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, encoding='utf-8') as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(lang_res.error_messages['SETTINGS_LOAD'].format(e))
                self.settings = dict(self.default_settings)
        else:
            self.save_settings()

        return self.settings

    def save_settings(self) -> bool:
        """
        현재 설정을 파일에 저장

        Returns:
            저장 성공 여부
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(lang_res.error_messages['SETTINGS_SAVE'].format(e))
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        설정 값 반환

        Args:
            key: 설정 키
            default: 설정이 존재하지 않을 경우 반환할 기본값

        Returns:
            설정 값 또는 기본값
        """
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """
        설정 값 설정 및 옵저버에 알림

        Args:
            key: 설정 키
            value: 설정 값
        """
        old_value = self.settings.get(key)
        self.settings[key] = value
        self._notify_observers(key, old_value, value)

    def update_settings(self, new_settings: dict[str, Any], validate: bool = True) -> dict[str, str]:
        """
        여러 설정 값 업데이트 및 저장

        Args:
            new_settings: 업데이트할 설정 딕셔너리
            validate: 유효성 검사 수행 여부

        Returns:
            유효성 검사 오류 메시지 딕셔너리 (키: 설정 키, 값: 오류 메시지)
            유효성 검사를 통과하면 빈 딕셔너리 반환
        """
        errors: dict[str, str] = {}

        if validate:
            errors = self._validate_settings(new_settings)
            if errors:
                return errors

        # 설정 업데이트 및 옵저버에 알림
        for key, value in new_settings.items():
            old_value = self.settings.get(key)
            self.settings[key] = value
            self._notify_observers(key, old_value, value)

        self.save_settings()
        return {}

    def _validate_settings(self, settings: dict[str, Any]) -> dict[str, str]:
        """
        설정 유효성 검사

        Args:
            settings: 검사할 설정 딕셔너리

        Returns:
            유효성 검사 오류 메시지 딕셔너리 (키: 설정 키, 값: 오류 메시지)
            유효성 검사를 통과하면 빈 딕셔너리 반환
        """
        errors: dict[str, str] = {}

        # 학습 시간 검증
        if "study_time" in settings:
            study_time = settings["study_time"]
            if not isinstance(study_time, int) or study_time < 1 or study_time > 120:
                errors["study_time"] = lang_res.error_messages.get(
                    'INVALID_STUDY_TIME',
                    "학습 시간은 1~120 사이의 정수여야 합니다."
                )

        # 짧은 휴식 시간 검증
        if "short_break" in settings:
            short_break = settings["short_break"]
            if not isinstance(short_break, int) or short_break < 1 or short_break > 30:
                errors["short_break"] = lang_res.error_messages.get(
                    'INVALID_SHORT_BREAK',
                    "짧은 휴식 시간은 1~30 사이의 정수여야 합니다."
                )

        # 긴 휴식 시간 검증
        if "long_break" in settings:
            long_break = settings["long_break"]
            if not isinstance(long_break, int) or long_break < 5 or long_break > 60:
                errors["long_break"] = lang_res.error_messages.get(
                    'INVALID_LONG_BREAK',
                    "긴 휴식 시간은 5~60 사이의 정수여야 합니다."
                )

        # 사이클 수 검증
        if "cycles" in settings:
            cycles = settings["cycles"]
            if not isinstance(cycles, int) or cycles < 1 or cycles > 10:
                errors["cycles"] = lang_res.error_messages.get(
                    'INVALID_CYCLES',
                    "사이클 수는 1~10 사이의 정수여야 합니다."
                )

        # 언어 설정 검증
        if SET_LANGUAGE in settings:
            language = settings[SET_LANGUAGE]
            if language not in ["ko", "en"]:
                errors[SET_LANGUAGE] = lang_res.error_messages.get(
                    'INVALID_LANGUAGE',
                    "지원하지 않는 언어입니다. 지원 언어: ko, en"
                )

        return errors

    def get_language(self) -> str:
        """
        현재 설정된 언어 코드 반환

        Returns:
            언어 코드 (기본값: "ko")
        """
        return self.settings.get(SET_LANGUAGE, "ko")

    def set_language(self, lang: str) -> None:
        """
        언어 코드 설정

        Args:
            lang: 언어 코드 ("ko" 또는 "en")
        """
        self.set_setting(SET_LANGUAGE, lang)

    def reset_to_defaults(self) -> None:
        """설정을 기본값으로 초기화"""
        old_settings = dict(self.settings)
        self.settings = dict(self.default_settings)

        # 변경된 모든 설정에 대해 옵저버에 알림
        for key, new_value in self.settings.items():
            old_value = old_settings.get(key)
            if old_value != new_value:
                self._notify_observers(key, old_value, new_value)

        self.save_settings()
