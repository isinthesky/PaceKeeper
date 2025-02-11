# views/controls.py
import wx
from pacekeeper.consts.labels import load_language_resource

lang_res = load_language_resource()

class TimerLabel(wx.StaticText):
    """재사용 가능한 타이머 라벨"""
    def __init__(self, parent, initial_text="00:00", font_increment=0, bold=False, alignment=wx.ALIGN_CENTER):
        super().__init__(parent, label=initial_text, style=alignment)
        font = self.GetFont()
        if font_increment:
            font.PointSize += font_increment
        if bold:
            font = font.Bold()
        self.SetFont(font)

class RecentLogsControl(wx.Panel):
    """최근 로그를 리스트로 보여주는 재사용 가능한 컨트롤"""
    def __init__(self, parent, config_controller, on_double_click=None):
        super().__init__(parent)
        self.config = config_controller
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        # from wx import LC_REPORT, BORDER_SUNKEN, ListCtrl  # 또는 기존 구현 재사용
        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, "시간", width=150)
        self.list_ctrl.InsertColumn(1, "메시지", width=400)
        self.list_ctrl.InsertColumn(2, "태그", width=200)
        if on_double_click:
            self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, on_double_click)
        self.sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        self.load_data()

    def load_data(self, limit=10):
        self.list_ctrl.DeleteAllItems()
        if hasattr(self.config, "data_model"):
            rows = self.config.data_model.get_last_logs(limit)
            for idx, row in enumerate(reversed(rows)):
                self.list_ctrl.InsertItem(idx, row[2])  # timestamp
                self.list_ctrl.SetItem(idx, 1, row[3])   # message
                self.list_ctrl.SetItem(idx, 2, row[4] or "")  # tags

class TagButtonsPanel(wx.Panel):
    """태그 버튼들을 관리하는 패널"""
    def __init__(self, parent, on_tag_selected):
        super().__init__(parent)
        self.on_tag_selected = on_tag_selected
        self.sizer = wx.WrapSizer()
        self.SetSizer(self.sizer)
        
    def update_tags(self, tags):
        for child in self.GetChildren():
            child.Destroy()
        for tag in sorted(tags):
            if tag:
                btn = wx.Button(self, label=tag)
                btn.Bind(wx.EVT_BUTTON, lambda event, t=tag: self.on_tag_selected(t))
                self.sizer.Add(btn, 0, wx.ALL, 5)
        self.Layout()

class TextInputPanel(wx.Panel):
    """텍스트 입력창과 (옵션) 버튼을 포함하는 패널"""
    def __init__(self, parent, box_label=None, button_label=None, text_style=wx.TE_PROCESS_ENTER):
        super().__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        if box_label:
            self.static_box = wx.StaticBox(self, label=box_label)
            self.box_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
            self.sizer.Add(self.box_sizer, 0, wx.EXPAND | wx.ALL, 5)
            self.input_ctrl = wx.TextCtrl(self, style=text_style)
            self.box_sizer.Add(self.input_ctrl, flag=wx.EXPAND | wx.ALL, border=5)
        else:
            self.input_ctrl = wx.TextCtrl(self, style=text_style)
            self.sizer.Add(self.input_ctrl, flag=wx.EXPAND | wx.ALL, border=5)
        
        if button_label:
            self.button = wx.Button(self, label=button_label)
            self.sizer.Add(self.button, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        else:
            self.button = None

    def get_value(self):
        return self.input_ctrl.GetValue()
        
    def set_value(self, value):
        self.input_ctrl.SetValue(value)
        
    def bind_text_change(self, handler):
        self.input_ctrl.Bind(wx.EVT_TEXT, handler)
        
    def bind_button(self, handler):
        if self.button:
            self.button.Bind(wx.EVT_BUTTON, handler)

class BreakDialogPanel(wx.Panel):
    """
    BreakDialog 전용 UI 패널  
    안내 문구, 타이머 라벨, 최근 로그, 태그 버튼, 텍스트 입력창을 포함.
    """
    def __init__(self, parent, config_ctrl, on_item_double_click, on_tag_selected, on_text_change, on_submit):
        super().__init__(parent)
        self.config = config_ctrl
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # (1) 안내 문구
        st = wx.StaticText(self, label=lang_res.messages['START_BREAK'], style=wx.ALIGN_CENTER)
        main_sizer.Add(st, flag=wx.ALIGN_CENTER | wx.TOP, border=20)

        # (2) 남은 시간 표시
        self.break_label = TimerLabel(self, initial_text="00:00", font_increment=10, alignment=wx.ALIGN_CENTER)
        main_sizer.Add(self.break_label, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)

        # (3) 최근 기록 컨트롤
        self.recent_logs = RecentLogsControl(self, config_ctrl, on_double_click=on_item_double_click)
        main_sizer.Add(self.recent_logs, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)

        # (4) 태그 버튼 패널
        self.tag_panel = TagButtonsPanel(self, on_tag_selected=on_tag_selected)
        main_sizer.Add(self.tag_panel, flag=wx.EXPAND | wx.ALL, border=10)

        # (5) 사용자 입력 필드 + 제출 버튼
        self.input_panel = TextInputPanel(self, box_label=None, button_label=lang_res.button_labels['SUBMIT'])
        self.input_panel.bind_text_change(on_text_change)
        self.input_panel.bind_button(on_submit)
        main_sizer.Add(self.input_panel, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=20)

        self.SetSizer(main_sizer)