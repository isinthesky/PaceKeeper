"""
PaceKeeper Qt - 로그 대화상자
로그 조회 및 관리 UI
"""

from datetime import datetime, timedelta

from PyQt6.QtCore import QDate, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QBrush, QColor, QIcon
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
                             QDialog, QFormLayout, QGroupBox, QHBoxLayout,
                             QHeaderView, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QToolBar, QVBoxLayout, QWidget)

from app.domain.category.category_service import CategoryService
from app.domain.log.log_entity import LogEntity
from app.domain.log.log_service import LogService


class LogDialog(QDialog):
    """로그 조회 대화상자 클래스"""

    def __init__(self, parent=None, controller_or_service=None, category_service=None):
        """
        로그 대화상자 초기화

        Args:
            parent: 부모 위젯
            controller_or_service: 메인 컨트롤러 또는 로그 서비스 인스턴스
            category_service: 카테고리 서비스 인스턴스
        """
        super().__init__(parent)

        from app.controllers.main_controller import MainController

        # 컨트롤러 또는 서비스 구분
        if isinstance(controller_or_service, MainController):
            self.controller = controller_or_service
            self.log_service = self.controller.log_service
            self.category_service = self.controller.category_service
        else:
            # 이전 방식 지원 (후박성)
            self.controller = None
            self.log_service = controller_or_service or LogService()
            self.category_service = category_service or CategoryService()

        # 현재 필터 설정
        self.current_filter = {
            "search_term": "",
            "date_from": datetime.now() - timedelta(days=30),
            "date_to": datetime.now(),
            "category_id": None,
        }

        # UI 초기화
        self.setupUI()

        # 카테고리 목록 로드
        self.loadCategories()

        # 로그 목록 로드
        self.loadLogs()

        # 시그널 연결
        self.connectSignals()

    def setupUI(self):
        """UI 초기화"""
        # 창 제목 및 크기 설정
        self.setWindowTitle("로그 관리")
        self.resize(800, 600)

        # 메인 레이아웃
        self.layout = QVBoxLayout(self)

        # 필터 영역
        self.filterGroup = QGroupBox("필터")
        self.filterLayout = QFormLayout(self.filterGroup)

        # 검색어 입력
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("검색어 입력...")
        self.filterLayout.addRow("검색:", self.searchInput)

        # 날짜 범위 선택
        self.dateFilterLayout = QHBoxLayout()

        self.fromDateEdit = QDateEdit()
        self.fromDateEdit.setCalendarPopup(True)
        self.fromDateEdit.setDate(QDate.currentDate().addDays(-30))

        self.toDateEdit = QDateEdit()
        self.toDateEdit.setCalendarPopup(True)
        self.toDateEdit.setDate(QDate.currentDate())

        self.dateFilterLayout.addWidget(self.fromDateEdit)
        self.dateFilterLayout.addWidget(QLabel("~"))
        self.dateFilterLayout.addWidget(self.toDateEdit)

        self.filterLayout.addRow("기간:", self.dateFilterLayout)

        # 카테고리 선택
        self.categoryComboBox = QComboBox()
        self.categoryComboBox.addItem("모든 카테고리", None)
        self.filterLayout.addRow("카테고리:", self.categoryComboBox)

        # 필터 적용 버튼
        self.filterButtonLayout = QHBoxLayout()
        self.applyFilterButton = QPushButton("필터 적용")
        self.resetFilterButton = QPushButton("필터 초기화")
        self.filterButtonLayout.addWidget(self.applyFilterButton)
        self.filterButtonLayout.addWidget(self.resetFilterButton)
        self.filterLayout.addRow("", self.filterButtonLayout)

        self.layout.addWidget(self.filterGroup)

        # 툴바 추가
        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # 로그 편집 액션
        self.editAction = QAction("편집", self)
        self.toolbar.addAction(self.editAction)

        # 로그 삭제 액션
        self.deleteAction = QAction("삭제", self)
        self.toolbar.addAction(self.deleteAction)

        # 구분선 추가
        self.toolbar.addSeparator()

        # 통계 보기 액션
        self.statsAction = QAction("통계", self)
        self.toolbar.addAction(self.statsAction)

        # 내보내기 액션
        self.exportAction = QAction("내보내기", self)
        self.toolbar.addAction(self.exportAction)

        self.layout.addWidget(self.toolbar)

        # 로그 테이블
        self.logTable = QTableWidget()
        self.logTable.setColumnCount(6)
        self.logTable.setHorizontalHeaderLabels(
            ["날짜", "시간", "내용", "태그", "카테고리", "소요 시간"]
        )
        self.logTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.logTable.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )  # 내용 컬럼 늘리기
        self.logTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.logTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.layout.addWidget(self.logTable)

        # 닫기 버튼
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addStretch()
        self.closeButton = QPushButton("닫기")
        self.buttonLayout.addWidget(self.closeButton)

        self.layout.addLayout(self.buttonLayout)

    def connectSignals(self):
        """시그널 연결"""
        # 필터 관련
        self.applyFilterButton.clicked.connect(self.onApplyFilter)
        self.resetFilterButton.clicked.connect(self.onResetFilter)

        # 툴바 액션 관련
        self.editAction.triggered.connect(self.onEditLog)
        self.deleteAction.triggered.connect(self.onDeleteLog)
        self.statsAction.triggered.connect(self.onShowStats)
        self.exportAction.triggered.connect(self.onExportLogs)

        # 로그 테이블 관련
        self.logTable.itemDoubleClicked.connect(self.onLogDoubleClicked)

        # 닫기 버튼
        self.closeButton.clicked.connect(self.accept)

    def loadCategories(self):
        """카테고리 목록 로드"""
        # 콤보박스 초기화 (첫 번째 항목은 유지)
        while self.categoryComboBox.count() > 1:
            self.categoryComboBox.removeItem(1)

        # 카테고리 조회
        categories = []

        if hasattr(self.category_service, "get_all_categories"):
            # CategoryService의 메서드 사용
            categories = self.category_service.get_all_categories()
        elif (
            self.controller
            and hasattr(self.controller, "category_service")
            and hasattr(self.controller.category_service, "get_all_categories")
        ):
            # 컨트롤러를 통해 접근
            categories = self.controller.category_service.get_all_categories()

        # 콤보박스에 추가
        for category in categories:
            self.categoryComboBox.addItem(category.name, category.id)

    def loadLogs(self):
        """로그 목록 로드"""
        # 테이블 초기화
        self.logTable.setRowCount(0)

        # 필터 적용하여 로그 조회
        logs = []

        # 현재 필터와 서비스/컨트롤러에 맞게 로그 가져오기
        if hasattr(self.log_service, "get_all_logs"):
            # LogService의 메서드 사용
            logs = self.log_service.get_all_logs(limit=100)
        elif (
            self.controller
            and hasattr(self.controller, "log_service")
            and hasattr(self.controller.log_service, "get_all_logs")
        ):
            # 컨트롤러를 통해 접근
            logs = self.controller.log_service.get_all_logs(limit=100)

        # 테이블에 추가
        for log in logs:
            row_position = self.logTable.rowCount()
            self.logTable.insertRow(row_position)

            # 날짜 및 시간
            date_str = (
                log.start_date.split(" ")[0]
                if " " in log.start_date
                else log.start_date
            )
            time_str = log.start_date.split(" ")[1] if " " in log.start_date else ""

            # 태그 문자열 생성
            tags_str = log.tags

            # 카테고리 이름 가져오기
            category_name = ""  # 현재 카테고리 정보가 없으므로 빈 문자열 사용

            # 소요 시간 포맷팅 (현재 LogEntity에는 duration 필드가 없을 수 있음)
            duration_str = ""  # 필요한 경우 start_date와 end_date로부터 계산

            # 테이블에 데이터 추가
            self.logTable.setItem(row_position, 0, QTableWidgetItem(date_str))
            self.logTable.setItem(row_position, 1, QTableWidgetItem(time_str))
            self.logTable.setItem(row_position, 2, QTableWidgetItem(log.message))
            self.logTable.setItem(row_position, 3, QTableWidgetItem(tags_str))
            self.logTable.setItem(row_position, 4, QTableWidgetItem(category_name))
            self.logTable.setItem(row_position, 5, QTableWidgetItem(duration_str))

            # 로그 데이터 저장
            for col in range(6):
                self.logTable.item(row_position, col).setData(
                    Qt.ItemDataRole.UserRole, log
                )

            # 카테고리에 따른 색상 설정 (현재 LogEntity에는 category 속성이 없음)
            # 나중에 category 속성이 추가되면 아래 주석을 해제하세요
            # if hasattr(log, 'category') and log.category:
            #     color = QColor(log.category.color)
            #     color.setAlpha(40)  # 투명도 설정
            #     for col in range(6):
            #         self.logTable.item(row_position, col).setBackground(QBrush(color))

    @pyqtSlot()
    def onApplyFilter(self):
        """필터 적용 버튼 이벤트 핸들러"""
        # 필터 데이터 수집
        self.current_filter["search_term"] = self.searchInput.text()
        self.current_filter["date_from"] = self.fromDateEdit.date().toPyDate()
        self.current_filter["date_to"] = self.toDateEdit.date().toPyDate()
        self.current_filter["category_id"] = self.categoryComboBox.currentData()

        # 로그 다시 로드
        self.loadLogs()

    @pyqtSlot()
    def onResetFilter(self):
        """필터 초기화 버튼 이벤트 핸들러"""
        # 필터 컨트롤 초기화
        self.searchInput.clear()
        self.fromDateEdit.setDate(QDate.currentDate().addDays(-30))
        self.toDateEdit.setDate(QDate.currentDate())
        self.categoryComboBox.setCurrentIndex(0)

        # 필터 데이터 초기화
        self.current_filter = {
            "search_term": "",
            "date_from": datetime.now() - timedelta(days=30),
            "date_to": datetime.now(),
            "category_id": None,
        }

        # 로그 다시 로드
        self.loadLogs()

    @pyqtSlot()
    def onEditLog(self):
        """로그 편집 액션 이벤트 핸들러"""
        # 현재 선택된 항목 확인
        selected_items = self.logTable.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "편집 오류", "편집할 로그를 선택하세요.")
            return

        # 선택된 로그 가져오기
        log = selected_items[0].data(Qt.ItemDataRole.UserRole)

        # 로그 편집 대화상자 표시
        # 실제 구현에서는 로그 편집 대화상자를 생성하여 표시
        QMessageBox.information(
            self,
            "로그 편집",
            f"로그 편집 기능은 개발 중입니다.\n선택된 로그: {log.message}",
        )

    @pyqtSlot()
    def onDeleteLog(self):
        """로그 삭제 액션 이벤트 핸들러"""
        # 현재 선택된 항목 확인
        selected_items = self.logTable.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "삭제 오류", "삭제할 로그를 선택하세요.")
            return

        # 선택된 로그 가져오기
        log = selected_items[0].data(Qt.ItemDataRole.UserRole)

        # 확인 대화상자 표시
        reply = QMessageBox.question(
            self,
            "로그 삭제",
            f"선택한 로그를 삭제하시겠습니까?\n\n{log.message}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 로그 삭제
            if hasattr(self.log_service, "delete_log"):
                self.log_service.delete_log(log.id)
            elif self.controller and hasattr(self.controller.log_service, "delete_log"):
                self.controller.log_service.delete_log(log.id)

            # 로그 목록 다시 로드
            self.loadLogs()

    @pyqtSlot()
    def onShowStats(self):
        """통계 보기 액션 이벤트 핸들러"""
        # 통계 대화상자 표시
        # 실제 구현에서는 통계 대화상자를 생성하여 표시
        QMessageBox.information(self, "통계", "통계 기능은 개발 중입니다.")

    @pyqtSlot()
    def onExportLogs(self):
        """로그 내보내기 액션 이벤트 핸들러"""
        # 내보내기 대화상자 표시
        # 실제 구현에서는 파일 저장 대화상자를 표시하여 CSV 등으로 내보내기
        QMessageBox.information(self, "내보내기", "내보내기 기능은 개발 중입니다.")

    @pyqtSlot(QTableWidgetItem)
    def onLogDoubleClicked(self, item):
        """
        로그 항목 더블 클릭 이벤트 핸들러

        Args:
            item: 클릭된 테이블 항목
        """
        # 로그 데이터 가져오기
        log = item.data(Qt.ItemDataRole.UserRole)

        # 로그 상세 정보 표시
        # 실제 구현에서는 로그 상세 대화상자를 생성하여 표시
        QMessageBox.information(
            self,
            "로그 상세 정보",
            f"메시지: {log.message}\n"
            f"시작 시간: {log.start_date}\n"
            f"종료 시간: {log.end_date}\n"
            f"태그: {log.tags}",
        )
