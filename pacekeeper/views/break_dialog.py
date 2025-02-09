# views/break_dialog.py
import wx
from pacekeeper.controllers.config_controller import ConfigController, AppStatus
from pacekeeper.controllers.timer_controller import TimerController
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import CONFIG_DATA_MODEL, SET_PADDING_SIZE

lang_res = load_language_resource()

class BreakDialog(wx.Dialog):
    """
    휴식 시간을 카운트다운하는 모달 다이얼로그.
    """
    def __init__(self, parent,
                 config_controller=None,
                 break_minutes=5,
                 on_break_end=None):
        """
        break_minutes: 휴식 시간 (분)
        config_controller: ConfigController 인스턴스
        """
        display_width, display_height = wx.GetDisplaySize()
        self.config: ConfigController = config_controller
        self.on_break_end = on_break_end
        self.timer_ctrl = TimerController(self.config)
        message = lang_res.messages['START_BREAK']

        super().__init__(
            parent,
            title=lang_res.base_labels['BREAK_DIALOG_TITLE'],
            size=(display_width - self.config.get_setting(SET_PADDING_SIZE, 100),
                  display_height - self.config.get_setting(SET_PADDING_SIZE, 100)),
            style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP
        )

        self.break_minutes = break_minutes
        self.on_break_end = on_break_end
        self._destroyed = False  # 종료 상태 추적용 플래그 추가

        # UI 초기화
        self.init_ui(message)
        self.CenterOnScreen()
        self.start_break_timer()

    def init_ui(self, message):
        """
        UI 컴포넌트 배치
        1) 안내 문구
        2) 남은 휴식 시간 타이머 라벨
        3) 최근 5개 로그 표시
        4) 태그 버튼 패널
        5) 사용자 입력창 + 제출 버튼 (TextInputPanel 활용)
        """
        self.SetBackgroundColour('#a3cca3')
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # (1) 안내 문구
        st = wx.StaticText(self, label=message, style=wx.ALIGN_CENTER)
        main_sizer.Add(st, flag=wx.ALIGN_CENTER | wx.TOP, border=20)

        # (2) 남은 시간 표시 - TimerLabel 사용
        self.break_label = TimerLabel(self, initial_text="00:00", font_increment=10, alignment=wx.ALIGN_CENTER)
        main_sizer.Add(self.break_label, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)

        # (3) 최근 기록 컨트롤
        self.recent_logs = RecentLogsControl(
            self, 
            self.config,
            on_double_click=self.on_item_double_click
        )
        main_sizer.Add(self.recent_logs, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)

        # (4) 태그 버튼 패널
        self.tag_buttons_panel = wx.Panel(self)
        self.tag_buttons_sizer = wx.WrapSizer()
        self.tag_buttons_panel.SetSizer(self.tag_buttons_sizer)
        self.tag_panel = TagButtonsPanel(
            self.tag_buttons_panel, 
            on_tag_selected=self.add_tag_to_input
        )
        self.tag_buttons_sizer.Add(self.tag_panel, 1, wx.EXPAND)
        main_sizer.Add(self.tag_buttons_panel, flag=wx.EXPAND | wx.ALL, border=10)

        # (5) 사용자 입력 필드 + 종료 버튼 - TextInputPanel 사용
        self.input_panel = TextInputPanel(self, 
            box_label=None, 
            button_label=lang_res.button_labels['SUBMIT']
        )
        self.input_panel.bind_text_change(self.on_text_change)
        self.input_panel.bind_button(self.on_submit)
        main_sizer.Add(self.input_panel, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=20)

        self.SetSizer(main_sizer)

    def start_break_timer(self):
        def update_label(time_str):
            if not self._destroyed:  # 객체 파괴 후 콜백 방지
                wx.CallAfter(self.break_label.SetLabel, time_str)

        def on_finish():
            """타이머 완료 시 자동으로 다이얼로그 닫기"""
            if not self._destroyed and self.on_break_end:
                wx.CallAfter(self.on_break_end)
            if not self._destroyed:
                wx.CallAfter(self.EndModal, wx.ID_OK)

        # TimerController를 사용한 타이머 시작
        total_seconds = self.break_minutes * 20
        self.timer_ctrl.start_timer(
            total_seconds=total_seconds,
            update_callback=update_label,
            on_finish=on_finish,
            pauseable=False,
            app_status_when_running=AppStatus.SHORT_BREAK
        )

    def on_text_change(self, event):
        """
        텍스트 입력창에 내용이 있어야만 '종료' 버튼 활성화
        """
        user_text = self.input_panel.get_value().strip()
        if self.input_panel.button:
            self.input_panel.button.Enable(bool(user_text))

    def on_item_double_click(self, event):
        """항목 더블클릭 시 텍스트 입력창에 내용 채우기"""
        index = event.GetIndex()
        message = self.recent_logs.list_ctrl.GetItemText(index, 1)
        tags = self.recent_logs.list_ctrl.GetItemText(index, 2)
        
        # 태그가 있으면 메시지 앞에 추가
        full_text = f"{tags} {message}".strip() if tags else message
        self.input_panel.set_value(full_text)
        if self.input_panel.button:
            self.input_panel.button.Enable(True)

    def on_submit(self, event):
        """사용자 조기 제출 시 타이머 중지 처리 추가"""
        self._destroyed = True  # 객체 파괴 표시
        self.timer_ctrl.stop_timer()  # 타이머 강제 종료
        
        user_text = self.input_panel.get_value().strip()

        # DB 저장
        if hasattr(self.config, CONFIG_DATA_MODEL) and user_text:
            self.config.data_model.log_study(user_text)
            self.load_recent_logs()

        if self.on_break_end:
            self.on_break_end(manual_submit=True)  # 수동 제출 플래그 추가

        self.EndModal(wx.ID_OK)

    def load_recent_logs(self):
        # 기존 코드 대체
        unique_tags = set()
        if self.config and hasattr(self.config, CONFIG_DATA_MODEL):
            rows = self.config.data_model.get_last_logs(10)
            for row in rows:
                if row[4]:  # tags
                    unique_tags.update(tag.strip() for tag in row[4].split(','))
            self.tag_panel.update_tags(unique_tags)

    def add_tag_to_input(self, tag):
        # 기존 on_tag_button_click 로직 단순화
        current = self.input_panel.get_value()
        if tag not in current:
            new_text = f"{current} {tag} " if current else f"{tag} "
            self.input_panel.set_value(new_text.strip())