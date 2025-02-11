# views/main_frame.py
import wx
import os
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.controllers.main_controller import MainController
from pacekeeper.views.settings_dialog import SettingsDialog
from pacekeeper.views.log_dialog import LogDialog
from pacekeeper.views.break_dialog import BreakDialog
from pacekeeper.views.controls import RecentLogsControl, TimerLabel, TextInputPanel
from pacekeeper.utils import resource_path
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import (
    APP_TITLE, ASSETS_DIR, ICONS_DIR, ICON_ICO,
    SET_MAIN_DLG_WIDTH, SET_MAIN_DLG_HEIGHT
)

lang_res = load_language_resource()

class MainFrame(wx.Frame):
    """
    MainFrame: UI View 컴포넌트  
    책임: UI 구성, 레이아웃 초기화, 이벤트 바인딩 및 MainController와의 상호작용
    """
    def __init__(self, parent, config_ctrl: ConfigController):
        width = config_ctrl.get_setting(SET_MAIN_DLG_WIDTH, 800)
        height = config_ctrl.get_setting(SET_MAIN_DLG_HEIGHT, 400)
        super().__init__(parent, title=APP_TITLE, size=(width, height))
        self.config_ctrl = config_ctrl

        # 의존성 주입: MainController 생성
        self.main_controller = MainController(main_frame=self, config_ctrl=self.config_ctrl)
        
        self.timer_running = False
        self.timer_paused = False

        # 아이콘 설정
        icon_path = resource_path(os.path.join(ASSETS_DIR, ICONS_DIR, ICON_ICO))
        if os.path.exists(icon_path):
            self.SetIcon(wx.Icon(icon_path))
        
        # UI 구성 및 이벤트 바인딩 분리
        self.init_ui()
        self.init_menu()
        self.init_events()

        self.Layout()
        self.Fit()

    def init_ui(self):
        """UI 컴포넌트 초기화 및 레이아웃 구성"""
        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 타이머 라벨
        self.timer_label = TimerLabel(self.panel, font_increment=20, bold=True, alignment=wx.ALIGN_LEFT)
        self.main_sizer.Add(self.timer_label, flag=wx.EXPAND | wx.ALL, border=20)

        # 최근 기록 표시 영역
        self.recent_logs = RecentLogsControl(self.panel, self.config_ctrl)
        self.main_sizer.Add(self.recent_logs, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # 텍스트 입력 패널 (예: 할일 입력)
        self.log_input_panel = TextInputPanel(self.panel, box_label="할일 입력")
        self.main_sizer.Add(self.log_input_panel, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # 시작/중지 버튼 패널
        self.button_panel = wx.Panel(self.panel)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 시작 버튼 (토글 버튼으로 Start/Stop 기능 수행)
        self.start_button = wx.Button(self.button_panel, label=lang_res.button_labels.get('START', "START"))
        # 일시정지 버튼
        self.pause_button = wx.Button(self.button_panel, label=lang_res.button_labels.get('PAUSE', "PAUSE"))
        
        # 버튼 폰트 조정
        for btn in (self.start_button, self.pause_button):
            font = btn.GetFont()
            font.PointSize += 3
            btn.SetFont(font)
            
        self.pause_button.Disable()

        button_sizer.Add(self.start_button, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=15)
        button_sizer.Add(self.pause_button, proportion=1, flag=wx.EXPAND | wx.LEFT, border=15)
        self.button_panel.SetSizer(button_sizer)
        self.main_sizer.Add(self.button_panel, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=20)

        self.panel.SetSizer(self.main_sizer)

    def init_menu(self):
        """메뉴바 초기화 및 메뉴 아이템 생성"""
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        self.settings_item = file_menu.Append(wx.ID_PREFERENCES, f"{lang_res.base_labels['SETTINGS']}\tCtrl+S")
        self.track_item = file_menu.Append(wx.ID_ANY, f"{lang_res.base_labels['LOGS']}\tCtrl+L")
        self.exit_item = file_menu.Append(wx.ID_EXIT, f"{lang_res.base_labels['EXIT']}\tCtrl+Q")
        menu_bar.Append(file_menu, lang_res.base_labels['FILE'])
        self.SetMenuBar(menu_bar)

    def init_events(self):
        """이벤트 바인딩"""
        self.Bind(wx.EVT_CLOSE, self.on_close)  # 창 닫기 이벤트 바인딩 추가
        self.Bind(wx.EVT_MENU, self.on_open_settings, self.settings_item)
        self.Bind(wx.EVT_MENU, self.on_show_track, self.track_item)
        self.Bind(wx.EVT_MENU, self.on_exit, self.exit_item)
        self.start_button.Bind(wx.EVT_BUTTON, self.on_toggle_timer)
        self.pause_button.Bind(wx.EVT_BUTTON, self.on_pause)
        # 텍스트 입력 엔터키 이벤트 (필요시)
        self.log_input_panel.input_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter)

    def on_open_settings(self, event):
        """설정 다이얼로그 오픈"""
        dlg = SettingsDialog(self, self.config_ctrl)
        if dlg.ShowModal() == wx.ID_OK:
            # 설정 변경 후 필요한 업데이트 처리
            pass
        dlg.Destroy()

    def on_show_track(self, event):
        """로그 다이얼로그 오픈"""
        dlg = LogDialog(self, self.config_ctrl)
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, event):
        """앱 종료 처리"""
        self.Close()

    def on_toggle_timer(self, event):
        """타이머 시작/중단 토글 이벤트 핸들러"""
        if not self.timer_running:
            # 타이머 시작
            self.timer_running = True
            self.start_button.SetLabel(lang_res.button_labels.get('STOP', "STOP"))
            self.pause_button.Enable()
            self.main_controller.start_study_timer()
        else:
            # 타이머 중단
            self.timer_running = False
            self.start_button.SetLabel(lang_res.button_labels.get('START', "START"))
            self.pause_button.Disable()
            self.main_controller.stop_study_timer()
            # 타이머 중단 시 타이머 라벨 초기화 (원하는 값으로 수정 가능)
            self.timer_label.SetLabel("00:00")

    def on_pause(self, event):
        """타이머 일시정지/재개 이벤트 핸들러"""
        self.main_controller.toggle_pause()
        self.timer_paused = not self.timer_paused  # 상태 토글
        
        # 버튼 라벨 동적 변경
        if self.timer_paused:
            self.pause_button.SetLabel(lang_res.button_labels.get('RESUME', "RESUME"))
        else:
            self.pause_button.SetLabel(lang_res.button_labels.get('PAUSE', "PAUSE"))
        

    def on_text_enter(self, event):
        """사용자 입력 텍스트 처리"""
        text = self.log_input_panel.get_value()
        # 입력값 처리 로직 구현 (예: 로그 저장, 태그 처리 등)
        self.log_input_panel.set_value("")
        event.Skip()

    def update_timer_label(self, time_str: str):
        """타이머 라벨 업데이트 (Controller에서 호출)"""
        self.timer_label.SetLabel(time_str)

    def show_break_dialog(self, break_min):
        """휴식 다이얼로그 표시 (Controller에서 호출)"""
        dlg = BreakDialog(self, self.config_ctrl, break_minutes=break_min)
        dlg.ShowModal()
        dlg.Destroy()

    def on_close(self, event):
        """창 닫기 시 타이머 스레드 정리"""
        self.main_controller.timer_service.stop()
        event.Skip()  # 정상 종료 처리