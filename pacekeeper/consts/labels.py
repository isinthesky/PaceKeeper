import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LanguageResource:
    base_labels: dict[str, str]
    title_labels: dict[str, str]
    button_labels: dict[str, str]
    menu_labels: dict[str, str]
    tab_labels: dict[str, str]
    group_labels: dict[str, str]
    setting_labels: dict[str, str]
    messages: dict[str, str]
    error_messages: dict[str, str]

def load_language_resource(language: str = "ko") -> LanguageResource:
    """
    주어진 언어 코드('en' 또는 'ko')에 따른 리소스 파일을 로드하여 LanguageResource 객체를 반환합니다.
    만약 지원되지 않는 언어 코드가 전달되면 기본값 'ko'를 사용합니다.
    """
    allowed_languages = ['en', 'ko']
    if language not in allowed_languages:
        print(f"지원되지 않는 언어 코드 '{language}' 입니다. 기본값 'ko'로 설정합니다.")
        language = "ko"

    # PyInstaller로 빌드된 경우 리소스 경로 처리
    if getattr(sys, 'frozen', False):
        # 빌드된 실행파일에서는 _MEIPASS 경로 사용
        base_path = os.path.join(sys._MEIPASS, 'pacekeeper', 'consts')
        file_path = os.path.join(base_path, f"lang_{language}.json")
    else:
        # 개발 환경에서는 현재 파일 기준 경로 사용
        file_path = Path(__file__).parent / f"lang_{language}.json"
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise RuntimeError(f"언어 리소스 로드 실패: {e}") from e

    return LanguageResource(
        base_labels=data.get("BASE_LABELS", {}),
        title_labels=data.get("TITLE_LABELS", {}),
        button_labels=data.get("BUTTON_LABELS", {}),
        menu_labels=data.get("MENU_LABELS", {}),
        tab_labels=data.get("TAB_LABELS", {}),
        group_labels=data.get("GROUP_LABELS", {}),
        setting_labels=data.get("SETTING_LABELS", {}),
        messages=data.get("MESSAGES", {}),
        error_messages=data.get("ERROR_MESSAGES", {})
    )
