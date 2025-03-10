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
    SET_LANGUAGE,
    SET_THEME,
    THEME_DEFAULT,
    THEME_PINK,
    THEME_DARK
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
        super().__init__(parent, title=lang_res.title_labels['SETTINGS_DIALOG_TITLE'], size=(500, 500))
        self.config = config_controller
        self.InitUI()
        self.CenterOnParent()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 고정 크기를 설정할 변수 (픽셀 단위)
        label_width = 150  # 레이블의 고정 너비 (필요에 따라 조정)
        ctrl_width = 150   # 선택 리스트, 슬라이더 등 컨트롤의 고정 너비 (필요에 따라 조정)

        # 작업 시간: 드롭다운 리스트 (15분, 25분, 30분, 45분, 60분)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        study_time_label = wx.StaticText(panel, label=lang_res.messages['STUDY_TIME'])
        study_time_label.SetMinSize((label_width, -1))
        hbox1.Add(study_time_label, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=8)
        self.study_time_choices = ["15", "25", "30", "45", "60"]
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
        self.short_break_choices = ["3", "5", "7", "10"]
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

        # 테마 선택: 드롭다운 리스트 (기본 테마, 핑크 테마, 다크 테마)
        hbox_theme = wx.BoxSizer(wx.HORIZONTAL)
        theme_label = wx.StaticText(panel, label="테마")
        theme_label.SetMinSize((label_width, -1))
        hbox_theme.Add(theme_label, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=8)
        
        self.theme_choices = [THEME_DEFAULT, THEME_PINK, THEME_DARK]
        display_theme = ["기본 테마", "핑크 테마", "다크 테마"]
        self.theme = wx.Choice(panel, choices=display_theme)
        self.theme.SetMinSize((ctrl_width, -1))
        
        current_theme = self.config.get_theme()
        if current_theme in self.theme_choices:
            default_index = self.theme_choices.index(current_theme)
        else:
            default_index = 0  # 기본 테마
        self.theme.SetSelection(default_index)
        
        hbox_theme.Add(self.theme, flag=wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox_theme, flag=wx.EXPAND | wx.ALL, border=10)
        
        # 언어 선택: 드롭다운 리스트 (한국어, 영어)
        hbox_lang = wx.BoxSizer(wx.HORIZONTAL)
        lang_label = wx.StaticText(panel, label=lang_res.messages['LANGUAGE'])
        lang_label.SetMinSize((label_width, -1))
        hbox_lang.Add(lang_label, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=8)
        
        self.lang_choices = ["ko", "en"]
        display_lang = ["한국어", "English"]
        self.lang = wx.Choice(panel, choices=display_lang)
        self.lang.SetMinSize((ctrl_width, -1))
        
        current_lang = self.config.get_language()
        if current_lang in self.lang_choices:
            default_index = self.lang_choices.index(current_lang)
        else:
            default_index = 0  # 한국어
        self.lang.SetSelection(default_index)
        
        hbox_lang.Add(self.lang, flag=wx.ALIGN_CENTER_VERTICAL)
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
        """설정 저장"""
        # 선택된 값 가져오기
        study_time = int(self.study_time_choices[self.study_time.GetSelection()])
        short_break = int(self.short_break_choices[self.short_break.GetSelection()])
        long_break = int(self.long_break_choices[self.long_break.GetSelection()])
        cycles = int(self.cycles_choices[self.cycles.GetSelection()])
        volume = self.break_sound_volume_slider.GetValue()
        break_color = self.selected_color
        lang = self.lang_choices[self.lang.GetSelection()]
        theme = self.theme_choices[self.theme.GetSelection()]
        
        # 설정 업데이트
        self.config.update_settings({
            SET_STUDY_TIME: study_time,
            SET_SHORT_BREAK: short_break,
            SET_LONG_BREAK: long_break,
            SET_CYCLES: cycles,
            SET_SOUND_VOLUME: volume,
            SET_BREAK_COLOR: break_color,
            SET_LANGUAGE: lang,
            SET_THEME: theme
        })
        
        # 언어 또는 테마 변경 시 재시작 필요 메시지
        need_restart = False
        restart_message = ""
        
        if lang != self.config.get_language():
            need_restart = True
            if lang == "ko":
                restart_message += "언어 설정이 변경되었습니다. "
            else:
                restart_message += "Language setting has been changed. "
                
        if theme != self.config.get_theme():
            need_restart = True
            if lang == "ko":
                restart_message += "테마 설정이 변경되었습니다. "
            else:
                restart_message += "Theme setting has been changed. "
                
        if need_restart:
            if lang == "ko":
                restart_message += "변경 사항을 적용하려면 앱을 다시 시작하세요."
                title = "알림"
            else:
                restart_message += "Please restart the app to apply the changes."
                title = "Notice"
                
            wx.MessageBox(
                restart_message,
                title,
                wx.OK | wx.ICON_INFORMATION
            )
        
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
