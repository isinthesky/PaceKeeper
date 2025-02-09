# views/settings_dialog.py
import wx
from pacekeeper.consts.settings import (
    SET_STUDY_TIME,
    SET_SHORT_BREAK,
    SET_LONG_BREAK,
    SET_CYCLES,
    SET_SOUND_VOLUME
)

from pacekeeper.consts.labels import load_language_resource

lang_res = load_language_resource()

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, config_controller):
        super().__init__(parent, title=lang_res.base_labels['SETTINGS'], size=(350, 350),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        self.config = config_controller
        self.InitUI()
        self.Center()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # study_time
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.StaticText(panel, label=lang_res.messages['STUDY_TIME']), flag=wx.RIGHT, border=8)
        self.study_time = wx.SpinCtrl(
            panel, value=str(self.config.get_setting(SET_STUDY_TIME, 25)),
            min=1, max=120
        )
        hbox1.Add(self.study_time, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND | wx.ALL, border=10)

        # short_break
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(wx.StaticText(panel, label=lang_res.messages['SHORT_BREAK']), flag=wx.RIGHT, border=8)
        self.short_break = wx.SpinCtrl(
            panel, value=str(self.config.get_setting(SET_SHORT_BREAK, 5)),
            min=1, max=60
        )
        hbox2.Add(self.short_break, proportion=1)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.ALL, border=10)

        # long_break
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(wx.StaticText(panel, label=lang_res.messages['LONG_BREAK']), flag=wx.RIGHT, border=8)
        self.long_break = wx.SpinCtrl(
            panel, value=str(self.config.get_setting(SET_LONG_BREAK, 15)),
            min=1, max=120
        )
        hbox3.Add(self.long_break, proportion=1)
        vbox.Add(hbox3, flag=wx.EXPAND | wx.ALL, border=10)

        # cycles
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(wx.StaticText(panel, label=lang_res.messages['CYCLES']), flag=wx.RIGHT, border=8)
        self.cycles = wx.SpinCtrl(
            panel, value=str(self.config.get_setting(SET_CYCLES, 4)),
            min=1, max=20
        )
        hbox4.Add(self.cycles, proportion=1)
        vbox.Add(hbox4, flag=wx.EXPAND | wx.ALL, border=10)

        # --- break_sound_volume ---
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        volume_label = wx.StaticText(panel, label=lang_res.messages['SOUND_VOLUME'])
        hbox5.Add(volume_label, flag=wx.RIGHT, border=8)
        current_volume = self.config.get_setting(SET_SOUND_VOLUME, 50)  # 기본값 50
        self.break_sound_volume_slider = wx.Slider(
            panel, value=current_volume, minValue=0, maxValue=100,
            style=wx.SL_HORIZONTAL | wx.SL_LABELS
        )
        hbox5.Add(self.break_sound_volume_slider, proportion=1)
        vbox.Add(hbox5, flag=wx.EXPAND | wx.ALL, border=10) 
        
        # 버튼
        hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, wx.ID_OK, label=lang_res.button_labels['SAVE'])
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, label=lang_res.button_labels['CANCEL'])
        hbox_btn.Add(btn_ok)
        hbox_btn.Add(btn_cancel, flag=wx.LEFT, border=10)
        vbox.Add(hbox_btn, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        panel.SetSizer(vbox)

        # 이벤트
        btn_ok.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event):
        new_settings = {
            SET_STUDY_TIME: self.study_time.GetValue(),
            SET_SHORT_BREAK: self.short_break.GetValue(),
            SET_LONG_BREAK: self.long_break.GetValue(),
            SET_CYCLES: self.cycles.GetValue(),
            SET_SOUND_VOLUME: self.break_sound_volume_slider.GetValue()
        }
        self.config.update_settings(new_settings)
        self.EndModal(wx.ID_OK)
