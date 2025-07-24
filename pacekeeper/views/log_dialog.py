# views/log_dialog.py
import json
from datetime import date, datetime, timedelta

from icecream import ic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from pacekeeper.consts.labels import load_language_resource
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.repository.entities import Log
from pacekeeper.views.controls import TagButtonsPanel

lang_res = load_language_resource(ConfigController().get_language())

class LogDialog(QDialog):
    def __init__(self, parent, config_controller, log_service=None, tag_service=None):
        super().__init__(parent)
        self.setWindowTitle(lang_res.base_labels['LOGS'])
        self.resize(800, 800)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.config = config_controller

        # 서비스들이 전달되지 않으면 None으로 설정 (에러 방지)
        self.log_service = log_service
        self.tag_service = tag_service

        # 종료일 기본값: 오늘
        end_dt = date.today()
        start_dt = end_dt - timedelta(days=90)
        self.selected_start_date = start_dt.strftime("%Y-%m-%d")
        self.selected_end_date = end_dt.strftime("%Y-%m-%d")

        self.InitUI()
        self.center_on_screen()

    def InitUI(self):
        main_layout = QVBoxLayout(self)

        # 레이블
        title_label = QLabel(lang_res.base_labels['LOGS'])
        font = title_label.font()
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # ---------------------------------------------------------------------
        # (1) 검색 영역: 날짜 범위 + 태그 + 검색 버튼
        # ---------------------------------------------------------------------
        search_layout = QHBoxLayout()

        # -- 기간 선택 버튼들 --
        # 1년 / 3달 / 1달 / 1주 / 1일
        period_buttons = [
            ("1년", 365),
            ("3달", 90),
            ("1달", 30),
            ("1주", 7),
            ("1일", 1),
        ]

        for label, days in period_buttons:
            btn = QPushButton(label)
            btn.setFixedWidth(40)
            btn.clicked.connect(lambda checked, d=days: self.on_period_button(d))
            search_layout.addWidget(btn)

        # 종료일 (기본값: 오늘)
        search_layout.addWidget(QLabel(lang_res.base_labels['SEARCH_DATE']))
        today_str = date.today().strftime("%Y-%m-%d")
        self.end_date_tc = QLineEdit(today_str)
        self.end_date_tc.setFixedWidth(100)
        self.end_date_tc.setAlignment(Qt.AlignCenter)
        search_layout.addWidget(self.end_date_tc)

        # 태그
        search_layout.addWidget(QLabel(lang_res.base_labels['TAG']))
        self.tag_tc = QLineEdit()
        self.tag_tc.setFixedWidth(100)
        search_layout.addWidget(self.tag_tc)

        # 검색 버튼
        search_btn = QPushButton(lang_res.button_labels['SEARCH'])
        search_btn.clicked.connect(self.on_search)
        search_layout.addWidget(search_btn)

        # 레이아웃에 검색 영역 추가
        main_layout.addLayout(search_layout)

        # ---------------------------------------------------------------------
        # (1-1) 태그 버튼 패널: 자주 사용하는 태그 버튼 표시
        # ---------------------------------------------------------------------
        tag_panel_layout = QVBoxLayout()
        tag_panel_label = QLabel("자주 사용하는 태그")
        tag_panel_label.setAlignment(Qt.AlignCenter)
        tag_panel_layout.addWidget(tag_panel_label)

        # 태그 버튼 패널 생성
        self.tag_buttons_panel = TagButtonsPanel(self, self.on_tag_button_clicked)

        # 태그 버튼 패널을 스크롤 영역에 추가
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.tag_buttons_panel)
        scroll_area.setMaximumHeight(100)  # 높이 제한

        tag_panel_layout.addWidget(scroll_area)
        main_layout.addLayout(tag_panel_layout)

        # 태그 버튼 패널 업데이트
        self.update_tag_buttons()

        # ---------------------------------------------------------------------
        # (2) TableWidget: 로그를 테이블 형태로 표시
        # ---------------------------------------------------------------------
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Timestamp", "Message", "Tags"])
        self.table_widget.setColumnHidden(0, True)  # ID 컬럼 숨김
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.ExtendedSelection)
        main_layout.addWidget(self.table_widget)

        # ---------------------------------------------------------------------
        # (3) 삭제 버튼: 선택한 로그 항목들을 삭제
        # ---------------------------------------------------------------------
        btn_layout = QHBoxLayout()
        delete_btn = QPushButton("선택 삭제")
        delete_btn.clicked.connect(self.on_delete)
        btn_layout.addWidget(delete_btn)
        btn_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.load_all_logs()

    def load_all_logs(self):
        """
        DB에서 전체 로그를 가져와서 TableWidget에 표시
        """
        if not self.log_service:
            return
        rows: list[Log] = self.log_service.retrieve_all_logs()
        self.load_rows(rows)

    def load_rows(self, rows):
        """
        TableWidget 초기화 후, rows 데이터(ID, start_date, message, tags) 출력
        """
        self.table_widget.setRowCount(0)

        # 데이터가 없는 경우 메시지 표시
        if not rows:
            # 테이블에 "데이터가 없습니다" 메시지를 표시
            self.table_widget.setRowCount(1)
            self.table_widget.setColumnCount(4)
            no_data_item = QTableWidgetItem("데이터가 없습니다")
            no_data_item.setTextAlignment(Qt.AlignCenter)
            # 첫 번째 열에 메시지 표시
            self.table_widget.setItem(0, 1, no_data_item)
            # 셀 병합
            self.table_widget.setSpan(0, 1, 1, 3)
            return

        for row_idx, row in enumerate(rows):
            self.table_widget.insertRow(row_idx)
            self.table_widget.setItem(row_idx, 0, QTableWidgetItem(str(row.id)))
            self.table_widget.setItem(row_idx, 1, QTableWidgetItem(str(row.start_date)))
            self.table_widget.setItem(row_idx, 2, QTableWidgetItem(str(row.message)))

            # 태그 ID를 태그 이름으로 변환
            tag_text = ""
            try:
                if row.tags and row.tags != "[]":
                    # JSON 문자열을 리스트로 변환
                    try:
                        tag_ids = json.loads(row.tags)
                    except (json.JSONDecodeError, TypeError) as e:
                        ic(f"JSON 파싱 오류: {e} - 입력: {row.tags}")
                        tag_ids = []

                    # 유효한 태그 ID 리스트인 경우 태그 서비스를 통해 이름 가져오기
                    if isinstance(tag_ids, list) and tag_ids and self.tag_service:
                        tag_names = self.tag_service.get_tag_text(tag_ids)
                        # 유효한 태그 이름이 있는 경우 쉼표로 구분하여 연결
                        if tag_names:
                            # 문자열 연결 전에 각 항목이 문자열인지 확인하고 인코딩 보장
                            tag_text = ", ".join(str(name) for name in tag_names if name)
            except Exception as e:
                ic(f"태그 변환 오류: {e}")
                tag_text = ""

            # 태그 텍스트 설정
            tag_item = QTableWidgetItem(tag_text)
            self.table_widget.setItem(row_idx, 3, tag_item)

    def on_period_button(self, days):
        """
        기간 버튼 클릭 시 종료일에서 days일 만큼 빼서 시작일을 결정하고 검색 실행
        """
        end_date_str = self.end_date_tc.text().strip()
        if not end_date_str:
            end_date_str = date.today().strftime("%Y-%m-%d")
            self.end_date_tc.setText(end_date_str)
        try:
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            QMessageBox.critical(self, lang_res.base_labels['ERROR'],
                               lang_res.error_messages['SEARCH_DATE'])
            return

        start_dt = end_dt - timedelta(days=days)
        self.selected_start_date = start_dt.strftime("%Y-%m-%d")
        self.selected_end_date = end_date_str
        self.on_search()

    def on_search(self):
        """
        '검색' 버튼 클릭 시 날짜 범위와 태그 검색을 수행
        """
        start_date = self.selected_start_date
        end_date = self.selected_end_date
        tag_keyword = self.tag_tc.text().strip().lower()  # 소문자로 변환

        # 서비스가 없으면 빈 결과 반환
        if not self.log_service:
            self.load_rows([])
            return

        # 날짜 범위 조건 처리
        rows_date = self.log_service.retrieve_logs_by_period(start_date, end_date) if start_date and end_date else self.log_service.retrieve_all_logs()

        # 태그 조건 처리
        if tag_keyword:
            rows_tag = self.log_service.retrieve_logs_by_tag(tag_keyword)

            # ID 기반으로 교집합 찾기
            date_ids = {log.id for log in rows_date}
            tag_ids = {log.id for log in rows_tag}
            common_ids = date_ids.intersection(tag_ids)

            # 교집합 ID에 해당하는 로그만 필터링
            result_rows = [log for log in rows_date if log.id in common_ids]
        else:
            # 태그 키워드가 없으면 날짜 기준 결과만 사용
            result_rows = rows_date

        # ID 기준 내림차순 정렬
        sorted_rows = sorted(result_rows, key=lambda x: x.id, reverse=True)
        self.load_rows(sorted_rows)

    def on_delete(self):
        """
        선택된 로그 항목들을 삭제하는 이벤트 핸들러
        """
        # 선택된 항목 인덱스를 가져옴
        selected_rows = self.table_widget.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.information(self, "알림", "삭제할 로그를 선택하세요.")
            return

        answer = QMessageBox.question(self, "확인", "선택한 로그를 삭제하시겠습니까?",
                                    QMessageBox.Yes | QMessageBox.No)
        if answer != QMessageBox.Yes:
            return

        ids_to_delete = []
        for index in selected_rows:
            row = index.row()
            id_str = self.table_widget.item(row, 0).text()
            try:
                log_id = int(id_str)
                ids_to_delete.append(log_id)
            except ValueError:
                continue

        if self.log_service:
            self.log_service.remove_logs_by_ids(ids_to_delete)
            QMessageBox.information(self, "정보", "선택한 로그가 삭제되었습니다.")
            self.load_all_logs()
        else:
            QMessageBox.warning(self, "오류", "로그 서비스가 초기화되지 않았습니다.")

    def center_on_screen(self):
        """화면 중앙에 다이얼로그를 배치합니다."""
        screen_geometry = self.screen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def update_tag_buttons(self):
        """
        태그 버튼 패널을 업데이트합니다.
        """
        try:
            # 태그 서비스에서 모든 태그 가져오기
            if not self.tag_service:
                ic("태그 서비스가 초기화되지 않았습니다.")
                return
            tags = self.tag_service.get_tags()
            ic("태그 목록 조회 성공", len(tags))

            # 태그 버튼 패널 업데이트
            self.tag_buttons_panel.update_tags(tags)
        except Exception as e:
            ic("태그 버튼 패널 업데이트 실패", e)

    def on_tag_button_clicked(self, tag):
        """
        태그 버튼 클릭 시 해당 태그로 검색을 수행합니다.
        """
        # 명시적으로 문자열 변환하여 인코딩 보장
        tag_name = str(tag["name"])
        self.tag_tc.setText(tag_name)
        self.on_search()
