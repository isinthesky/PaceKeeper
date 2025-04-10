"""
PaceKeeper Qt - 위젯 헬퍼 함수
위젯 관리를 위한 유틸리티 함수
"""

from PyQt6.QtWidgets import QWidget


def setup_widget_helpers():
    """QWidget 클래스에 헬퍼 메서드 추가"""

    # 위젯이 소멸됐는지 확인하는 메서드
    def is_destroyed(self):
        """위젯이 소멸되었는지 확인"""
        try:
            # 소멸된 위젯에 접근하면 RuntimeError 발생
            _ = self.objectName()
            return False
        except RuntimeError:
            return True

    # QWidget 클래스에 메서드 추가
    if not hasattr(QWidget, "isDestroyed"):
        QWidget.isDestroyed = is_destroyed
