import json
from dataclasses import dataclass
from typing import Dict
from pathlib import Path

@dataclass(frozen=True)
class LanguageResource:
    base_labels: Dict[str, str]
    title_labels: Dict[str, str]
    button_labels: Dict[str, str]
    messages: Dict[str, str]
    error_messages: Dict[str, str]

def load_language_resource(language: str = "ko") -> LanguageResource:
    """
    주어진 언어 코드('en' 또는 'ko')에 따른 리소스 파일을 로드하여 LanguageResource 객체를 반환합니다.
    만약 지원되지 않는 언어 코드가 전달되면 기본값 'ko'를 사용합니다.
    """
    allowed_languages = ['en', 'ko']
    if language not in allowed_languages:
        print(f"지원되지 않는 언어 코드 '{language}' 입니다. 기본값 'ko'로 설정합니다.")
        language = "ko"

    file_path = Path(__file__).parent / f"lang_{language}.json"
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise RuntimeError(f"언어 리소스 로드 실패: {e}")

    return LanguageResource(
        base_labels=data.get("BASE_LABELS", {}),
        title_labels=data.get("TITLE_LABELS", {}),
        button_labels=data.get("BUTTON_LABELS", {}),
        messages=data.get("MESSAGES", {}),
        error_messages=data.get("ERROR_MESSAGES", {})
    )
