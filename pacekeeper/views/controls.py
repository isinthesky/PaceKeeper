# views/controls.py
from icecream import ic
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from pacekeeper.consts.labels import load_language_resource
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.utils.theme_manager import theme_manager

lang_res = load_language_resource(ConfigController().get_language())

class TimerLabel(QLabel):
    """재사용 가능한 타이머 라벨"""
    def __init__(self, parent=None, initial_text="00:00", font_increment=0, bold=False):
        super().__init__(initial_text, parent)
        font = self.font()
        if font_increment:
            font.setPointSize(font.pointSize() + font_increment)
        if bold:
            font.setBold(True)
        self.setFont(font)
        self.setAlignment(Qt.AlignCenter)
        # 타이머 라벨 크기 설정
        self.setMinimumWidth(120)
        self.setMinimumHeight(32)

class RecentLogsControl(QWidget):
    """최근 로그를 리스트로 보여주는 재사용 가능한 컨트롤"""
    item_double_clicked = pyqtSignal(int)  # 더블 클릭 시그널

    def __init__(self, parent, config_controller, on_double_click=None, on_logs_updated=None):
        super().__init__(parent)
        self.config = config_controller
        self.on_logs_updated = on_logs_updated  # 로그 업데이트 후 호출될 콜백

        # 메인 레이아웃 설정
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)

        # 테이블 위젯 직접 생성 (그룹박스 제거)
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["시간", "메시지", "태그"])
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setDefaultSectionSize(150)

        # 더블 클릭 이벤트 연결
        if on_double_click:
            self.table_widget.itemDoubleClicked.connect(lambda item: on_double_click(item.row()))

        self.layout.addWidget(self.table_widget)

        # 초기 데이터 로드를 제한된 개수의 로그를 불러옵니다.
        self.update_logs(limit=10)

    def update_logs(self, logs=None, limit=50):
        """
        테이블 위젯의 항목들을 최신 로그로 업데이트합니다.

        파라미터:
            logs: MainController 등에서 전달받은 로그 데이터 (리스트).
            limit: 보여줄 로그 수의 제한 (기본값 10)
        """
        ic("RecentLogsControl.update_logs 호출됨")

        try:
            # 테이블 위젯 초기화
            self.table_widget.clearContents()

            # 로그 데이터 검증 및 처리
            if logs is None:
                ic("로그 데이터가 None입니다. 빈 리스트로 처리합니다.")
                logs = []

            # 로그 데이터가 리스트가 아니면 리스트로 변환
            if not isinstance(logs, list):
                ic(f"로그 데이터가 리스트가 아닙니다. 타입: {type(logs)}. 빈 리스트로 처리합니다.")
                logs = []

            # 로그 개수 제한 적용
            logs = logs[:limit] if logs else []
            ic(f"처리할 로그 개수: {len(logs)}")

            # 행 수 설정
            self.table_widget.setRowCount(len(logs))

            # 로그 데이터가 없으면 콜백 호출 후 종료
            if not logs:
                ic("로그 데이터가 없습니다.")
                # 로그 업데이트가 완료되면 콜백으로 태그 버튼 업데이트 진행
                if self.on_logs_updated:
                    ic("로그 업데이트 완료, 태그 버튼 업데이트 콜백 호출")
                    try:
                        self.on_logs_updated()
                        ic("태그 버튼 업데이트 콜백 성공적으로 실행됨")
                    except Exception as e:
                        ic(f"태그 버튼 업데이트 콜백 실행 중 오류 발생: {e}")
                return

            # 로그 데이터 테이블에 추가
            for idx, row in enumerate(reversed(logs)):
                try:
                    # 필수 속성 확인
                    if not hasattr(row, 'start_date') or not hasattr(row, 'message') or not hasattr(row, 'tag_text'):
                        ic(f"로그 항목에 필수 속성이 없습니다: {row}")
                        continue

                    # 시간 열
                    time_item = QTableWidgetItem(row.start_date)
                    self.table_widget.setItem(idx, 0, time_item)

                    # 메시지 열
                    message_item = QTableWidgetItem(row.message)
                    self.table_widget.setItem(idx, 1, message_item)

                    # 태그 열
                    tag_item = QTableWidgetItem(row.tag_text)
                    self.table_widget.setItem(idx, 2, tag_item)

                    ic(f"로그 항목 추가됨: {row.start_date} - {row.message}")
                except Exception as e:
                    ic(f"로그 항목 추가 중 오류 발생: {e}")

            # 로그 업데이트가 완료되면 콜백으로 태그 버튼 업데이트 진행
            if self.on_logs_updated:
                ic("로그 업데이트 완료, 태그 버튼 업데이트 콜백 호출")
                try:
                    self.on_logs_updated()
                    ic("태그 버튼 업데이트 콜백 성공적으로 실행됨")
                except Exception as e:
                    ic(f"태그 버튼 업데이트 콜백 실행 중 오류 발생: {e}")
        except Exception as e:
            ic(f"로그 업데이트 중 오류 발생: {e}")

    def get_message_at(self, row):
        """특정 행의 메시지를 반환합니다."""
        try:
            # 행 번호 유효성 검사
            if row < 0 or row >= self.table_widget.rowCount():
                ic(f"유효하지 않은 행 번호: {row}, 총 행 수: {self.table_widget.rowCount()}")
                return ""

            # 항목 존재 여부 확인
            item = self.table_widget.item(row, 1)
            if item is None:
                ic(f"행 {row}의 메시지 항목이 없습니다.")
                return ""

            # 메시지 반환
            message = item.text()
            ic(f"행 {row}에서 메시지 '{message}' 반환")
            return message
        except Exception as e:
            ic(f"메시지 가져오기 중 오류 발생: {e}")
            return ""

class QFlowLayout(QLayout):
    """Qt에서 기본 제공하지 않는 FlowLayout 구현 (태그 버튼 배치용)"""
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self._items = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins().left()
        size += QSize(2 * margin, 2 * margin)
        return size

    def _doLayout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._items:
            widget = item.widget()
            style = widget.style() if widget else None

            space_x = spacing
            space_y = spacing

            if style:
                space_x = style.layoutSpacing(
                    QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
                space_y = style.layoutSpacing(
                    QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)

            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()

class TagButtonsPanel(QWidget):
    """태그 버튼들을 관리하는 패널"""
    def __init__(self, parent, on_tag_selected=None, category_service=None):
        super().__init__(parent)
        self.on_tag_selected = on_tag_selected
        self.category_service = category_service  # 의존성 주입을 통해 전달받음
        self.layout = QFlowLayout(self, margin=2, spacing=3)
        self.setLayout(self.layout)

    def update_tags(self, tags):
        """
        태그 버튼 업데이트 메서드.
        """
        ic("TagButtonsPanel.update_tags 호출됨")

        # 기존 버튼 제거
        try:
            while self.layout.count():
                item = self.layout.takeAt(0)
                if item and item.widget():
                    item.widget().deleteLater()
            ic("기존 태그 버튼 제거 완료")
        except Exception as e:
            ic(f"기존 버튼 제거 중 오류 발생: {e}")

        # 태그가 None이면 빈 리스트로 처리
        if tags is None:
            ic("태그가 None입니다. 빈 리스트로 처리합니다.")
            tags = []

        # 태그가 리스트가 아니면 리스트로 변환
        if not isinstance(tags, list):
            ic(f"태그가 리스트가 아닙니다. 타입: {type(tags)}. 빈 리스트로 처리합니다.")
            tags = []

        # 카테고리 정보 가져오기
        try:
            if self.category_service:
                categories = self.category_service.get_categories()
                color_set = {category.id: category for category in categories}
                ic(f"{len(categories)}개의 카테고리 정보를 가져왔습니다.")
            else:
                ic("카테고리 서비스가 없습니다.")
                color_set = {}
        except Exception as e:
            ic(f"카테고리 정보 가져오기 실패: {e}")
            color_set = {}

        ic(f"태그 버튼 업데이트 시작, 태그 수: {len(tags)}")

        # 태그가 없으면 패널 숨기기
        if not tags:
            ic("태그가 없습니다. 패널을 숨깁니다.")
            self.hide()
            return
        else:
            self.show()

        # 태그 버튼 생성
        for tag in tags:
            if not tag:
                ic("빈 태그 항목을 건너뜁니다.")
                continue

            try:
                # Tag 객체인 경우 to_dict 메서드 사용
                if hasattr(tag, 'to_dict'):
                    tag_dict = tag.to_dict()
                    ic(f"Tag 객체를 딕셔너리로 변환: {tag_dict}")
                else:
                    # 이미 딕셔너리인 경우 그대로 사용
                    tag_dict = tag
                    ic(f"이미 딕셔너리 형태의 태그: {tag_dict}")

                # 필수 키가 있는지 확인
                if 'name' not in tag_dict:
                    ic(f"태그에 'name' 키가 없습니다: {tag_dict}")
                    continue

                if 'category_id' not in tag_dict:
                    ic(f"태그에 'category_id' 키가 없습니다: {tag_dict}")
                    tag_dict['category_id'] = None

                # 버튼 생성 - 명시적으로 문자열 변환하여 인코딩 보장
                tag_name = str(tag_dict["name"])
                btn = QPushButton(tag_name, self)
                theme_manager.apply_button_style(btn, "tag")

                # 클릭 이벤트 연결
                try:
                    # 람다 함수에서 태그 딕셔너리를 복사하여 사용
                    tag_copy = dict(tag_dict)
                    btn.clicked.connect(lambda: self.on_tag_selected(tag_copy))
                except Exception as e:
                    ic(f"버튼 클릭 이벤트 연결 중 오류 발생: {e}")

                # 카테고리 색상 설정 (ThemeManager를 통해 적용)
                try:
                    category = color_set.get(tag_dict["category_id"])
                    if category and hasattr(category, 'color') and category.color:
                        # ThemeManager를 사용하여 카테고리 색상 적용
                        theme_manager.apply_category_color(btn, category.color, "tag")
                    else:
                        ic(f"카테고리 ID {tag_dict['category_id']}에 해당하는 카테고리를 찾을 수 없거나 색상 정보가 없습니다.")
                except Exception as e:
                    ic(f"카테고리 색상 설정 중 오류 발생: {e}")

                # 버튼 추가
                self.layout.addWidget(btn)
                ic(f"태그 버튼 '{tag_dict['name']}' 추가됨")
            except Exception as e:
                ic(f"태그 버튼 생성 중 오류 발생: {e}")

        # 레이아웃 업데이트
        try:
            self.updateGeometry()
            ic("태그 버튼 패널 업데이트 완료")
        except Exception as e:
            ic(f"레이아웃 업데이트 중 오류 발생: {e}")

class TextInputPanel(QWidget):
    """텍스트 입력창과 (옵션) 버튼을 포함하는 패널"""
    textChanged = pyqtSignal()

    def __init__(self, parent, label_text=None, on_text_changed=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)

        # 텍스트 입력 필드 직접 생성 (그룹박스 제거)
        self.input_ctrl = QLineEdit(self)
        placeholder = label_text if label_text else "#태그 형식으로 작업 입력..."
        self.input_ctrl.setPlaceholderText(placeholder)
        if on_text_changed:
            self.input_ctrl.textChanged.connect(on_text_changed)
        else:
            self.input_ctrl.textChanged.connect(self.on_text_changed)
        self.layout.addWidget(self.input_ctrl)

    def get_value(self):
        """입력 필드의 현재 값을 반환"""
        return self.input_ctrl.text()

    def set_value(self, value):
        """입력 필드의 값을 설정"""
        self.input_ctrl.setText(value)

    def set_hint(self, hint_text):
        """플레이스홀더 텍스트 설정"""
        self.input_ctrl.setPlaceholderText(hint_text)

    def on_text_changed(self):
        """텍스트 변경 이벤트 핸들러"""
        self.textChanged.emit()
