"""
PaceKeeper Qt - 설정 대화상자
애플리케이션 설정 관리 UI
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QSpinBox, QComboBox, 
                             QCheckBox, QTabWidget, QWidget, QFormLayout,
                             QFileDialog, QSlider)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal

from app.config.app_config import AppConfig
from app.views.styles.advanced_theme_manager import AdvancedThemeManager


class SettingsDialog(QDialog):
    """설정 대화상자 클래스"""
    
    # 시그널 정의
    settingsChanged = pyqtSignal(dict)  # 변경된 설정 값
    
    def __init__(self, parent=None, app_config=None, theme_manager=None):
        """
        설정 대화상자 초기화
        
        Args:
            parent: 부모 위젯
            app_config: 설정 관리자 인스턴스
            theme_manager: 테마 관리자 인스턴스
        """
        super().__init__(parent)
        
        self.config = app_config or AppConfig()
        self.theme_manager = theme_manager or AdvancedThemeManager()
        
        # 초기 설정 값 저장 (취소 시 복원용)
        self.original_settings = {}
        self.current_settings = {}
        
        # UI 초기화
        self.setupUI()
        
        # 초기 설정 값 로드
        self.loadSettings()
    
    def setupUI(self):
        """UI 초기화"""
        # 창 제목 및 크기 설정
        self.setWindowTitle("설정")
        self.resize(500, 400)
        
        # 메인 레이아웃
        self.layout = QVBoxLayout(self)
        
        # 탭 위젯
        self.tabWidget = QTabWidget()
        
        # 일반 탭
        self.generalTab = QWidget()
        self.setupGeneralTab()
        self.tabWidget.addTab(self.generalTab, "일반")
        
        # 타이머 탭
        self.timerTab = QWidget()
        self.setupTimerTab()
        self.tabWidget.addTab(self.timerTab, "타이머")
        
        # 소리 탭
        self.soundTab = QWidget()
        self.setupSoundTab()
        self.tabWidget.addTab(self.soundTab, "소리")
        
        # UI 탭
        self.uiTab = QWidget()
        self.setupUITab()
        self.tabWidget.addTab(self.uiTab, "UI")
        
        # 메인 레이아웃에 탭 위젯 추가
        self.layout.addWidget(self.tabWidget)
        
        # 버튼 레이아웃
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        
        # 확인 및 취소 버튼
        self.okButton = QPushButton("확인")
        self.okButton.clicked.connect(self.accept)
        
        self.cancelButton = QPushButton("취소")
        self.cancelButton.clicked.connect(self.reject)
        
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)
        
        # 메인 레이아웃에 버튼 레이아웃 추가
        self.layout.addLayout(buttonLayout)
    
    def setupGeneralTab(self):
        """일반 설정 탭 초기화"""
        layout = QVBoxLayout(self.generalTab)
        
        # 테마 설정 그룹
        themeGroup = QGroupBox("테마")
        themeLayout = QFormLayout(themeGroup)

        print(self.theme_manager.get_available_themes())
        
        # 테마 콤보박스
        self.themeComboBox = QComboBox()
        self.themeComboBox.addItems(self.theme_manager.get_available_themes())
        self.themeComboBox.currentTextChanged.connect(self.onThemeChanged)
        themeLayout.addRow("테마:", self.themeComboBox)
        
        # 언어 콤보박스
        self.languageComboBox = QComboBox()
        self.languageComboBox.addItems(["한국어", "English"])
        themeLayout.addRow("언어:", self.languageComboBox)
        
        layout.addWidget(themeGroup)
        
        # 알림 설정 그룹
        notificationGroup = QGroupBox("알림")
        notificationLayout = QFormLayout(notificationGroup)
        
        # 알림 활성화 체크박스
        self.notificationsEnabledCheckBox = QCheckBox("알림 활성화")
        notificationLayout.addRow("", self.notificationsEnabledCheckBox)
        
        # 알림 소리 체크박스
        self.notificationSoundCheckBox = QCheckBox("알림 소리")
        notificationLayout.addRow("", self.notificationSoundCheckBox)
        
        layout.addWidget(notificationGroup)
        
        # 여백 추가
        layout.addStretch(1)
    
    def setupTimerTab(self):
        """타이머 설정 탭 초기화"""
        layout = QVBoxLayout(self.timerTab)
        
        # 타이머 설정 그룹
        timerGroup = QGroupBox("타이머 시간 설정")
        timerLayout = QFormLayout(timerGroup)
        
        # 뽀모도로 시간 설정
        self.studyTimeSpinBox = QSpinBox()
        self.studyTimeSpinBox.setRange(1, 120)
        self.studyTimeSpinBox.setSuffix(" 분")
        timerLayout.addRow("뽀모도로 시간:", self.studyTimeSpinBox)
        
        # 짧은 휴식 시간 설정
        self.breakTimeSpinBox = QSpinBox()
        self.breakTimeSpinBox.setRange(1, 30)
        self.breakTimeSpinBox.setSuffix(" 분")
        timerLayout.addRow("짧은 휴식 시간:", self.breakTimeSpinBox)
        
        # 긴 휴식 시간 설정
        self.longBreakTimeSpinBox = QSpinBox()
        self.longBreakTimeSpinBox.setRange(1, 60)
        self.longBreakTimeSpinBox.setSuffix(" 분")
        timerLayout.addRow("긴 휴식 시간:", self.longBreakTimeSpinBox)
        
        # 긴 휴식 간격 설정
        self.longBreakIntervalSpinBox = QSpinBox()
        self.longBreakIntervalSpinBox.setRange(1, 10)
        self.longBreakIntervalSpinBox.setSuffix(" 세션")
        timerLayout.addRow("긴 휴식 간격:", self.longBreakIntervalSpinBox)
        
        layout.addWidget(timerGroup)
        
        # 자동 시작 설정 그룹
        autoStartGroup = QGroupBox("자동 시작 설정")
        autoStartLayout = QFormLayout(autoStartGroup)
        
        # 휴식 자동 시작 체크박스
        self.autoStartBreaksCheckBox = QCheckBox("세션 종료 후 휴식 자동 시작")
        autoStartLayout.addRow("", self.autoStartBreaksCheckBox)
        
        # 뽀모도로 자동 시작 체크박스
        self.autoStartPomodorosCheckBox = QCheckBox("휴식 종료 후 세션 자동 시작")
        autoStartLayout.addRow("", self.autoStartPomodorosCheckBox)
        
        layout.addWidget(autoStartGroup)
        
        # 여백 추가
        layout.addStretch(1)
    
    def setupSoundTab(self):
        """소리 설정 탭 초기화"""
        layout = QVBoxLayout(self.soundTab)
        
        # 소리 설정 그룹
        soundGroup = QGroupBox("소리 설정")
        soundLayout = QFormLayout(soundGroup)
        
        # 소리 활성화 체크박스
        self.soundEnabledCheckBox = QCheckBox("소리 활성화")
        soundLayout.addRow("", self.soundEnabledCheckBox)
        
        # 타이머 종료 소리 선택
        self.timerEndSoundComboBox = QComboBox()
        self.timerEndSoundComboBox.addItems(["Bell", "Alarm", "Notification"])
        soundLayout.addRow("타이머 종료 소리:", self.timerEndSoundComboBox)
        
        # 휴식 종료 소리 선택
        self.breakEndSoundComboBox = QComboBox()
        self.breakEndSoundComboBox.addItems(["Bell", "Alarm", "Notification"])
        soundLayout.addRow("휴식 종료 소리:", self.breakEndSoundComboBox)
        
        # 볼륨 슬라이더
        self.volumeSlider = QSlider(Qt.Orientation.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(50)
        soundLayout.addRow("볼륨:", self.volumeSlider)
        
        layout.addWidget(soundGroup)
        
        # 여백 추가
        layout.addStretch(1)
    
    def setupUITab(self):
        """UI 설정 탭 초기화"""
        layout = QVBoxLayout(self.uiTab)
        
        # UI 설정 그룹
        uiGroup = QGroupBox("UI 설정")
        uiLayout = QFormLayout(uiGroup)
        
        # 초 표시 체크박스
        self.showSecondsCheckBox = QCheckBox("타이머에 초 표시")
        uiLayout.addRow("", self.showSecondsCheckBox)
        
        # 트레이로 최소화 체크박스
        self.minimizeToTrayCheckBox = QCheckBox("닫기 버튼 클릭 시 트레이로 최소화")
        uiLayout.addRow("", self.minimizeToTrayCheckBox)
        
        layout.addWidget(uiGroup)
        
        # 창 크기 설정 그룹
        windowGroup = QGroupBox("창 크기 설정")
        windowLayout = QFormLayout(windowGroup)
        
        # 창 너비 설정
        self.windowWidthSpinBox = QSpinBox()
        self.windowWidthSpinBox.setRange(400, 1200)
        self.windowWidthSpinBox.setSuffix(" px")
        windowLayout.addRow("창 너비:", self.windowWidthSpinBox)
        
        # 창 높이 설정
        self.windowHeightSpinBox = QSpinBox()
        self.windowHeightSpinBox.setRange(300, 900)
        self.windowHeightSpinBox.setSuffix(" px")
        windowLayout.addRow("창 높이:", self.windowHeightSpinBox)
        
        layout.addWidget(windowGroup)
        
        # 여백 추가
        layout.addStretch(1)
    
    def loadSettings(self):
        """설정 값 로드"""
        # 일반 설정
        theme = self.config.get("theme", "default")
        index = self.themeComboBox.findText(theme)
        if index >= 0:
            self.themeComboBox.setCurrentIndex(index)
        
        language = self.config.get("language", "ko")
        index = self.languageComboBox.findText("한국어" if language == "ko" else "English")
        if index >= 0:
            self.languageComboBox.setCurrentIndex(index)
        
        self.notificationsEnabledCheckBox.setChecked(self.config.get("notifications_enabled", True))
        self.notificationSoundCheckBox.setChecked(self.config.get("notification_sound", True))
        
        # 타이머 설정
        self.studyTimeSpinBox.setValue(self.config.get("study_time", 25))
        self.breakTimeSpinBox.setValue(self.config.get("break_time", 5))
        self.longBreakTimeSpinBox.setValue(self.config.get("long_break_time", 15))
        self.longBreakIntervalSpinBox.setValue(self.config.get("long_break_interval", 4))
        self.autoStartBreaksCheckBox.setChecked(self.config.get("auto_start_breaks", True))
        self.autoStartPomodorosCheckBox.setChecked(self.config.get("auto_start_pomodoros", False))
        
        # 소리 설정
        self.soundEnabledCheckBox.setChecked(self.config.get("sound_enabled", True))
        
        timer_end_sound = self.config.get("timer_end_sound", "bell.wav")
        if "bell" in timer_end_sound.lower():
            self.timerEndSoundComboBox.setCurrentIndex(0)
        elif "alarm" in timer_end_sound.lower():
            self.timerEndSoundComboBox.setCurrentIndex(1)
        elif "notification" in timer_end_sound.lower():
            self.timerEndSoundComboBox.setCurrentIndex(2)
        
        break_end_sound = self.config.get("break_end_sound", "bell.wav")
        if "bell" in break_end_sound.lower():
            self.breakEndSoundComboBox.setCurrentIndex(0)
        elif "alarm" in break_end_sound.lower():
            self.breakEndSoundComboBox.setCurrentIndex(1)
        elif "notification" in break_end_sound.lower():
            self.breakEndSoundComboBox.setCurrentIndex(2)
        
        # UI 설정
        self.showSecondsCheckBox.setChecked(self.config.get("show_seconds", True))
        self.minimizeToTrayCheckBox.setChecked(self.config.get("minimize_to_tray", False))
        self.windowWidthSpinBox.setValue(self.config.get("main_dlg_width", 800))
        self.windowHeightSpinBox.setValue(self.config.get("main_dlg_height", 500))
        
        # 원본 설정 저장
        self.original_settings = {
            "theme": theme,
            "language": language,
            "notifications_enabled": self.notificationsEnabledCheckBox.isChecked(),
            "notification_sound": self.notificationSoundCheckBox.isChecked(),
            "study_time": self.studyTimeSpinBox.value(),
            "break_time": self.breakTimeSpinBox.value(),
            "long_break_time": self.longBreakTimeSpinBox.value(),
            "long_break_interval": self.longBreakIntervalSpinBox.value(),
            "auto_start_breaks": self.autoStartBreaksCheckBox.isChecked(),
            "auto_start_pomodoros": self.autoStartPomodorosCheckBox.isChecked(),
            "sound_enabled": self.soundEnabledCheckBox.isChecked(),
            "timer_end_sound": timer_end_sound,
            "break_end_sound": break_end_sound,
            "show_seconds": self.showSecondsCheckBox.isChecked(),
            "minimize_to_tray": self.minimizeToTrayCheckBox.isChecked(),
            "main_dlg_width": self.windowWidthSpinBox.value(),
            "main_dlg_height": self.windowHeightSpinBox.value()
        }
    
    def saveSettings(self):
        """설정 값 저장"""
        # 현재 설정 수집
        self.current_settings = {
            "theme": self.themeComboBox.currentText(),
            "language": "ko" if self.languageComboBox.currentText() == "한국어" else "en",
            "notifications_enabled": self.notificationsEnabledCheckBox.isChecked(),
            "notification_sound": self.notificationSoundCheckBox.isChecked(),
            "study_time": self.studyTimeSpinBox.value(),
            "break_time": self.breakTimeSpinBox.value(),
            "long_break_time": self.longBreakTimeSpinBox.value(),
            "long_break_interval": self.longBreakIntervalSpinBox.value(),
            "auto_start_breaks": self.autoStartBreaksCheckBox.isChecked(),
            "auto_start_pomodoros": self.autoStartPomodorosCheckBox.isChecked(),
            "sound_enabled": self.soundEnabledCheckBox.isChecked(),
            "timer_end_sound": f"{self.timerEndSoundComboBox.currentText().lower()}.wav",
            "break_end_sound": f"{self.breakEndSoundComboBox.currentText().lower()}.wav",
            "show_seconds": self.showSecondsCheckBox.isChecked(),
            "minimize_to_tray": self.minimizeToTrayCheckBox.isChecked(),
            "main_dlg_width": self.windowWidthSpinBox.value(),
            "main_dlg_height": self.windowHeightSpinBox.value()
        }
        
        # 설정 저장
        for key, value in self.current_settings.items():
            self.config.set(key, value)
        
        # 설정 파일에 저장
        self.config.save_settings()
        
        # 변경된 설정 시그널 발생
        self.settingsChanged.emit(self.current_settings)
    
    @pyqtSlot(str)
    def onThemeChanged(self, theme_name):
        """
        테마 변경 이벤트 핸들러
        
        Args:
            theme_name: 테마 이름
        """
        if self.theme_manager:
            self.theme_manager.apply_theme(None, theme_name)
    
    def accept(self):
        """확인 버튼 클릭 이벤트 처리"""
        # 설정 저장
        self.saveSettings()
        
        # 다이얼로그 닫기
        super().accept()
    
    def reject(self):
        """취소 버튼 클릭 이벤트 처리"""
        # 원래 테마로 복원
        if self.theme_manager:
            self.theme_manager.apply_theme(None, self.original_settings["theme"])
        
        # 다이얼로그 닫기
        super().reject()
