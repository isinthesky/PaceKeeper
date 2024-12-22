# views/main_frame.py
import wx
import os
from breaktrack.views.settings_dialog import SettingsDialog
from breaktrack.views.track_dialog import TrackDialog
from breaktrack.utils import resource_path

class MainFrame(wx.Frame):
    def __init__(self, parent, title, config_controller):
        super().__init__(parent, title=title, size=(300, 200))
        self.config_controller = config_controller

        # 아이콘 설정 (있다면)
        icon_path = resource_path(os.path.join("assets", "icons", "app.ico"))
        if os.path.exists(icon_path):
            self.SetIcon(wx.Icon(icon_path))

        # 메뉴 초기화
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
        self.start_button = wx.Button(panel, label="시작")
        vbox.Add(self.start_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=20)

        panel.SetSizer(vbox)

    def init_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        settings_item = file_menu.Append(wx.ID_PREFERENCES, "설정\tCtrl+S")
        track_item = file_menu.Append(wx.ID_ANY, "기록 보기\tCtrl+L")
        exit_item = file_menu.Append(wx.ID_EXIT, "종료\tCtrl+Q")

        menu_bar.Append(file_menu, "파일")
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