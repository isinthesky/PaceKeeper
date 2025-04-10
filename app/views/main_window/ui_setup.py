"""
PaceKeeper Qt - 메인 윈도우 UI 설정
UI 관련 초기화 및 설정 메서드 모음
"""

import os
import sys

from icecream import ic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor
from PyQt6.QtWidgets import (
    QLabel, QMenu, QMenuBar, QSplitter,
    QStatusBar, QSystemTrayIcon, QToolBar, QVBoxLayout,
    QWidget
)
from app.views.log_widget import LogListWidget
from app.views.tag_widget import TagButtonsWidget
from app.views.text_input_widget import TextInputWidget
from app.views.timer_widget_responsive import TimerWidget


def resource_path(relative_path):
    """
    절대 경로 변환 유틸리티 함수
    frozen 여부에 따라 적절한 경로 반환
    """
    try:
        # PyInstaller로 빌드된 경우
        # Pylance 경고 무시: 이 속성은 PyInstaller 실행 시에만 존재함
        # type: ignore
        base_path = getattr(sys, '_MEIPASS', None)
        if base_path is None:
            # 일반 실행인 경우
            base_path = os.path.abspath(".")
    except Exception:
        # 일반 실행인 경우
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def find_app_icon():
    """
    애플리케이션 아이콘 파일 찾기
    여러 가능한 위치에서 검색
    """
    # 가능한 아이콘 경로들
    possible_paths = [
        resource_path(os.path.join("app", "assets", "icons", "pacekeeper.ico")),
        resource_path(os.path.join("app", "assets", "icons", "pacekeeper.png")),
        resource_path(os.path.join("app", "assets", "icons", "pacekeeper.icns")),
        resource_path(os.path.join("assets", "icons", "pacekeeper.ico")),
        resource_path(os.path.join("assets", "icons", "pacekeeper.png")),
        resource_path(os.path.join("assets", "icons", "pacekeeper.icns")),
        resource_path(os.path.join("app", "assets", "icons", "app_icon.ico")),
        resource_path(os.path.join("app", "assets", "icons", "app_icon.png")),
        resource_path(os.path.join("app", "assets", "icons", "app_icon.icns")),
        resource_path(os.path.join("assets", "icons", "app_icon.ico")),
        resource_path(os.path.join("assets", "icons", "app_icon.png")),
        resource_path(os.path.join("assets", "icons", "app_icon.icns")),
    ]
    
    # 존재하는 첫 번째 아이콘 파일 반환
    for path in possible_paths:
        if os.path.exists(path):
            print(f"[DEBUG] 앱 아이콘 파일 발견: {path}")
            return path
    
    print("[DEBUG] 경고: 앱 아이콘 파일을 찾을 수 없습니다.")
    return None


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
    fileMenu = QMenu("파일(&F)", self)
    self.menuBar.addMenu(fileMenu)

    # 설정 액션
    settingsAction = QAction("설정(&S)...", self)
    # 단축키 제거
    # 메서드 이름 변경: openSettings → open_settings
    settingsAction.triggered.connect(lambda: self.open_settings())
    fileMenu.addAction(settingsAction)

    fileMenu.addSeparator()

    # 종료 액션
    exitAction = QAction("종료(&X)", self)
    exitAction.setShortcut("Alt+F4")
    exitAction.triggered.connect(self.close)
    fileMenu.addAction(exitAction)

    # 보기 메뉴
    viewMenu = QMenu("보기(&V)", self)
    self.menuBar.addMenu(viewMenu)

    # 로그 보기 액션
    viewLogsAction = QAction("로그 관리(&L)...", self)
    viewLogsAction.setShortcut("Ctrl+L")
    # 메서드 이름 변경: openLogDialog → open_log_dialog
    viewLogsAction.triggered.connect(lambda: self.open_log_dialog())
    viewMenu.addAction(viewLogsAction)

    # 카테고리 관리 액션
    manageCategoriesAction = QAction("카테고리 관리(&C)...", self)
    # 메서드 이름 변경: openCategoryDialog → open_category_dialog
    manageCategoriesAction.triggered.connect(lambda: self.open_category_dialog())
    viewMenu.addAction(manageCategoriesAction)

    # 태그 관리 액션
    manageTagsAction = QAction("태그 관리(&T)...", self)
    # 메서드 이름 변경: openTagDialog → open_tag_dialog
    manageTagsAction.triggered.connect(lambda: self.open_tag_dialog())
    viewMenu.addAction(manageTagsAction)

    # 테마 메뉴
    themeMenu = QMenu("테마(&T)", self)
    self.menuBar.addMenu(themeMenu)

    # 테마 액션 추가
    themes = self.theme_manager.get_available_themes()

    ic("테마 액션 추가", themes)
    for theme in themes:
        themeAction = QAction(theme, self)
        themeAction.triggered.connect(
            lambda checked, t=theme: self.theme_manager.apply_theme(None, t)
        )
        themeMenu.addAction(themeAction)

    # 도움말 메뉴
    helpMenu = QMenu("도움말(&H)", self)
    self.menuBar.addMenu(helpMenu)

    # 도움말 액션
    helpAction = QAction("도움말(&H)", self)
    helpAction.setShortcut("F1")
    # 메서드 이름 변경: showHelp → show_help
    helpAction.triggered.connect(lambda: self.show_help())
    helpMenu.addAction(helpAction)

    helpMenu.addSeparator()

    # 정보 액션
    aboutAction = QAction("PaceKeeper 정보(&A)", self)
    # 메서드 이름 변경: showAbout → show_about
    aboutAction.triggered.connect(lambda: self.show_about())
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
    # 메서드 이름 변경: openLogDialog → open_log_dialog
    self.logAction.triggered.connect(lambda: self.open_log_dialog())
    self.toolBar.addAction(self.logAction)

    # 통계 액션
    self.statsAction = QAction("통계", self)
    # 메서드 이름 변경: showStats → show_stats
    self.statsAction.triggered.connect(lambda: self.show_stats())
    self.toolBar.addAction(self.statsAction)


def setup_tray_icon(self):
    """시스템 트레이 아이콘 설정"""
    # 아이콘 생성 - 적절한 아이콘 파일 찾기
    self.trayIcon = QSystemTrayIcon(self)
    
    # 아이콘 파일 찾기
    icon_path = find_app_icon()
    if icon_path:
        app_icon = QIcon(icon_path)
        self.trayIcon.setIcon(app_icon)
        print(f"[DEBUG] 트레이 아이콘 설정 완료: {icon_path}")
    else:
        # 아이콘이 없으면 fallback 아이콘 생성
        fallback_icon = QIcon()
        # 바탕 픽셀을 몇 개 추가하여 기본 아이콘 생성
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 120, 212))  # 기본 파란색
        fallback_icon = QIcon(pixmap)
        self.trayIcon.setIcon(fallback_icon)
        print("[DEBUG] 트레이 아이콘 설정: 대체 아이콘 사용")

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
        print(f"[DEBUG] 경고: 트레이 아이콘 활성화 시그널 연결 실패: {e}")

    # 트레이 아이콘 표시
    self.trayIcon.show()
