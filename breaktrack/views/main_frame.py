# views/main_frame.py
import wx
import os
from breaktrack.views.settings_dialog import SettingsDialog
from breaktrack.views.track_dialog import TrackDialog
from breaktrack.utils import resource_path
from breaktrack.const import (
    APP_TITLE, ASSETS_DIR, ICONS_DIR, ICON_ICO,
    MENU_FILE, MENU_SETTINGS, MENU_VIEW_LOGS, MENU_EXIT,
    BTN_START
)

class MainFrame(wx.Frame):
    def __init__(self, parent, title=APP_TITLE, config_controller=None):
        super().__init__(parent, title=title, size=(300, 200))
        self.config_controller = config_controller

        icon_path = resource_path(os.path.join(ASSETS_DIR, ICONS_DIR, ICON_ICO))
        if os.path.exists(icon_path):
            self.SetIcon(wx.Icon(icon_path))

        self.init_menu()

        # 메인 패널
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 타이머 라벨
        self.timer_label = wx.StaticText(panel, label="00:00", style=wx.ALIGN_CENTER)
        font = self.timer_label.GetFont()
        font.PointSize += 20
        font = font.Bold()
        self.timer_label.SetFont(font)
        vbox.Add(self.timer_label, flag=wx.EXPAND | wx.ALL, border=20)

        # 시작/중지 버튼
        self.start_button = wx.Button(panel, label=BTN_START)
        vbox.Add(self.start_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=20)

        panel.SetSizer(vbox)

    def init_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        settings_item = file_menu.Append(wx.ID_PREFERENCES, f"{MENU_SETTINGS}\tCtrl+S")
        track_item = file_menu.Append(wx.ID_ANY, f"{MENU_VIEW_LOGS}\tCtrl+L")
        exit_item = file_menu.Append(wx.ID_EXIT, f"{MENU_EXIT}\tCtrl+Q")

        menu_bar.Append(file_menu, MENU_FILE)
        self.SetMenuBar(menu_bar)
        self.menu_bar = menu_bar

        # 이벤트 바인딩
        self.Bind(wx.EVT_MENU, self.on_open_settings, settings_item)
        self.Bind(wx.EVT_MENU, self.on_show_track, track_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)

    def on_open_settings(self, event):
        dialog = SettingsDialog(self, self.config_controller)
        if dialog.ShowModal() == wx.ID_OK:
            pass
        dialog.Destroy()

    def on_show_track(self, event):
        dlg = TrackDialog(self, self.config_controller)
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, event):
        self.Close()
