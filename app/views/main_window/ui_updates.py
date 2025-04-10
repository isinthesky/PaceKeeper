"""
PaceKeeper Qt - UI 업데이트 함수 모듈
메인 윈도우 UI 업데이트 관련 함수
"""

from PyQt6.QtWidgets import QApplication


def update_ui(window):
    """
    사용자 설정에 따라 UI 업데이트

    Args:
        window: 메인 윈도우 인스턴스
    """
    print(f"[DEBUG] UI 업데이트 시작")
    theme = window.config.get("theme", "default")
    print(f"[DEBUG] 현재 테마: {theme}")

    # 테마 적용 (QApplication에 적용)
    if window.theme_manager:
        app = window.app_instance or QApplication.instance()
        if app:
            # 테마 매니저를 통해 테마 적용
            window.theme_manager.apply_theme(app, theme)
        else:
            # app 인스턴스가 없는 경우 메인 윈도우에만 적용
            style_content = window.theme_manager.get_theme_style(theme)
            if style_content:
                window.setStyleSheet(style_content)

    # 타이머 표시 설정 (초 표시 여부 등)
    show_seconds = window.config.get("show_seconds", True)
    if (
        hasattr(window, "timerWidget")
        and hasattr(window.timerWidget, "isDestroyed")
        and not window.timerWidget.isDestroyed()
    ):
        window.timerWidget.showSeconds(show_seconds)

    # 기타 UI 설정 적용
    # window.setupLayout() # 필요시 레이아웃 다시 설정


def update_recent_logs(window):
    """
    최근 로그 목록 업데이트

    Args:
        window: 메인 윈도우 인스턴스
    """
    # 위젯 유효성 검사 추가
    if (
        not hasattr(window, "logListWidget")
        or not hasattr(window.logListWidget, "isDestroyed")
        or window.logListWidget.isDestroyed()
    ):
        print(f"[DEBUG] 로그 위젯이 없거나 파괴됨")
        return

    # 목록 초기화
    window.logListWidget.clear()

    try:
        # 최근 로그 가져오기 (limit=5)
        recent_logs = window.main_controller.get_recent_logs(limit=5)

        # 목록에 로그 추가
        window.logListWidget.add_logs(recent_logs)
    except Exception as e:
        print(f"[DEBUG] 최근 로그 업데이트 중 오류 발생: {e}")


def update_tags(window):
    """
    태그 버튼 업데이트

    Args:
        window: 메인 윈도우 인스턴스
    """
    # 위젯 유효성 검사 추가
    if (
        not hasattr(window, "tagButtonsWidget")
        or not hasattr(window.tagButtonsWidget, "isDestroyed")
        or window.tagButtonsWidget.isDestroyed()
    ):
        print(f"[DEBUG] 태그 위젯이 없거나 파괴됨")
        return

    try:
        # 최근 사용된 태그 가져오기
        recent_tags = window.main_controller.get_recent_tags(limit=8)

        # 태그 버튼 업데이트
        window.tagButtonsWidget.update_tags(recent_tags)
    except Exception as e:
        print(f"[DEBUG] 태그 업데이트 중 오류 발생: {e}")
