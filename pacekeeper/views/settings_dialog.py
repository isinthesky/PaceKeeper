# views/settings_dialog.py
import wx
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import (
    SET_STUDY_TIME,
    SET_SHORT_BREAK,
    SET_LONG_BREAK,
    SET_CYCLES,
    SET_SOUND_VOLUME,
    SET_BREAK_COLOR,
    SET_LANGUAGE
)

lang_res = load_language_resource(ConfigController().get_language())

class ColorOptionPanel(wx.Panel):
    """
    색상 팔레트의 각각의 옵션을 나타내는 커스텀 패널입니다.
    선택된 상태라면 진한 검은색 보더가 그려집니다.
    """
    def __init__(self, parent, color, on_select_callback, size=(40, 40)):
        super().__init__(parent, size=size)
        self.color = color
        self.selected = False
        self.on_select_callback = on_select_callback
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        rect = self.GetClientRect()
        # 배경을 옵션 색상으로 채웁니다.
        dc.SetBrush(wx.Brush(self.color))
        dc.SetPen(wx.Pen(self.color))
        dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)
        # 만약 선택된 상태라면 진한 보더를 그립니다.
        if self.selected:
            dc.SetPen(wx.Pen("black", 3))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)

    def OnClick(self, event):
        if self.on_select_callback:
            self.on_select_callback(self)
        event.Skip()


class SettingsDialog(wx.Dialog):
    def __init__(self, parent, config_controller):
        super().__init__(parent, title=lang_res.base_labels['SETTINGS'], size=(350, 430),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        self.config = config_controller
        self.InitUI()
        self.Center()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 고정 크기를 설정할 변수 (픽셀 단위)
        label_width = 110  # 레이블의 고정 너비 (필요에 따라 조정)
        ctrl_width = 200   # 선택 리스트, 슬라이더 등 컨트롤의 고정 너비 (필요에 따라 조정)

        # 작업 시간: 드롭다운 리스트 (15분, 25분, 30분, 45분, 60분)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        study_label = wx.StaticText(panel, label=lang_res.messages['STUDY_TIME'])
        study_label.SetMinSize((label_width, -1))
        hbox1.Add(study_label, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=8)
        self.study_time_choices = ["15", "25", "30", "45", "1"]
        display_study_time = [f"{choice}분" for choice in self.study_time_choices]
        self.study_time = wx.Choice(panel, choices=display_study_time)
        self.study_time.SetMinSize((ctrl_width, -1))
        default_study_time = self.config.get_setting(SET_STUDY_TIME, 25)
        if str(default_study_time) in self.study_time_choices:
            default_index = self.study_time_choices.index(str(default_study_time))
        else:
            default_index = self.study_time_choices.index("25")
        self.study_time.SetSelection(default_index)
        hbox1.Add(self.study_time, flag=wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox1, flag=wx.EXPAND | wx.ALL, border=10)

        # 짧은 휴식 시간: 드롭다운 리스트 (3분, 5분, 7분, 10분)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        short_break_label = wx.StaticText(panel, label=lang_res.messages['SHORT_BREAK'])
        short_break_label.SetMinSize((label_width, -1))
        hbox2.Add(short_break_label, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=8)
        self.short_break_choices = ["3", "5", "7", "1"]
        display_short_break = [f"{choice}분" for choice in self.short_break_choices]
        self.short_break = wx.Choice(panel, choices=display_short_break)
        self.short_break.SetMinSize((ctrl_width, -1))
        default_short_break = self.config.get_setting(SET_SHORT_BREAK, 5)
        if str(default_short_break) in self.short_break_choices:
            default_index = self.short_break_choices.index(str(default_short_break))
        else:
            default_index = self.short_break_choices.index("5")
        self.short_break.SetSelection(default_index)
        hbox2.Add(self.short_break, flag=wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.ALL, border=10)

        # 긴 휴식 시간: 드롭다운 리스트 (10분, 15분, 20분, 30분)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        long_break_label = wx.StaticText(panel, label=lang_res.messages['LONG_BREAK'])
        long_break_label.SetMinSize((label_width, -1))
        hbox3.Add(long_break_label, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=8)
        self.long_break_choices = ["10", "15", "20", "30"]
        display_long_break = [f"{choice}분" for choice in self.long_break_choices]
        self.long_break = wx.Choice(panel, choices=display_long_break)
        self.long_break.SetMinSize((ctrl_width, -1))
        default_long_break = self.config.get_setting(SET_LONG_BREAK, 15)
        if str(default_long_break) in self.long_break_choices:
            default_index = self.long_break_choices.index(str(default_long_break))
        else:
            default_index = self.long_break_choices.index("15")
        self.long_break.SetSelection(default_index)
        hbox3.Add(self.long_break, flag=wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox3, flag=wx.EXPAND | wx.ALL, border=10)

        # 작업 반복 횟수: 드롭다운 리스트 (2회, 4회, 6회, 8회)
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        cycles_label = wx.StaticText(panel, label=lang_res.messages['CYCLES'])
        cycles_label.SetMinSize((label_width, -1))
        hbox4.Add(cycles_label, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=8)
        self.cycles_choices = ["2", "4", "6", "8"]
        display_cycles = [f"{choice}회" for choice in self.cycles_choices]
        self.cycles = wx.Choice(panel, choices=display_cycles)
        self.cycles.SetMinSize((ctrl_width, -1))
        default_cycles = self.config.get_setting(SET_CYCLES, 4)
        if str(default_cycles) in self.cycles_choices:
            default_index = self.cycles_choices.index(str(default_cycles))
        else:
            default_index = self.cycles_choices.index("4")
        self.cycles.SetSelection(default_index)
        hbox4.Add(self.cycles, flag=wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox4, flag=wx.EXPAND | wx.ALL, border=10)

        # 소리 볼륨: 슬라이더 (기본값 50)
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        volume_label = wx.StaticText(panel, label=lang_res.messages['SOUND_VOLUME'])
        volume_label.SetMinSize((label_width, -1))
        hbox5.Add(volume_label, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=8)
        current_volume = self.config.get_setting(SET_SOUND_VOLUME, 50)
        self.break_sound_volume_slider = wx.Slider(
            panel, value=current_volume, minValue=0, maxValue=100,
            style=wx.SL_HORIZONTAL | wx.SL_LABELS
        )
        self.break_sound_volume_slider.SetMinSize((ctrl_width, -1))
        hbox5.Add(self.break_sound_volume_slider, flag=wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox5, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # --- 새로 추가: 언어 설정 드롭다운 리스트 ---
        hbox_lang = wx.BoxSizer(wx.HORIZONTAL)
        lang_label = wx.StaticText(panel, label="언어 설정:")
        lang_label.SetMinSize((label_width, -1))
        hbox_lang.Add(lang_label, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=8)
        self.lang_choices = ["ko", "en"]
        self.language_choice = wx.Choice(panel, choices=self.lang_choices)
        self.language_choice.SetMinSize((ctrl_width, -1))
        default_language = self.config.get_setting(SET_LANGUAGE, "ko")
        if str(default_language) in self.lang_choices:
            default_index = self.lang_choices.index(str(default_language))
        else:
            default_index = self.lang_choices.index("ko")
        self.language_choice.SetSelection(default_index)
        hbox_lang.Add(self.language_choice, flag=wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox_lang, flag=wx.EXPAND | wx.ALL, border=10)

        # 색상 팔레트 컨트롤 추가
        hbox_color = wx.BoxSizer(wx.HORIZONTAL)
        color_label = wx.StaticText(panel, label="색상 팔레트:")
        color_label.SetMinSize((label_width, -1))
        hbox_color.Add(color_label, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=8)
        color_options_panel = wx.Panel(panel)
        grid_sizer = wx.GridSizer(rows=2, cols=5, hgap=5, vgap=5)

        self.available_colors = [
            "#FFD6A5", "#FDFFB6",
            "#FFADAD", "#A8E6CF",
            "#D4A5FF", "#A2D2FF",
            "#B8E0D2", "#F8EDEB",
            "#BEE1E6", "#FFC8DD"
        ]
        # 기본 설정으로 "#FDFFB6" (또는 config에 저장된 값)을 사용합니다.
        default_color = self.config.get_setting(SET_BREAK_COLOR, "#FDFFB6")
        self.selected_color = default_color
        self.color_option_panels = []
        for color in self.available_colors:
            option = ColorOptionPanel(color_options_panel, color, self.on_color_selected, size=(35, 35))
            if color == default_color:
                option.selected = True
            self.color_option_panels.append(option)
            grid_sizer.Add(option, 0, wx.EXPAND)
        color_options_panel.SetSizer(grid_sizer)
        hbox_color.Add(color_options_panel, flag=wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox_color, flag=wx.EXPAND | wx.ALL, border=10)

        # 버튼들
        hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, wx.ID_OK, label=lang_res.base_labels['SAVE'])
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, label=lang_res.base_labels['CANCEL'])
        hbox_btn.Add(btn_ok)
        hbox_btn.Add(btn_cancel, flag=wx.LEFT, border=10)
        vbox.Add(hbox_btn, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        panel.SetSizer(vbox)

        # 이벤트 바인딩
        btn_ok.Bind(wx.EVT_BUTTON, self.on_save)
        # ESC 키 이벤트 바인딩 추가
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)

    def on_color_selected(self, clicked_panel):
        """
        색상 팔레트 내 옵션이 클릭되면 호출됩니다.
        선택된 항목만 true로 설정하고, 나머지는 false로 리프레시합니다.
        """
        self.selected_color = clicked_panel.color
        for panel in self.color_option_panels:
            panel.selected = (panel == clicked_panel)
            panel.Refresh()

    def on_save(self, event):
        """
        기존 설정들과 함께 선택된 색상 및 언어도 저장합니다.
        """
        study_time_str = self.study_time.GetStringSelection().replace("분", "")
        short_break_str = self.short_break.GetStringSelection().replace("분", "")
        long_break_str = self.long_break.GetStringSelection().replace("분", "")
        cycles_str = self.cycles.GetStringSelection().replace("회", "")

        new_settings = {
            SET_STUDY_TIME: int(study_time_str),
            SET_SHORT_BREAK: int(short_break_str),
            SET_LONG_BREAK: int(long_break_str),
            SET_CYCLES: int(cycles_str),
            SET_SOUND_VOLUME: self.break_sound_volume_slider.GetValue(),
            SET_BREAK_COLOR: self.selected_color,
            SET_LANGUAGE: self.language_choice.GetStringSelection()  # 언어 설정 저장
        }
        self.config.update_settings(new_settings)
        self.EndModal(wx.ID_OK)

    def on_key_down(self, event):
        """
        키 입력 이벤트를 처리하는 핸들러입니다.
        ESC 키를 누르면 다이얼로그를 닫습니다.
        """
        keycode = event.GetKeyCode()
        
        if keycode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()  # 다른 키 입력은 기본 처리로 전달
