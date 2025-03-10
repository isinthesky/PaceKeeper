import wx
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.controllers.main_controller import MainController
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import SET_PADDING_SIZE, SET_BREAK_COLOR
from pacekeeper.views.controls import TimerLabel, RoundButton, RoundPanel
from pacekeeper.consts.styles import *

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
        
        # 추가: config에 저장된 SET_BREAK_COLOR 값으로 배경색 설정 (기본값 파스텔 핑크)
        bg_color = self.config.get_setting(SET_BREAK_COLOR, PASTEL_PINK_LIGHT)
        self.SetBackgroundColour(bg_color)
        
        # 타이머 정지를 위한 함수 지정
        self.stop_timer_func = self.main_controller.timer_service.stop
        
        self.init_ui()
        self.init_events()
        self.CenterOnScreen()
        
    def init_ui(self):
        """UI 컴포넌트 초기화 및 레이아웃 구성"""
        # 테마에 따라 일반 Panel 또는 RoundPanel 사용
        if USE_ROUND_CORNERS:
            main_panel = RoundPanel(self, bg_color=PASTEL_PINK_LIGHT)
        else:
            main_panel = wx.Panel(self)
            main_panel.SetBackgroundColour(PASTEL_PINK_LIGHT)
            
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 안내 문구
        message = lang_res.messages['BREAK_MESSAGE'].format(minutes=self.break_minutes)
        st = wx.StaticText(main_panel, label=message)
        st.SetForegroundColour(TEXT_COLOR)
        font = st.GetFont()
        font.PointSize += 2
        font = font.Bold()
        st.SetFont(font)
        
        # 타이머 라벨
        self.timer_label = TimerLabel(main_panel, initial_text="00:00", font_increment=10, alignment=wx.ALIGN_CENTER)
        self.timer_label.SetForegroundColour(TEXT_COLOR)
        
        # 휴식 닫기 버튼
        if USE_ROUND_CORNERS:
            self.close_button = RoundButton(
                main_panel, 
                label=lang_res.button_labels.get('CLOSE_BREAK', "휴식 닫기"),
                bg_color=BUTTON_BACKGROUND,
                hover_color=BUTTON_HOVER,
                text_color=TEXT_COLOR,
                border_color=BUTTON_BORDER
            )
        else:
            self.close_button = wx.Button(
                main_panel, 
                label=lang_res.button_labels.get('CLOSE_BREAK', "휴식 닫기")
            )
        
        # 레이아웃 구성
        main_sizer.Add(st, flag=wx.ALIGN_CENTER | wx.TOP, border=20)
        main_sizer.Add(self.timer_label, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)
        main_sizer.Add(self.close_button, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=20)
        
        main_panel.SetSizer(main_sizer)
        
        # 전체 레이아웃
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        dialog_sizer.Add(main_panel, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(dialog_sizer)
        
    def init_events(self):
        """이벤트 핸들러 초기화"""
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.close_button.Bind(wx.EVT_BUTTON, self.on_close_button)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
    def on_close(self, event):
        """다이얼로그 닫기 이벤트 처리"""
        self._destroyed = True
        self.stop_timer_func()
        event.Skip()
        
    def on_close_button(self, event):
        """휴식 닫기 버튼 클릭 이벤트 처리"""
        self._destroyed = True
        self.stop_timer_func()
        
        # 콜백 함수가 있으면 실행
        if self.on_break_end:
            self.on_break_end()
            
        self.EndModal(wx.ID_OK)
        
    def on_key_down(self, event):
        """키 입력 이벤트 처리 (ESC 키로 닫기)"""
        key_code = event.GetKeyCode()
        
        # ESC 키 처리
        if key_code == wx.WXK_ESCAPE:
            self._destroyed = True
            self.stop_timer_func()
            
            # 콜백 함수가 있으면 실행
            if self.on_break_end:
                self.on_break_end()
                
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()
            
    def on_break_finish(self):
        """휴식 시간 종료 처리"""
        if not self._destroyed:
            self._destroyed = True
            
            # 콜백 함수가 있으면 실행
            if self.on_break_end:
                self.on_break_end()
                
            self.EndModal(wx.ID_OK)
            
    def update_timer(self, time_str):
        """타이머 라벨 업데이트"""
        if not self._destroyed and self.timer_label:
            self.timer_label.SetLabel(time_str)