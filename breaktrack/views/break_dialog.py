# views/break_dialog.py
import wx
import threading
import time

class BreakDialog(wx.Dialog):
    def __init__(self, parent, title="휴식", message="휴식을 시작하세요!",
                 break_minutes=5, config_controller=None, on_break_end=None):
        """
        break_minutes: 휴식 시간 (분)
        config_controller: ConfigController 인스턴스
        """
        display_width, display_height = wx.GetDisplaySize()
        padding_size = 70  

        self.config = config_controller

        super().__init__(
            parent,
            title=title,
            size=(display_width - padding_size, display_height - padding_size),
            style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP
        )

        self.break_minutes = break_minutes
        self.on_break_end = on_break_end  # 콜백 저장
        self._running = True

        # UI 초기화
        self.init_ui(message)
        self.CenterOnScreen()

        # 카운트다운 시작 (예시: 실제 60초 대신 10초로 테스트)
        self.break_thread = threading.Thread(target=self.run_countdown)
        self.break_thread.start()

    def init_ui(self, message):
        """
        UI 컴포넌트 배치
        1) 안내 문구
        2) 남은 휴식 시간 라벨
        3) (신규) 메시지 입력창
        4) 제출 버튼
        """
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 안내 문구
        st = wx.StaticText(self, label=message, style=wx.ALIGN_CENTER)
        vbox.Add(st, flag=wx.ALIGN_CENTER | wx.TOP, border=20)

        # 남은 시간 표시
        self.break_label = wx.StaticText(self, label="00:00", style=wx.ALIGN_CENTER)
        font = self.break_label.GetFont()
        font.PointSize += 10
        self.break_label.SetFont(font)
        vbox.Add(self.break_label, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)

        # (신규) 사용자 입력 필드
        self.user_input = wx.TextCtrl(self, value="", style=wx.TE_PROCESS_ENTER)
        self.user_input.Bind(wx.EVT_TEXT, self.on_text_change)
        vbox.Add(self.user_input, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)

        # Submit 버튼
        self.submit_btn = wx.Button(self, label="종료")
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit)
        # 초기에는 비활성화
        self.submit_btn.Enable(False)
        vbox.Add(self.submit_btn, flag=wx.ALIGN_CENTER | wx.ALL, border=20)

        self.SetSizer(vbox)

    def run_countdown(self):
        """
        휴식 시간 카운트다운
        실제 1분=60초 대신 테스트 목적이면 10초로 변경 가능
        """
        # 예) 실제 사용 시: self.break_minutes * 60
        remaining = self.break_minutes * 60
        while remaining >= 0 and self._running:
            mins, secs = divmod(remaining, 60)
            try:
                wx.CallAfter(self.break_label.SetLabel, f"{mins:02d}:{secs:02d}")
            except:  # 라벨이 이미 파괴되었을 수 있음
                break

            time.sleep(1)
            remaining -= 1

    def on_text_change(self, event):
        """
        텍스트 입력창 내용 변경 시 호출
        - 내용이 있으면 Submit 버튼 활성화
        - 없으면 비활성화
        """
        user_text = self.user_input.GetValue().strip()
        if user_text:
            self.submit_btn.Enable(True)
        else:
            self.submit_btn.Enable(False)

    def on_submit(self, event):
        """
        Submit 버튼 클릭 시 (사용자가 '종료' 버튼 누름)
        - _running=False => 카운트다운 스레드 종료
        - DB에 로그(옵션)
        - 다이얼로그 닫기
        """
        self._running = False
        user_text = self.user_input.GetValue().strip()

        # DB 저장
        if hasattr(self.config, "data_model") and user_text:
            self.config.data_model.log_break(user_text)

        if self.on_break_end:
            self.on_break_end()

        self.EndModal(wx.ID_OK)
