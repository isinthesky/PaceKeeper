# views/main_frame.py
import wx
import os
from pacekeeper.controllers.config_controller import ConfigController, AppStatus
from pacekeeper.controllers.main_controller import MainController
from pacekeeper.views.settings_dialog import SettingsDialog
from pacekeeper.views.log_dialog import LogDialog
from pacekeeper.views.break_dialog import BreakDialog
from pacekeeper.utils import resource_path
from pacekeeper.consts.settings import (
    APP_TITLE, ASSETS_DIR, ICONS_DIR, ICON_ICO,
    SET_MAIN_DLG_WIDTH, SET_MAIN_DLG_HEIGHT, SET_STUDY_TIME
)
from pacekeeper.views.controls import RecentLogsControl, TimerLabel, TextInputPanel
from pacekeeper.consts.labels import load_language_resource

lang_res = load_language_resource()

class MainFrame(wx.Frame):
    def __init__(
        self, 
        parent, 
        config_ctrl: ConfigController
    ):
        super().__init__(parent, 
                         title=APP_TITLE, 
                         size=(config_ctrl.get_setting(SET_MAIN_DLG_WIDTH, 800), 
                               config_ctrl.get_setting(SET_MAIN_DLG_HEIGHT, 400)))
        
        self.config_ctrl = config_ctrl
        self.main_ctrl = MainController(self, self.config_ctrl)
        
        icon_path = resource_path(os.path.join(ASSETS_DIR, ICONS_DIR, ICON_ICO))
        
        if os.path.exists(icon_path):
            self.SetIcon(wx.Icon(icon_path))

        self.init_menu()

        # 메인 패널
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 타이머 라벨
        self.timer_label = TimerLabel(panel, font_increment=20, bold=True, alignment=wx.ALIGN_LEFT)
        vbox.Add(self.timer_label, flag=wx.EXPAND | wx.ALL, border=20)

        # 최근 기록 표시 영역 추가
        recent_logs_sizer = RecentLogsControl(panel, self.config_ctrl)
        vbox.Add(recent_logs_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # 사용자 입력창 (TextCtrl)
        self.log_input = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        
        box = wx.StaticBox(panel, label="할일 입력")
        box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        box_sizer.Add(self.log_input, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
        vbox.Add(box_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        
        # 시작/중지 버튼
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.start_button = wx.Button(panel, label=lang_res.button_labels['START'])
        font_btn = self.start_button.GetFont()
        font_btn.PointSize += 3
        self.start_button.SetFont(font_btn)
        
        self.pause_button = wx.Button(panel, label=lang_res.button_labels['PAUSE'])
        font_btn = self.pause_button.GetFont()
        font_btn.PointSize += 3
        self.pause_button.SetFont(font_btn)
        self.pause_button.Disable()
        
        button_sizer.Add(self.start_button, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=15)
        button_sizer.Add(self.pause_button, proportion=1, flag=wx.EXPAND | wx.LEFT, border=15)
        
        vbox.Add(button_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=20)

        panel.SetSizer(vbox)
        
        frame_sizer = wx.BoxSizer()
        frame_sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizerAndFit(frame_sizer)

    def init_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        settings_item = file_menu.Append(wx.ID_PREFERENCES, f"{lang_res.base_labels['SETTINGS']}\tCtrl+S")
        track_item = file_menu.Append(wx.ID_ANY, f"{lang_res.base_labels['LOGS']}\tCtrl+L")
        exit_item = file_menu.Append(wx.ID_EXIT, f"{lang_res.base_labels['EXIT']}\tCtrl+Q")

        menu_bar.Append(file_menu, lang_res.base_labels['FILE'])
        self.SetMenuBar(menu_bar)
        self.menu_bar = menu_bar

        # 이벤트 바인딩
        self.Bind(wx.EVT_MENU, self.on_open_settings, settings_item)
        self.Bind(wx.EVT_MENU, self.on_show_track, track_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        

    def on_open_settings(self, event):
        dialog = SettingsDialog(self, self.config_ctrl)
        if dialog.ShowModal() == wx.ID_OK:
            pass
        dialog.Destroy()

    def on_show_track(self, event):
        dlg = LogDialog(self, self.config_ctrl)
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, event):
        self.Close()

    def start_study_timer(self):
        """스터디 타이머 시작 로직"""
        study_minutes = self.config_ctrl.get_setting(SET_STUDY_TIME, 25)
        self.start_button.Disable()
                    
        self.main_ctrl.start_study_countdown(study_minutes*60)

    def show_break_dialog(self):
        """휴식 다이얼로그 표시 및 콜백 설정"""
        break_dlg = BreakDialog(
            self,
            config_ctrl=self.config_ctrl,
            on_break_end=lambda manual_submit=False: self.on_break_finished(manual_submit)
        )
        break_dlg.ShowModal()
        break_dlg.Destroy()

    def on_break_finished(self, manual_submit=False):
        """휴식 종료 후 처리"""
        if not manual_submit:
            self.start_study_timer()  # 자동 종료 시에만 스터디 타이머 재개
