"""
PaceKeeper Qt - Timer Widget (Responsive)
시간 표시 및 제어 위젯 구현 (반응형)
"""

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QSizePolicy,
                             QVBoxLayout, QWidget)

from app.utils.constants import TimerState  # TimerState 임포트 추가


class TimerWidget(QWidget):
    """타이머 위젯 클래스 (반응형)"""

    # 사용자 정의 시그널
    startRequested = pyqtSignal()
    pauseRequested = pyqtSignal()
    # timerStopped 시그널은 startRequested로 통합 (토글 방식)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        """UI 초기화"""
        # 메인 레이아웃 생성 및 설정
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # 여백 설정
        layout.setSpacing(8)  # 컴포넌트 간 간격
        self.setLayout(layout)  # 위젯에 레이아웃 설정

        # 타이머 표시 레이블
        self.timerLabel = QLabel("25:00")
        self.timerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timerLabel.setObjectName("timerLabel")  # QSS 선택자용

        # 크기 정책 설정 - 수평/수직 확장
        size_policy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.timerLabel.setSizePolicy(size_policy)

        # 최소 크기 설정
        self.timerLabel.setMinimumHeight(100)

        # 레이블 폰트 설정 - QSS에서 관리되므로 필요한 경우에만 직접 설정

        # 버튼 레이아웃 - 수평으로 버튼 배치
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(10)  # 버튼 간 간격

        # 시작/중지 버튼
        self.startButton = QPushButton("START")
        self.startButton.setObjectName("startButton")
        self.startButton.setMinimumWidth(100)  # 최소 너비
        self.startButton.clicked.connect(self.onStartClicked)

        # 일시정지/재개 버튼
        self.pauseButton = QPushButton("PAUSE")
        self.pauseButton.setObjectName("pauseButton")
        self.pauseButton.setMinimumWidth(100)  # 최소 너비
        self.pauseButton.setEnabled(False)
        self.pauseButton.clicked.connect(self.onPauseClicked)

        # 버튼 추가
        self.buttonLayout.addStretch(1)  # 왼쪽 여백 (가변)
        self.buttonLayout.addWidget(self.startButton)
        self.buttonLayout.addWidget(self.pauseButton)
        self.buttonLayout.addStretch(1)  # 오른쪽 여백 (가변)

        # 메인 레이아웃에 위젯 추가
        layout.addWidget(self.timerLabel)
        layout.addLayout(self.buttonLayout)

    def onStartClicked(self):
        """시작/정지 버튼 클릭 시그널 발생"""
        self.startRequested.emit()

    def onPauseClicked(self):
        """일시정지/재개 버튼 클릭 시그널 발생"""
        # 버튼이 활성화 상태일 때만 시그널 발생
        if self.pauseButton.isEnabled():
            self.pauseRequested.emit()

    def setTimerState(self, state, timeStr):
        """타이머 상태에 따라 위젯 UI 업데이트"""
        self.timerLabel.setText(timeStr)

        if state == TimerState.RUNNING:
            self.startButton.setText("STOP")
            self.pauseButton.setText("PAUSE")
            self.pauseButton.setEnabled(True)
        elif state == TimerState.PAUSED:
            self.startButton.setText("STOP")  # 중지 가능한 상태 유지
            self.pauseButton.setText("RESUME")
            self.pauseButton.setEnabled(True)
        elif state in [
            TimerState.IDLE,
            TimerState.FINISHED,
            TimerState.BREAK,
        ]:  # IDLE, FINISHED, BREAK 상태 추가
            self.startButton.setText("START")
            self.pauseButton.setText("PAUSE")
            self.pauseButton.setEnabled(False)
        # 필요시 다른 상태에 대한 처리 추가

    def updateTimer(self, timeStr):
        """타이머 시간만 업데이트 (기존 메서드 유지 또는 setTimerState로 통합 가능)"""
        self.timerLabel.setText(timeStr)

    def resizeEvent(self, event):
        """창 크기 조정 이벤트 처리"""
        # 부모 클래스의 이벤트 처리기 호출
        super().resizeEvent(event)

        # 위젯 크기에 따른 폰트 크기 조정
        self._adjustFontSizes()

    def _adjustFontSizes(self):
        """위젯 크기에 따라 폰트 크기 조정"""
        width = self.width()

        # 타이머 레이블 폰트 크기 조정을 위한 스타일시트 생성
        if width < 300:
            self.timerLabel.setStyleSheet("font-size: 28px; font-weight: bold;")
        elif width < 500:
            self.timerLabel.setStyleSheet("font-size: 36px; font-weight: bold;")
        else:
            self.timerLabel.setStyleSheet("font-size: 48px; font-weight: bold;")

        # 버튼 크기 조정
        button_width = max(
            80, min(int(width * 0.2), 140)
        )  # 위젯 너비의 20%, 최소 80px, 최대 140px
        self.startButton.setMinimumWidth(button_width)
        self.pauseButton.setMinimumWidth(button_width)

    def showSeconds(self, show=True):
        """초 표시 여부 설정

        Args:
            show: 초 표시 여부 (기본값: True)
        """
        # 이 메서드는 타이머 형식을 변경할 때 사용될 수 있음
        # 현재는 UI에서 초를 항상 표시하므로 구현만 제공
        pass
