import wx
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.controllers.main_controller import MainController
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import SET_PADDING_SIZE, SET_BREAK_COLOR
from pacekeeper.views.controls import TimerLabel

lang_res = load_language_resource(ConfigController().get_language())

class BreakDialog(wx.Dialog):
    """
    휴식 시간을 카운트다운하는 모달 다이얼로그 및 UI 패널 통합 클래스
    
    주요 기능:
      - 안내 문구와 남은 시간 표시(타이머 라벨) 제공
      - 타이머 중지 및 다이얼로그 종료 이벤트 처리
      - 타이머 종료 시 on_break_end 콜백 실행
      - '휴식 닫기' 버튼을 통한 휴식 종료 기능 추가
    """
    def __init__(self, parent, main_controller: MainController, config_ctrl: ConfigController, break_minutes=5, on_break_end=None):
        self.main_controller = main_controller
        self.config = config_ctrl
        self.break_minutes = break_minutes
        self.on_break_end = on_break_end
        self._destroyed = False
        
        # 디스플레이 전체 크기를 고려하여 대화상자 크기 설정
        display_width, display_height = wx.GetDisplaySize()
        dlg_width = display_width - self.config.get_setting(SET_PADDING_SIZE, 100)
        dlg_height = display_height - self.config.get_setting(SET_PADDING_SIZE, 100)
        
        super().__init__(
            parent,
            title=lang_res.title_labels['BREAK_DIALOG_TITLE'],
            size=(dlg_width, dlg_height),
            style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP
        )
        
        # 추가: config에 저장된 SET_BREAK_COLOR 값으로 배경색 설정 (기본값 "#FDFFB6")
        bg_color = self.config.get_setting(SET_BREAK_COLOR, "#FDFFB6")
        self.SetBackgroundColour(bg_color)
        
        # 타이머 정지를 위한 함수 지정
        self.stop_timer_func = self.main_controller.timer_service.stop
        
        self.init_ui()
        self.init_events()
        self.CenterOnScreen()
        
    def init_ui(self):
        """UI 구성: 안내 문구와 남은 시간 표시(타이머 라벨), 그리고 휴식 닫기 버튼 추가"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 안내 문구
        st = wx.StaticText(self, label=lang_res.messages['START_BREAK'], style=wx.ALIGN_CENTER)
        st.SetForegroundColour("black")  # 라벨 폰트 색상을 검정색으로 지정
        main_sizer.Add(st, flag=wx.ALIGN_CENTER | wx.TOP, border=20)
        
        # 남은 시간 표시를 위한 타이머 라벨
        self.break_label = TimerLabel(self, initial_text="00:00", font_increment=10, alignment=wx.ALIGN_CENTER)
        self.break_label.SetForegroundColour("black")  # 타이머 라벨의 폰트 색상을 검정색으로 지정 (필요시)
        main_sizer.Add(self.break_label, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)
        
        # 휴식 닫기 버튼 추가
        self.close_button = wx.Button(self, label="휴식 닫기")
        self.close_button.SetBackgroundColour("#797979")
        main_sizer.Add(self.close_button, flag=wx.ALIGN_CENTER | wx.ALL, border=20)
        
        self.SetSizer(main_sizer)
        
    def init_events(self):
        """이벤트 바인딩: 다이얼로그 종료 시 타이머 정지 처리 및 휴식 닫기 버튼 이벤트 바인딩"""
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.close_button.Bind(wx.EVT_BUTTON, self.on_close_button)
        # ESC 키 이벤트 바인딩 추가
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        
    def on_close(self, event):
        """다이얼로그 종료 시 타이머 정지 및 리소스 정리"""
        if hasattr(self, 'stop_timer_func') and callable(self.stop_timer_func):
            self.stop_timer_func()
        event.Skip()
        
    def on_close_button(self, event):
        """
        휴식 닫기 버튼 클릭 시 호출되는 이벤트 핸들러
        타이머를 정지시키고 휴식 종료 처리 후 다이얼로그를 종료합니다.
        """
        if hasattr(self, 'stop_timer_func') and callable(self.stop_timer_func):
            self.stop_timer_func()
        self.on_break_finish()
        
    def on_key_down(self, event):
        """
        키 입력 이벤트를 처리하는 핸들러입니다.
        ESC 키를 누르면 다이얼로그를 닫습니다.
        """
        keycode = event.GetKeyCode()
        
        if keycode == wx.WXK_ESCAPE:
            # 휴식 닫기 버튼과 동일한 동작 수행
            if hasattr(self, 'stop_timer_func') and callable(self.stop_timer_func):
                self.stop_timer_func()
            self.on_break_finish()
        else:
            event.Skip()  # 다른 키 입력은 기본 처리로 전달
        
    def on_break_finish(self):
        """
        타이머 종료 및 휴식 중 강제 종료 시 호출되는 메서드  
        on_break_end 콜백을 호출하고, 다이얼로그를 종료합니다.
        """
        if not self._destroyed:
            if self.on_break_end:
                wx.CallAfter(self.on_break_end)
            wx.CallAfter(self.EndModal, wx.ID_OK)