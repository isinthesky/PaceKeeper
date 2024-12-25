# views/break_dialog.py
import wx
import threading
import time
from breaktrack.controllers.config_controller import ConfigController
from breaktrack.const import DIALOG_BREAK, MSG_START_BREAK, MSG_ERROR_DEFAULT, BTN_SUBMIT, CONFIG_DATA_MODEL, SETTINGS_BREAK_DLG_PADDING_SIZE

class BreakDialog(wx.Dialog):
    """
    휴식 시간을 카운트다운하는 모달 다이얼로그.
    """
    def __init__(self, parent, title=DIALOG_BREAK, message=MSG_START_BREAK,
                 break_minutes=5, config_controller=None, on_break_end=None):
        """
        break_minutes: 휴식 시간 (분)
        config_controller: ConfigController 인스턴스
        """
        display_width, display_height = wx.GetDisplaySize()
        self.config :ConfigController = config_controller
        self._destroyed = False  # 객체 삭제 상태 추적

        super().__init__(
            parent,
            title=title,
            size=(display_width - self.config.get_setting(SETTINGS_BREAK_DLG_PADDING_SIZE, 70),
                  display_height - self.config.get_setting(SETTINGS_BREAK_DLG_PADDING_SIZE, 70)),
            style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP
        )

        self.break_minutes = break_minutes
        self.on_break_end = on_break_end
        self._running = True

        # UI 초기화
        self.init_ui(message)
        self.CenterOnScreen()

        # 카운트다운 스레드 시작
        self.break_thread = threading.Thread(target=self.run_countdown)
        self.break_thread.start()

    def init_ui(self, message):
        """
        UI 컴포넌트 배치
        1) 안내 문구
        2) 남은 휴식 시간 라벨
        3) 최근 5개 로그 표시 (신규 추가)
        4) 메시지 입력창 + 제출 버튼
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.tag_buttons_panel = wx.Panel(self)
        self.tag_buttons_sizer = wx.WrapSizer()
        self.tag_buttons_panel.SetSizer(self.tag_buttons_sizer)

        # (1) 안내 문구
        st = wx.StaticText(self, label=message, style=wx.ALIGN_CENTER)
        main_sizer.Add(st, flag=wx.ALIGN_CENTER | wx.TOP, border=20)

        # (2) 남은 시간 표시
        self.break_label = wx.StaticText(self, label="00:00", style=wx.ALIGN_CENTER)
        font = self.break_label.GetFont()
        font.PointSize += 10
        self.break_label.SetFont(font)
        main_sizer.Add(self.break_label, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)

        # (3) 최근 5개 로그 보여주기
        main_sizer.Add(self.create_recent_logs_ctrl(self), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)

        # (4) 태그 버튼들
        main_sizer.Add(self.tag_buttons_panel, flag=wx.EXPAND | wx.ALL, border=10)

        # (4) 사용자 입력 필드 + 종료 버튼
        self.user_input = wx.TextCtrl(self, value="", style=wx.TE_PROCESS_ENTER)
        self.user_input.Bind(wx.EVT_TEXT, self.on_text_change)
        main_sizer.Add(self.user_input, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=20)

        self.submit_btn = wx.Button(self, label=BTN_SUBMIT)
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit)
        self.submit_btn.Enable(False)  # 초기 비활성화
        main_sizer.Add(self.submit_btn, flag=wx.ALIGN_CENTER | wx.ALL, border=20)

        self.SetSizer(main_sizer)

    def create_recent_logs_ctrl(self, parent) -> wx.StaticBoxSizer:
        """
        '최근 5개 기록' 섹션(StaticBox + ListCtrl) 만들기
        """
        box = wx.StaticBox(parent, label="최근 5개 기록")
        box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        # ListCtrl 생성 (보고서 스타일)
        self.recent_logs_lc = wx.ListCtrl(
            box,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN,
        )
        
        # 컬럼 추가
        self.recent_logs_lc.InsertColumn(0, "시간", format=wx.LIST_FORMAT_CENTER, width=160)
        self.recent_logs_lc.InsertColumn(1, "메시지", format=wx.LIST_FORMAT_LEFT, width=500)
        self.recent_logs_lc.InsertColumn(2, "태그", format=wx.LIST_FORMAT_LEFT, width=300)
        
        # 데이터 로드
        self.load_recent_logs()
        
        self.recent_logs_lc.SetMinSize((300, 250))
        box_sizer.Add(self.recent_logs_lc, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        return box_sizer

    def load_recent_logs(self):
        """
        DB에서 최근 5개 로그를 조회하여 ListCtrl에 표시
        """
        if self.config and hasattr(self.config, CONFIG_DATA_MODEL):
            # 기존 항목 삭제
            self.recent_logs_lc.DeleteAllItems()

            # 태그 집합 초기화
            unique_tags = set()
            
            rows = self.config.data_model.get_last_logs(10)
            rows.reverse()
            for idx, row in enumerate(rows):
                log_time = row[2]   # timestamp
                log_msg = row[3]    # message
                log_tags = row[4]   # tags

                # ListCtrl에 항목 추가
                index = self.recent_logs_lc.InsertItem(idx, log_time)
                self.recent_logs_lc.SetItem(index, 1, log_msg)
                self.recent_logs_lc.SetItem(index, 2, log_tags or "")

                # 태그 추출 및 집합에 추가
                if log_tags:
                    tags = [tag.strip() for tag in log_tags.split(',')]
                    unique_tags.update(tags)
            
            # 기존 태그 버튼들 제거
            for child in self.tag_buttons_panel.GetChildren():
                child.Destroy()
            
            # 새로운 태그 버튼들 생성
            for tag in sorted(unique_tags):
                if tag:  # 빈 태그 제외
                    btn = self.create_tag_button(tag)
                    self.tag_buttons_sizer.Add(btn, 0, wx.ALL, 5)
            
            self.tag_buttons_panel.Layout()
        
    def create_tag_button(self, tag: str) -> wx.Button:
        """
        둥근 모서리의 태그 버튼 생성
        """
        btn = wx.Button(self.tag_buttons_panel, label=tag)
                
        # 클릭 이벤트 바인딩
        btn.Bind(wx.EVT_BUTTON, lambda evt, t=tag: self.on_tag_button_click(evt, t))
        
        return btn
    
    def on_tag_button_click(self, event, tag: str):
        """
        태그 버튼 클릭 시 입력창에 태그 추가
        """
        current_text = self.user_input.GetValue()
        if not tag.startswith('#'):
            tag = f"#{tag}"
        
        # 이미 해당 태그가 있는지 확인
        if tag not in current_text:
            # 입력창이 비어있지 않고 마지막 문자가 공백이 아니면 공백 추가
            if current_text and not current_text.endswith(' '):
                current_text += ' '
            current_text += f"{tag} "
            self.user_input.SetValue(current_text)

    def run_countdown(self):
        """
        휴식 시간 카운트다운 (break_minutes * 60초)
        """
        remaining = self.break_minutes * 60
        while remaining >= 0 and self._running:
            mins, secs = divmod(remaining, 60)
            if not self._destroyed:  # 객체가 살아있을 때만 UI 업데이트
                try:
                    wx.CallAfter(self.break_label.SetLabel, f"{mins:02d}:{secs:02d}")
                except Exception as e:
                    self.config.data_model.log_break(MSG_ERROR_DEFAULT.format(e))
                    break
            time.sleep(1)
            remaining -= 1

    def on_text_change(self, event):
        """
        텍스트 입력창에 내용이 있어야만 '종료' 버튼 활성화
        """
        user_text = self.user_input.GetValue().strip()
        self.submit_btn.Enable(bool(user_text))

    def on_submit(self, event):
        """
        사용자가 '종료' 버튼을 누르면:
        1) 카운트다운 스레드 종료
        2) DB에 메시지 로그 기록
        3) 로그 목록 갱신
        4) 다이얼로그 닫기
        """
        self._running = False
        self._destroyed = True  # 객체가 곧 삭제될 것임을 표시
        user_text = self.user_input.GetValue().strip()

        # DB 저장
        if hasattr(self.config, CONFIG_DATA_MODEL) and user_text:
            self.config.data_model.log_break(user_text)
            self.load_recent_logs()  # 로그 목록 갱신

        if self.on_break_end:
            self.on_break_end()

        # 스레드가 완전히 종료될 때까지 잠시 대기
        if self.break_thread and self.break_thread.is_alive():
            self.break_thread.join(timeout=1)

        self.EndModal(wx.ID_OK)