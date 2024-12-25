# views/settings_dialog.py
import wx
from breaktrack.const import (
    MENU_SETTINGS, BTN_SAVE, BTN_CANCEL,
    SETTINGS_LABEL_STUDY_TIME, SETTINGS_LABEL_SHORT_BREAK, SETTINGS_LABEL_LONG_BREAK, SETTINGS_LABEL_CYCLES, SETTINGS_STUDY_TIME, SETTINGS_SHORT_BREAK, SETTINGS_LONG_BREAK, SETTINGS_CYCLES)

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, config_controller):
        super().__init__(parent, title=MENU_SETTINGS, size=(350, 300),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        self.config = config_controller
        self.InitUI()
        self.Center()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # study_time
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.StaticText(panel, label=SETTINGS_LABEL_STUDY_TIME), flag=wx.RIGHT, border=8)
        self.study_time = wx.SpinCtrl(
            panel, value=str(self.config.get_setting(SETTINGS_STUDY_TIME, 25)),
            min=1, max=120
        )
        hbox1.Add(self.study_time, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND | wx.ALL, border=10)

        # short_break
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(wx.StaticText(panel, label=SETTINGS_LABEL_SHORT_BREAK), flag=wx.RIGHT, border=8)
        self.short_break = wx.SpinCtrl(
            panel, value=str(self.config.get_setting(SETTINGS_SHORT_BREAK, 5)),
            min=1, max=60
        )
        hbox2.Add(self.short_break, proportion=1)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.ALL, border=10)

        # long_break
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(wx.StaticText(panel, label=SETTINGS_LABEL_LONG_BREAK), flag=wx.RIGHT, border=8)
        self.long_break = wx.SpinCtrl(
            panel, value=str(self.config.get_setting(SETTINGS_LONG_BREAK, 15)),
            min=1, max=120
        )
        hbox3.Add(self.long_break, proportion=1)
        vbox.Add(hbox3, flag=wx.EXPAND | wx.ALL, border=10)

        # cycles
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(wx.StaticText(panel, label=SETTINGS_LABEL_CYCLES), flag=wx.RIGHT, border=8)
        self.cycles = wx.SpinCtrl(
            panel, value=str(self.config.get_setting(SETTINGS_CYCLES, 4)),
            min=1, max=20
        )
        hbox4.Add(self.cycles, proportion=1)
        vbox.Add(hbox4, flag=wx.EXPAND | wx.ALL, border=10)

        # 버튼
        hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, wx.ID_OK, label=BTN_SAVE)
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, label=BTN_CANCEL)
        hbox_btn.Add(btn_ok)
        hbox_btn.Add(btn_cancel, flag=wx.LEFT, border=10)
        vbox.Add(hbox_btn, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        panel.SetSizer(vbox)

        # 이벤트
        btn_ok.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event):
        new_settings = {
            SETTINGS_STUDY_TIME: self.study_time.GetValue(),
            SETTINGS_SHORT_BREAK: self.short_break.GetValue(),
            SETTINGS_LONG_BREAK: self.long_break.GetValue(),
            SETTINGS_CYCLES: self.cycles.GetValue()
        }
        self.config.update_settings(new_settings)
        self.EndModal(wx.ID_OK)
