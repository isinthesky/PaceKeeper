"""
PaceKeeper Qt - 메인 윈도우 UI 설정
UI 관련 초기화 및 설정 메서드 모음
"""

from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QMenu, QMenuBar, QPushButton,
                             QSplitter, QStatusBar, QSystemTrayIcon, QToolBar,
                             QVBoxLayout, QWidget)

from app.utils.constants import SessionType, TimerState
from app.views.log_widget import LogListWidget
from app.views.tag_widget import TagButtonsWidget
from app.views.text_input_widget import TextInputWidget
from app.views.timer_widget_responsive import TimerWidget


def setup_ui(self):
    """메인 윈도우 UI 초기화"""
    # 창 제목 및 크기 설정
    self.setWindowTitle("PaceKeeper")
    self.resize(
        self.config.get("main_dlg_width", 800), self.config.get("main_dlg_height", 500)
    )

    # 중앙 위젯 설정
    self.centralWidget = QWidget()
    self.setCentralWidget(self.centralWidget)

    # 메인 레이아웃
    self.mainLayout = QVBoxLayout(self.centralWidget)
    self.mainLayout.setContentsMargins(10, 10, 10, 10)
    self.mainLayout.setSpacing(10)

    # 타이머 위젯 (새로 추가)
    self.timerWidget = TimerWidget()
    self.mainLayout.addWidget(self.timerWidget)

    # 스플리터 (로그, 태그, 입력 영역)
    self.contentSplitter = QSplitter(Qt.Orientation.Vertical)

    # 로그 위젯
    self.logListWidget = LogListWidget()
    self.contentSplitter.addWidget(self.logListWidget)

    # 입력 영역 컨테이너
    self.inputContainer = QWidget()
    self.inputLayout = QVBoxLayout(self.inputContainer)
    self.inputLayout.setContentsMargins(0, 0, 0, 0)

    # 태그 위젯
    self.tagButtonsWidget = TagButtonsWidget()
    self.inputLayout.addWidget(self.tagButtonsWidget)

    # 텍스트 입력 위젯
    self.textInputWidget = TextInputWidget()
    self.inputLayout.addWidget(self.textInputWidget)

    self.contentSplitter.addWidget(self.inputContainer)

    # 스플리터 비율 설정
    self.contentSplitter.setStretchFactor(0, 3)  # 로그 영역
    self.contentSplitter.setStretchFactor(1, 2)  # 입력 영역

    self.mainLayout.addWidget(self.contentSplitter)

    # 메뉴바 설정
    setup_menu_bar(self)

    # 툴바 설정
    setup_tool_bar(self)

    # 상태바 설정
    self.statusBar = QStatusBar()
    self.setStatusBar(self.statusBar)

    # 상태바 레이블
    self.statusLabel = QLabel("준비")
    self.statusBar.addPermanentWidget(self.statusLabel)


def setup_menu_bar(self):
    """메뉴바 설정"""
    self.menuBar = QMenuBar()
    self.setMenuBar(self.menuBar)

    # 파일 메뉴
    fileMenu = self.menuBar.addMenu("파일(&F)")

    # 설정 액션
    settingsAction = QAction("설정(&S)...", self)
    settingsAction.setShortcut("Ctrl+S")
    settingsAction.triggered.connect(self.openSettings)
    fileMenu.addAction(settingsAction)

    fileMenu.addSeparator()

    # 종료 액션
    exitAction = QAction("종료(&X)", self)
    exitAction.setShortcut("Alt+F4")
    exitAction.triggered.connect(self.close)
    fileMenu.addAction(exitAction)

    # 보기 메뉴
    viewMenu = self.menuBar.addMenu("보기(&V)")

    # 로그 보기 액션
    viewLogsAction = QAction("로그 관리(&L)...", self)
    viewLogsAction.setShortcut("Ctrl+L")
    viewLogsAction.triggered.connect(self.openLogDialog)
    viewMenu.addAction(viewLogsAction)

    # 카테고리 관리 액션
    manageCategoriesAction = QAction("카테고리 관리(&C)...", self)
    manageCategoriesAction.triggered.connect(self.openCategoryDialog)
    viewMenu.addAction(manageCategoriesAction)

    # 태그 관리 액션
    manageTagsAction = QAction("태그 관리(&T)...", self)
    manageTagsAction.triggered.connect(self.openTagDialog)
    viewMenu.addAction(manageTagsAction)

    # 테마 메뉴
    themeMenu = self.menuBar.addMenu("테마(&T)")

    # 테마 액션 추가
    themes = self.theme_manager.get_available_themes()
    for theme in themes:
        themeAction = QAction(theme, self)
        themeAction.triggered.connect(
            lambda checked, t=theme: self.theme_manager.apply_theme(None, t)
        )
        themeMenu.addAction(themeAction)

    # 도움말 메뉴
    helpMenu = self.menuBar.addMenu("도움말(&H)")

    # 도움말 액션
    helpAction = QAction("도움말(&H)", self)
    helpAction.setShortcut("F1")
    helpAction.triggered.connect(self.showHelp)
    helpMenu.addAction(helpAction)

    helpMenu.addSeparator()

    # 정보 액션
    aboutAction = QAction("PaceKeeper 정보(&A)", self)
    aboutAction.triggered.connect(self.showAbout)
    helpMenu.addAction(aboutAction)


def setup_tool_bar(self):
    """툴바 설정"""
    self.toolBar = QToolBar("메인 툴바")
    self.toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
    self.addToolBar(self.toolBar)

    # 시작/중지 액션
    self.startStopAction = QAction("시작", self)
    self.startStopAction.triggered.connect(self._handle_timer_toggle_request)
    self.toolBar.addAction(self.startStopAction)

    # 일시정지/재개 액션
    self.pauseResumeAction = QAction("일시정지", self)
    self.pauseResumeAction.triggered.connect(self._handle_timer_pause_toggle_request)
    self.pauseResumeAction.setEnabled(False)  # 초기에는 비활성화
    self.toolBar.addAction(self.pauseResumeAction)

    self.toolBar.addSeparator()

    # 로그 액션
    self.logAction = QAction("로그", self)
    self.logAction.triggered.connect(self.openLogDialog)
    self.toolBar.addAction(self.logAction)

    # 통계 액션
    self.statsAction = QAction("통계", self)
    self.statsAction.triggered.connect(self.showStats)
    self.toolBar.addAction(self.statsAction)


def setup_tray_icon(self):
    """시스템 트레이 아이콘 설정"""
    # 아이콘 생성 (실제 구현에서는 적절한 아이콘 파일 사용)
    self.trayIcon = QSystemTrayIcon(self)
    # self.trayIcon.setIcon(QIcon("path/to/icon.png"))

    # 트레이 메뉴
    trayMenu = QMenu()

    # 복원 액션
    restoreAction = QAction("복원", self)
    restoreAction.triggered.connect(self.showNormal)
    trayMenu.addAction(restoreAction)

    trayMenu.addSeparator()

    # 시작/중지 액션
    self.trayStartStopAction = QAction("시작", self)
    self.trayStartStopAction.triggered.connect(self._handle_timer_toggle_request)
    trayMenu.addAction(self.trayStartStopAction)

    # 일시정지/재개 액션
    self.trayPauseResumeAction = QAction("일시정지", self)
    self.trayPauseResumeAction.triggered.connect(
        self._handle_timer_pause_toggle_request
    )
    self.trayPauseResumeAction.setEnabled(False)  # 초기에는 비활성화
    trayMenu.addAction(self.trayPauseResumeAction)

    trayMenu.addSeparator()

    # 종료 액션
    exitAction = QAction("종료", self)
    exitAction.triggered.connect(self.onExitFromTray)
    trayMenu.addAction(exitAction)

    # 메뉴 설정
    self.trayIcon.setContextMenu(trayMenu)

    # 더블 클릭 시 창 열기 시그널 연결
    try:
        self.trayIcon.activated.connect(self.onTrayIconActivated)
    except Exception as e:
        print(f"Warning: Failed to connect tray icon activated signal: {e}")

    # 트레이 아이콘 표시
    self.trayIcon.show()
