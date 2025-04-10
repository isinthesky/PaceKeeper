"""
위젯 유효성 검사 헬퍼 유틸리티
isDestroyed 메서드를 활용한 위젯 상태 확인
"""

def is_widget_valid(widget):
    """
    위젯이 유효한지 검사

    Args:
        widget: 검사할 위젯

    Returns:
        bool: 위젯이 유효하면 True, 그렇지 않으면 False
    """
    return (widget is not None and 
            hasattr(widget, 'isDestroyed') and 
            not widget.isDestroyed())

def validate_widgets_before_theme_update(window):
    """
    테마 업데이트 전 메인 윈도우의 모든 중요 위젯 유효성 검사

    Args:
        window: 메인 윈도우 인스턴스
    """
    # 로그 위젯 검사
    if hasattr(window, 'logListWidget') and is_widget_valid(window.logListWidget):
        window.updateRecentLogs()
        
    # 태그 버튼 위젯 검사
    if hasattr(window, 'tagButtonsWidget') and is_widget_valid(window.tagButtonsWidget):
        window.updateTags()
        
    # 타이머 위젯 검사
    if hasattr(window, 'timerWidget') and is_widget_valid(window.timerWidget):
        # 타이머 위젯 업데이트 로직이 필요하다면 여기에 추가
        pass
        
    # 텍스트 입력 위젯 검사
    if hasattr(window, 'textInputWidget') and is_widget_valid(window.textInputWidget):
        # 텍스트 입력 위젯 업데이트 로직이 필요하다면 여기에 추가
        pass
