# controls.py
import wx
from pacekeeper.consts.settings import CONFIG_DATA_MODEL

class TimerLabel(wx.StaticText):
    """타이머 표시 라벨 (폰트 크기 및 Bold 옵션 제공)"""
    def __init__(self, parent, initial_text="00:00", font_increment=0, bold=False, alignment=wx.ALIGN_CENTER):
        super().__init__(parent, label=initial_text, style=alignment)
        font = self.GetFont()
        if font_increment:
            font.PointSize += font_increment
        if bold:
            font = font.Bold()
        self.SetFont(font)

class RecentLogsControl(wx.StaticBoxSizer):
    """최근 기록을 표시하는 재사용 가능한 ListCtrl 컴포넌트"""
    def __init__(self, parent, config_controller, on_double_click=None):
        super().__init__(wx.VERTICAL, parent, label="최근 기록")
        self.config = config_controller
        self.parent = parent
        
        # ListCtrl 생성
        self.list_ctrl = wx.ListCtrl(
            self.GetStaticBox(),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.InsertColumn(0, "시간", width=150)
        self.list_ctrl.InsertColumn(1, "메시지", width=400)
        self.list_ctrl.InsertColumn(2, "태그", width=200)
        
        if on_double_click:
            self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, on_double_click)
        
        self.Add(self.list_ctrl, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        self.load_data()

    def load_data(self, limit=10):
        """데이터 로드 및 리스트 갱신"""
        self.list_ctrl.DeleteAllItems()
        if hasattr(self.config, CONFIG_DATA_MODEL):
            rows = self.config.data_model.get_last_logs(limit)
            for idx, row in enumerate(reversed(rows)):
                self.list_ctrl.InsertItem(idx, row[2])  # timestamp
                self.list_ctrl.SetItem(idx, 1, row[3])  # message
                self.list_ctrl.SetItem(idx, 2, row[4] or "")  # tags

class TagButtonsPanel(wx.Panel):
    """태그 버튼을 관리하는 재사용 가능한 패널"""
    def __init__(self, parent, on_tag_selected):
        super().__init__(parent)
        self.on_tag_selected = on_tag_selected
        self.sizer = wx.WrapSizer()
        self.SetSizer(self.sizer)
        
    def update_tags(self, tags):
        """태그 목록 갱신"""
        # 기존 버튼 제거
        for child in self.GetChildren():
            child.Destroy()
        
        # 새 태그 버튼 생성
        for tag in sorted(tags):
            if tag:
                btn = wx.Button(self, label=tag)
                btn.Bind(wx.EVT_BUTTON, lambda e, t=tag: self.on_tag_click(t))
                self.sizer.Add(btn, 0, wx.ALL, 5)
        self.Layout()

    def on_tag_click(self, tag):
        """태그 클릭 이벤트 처리"""
        if not tag.startswith('#'):
            tag = f"#{tag}"
        self.on_tag_selected(tag)

class TextInputPanel(wx.Panel):
    """
    텍스트 입력 필드와 (선택적) 버튼을 포함하는 패널.
    
    :param parent: 부모 윈도우
    :param box_label: StaticBox 사용 시 라벨 (None이면 StaticBox 없이 단순 패널)
    :param button_label: 버튼 라벨 (None이면 버튼 미생성)
    :param text_style: 텍스트 컨트롤 스타일 (기본: wx.TE_PROCESS_ENTER)
    """
    def __init__(self, parent, box_label=None, button_label=None, text_style=wx.TE_PROCESS_ENTER):
        super().__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        if box_label:
            # StaticBox로 감싸서 영역 구성
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