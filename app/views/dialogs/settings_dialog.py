from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                             QFileDialog, QFormLayout, QFrame, QGroupBox,
                             QHBoxLayout, QLabel, QPushButton, QSlider,
                             QSpinBox, QTabWidget, QVBoxLayout, QWidget)

from app.config.app_config import AppConfig
from app.views.styles.advanced_theme_manager import AdvancedThemeManager
from app.views.styles.update_dialogs import set_object_names, apply_theme_change


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
        # 단일 테마 관리자 인스턴스 사용
        self.theme_manager = theme_manager or AdvancedThemeManager.get_instance()

        # 테마 관리자에 대화상자 등록 및 시그널 연결
        if self.theme_manager:
            self.theme_manager.register_widget(self)
            # 테마 변경 시그널 연결
            self.theme_manager.themeChanged.connect(self.on_theme_changed)

        # 초기 설정 값 저장 (취소 시 복원용)
        self.original_settings = {}
        self.current_settings = {}

        # UI 초기화
        self.setupUI()
        
        # 다이얼로그의 모든 객체에 이름 설정
        set_object_names(self)

        # 초기 설정 값 로드
        self.loadSettings()

    def setupUI(self):
        """UI 초기화 - 개선된 버전"""
        # 창 제목 및 크기 설정
        self.setWindowTitle("설정")
        self.resize(550, 450)  # 약간 더 크게 조정

        # 메인 레이아웃
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)  # 더 넓은 여백
        self.main_layout.setSpacing(10)  # 요소 간 간격 증가

        # 탭 위젯 스타일 개선
        self.tabWidget = QTabWidget()
        self.tabWidget.setDocumentMode(True)  # 현대적인 탭 스타일
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.North)

        # 각 탭 설정
        self.setupGeneralTab()
        self.setupTimerTab()
        self.setupSoundTab()
        self.setupUITab()

        # 메인 레이아웃에 탭 위젯 추가
        self.main_layout.addWidget(self.tabWidget)

        # 버튼 레이아웃 개선
        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(0, 10, 0, 0)  # 상단 여백 추가
        buttonLayout.addStretch(1)

        # 확인 및 취소 버튼 - 더 현대적인 모양
        self.cancelButton = QPushButton("취소")
        self.cancelButton.setMinimumWidth(100)
        self.cancelButton.clicked.connect(self.reject)

        self.okButton = QPushButton("확인")
        self.okButton.setMinimumWidth(100)
        self.okButton.setDefault(True)  # 기본 버튼으로 설정
        self.okButton.clicked.connect(self.accept)

        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.okButton)

        # 메인 레이아웃에 버튼 레이아웃 추가
        self.main_layout.addLayout(buttonLayout)

    def setupGeneralTab(self):
        """일반 설정 탭 초기화 - 개선된 버전"""
        self.generalTab = QWidget()
        layout = QVBoxLayout(self.generalTab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)  # 그룹 간 간격 증가

        # 테마 설정 그룹 - 카드 형태 스타일
        themeGroup = QGroupBox("테마")
        themeGroup.setStyleSheet(
            """
            QGroupBox {
                background-color: palette(base);
                border-radius: 6px;
                border: 1px solid palette(mid);
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )

        themeLayout = QFormLayout(themeGroup)
        themeLayout.setContentsMargins(20, 25, 20, 15)
        themeLayout.setSpacing(12)  # 요소 간 간격 증가
        themeLayout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        themeLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # 테마 콤보박스 - 더 넓은 드롭다운
        self.themeComboBox = QComboBox()
        self.themeComboBox.setMinimumWidth(200)
        self.themeComboBox.addItems(self.theme_manager.get_available_themes())
        self.themeComboBox.currentTextChanged.connect(self.onThemeChanged)
        themeLayout.addRow("테마:", self.themeComboBox)

        # 언어 콤보박스
        self.languageComboBox = QComboBox()
        self.languageComboBox.setMinimumWidth(200)
        self.languageComboBox.addItems(["한국어", "English"])
        themeLayout.addRow("언어:", self.languageComboBox)

        layout.addWidget(themeGroup)

        # 알림 설정 그룹 - 카드 형태 스타일
        notificationGroup = QGroupBox("알림")
        notificationGroup.setStyleSheet(
            """
            QGroupBox {
                background-color: palette(base);
                border-radius: 6px;
                border: 1px solid palette(mid);
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )

        notificationLayout = QVBoxLayout(notificationGroup)
        notificationLayout.setContentsMargins(20, 25, 20, 15)
        notificationLayout.setSpacing(10)

        # 알림 활성화 체크박스 - 현대적인 스타일
        self.notificationsEnabledCheckBox = QCheckBox("알림 활성화")
        self.notificationsEnabledCheckBox.setStyleSheet(
            """
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }
        """
        )
        notificationLayout.addWidget(self.notificationsEnabledCheckBox)

        # 알림 소리 체크박스
        self.notificationSoundCheckBox = QCheckBox("알림 소리")
        self.notificationSoundCheckBox.setStyleSheet(
            """
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }
        """
        )
        notificationLayout.addWidget(self.notificationSoundCheckBox)

        layout.addWidget(notificationGroup)

        # 여백 추가
        layout.addStretch(1)

        self.tabWidget.addTab(self.generalTab, "일반")

    def setupTimerTab(self):
        """타이머 설정 탭 초기화 - 개선된 버전"""
        self.timerTab = QWidget()
        layout = QVBoxLayout(self.timerTab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)  # 그룹 간 간격 증가

        # 타이머 설정 그룹 - 카드 스타일 적용
        timerGroup = QGroupBox("타이머 시간 설정")
        timerGroup.setStyleSheet(
            """
            QGroupBox {
                background-color: palette(base);
                border-radius: 6px;
                border: 1px solid palette(mid);
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )

        timerLayout = QFormLayout(timerGroup)
        timerLayout.setContentsMargins(20, 25, 20, 15)
        timerLayout.setSpacing(12)  # 요소 간 간격 증가
        timerLayout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        timerLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # 뽀모도로 시간 설정 - 개선된 스핀박스
        self.studyTimeSpinBox = QSpinBox()
        self.studyTimeSpinBox.setRange(1, 120)
        self.studyTimeSpinBox.setSuffix(" 분")
        self.studyTimeSpinBox.setMinimumHeight(28)
        self.studyTimeSpinBox.setMinimumWidth(100)
        timerLayout.addRow("뽀모도로 시간:", self.studyTimeSpinBox)

        # 짧은 휴식 시간 설정
        self.breakTimeSpinBox = QSpinBox()
        self.breakTimeSpinBox.setRange(1, 30)
        self.breakTimeSpinBox.setSuffix(" 분")
        self.breakTimeSpinBox.setMinimumHeight(28)
        self.breakTimeSpinBox.setMinimumWidth(100)
        timerLayout.addRow("짧은 휴식 시간:", self.breakTimeSpinBox)

        # 긴 휴식 시간 설정
        self.longBreakTimeSpinBox = QSpinBox()
        self.longBreakTimeSpinBox.setRange(1, 60)
        self.longBreakTimeSpinBox.setSuffix(" 분")
        self.longBreakTimeSpinBox.setMinimumHeight(28)
        self.longBreakTimeSpinBox.setMinimumWidth(100)
        timerLayout.addRow("긴 휴식 시간:", self.longBreakTimeSpinBox)

        # 긴 휴식 간격 설정
        self.longBreakIntervalSpinBox = QSpinBox()
        self.longBreakIntervalSpinBox.setRange(1, 10)
        self.longBreakIntervalSpinBox.setSuffix(" 세션")
        self.longBreakIntervalSpinBox.setMinimumHeight(28)
        self.longBreakIntervalSpinBox.setMinimumWidth(100)
        timerLayout.addRow("긴 휴식 간격:", self.longBreakIntervalSpinBox)

        layout.addWidget(timerGroup)

        # 자동 시작 설정 그룹 - 카드 스타일 적용
        autoStartGroup = QGroupBox("자동 시작 설정")
        autoStartGroup.setStyleSheet(
            """
            QGroupBox {
                background-color: palette(base);
                border-radius: 6px;
                border: 1px solid palette(mid);
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )

        autoStartLayout = QVBoxLayout(autoStartGroup)
        autoStartLayout.setContentsMargins(20, 25, 20, 15)
        autoStartLayout.setSpacing(10)

        # 휴식 자동 시작 체크박스 - 현대적인 스타일
        self.autoStartBreaksCheckBox = QCheckBox("세션 종료 후 휴식 자동 시작")
        self.autoStartBreaksCheckBox.setStyleSheet(
            """
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }
        """
        )
        autoStartLayout.addWidget(self.autoStartBreaksCheckBox)

        # 뽀모도로 자동 시작 체크박스
        self.autoStartPomodorosCheckBox = QCheckBox("휴식 종료 후 세션 자동 시작")
        self.autoStartPomodorosCheckBox.setStyleSheet(
            """
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }
        """
        )
        autoStartLayout.addWidget(self.autoStartPomodorosCheckBox)

        layout.addWidget(autoStartGroup)

        # 여백 추가
        layout.addStretch(1)

        self.tabWidget.addTab(self.timerTab, "타이머")

    def setupSoundTab(self):
        """소리 설정 탭 초기화 - 개선된 버전"""
        self.soundTab = QWidget()
        layout = QVBoxLayout(self.soundTab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)  # 그룹 간 간격 증가

        # 소리 설정 그룹 - 카드 스타일 적용
        soundGroup = QGroupBox("소리 설정")
        soundGroup.setStyleSheet(
            """
            QGroupBox {
                background-color: palette(base);
                border-radius: 6px;
                border: 1px solid palette(mid);
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )

        soundLayout = QFormLayout(soundGroup)
        soundLayout.setContentsMargins(20, 25, 20, 15)
        soundLayout.setSpacing(12)  # 요소 간 간격 증가
        soundLayout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        soundLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # 소리 활성화 체크박스 - 현대적인 스타일
        self.soundEnabledCheckBox = QCheckBox("소리 활성화")
        self.soundEnabledCheckBox.setStyleSheet(
            """
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }
        """
        )
        soundLayout.addRow("", self.soundEnabledCheckBox)

        # 타이머 종료 소리 선택 - 개선된 드롭다운
        self.timerEndSoundComboBox = QComboBox()
        self.timerEndSoundComboBox.setMinimumHeight(28)
        self.timerEndSoundComboBox.setMinimumWidth(150)
        self.timerEndSoundComboBox.addItems(["Bell", "Alarm", "Notification"])
        soundLayout.addRow("타이머 종료 소리:", self.timerEndSoundComboBox)

        # 휴식 종료 소리 선택
        self.breakEndSoundComboBox = QComboBox()
        self.breakEndSoundComboBox.setMinimumHeight(28)
        self.breakEndSoundComboBox.setMinimumWidth(150)
        self.breakEndSoundComboBox.addItems(["Bell", "Alarm", "Notification"])
        soundLayout.addRow("휴식 종료 소리:", self.breakEndSoundComboBox)

        # 볼륨 슬라이더 - 개선된 슬라이더
        self.volumeSlider = QSlider(Qt.Orientation.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(50)
        self.volumeSlider.setMinimumWidth(200)
        self.volumeSlider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                height: 8px;
                background: palette(mid);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: palette(highlight);
                border: none;
                width: 16px;
                height: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
        """
        )
        soundLayout.addRow("볼륨:", self.volumeSlider)

        layout.addWidget(soundGroup)

        # 여백 추가
        layout.addStretch(1)

        self.tabWidget.addTab(self.soundTab, "소리")

    def setupUITab(self):
        """UI 설정 탭 초기화 - 개선된 버전"""
        self.uiTab = QWidget()
        layout = QVBoxLayout(self.uiTab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)  # 그룹 간 간격 증가

        # UI 설정 그룹 - 카드 스타일 적용
        uiGroup = QGroupBox("UI 설정")
        uiGroup.setStyleSheet(
            """
            QGroupBox {
                background-color: palette(base);
                border-radius: 6px;
                border: 1px solid palette(mid);
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )

        uiLayout = QVBoxLayout(uiGroup)
        uiLayout.setContentsMargins(20, 25, 20, 15)
        uiLayout.setSpacing(10)

        # 초 표시 체크박스 - 현대적인 스타일
        self.showSecondsCheckBox = QCheckBox("타이머에 초 표시")
        self.showSecondsCheckBox.setStyleSheet(
            """
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }
        """
        )
        uiLayout.addWidget(self.showSecondsCheckBox)

        # 트레이로 최소화 체크박스
        self.minimizeToTrayCheckBox = QCheckBox("닫기 버튼 클릭 시 트레이로 최소화")
        self.minimizeToTrayCheckBox.setStyleSheet(
            """
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }
        """
        )
        uiLayout.addWidget(self.minimizeToTrayCheckBox)

        layout.addWidget(uiGroup)

        # 창 크기 설정 그룹 - 카드 스타일 적용
        windowGroup = QGroupBox("창 크기 설정")
        windowGroup.setStyleSheet(
            """
            QGroupBox {
                background-color: palette(base);
                border-radius: 6px;
                border: 1px solid palette(mid);
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )

        windowLayout = QFormLayout(windowGroup)
        windowLayout.setContentsMargins(20, 25, 20, 15)
        windowLayout.setSpacing(12)  # 요소 간 간격 증가
        windowLayout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        windowLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # 창 너비 설정 - 개선된 스핀박스
        self.windowWidthSpinBox = QSpinBox()
        self.windowWidthSpinBox.setRange(400, 1200)
        self.windowWidthSpinBox.setSuffix(" px")
        self.windowWidthSpinBox.setMinimumHeight(28)
        self.windowWidthSpinBox.setMinimumWidth(100)
        windowLayout.addRow("창 너비:", self.windowWidthSpinBox)

        # 창 높이 설정
        self.windowHeightSpinBox = QSpinBox()
        self.windowHeightSpinBox.setRange(300, 900)
        self.windowHeightSpinBox.setSuffix(" px")
        self.windowHeightSpinBox.setMinimumHeight(28)
        self.windowHeightSpinBox.setMinimumWidth(100)
        windowLayout.addRow("창 높이:", self.windowHeightSpinBox)

        layout.addWidget(windowGroup)

        # 여백 추가
        layout.addStretch(1)

        self.tabWidget.addTab(self.uiTab, "UI")

    def loadSettings(self):
        """설정 값 로드"""
        # 일반 설정
        theme = self.config.get("theme", "default")
        index = self.themeComboBox.findText(theme)
        if index >= 0:
            self.themeComboBox.setCurrentIndex(index)

        language = self.config.get("language", "ko")
        index = self.languageComboBox.findText(
            "한국어" if language == "ko" else "English"
        )
        if index >= 0:
            self.languageComboBox.setCurrentIndex(index)

        self.notificationsEnabledCheckBox.setChecked(
            self.config.get("notifications_enabled", True)
        )
        self.notificationSoundCheckBox.setChecked(
            self.config.get("notification_sound", True)
        )

        # 타이머 설정
        self.studyTimeSpinBox.setValue(self.config.get("study_time", 25))
        self.breakTimeSpinBox.setValue(self.config.get("break_time", 5))
        self.longBreakTimeSpinBox.setValue(self.config.get("long_break_time", 15))
        self.longBreakIntervalSpinBox.setValue(
            self.config.get("long_break_interval", 4)
        )
        self.autoStartBreaksCheckBox.setChecked(
            self.config.get("auto_start_breaks", True)
        )
        self.autoStartPomodorosCheckBox.setChecked(
            self.config.get("auto_start_pomodoros", False)
        )

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
        self.minimizeToTrayCheckBox.setChecked(
            self.config.get("minimize_to_tray", False)
        )
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
            "main_dlg_height": self.windowHeightSpinBox.value(),
        }

    def saveSettings(self):
        """설정 값 저장"""
        # 현재 설정 수집
        self.current_settings = {
            "theme": self.themeComboBox.currentText(),
            "language": (
                "ko" if self.languageComboBox.currentText() == "한국어" else "en"
            ),
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
            "main_dlg_height": self.windowHeightSpinBox.value(),
        }

        # 설정 저장
        for key, value in self.current_settings.items():
            self.config.set(key, value)

        # 설정 파일에 저장
        self.config.save_settings()

        # 변경된 설정 시그널 발생
        self.settingsChanged.emit(self.current_settings)

    @pyqtSlot(str)
    def on_theme_changed(self, theme_name):
        """
        테마 관리자로부터 전달된 테마 변경 이벤트 처리 (다른 위젯에서 테마 변경시)

        Args:
            theme_name: 변경된 테마 이름
        """
        # 테마 콤보박스 업데이트
        index = self.themeComboBox.findText(theme_name)
        if index >= 0 and self.themeComboBox.currentText() != theme_name:
            self.themeComboBox.setCurrentIndex(index)

        # 공통 테마 변경 함수 호출
        apply_theme_change(self, theme_name, self.theme_manager)

    @pyqtSlot(str)
    def onThemeChanged(self, theme_name):
        """
        콤보박스에서 테마 선택 이벤트 핸들러 (설정 대화상자 내에서 변경시)

        Args:
            theme_name: 테마 이름
        """
        if self.theme_manager:
            # 현재 테마 이름 저장
            self.current_settings["theme"] = theme_name
            self.config.set("theme", theme_name)

            # 즉시 설정 파일에 저장 (중요!)
            self.config.save_settings()

            # QApplication 인스턴스를 얻어 테마 적용
            app = QApplication.instance()
            if app:
                # 테마 매니저를 통해 테마 적용
                self.theme_manager.apply_theme(app, theme_name)

                # 테마 스타일을 직접 가져와서 현재 대화상자에도 적용 (즉시 표시 효과)
                style_content = self.theme_manager.get_theme_style(theme_name)
                if style_content:
                    self.setStyleSheet(style_content)

    def closeEvent(self, event):
        """창 닫기 이벤트 처리"""
        if hasattr(self, "theme_manager") and self.theme_manager:
            # 테마 변경 시그널 연결 해제
            self.theme_manager.themeChanged.disconnect(self.on_theme_changed)
            self.theme_manager.unregister_widget(self)
        super().closeEvent(event)

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
            app = QApplication.instance()
            if app:
                self.theme_manager.apply_theme(app, self.original_settings["theme"])

        # 다이얼로그 닫기
        super().reject()
