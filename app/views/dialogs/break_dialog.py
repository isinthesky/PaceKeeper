"""
PaceKeeper Qt - 휴식 알림 대화상자
타이머 완료 후 휴식 알림 UI
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QGroupBox, QSpacerItem,
                             QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QFont, QColor, QPalette

from app.utils.constants import SessionType


class BreakDialog(QDialog):
    """휴식 알림 대화상자 클래스"""
    
    # 시그널 정의
    startBreakRequested = pyqtSignal()  # 휴식 시작 요청
    skipBreakRequested = pyqtSignal()   # 휴식 건너뛰기 요청
    
    def __init__(self, parent=None, session_type=SessionType.SHORT_BREAK):
        """
        휴식 알림 대화상자 초기화
        
        Args:
            parent: 부모 위젯
            session_type: 세션 타입 (SHORT_BREAK 또는 LONG_BREAK)
        """
        super().__init__(parent)
        
        self.session_type = session_type
        self.auto_start_timer = None
        self.countdown_seconds = 10  # 자동 시작 카운트다운 초
        
        # UI 초기화
        self.setupUI()
        
        # 시그널 연결
        self.connectSignals()
        
        # 모달리스 설정
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
    
    def setupUI(self):
        """UI 초기화"""
        # 창 제목 및 크기 설정
        break_type = "긴 휴식" if self.session_type == SessionType.LONG_BREAK else "짧은 휴식"
        self.setWindowTitle(f"{break_type} 시간")
        self.resize(400, 300)
        
        # 메인 레이아웃
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        
        # 메시지 레이블
        self.messageLabel = QLabel(f"뽀모도로 세션이 완료되었습니다.\n이제 {break_type} 시간입니다!")
        self.messageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.messageLabel.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        # 설명 레이블
        description_text = (
            "짧은 휴식 시간을 가지세요. 자리에서 일어나 스트레칭을 하거나, "
            "물을 마시거나, 잠시 눈을 쉬게 하세요."
        )
        if self.session_type == SessionType.LONG_BREAK:
            description_text = (
                "긴 휴식 시간을 가지세요. 깊은 호흡을 하고, 걷거나, "
                "가벼운 운동을 하거나, 명상을 해보세요."
            )
        
        self.descriptionLabel = QLabel(description_text)
        self.descriptionLabel.setWordWrap(True)
        self.descriptionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 진행 상자
        self.progressGroup = QGroupBox("자동 시작")
        self.progressLayout = QVBoxLayout(self.progressGroup)
        
        # 카운트다운 레이블
        self.countdownLabel = QLabel(f"{self.countdown_seconds}초 후 자동으로 시작됩니다...")
        self.countdownLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 진행 바
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, self.countdown_seconds)
        self.progressBar.setValue(self.countdown_seconds)
        
        self.progressLayout.addWidget(self.countdownLabel)
        self.progressLayout.addWidget(self.progressBar)
        
        # 버튼 레이아웃
        self.buttonLayout = QHBoxLayout()
        
        # 시작, 건너뛰기 버튼
        self.startButton = QPushButton("휴식 시작")
        self.startButton.setMinimumSize(QSize(120, 40))
        self.startButton.setFont(QFont("Arial", 12))
        
        self.skipButton = QPushButton("건너뛰기")
        self.skipButton.setMinimumSize(QSize(120, 40))
        
        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(self.startButton)
        self.buttonLayout.addWidget(self.skipButton)
        self.buttonLayout.addStretch()
        
        # 메인 레이아웃에 위젯 추가
        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.layout.addWidget(self.messageLabel)
        self.layout.addWidget(self.descriptionLabel)
        self.layout.addWidget(self.progressGroup)
        self.layout.addLayout(self.buttonLayout)
        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # 스타일 설정
        self.applyStyle()
    
    def applyStyle(self):
        """스타일 적용"""
        # 기본 색상 설정
        break_color = "#4caf50"  # 녹색 (휴식)
        if self.session_type == SessionType.LONG_BREAK:
            break_color = "#2196f3"  # 파란색 (긴 휴식)
        
        # 타이틀 색상 설정
        palette = self.messageLabel.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(break_color))
        self.messageLabel.setPalette(palette)
        
        # 시작 버튼 스타일
        self.startButton.setStyleSheet(f"""
            QPushButton {{
                background-color: {break_color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background-color: {QColor(break_color).lighter(110).name()};
            }}
            QPushButton:pressed {{
                background-color: {QColor(break_color).darker(110).name()};
            }}
        """)
    
    def connectSignals(self):
        """시그널 연결"""
        # 버튼 관련
        self.startButton.clicked.connect(self.onStartBreak)
        self.skipButton.clicked.connect(self.onSkipBreak)
    
    def showEvent(self, event):
        """대화상자 표시 이벤트"""
        super().showEvent(event)
        
        # 자동 시작 타이머 설정
        self.auto_start_timer = QTimer(self)
        self.auto_start_timer.timeout.connect(self.updateCountdown)
        self.auto_start_timer.start(1000)  # 1초마다 업데이트
    
    def closeEvent(self, event):
        """대화상자 닫기 이벤트"""
        # 타이머 정리
        if self.auto_start_timer and self.auto_start_timer.isActive():
            self.auto_start_timer.stop()
        
        super().closeEvent(event)
    
    @pyqtSlot()
    def updateCountdown(self):
        """카운트다운 업데이트"""
        self.countdown_seconds -= 1
        self.progressBar.setValue(self.countdown_seconds)
        self.countdownLabel.setText(f"{self.countdown_seconds}초 후 자동으로 시작됩니다...")
        
        if self.countdown_seconds <= 0:
            # 타이머 정지
            self.auto_start_timer.stop()
            
            # 휴식 시작
            self.onStartBreak()
    
    @pyqtSlot()
    def onStartBreak(self):
        """휴식 시작 버튼 이벤트 핸들러"""
        # 타이머 정지
        if self.auto_start_timer and self.auto_start_timer.isActive():
            self.auto_start_timer.stop()
        
        # 시그널 발생
        self.startBreakRequested.emit()
        
        # 대화상자 닫기
        self.accept()
    
    @pyqtSlot()
    def onSkipBreak(self):
        """휴식 건너뛰기 버튼 이벤트 핸들러"""
        # 타이머 정지
        if self.auto_start_timer and self.auto_start_timer.isActive():
            self.auto_start_timer.stop()
        
        # 시그널 발생
        self.skipBreakRequested.emit()
        
        # 대화상자 닫기
        self.reject()
