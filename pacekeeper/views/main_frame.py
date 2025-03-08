# views/main_frame.py
import wx
import re  # 추가: 해시태그 검사를 위한 정규식 모듈
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.controllers.main_controller import MainController
from pacekeeper.views.settings_dialog import SettingsDialog
from pacekeeper.views.log_dialog import LogDialog
from pacekeeper.views.category_dialog import CategoryDialog
from pacekeeper.views.break_dialog import BreakDialog
from pacekeeper.views.controls import RecentLogsControl, TimerLabel, TextInputPanel, TagButtonsPanel
from pacekeeper.services.tag_service import TagService
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import (
    APP_TITLE, SET_MAIN_DLG_WIDTH, SET_MAIN_DLG_HEIGHT
)
from icecream import ic
lang_res = load_language_resource(ConfigController().get_language())

class MainFrame(wx.Frame):
    """
    MainFrame: UI View 컴포넌트  
    책임: UI 구성, 레이아웃 초기화, 이벤트 바인딩 및 MainController와의 상호작용
    """
    def __init__(self, parent, config_ctrl: ConfigController):
        width = config_ctrl.get_setting(SET_MAIN_DLG_WIDTH, 800)
        height = config_ctrl.get_setting(SET_MAIN_DLG_HEIGHT, 550)
        super().__init__(parent, title=APP_TITLE, size=(width, height))
        self.config_ctrl = config_ctrl
        self.tag_service = TagService()

        # UI 구성 및 이벤트 바인딩 분리 먼저 호출
        self.init_ui()
        self.init_menu()
        self.init_events()

        # 이후에 MainController 생성
        self.main_controller = MainController(main_frame=self, config_ctrl=self.config_ctrl)

        self.Layout()
        self.Fit()

        self.original_size = self.GetSize()
        self.study_size = (250, 200)

    def hide_main_controls(self):
        """
        학습 타이머 실행 시, recent_logs(리스트 컨트롤), tag_panel(태그 버튼), 
        log_input_panel(텍스트 입력 컨트롤)을 숨기고 창 크기를 작게 만듭니다.
        """
        self.recent_logs.Hide()
        self.tag_panel.Hide()
        self.log_input_panel.Hide()
        self.SetSize(self.study_size)
        self.Layout()

    def restore_main_controls(self):
        """
        쉬는 시간 종료 후, 숨겨진 컨트롤들을 다시 보이고 원래 창 크기로 복원합니다.
        """
        self.recent_logs.Show()
        self.tag_panel.Show()
        self.log_input_panel.Show()
        self.SetSize(self.original_size)
        self.Layout()

    def init_ui(self):
        """UI 컴포넌트 초기화 및 레이아웃 구성"""
        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 타이머 라벨
        self.timer_label = TimerLabel(self.panel, font_increment=20, bold=True, alignment=wx.ALIGN_CENTER)
        self.main_sizer.Add(self.timer_label, flag=wx.EXPAND | wx.ALL, border=15)

        # 최근 기록 표시 영역 (콜백 on_logs_updated 설정)
        self.recent_logs = RecentLogsControl(
            self.panel, self.config_ctrl, 
            on_double_click=self.on_log_double_click,
            on_logs_updated=self.update_tag_buttons
        )
        self.main_sizer.Add(self.recent_logs, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        
        # 태그 버튼 패널
        self.tag_panel = TagButtonsPanel(self.panel, on_tag_selected=self.add_tag_to_input)
        self.main_sizer.Add(self.tag_panel, flag=wx.EXPAND | wx.ALL, border=10)
        # RecentLogsControl의 update_logs 호출 시 update_tag_buttons()가 자동 호출됩니다.
        
        # 텍스트 입력 패널 (예: 할일 입력)
        self.log_input_panel = TextInputPanel(self.panel)
        # 텍스트가 변경될 때마다 해시태그 포함 여부를 체크해 start button 활성화를 업데이트합니다.
        self.log_input_panel.Bind(wx.EVT_TEXT, self.on_log_input_text_change)
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
            font.PointSize += 2
            btn.SetFont(font)
            
        self.pause_button.Disable()

        button_sizer.Add(self.start_button, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=5)
        button_sizer.Add(self.pause_button, proportion=1, flag=wx.EXPAND | wx.LEFT, border=5)
        self.button_panel.SetSizer(button_sizer)
        self.main_sizer.Add(self.button_panel, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=20)

        self.panel.SetSizer(self.main_sizer)
        
        self.update_tag_buttons()
        self.update_start_button_state()

    def init_menu(self):
        """메뉴바 초기화 및 메뉴 아이템 생성"""
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        self.settings_item = file_menu.Append(wx.ID_PREFERENCES, f"{lang_res.base_labels['SETTINGS']}\tCtrl+S")
        self.track_item = file_menu.Append(wx.ID_ANY, f"{lang_res.base_labels['LOGS']}\tCtrl+L")
        self.category_item = file_menu.Append(wx.ID_ANY, f"{lang_res.base_labels['CATEGORY']}\tCtrl+C")
        self.exit_item = file_menu.Append(wx.ID_EXIT, f"{lang_res.base_labels['EXIT']}\tCtrl+Q")
        menu_bar.Append(file_menu, lang_res.base_labels['FILE'])
        self.SetMenuBar(menu_bar)

    def init_events(self):
        """이벤트 바인딩"""
        self.Bind(wx.EVT_CLOSE, self.on_close)  # 창 닫기 이벤트 바인딩 추가
        self.Bind(wx.EVT_MENU, self.on_open_settings, self.settings_item)
        self.Bind(wx.EVT_MENU, self.on_show_track, self.track_item)
        self.Bind(wx.EVT_MENU, self.on_show_category, self.category_item)
        self.Bind(wx.EVT_MENU, self.on_exit, self.exit_item)
        self.start_button.Bind(wx.EVT_BUTTON, self.on_toggle_timer)
        self.pause_button.Bind(wx.EVT_BUTTON, self.on_pause)
        
    def update_tag_buttons(self):
        """
        최근 로그에서 태그를 추출하여 TagButtonsPanel을 업데이트합니다.
        """
        # tag_panel이 아직 설정되지 않았으면 아무런 작업도 수행하지 않습니다.
        if not hasattr(self, "tag_panel"):
            return

        tags = self.tag_service.get_tags()
        ic("update_tag_buttons", tags)
        
        self.tag_panel.update_tags(tags)

    def on_log_double_click(self, event):
        """최근 로그 리스트의 항목을 더블 클릭했을 때, 해당 로그 메시지를 log_input_panel에 복사"""
        index = event.GetIndex()
        message = self.recent_logs.list_ctrl.GetItemText(index, 1)
        self.log_input_panel.set_value(message)
        event.Skip() 

    def on_open_settings(self, event):
        """설정 다이얼로그 오픈"""
        dlg = SettingsDialog(self, self.config_ctrl)
        if dlg.ShowModal() == wx.ID_OK:
            pass
        dlg.Destroy()

    def on_show_track(self, event):
        """로그 다이얼로그 오픈"""
        dlg = LogDialog(self, self.config_ctrl)
        dlg.ShowModal()
        dlg.Destroy()
        
    def on_show_category(self, event):
        """카테고리 다이얼로그 오픈"""
        dlg = CategoryDialog(self, self.config_ctrl)
        dlg.ShowModal()
        dlg.Destroy()
        # After closing the CategoryDialog, update tag buttons to reflect updated category id and color
        self.update_tag_buttons()

    def on_exit(self, event):
        """앱 종료 처리"""
        self.Close()

    def on_toggle_timer(self, event):
        """
        타이머 시작/중단 토글 이벤트 핸들러
        study timer 시작 시 주요 컨트롤(최근 로그, 태그 버튼, 텍스트 입력)을 숨기고 창 크기를 축소합니다.
        """
        if not self.main_controller.timer_service.is_running():
            # 타이머가 실행 중이 아니면 학습 세션 시작 전에 해시태그 검증 (추가 검증 가능)
            self.start_button.SetLabel(lang_res.button_labels.get('STOP', "STOP"))
            self.pause_button.Enable()
            self.main_controller.start_study_session()
            self.hide_main_controls()  # 컨트롤 숨기기 및 작은 창으로 전환
        else:
            # 타이머가 실행 중이면 강제 종료 처리 및 UI 복원
            self.main_controller.stop_study_timer()
            self.start_button.SetLabel(lang_res.button_labels.get('START', "START"))
            self.pause_button.Disable()
            self.timer_label.SetLabel("00:00")
            self.restore_main_controls()  # 원래 UI 복원

        self.update_start_button_state()

    def on_pause(self, event):
        """
        타이머 일시정지/재개 이벤트 핸들러
        수정: MainController의 토글 메서드를 활용하고, timer_service의 상태로 버튼 라벨 변경
        """
        self.main_controller.toggle_pause()
        if self.main_controller.timer_service.is_paused():
            self.pause_button.SetLabel(lang_res.button_labels.get('RESUME', "RESUME"))
        else:
            self.pause_button.SetLabel(lang_res.button_labels.get('PAUSE', "PAUSE"))
        
    def add_tag_to_input(self, tag):
        current = self.log_input_panel.get_value()
        new_text = f"{current} #{tag.name}" if tag else ""
        self.log_input_panel.set_value(new_text.strip())
        
        self.update_start_button_state()

    def update_timer_label(self, time_str: str):
        """타이머 라벨 업데이트 (Controller에서 호출)
        
           메인 타이머 라벨(self.timer_label)과, 휴식 다이얼로그가 열려 있다면 그 안의 
           타이머 라벨(self.break_label) 모두 업데이트합니다.
        """
        self.timer_label.SetLabel(time_str)
        if hasattr(self, "break_dialog") and self.break_dialog is not None:
            if hasattr(self.break_dialog, "break_label"):
                self.break_dialog.break_label.SetLabel(time_str)

    def show_break_dialog(self, break_min):
        def on_break_end():
            # 쉬는 시간 종료 후 UI 초기화
            self.start_button.SetLabel(lang_res.button_labels.get('START', "START"))
            self.pause_button.Disable()
            self.log_input_panel.set_value("")
            self.update_start_button_state()
            self.restore_main_controls() 
            self.update_tag_buttons()

        self.break_dialog = BreakDialog(
            self, 
            self.main_controller, 
            self.config_ctrl, 
            break_minutes=break_min, 
            on_break_end=on_break_end
        )
        original_update_callback = self.main_controller.timer_service.update_callback

        def break_update(time_str):
            if self.break_dialog and hasattr(self.break_dialog, "break_label"):
                self.break_dialog.break_label.SetLabel(time_str)
        self.main_controller.timer_service.update_callback = break_update

        self.break_dialog.ShowModal()
        self.main_controller.timer_service.update_callback = original_update_callback
        self.break_dialog.Destroy()
        self.break_dialog = None

    def on_close(self, event):
        """창 닫기 시 타이머 스레드 정리 및 앱 종료"""
        # 타이머 서비스 중지 및 리소스 정리
        self.main_controller.cleanup()
        
        # 앱 종료를 위해 프레임 파괴 및 메인 루프 종료
        self.Destroy()
        wx.CallAfter(wx.GetApp().ExitMainLoop)

    # 추가: TextInputPanel의 텍스트 변경 이벤트 핸들러
    def on_log_input_text_change(self, event):
        self.update_start_button_state()
        event.Skip()
    
    def update_start_button_state(self):
        # 세션 중이면 start_button은 항상 활성화 (STOP용)
        if hasattr(self, "main_controller") and self.main_controller.timer_service.is_running():
            self.start_button.Enable()
            return

        text = self.log_input_panel.get_value() or ""
        # 해시태그 패턴: '#' 뒤에 하나 이상의 알파벳, 숫자, 언더스코어가 오는 경우
        if re.search(r'#\w+', text):
            self.start_button.Enable()
        else:
            self.start_button.Disable() 