# views/controls.py
import wx
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.services.category_service import CategoryService
from pacekeeper.repository.entities import Tag
from pacekeeper.consts.labels import load_language_resource
from icecream import ic

lang_res = load_language_resource(ConfigController().get_language())

class TimerLabel(wx.StaticText):
    """재사용 가능한 타이머 라벨"""
    def __init__(self, parent, initial_text="00:00", font_increment=0, bold=False, alignment=wx.ALIGN_CENTER):
        self.alignment = alignment  # 정렬 정보를 저장합니다.
        super().__init__(parent, label=initial_text, style=alignment)
        font = self.GetFont()
        if font_increment:
            font.PointSize += font_increment
        if bold:
            font = font.Bold()
        self.SetFont(font)

    def SetLabel(self, label):
        """레이블 업데이트 후에도 alignment가 유지되도록 재설정합니다."""
        super().SetLabel(label)
        self.SetWindowStyleFlag(self.alignment)

class RecentLogsControl(wx.Panel):
    """최근 로그를 리스트로 보여주는 재사용 가능한 컨트롤"""
    def __init__(self, parent, config_controller, on_double_click=None, on_logs_updated=None):
        super().__init__(parent)
        self.config = config_controller
        self.on_logs_updated = on_logs_updated  # 로그 업데이트 후 호출될 콜백
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        # StaticBox와 그 내부를 구성하는 StaticBoxSizer를 생성합니다.
        self.static_box = wx.StaticBox(self, label=lang_res.messages['RECENT_LOGS'])
        self.box_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
        # 외부 여백은 유지하면서 box_sizer를 추가합니다.
        self.sizer.Add(self.box_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        # ListCtrl을 StaticBoxSizer 내부에 추가하여 간격 없이 표시합니다.
        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, "시간", width=150)
        self.list_ctrl.InsertColumn(1, "메시지", width=390)
        self.list_ctrl.InsertColumn(2, "태그", width=200)
        if on_double_click:
            self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, on_double_click)
        # 내부 여백(border 값 0)을 주어 ListCtrl과 StaticBox 사이의 간격을 제거합니다.
        self.box_sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 0)
        
        # 초기 데이터 로드를 제한된 개수의 로그를 불러옵니다.
        self.update_logs(limit=10)

    def update_logs(self, logs:list[any]=[], limit=50):
        """
        리스트 컨트롤의 항목들을 최신 로그로 업데이트합니다.
        
        파라미터:
            logs: MainController 등에서 전달받은 로그 데이터 (리스트).
            limit: 보여줄 로그 수의 제한 (기본값 10)
        """
        self.list_ctrl.DeleteAllItems()
        logs = logs[:limit] if logs else []
        
        for idx, row in enumerate(reversed(logs)):
            self.list_ctrl.InsertItem(idx, row["start_date"])
            self.list_ctrl.SetItem(idx, 1, row["message"])
            self.list_ctrl.SetItem(idx, 2, row["tag_text"])
        
        # 로그 업데이트가 완료되면 콜백으로 태그 버튼 업데이트 진행
        if self.on_logs_updated:
            self.on_logs_updated()

class TagButtonsPanel(wx.Panel):
    """태그 버튼들을 관리하는 패널"""
    def __init__(self, parent, on_tag_selected =  None):
        super().__init__(parent)
        self.on_tag_selected = on_tag_selected
        self.sizer = wx.WrapSizer()
        self.SetSizer(self.sizer)
        self.service = CategoryService()
        self.selected_tag = None
        
    def update_tags(self, tags:list[Tag]):
        """
        태그 버튼 업데이트 메서드.
        """
        
        for child in self.GetChildren():
            child.Destroy()
            
        categories = self.service.get_categories()
        color_set = {category.id: category for category in categories}
        
        ic("tags", tags)
        
        for tag in tags:
            if tag:         
                btn = wx.Button(self, label=tag.name)
                btn.Bind(wx.EVT_BUTTON, lambda event, t=tag: self.on_tag_selected(t))
            
                category = color_set.get(tag.category_id)
                if category:
                    btn.SetBackgroundColour(category.color)

                self.sizer.Add(btn, 0, wx.ALL, 5)
                
        self.Layout()        

class TextInputPanel(wx.Panel):
    """텍스트 입력창과 (옵션) 버튼을 포함하는 패널"""
    def __init__(self, parent, text_style=wx.TE_PROCESS_ENTER):
        super().__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        self.static_box = wx.StaticBox(self, label=lang_res.messages['TODO_INPUT'])
        self.box_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
        self.sizer.Add(self.box_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.input_ctrl = wx.TextCtrl(self, style=text_style)
        self.box_sizer.Add(self.input_ctrl, flag=wx.EXPAND | wx.ALL, border=5)

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
    안내 문구와 타이머 라벨만 포함.
    """
    def __init__(self, parent, config_ctrl):
        super().__init__(parent)
        self.config = config_ctrl
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # (1) 안내 문구
        st = wx.StaticText(self, label=lang_res.messages['START_BREAK'], style=wx.ALIGN_CENTER)
        main_sizer.Add(st, flag=wx.ALIGN_CENTER | wx.TOP, border=20)

        # (2) 남은 시간 표시
        self.break_label = TimerLabel(self, initial_text="00:00", font_increment=10, alignment=wx.ALIGN_CENTER)
        main_sizer.Add(self.break_label, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)

        self.SetSizer(main_sizer)

class RoundButton(wx.Control):
    """
    A custom button control with rounded corners, hover effects and customizable colors.
    """
    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, 
                 name="RoundButton", bg_color="#3498db", hover_color="#2980b9", 
                 text_color="#ffffff", border_color=None, corner_radius=10):
        """
        Initialize a button with rounded corners and custom colors.
        
        Args:
            parent: Parent window
            id: Button ID
            label: Button text
            pos: Button position
            size: Button size
            style: Button style
            validator: Button validator
            name: Button name
            bg_color: Background color (hex)
            hover_color: Color when mouse hovers over button (hex)
            text_color: Text color (hex)
            border_color: Border color (hex), None for no border
            corner_radius: Radius of the rounded corners (pixels)
        """
        super().__init__(parent, id, pos, size, style | wx.BORDER_NONE, validator, name)
        
        # Set button properties
        self.label = label
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.corner_radius = corner_radius
        self.current_color = bg_color
        
        # State tracking
        self.hover = False
        self.pressed = False
        
        # Set minimum size
        min_width, min_height = 80, 40
        width, height = size
        if width == -1:
            width = min_width
        if height == -1:
            height = min_height
        self.SetMinSize((width, height))
        self.SetSize((width, height))
        
        # Bind events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
        
        # Set background style for custom painting
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
    
    def OnPaint(self, event):
        """Paint the button with rounded corners."""
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        
        if not gc:
            dc.Clear()
            return
            
        # Get the button's dimensions
        width, height = self.GetSize()
        
        # Clear the background
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.Clear()
        
        # Create a rounded rectangle path
        path = gc.CreatePath()
        
        # Adjust corner radius if it's too large for the button size
        corner_radius = min(self.corner_radius, width/2, height/2)
        
        # Draw rounded rectangle
        path.AddRoundedRectangle(0, 0, width, height, corner_radius)
        
        # Fill the button
        gc.SetBrush(wx.Brush(self.current_color))
        if self.border_color:
            gc.SetPen(wx.Pen(self.border_color, 2))
        else:
            gc.SetPen(wx.TRANSPARENT_PEN)
            
        gc.DrawPath(path)
        
        # Draw the text
        if self.label:
            font = self.GetFont()
            gc.SetFont(font, wx.Colour(self.text_color))
            text_width, text_height = gc.GetTextExtent(self.label)
            gc.DrawText(self.label, (width - text_width) / 2, (height - text_height) / 2)
    
    def OnLeftDown(self, event):
        """Handle left mouse button down event."""
        self.pressed = True
        # Darken the button when pressed
        self.current_color = self.AdjustColor(self.hover_color, -30)
        self.Refresh()
        event.Skip()
    
    def OnLeftUp(self, event):
        """Handle left mouse button up event."""
        if self.pressed:
            self.pressed = False
            # If still hovering, use hover color
            if self.hover:
                self.current_color = self.hover_color
            else:
                self.current_color = self.bg_color
            self.Refresh()
            
            # Fire a button event
            evt = wx.CommandEvent(wx.wxEVT_BUTTON, self.GetId())
            evt.SetEventObject(self)
            self.GetEventHandler().ProcessEvent(evt)
        event.Skip()
    
    def OnMouseEnter(self, event):
        """Handle mouse enter event."""
        self.hover = True
        if not self.pressed:
            self.current_color = self.hover_color
            self.Refresh()
        event.Skip()
    
    def OnMouseLeave(self, event):
        """Handle mouse leave event."""
        self.hover = False
        if not self.pressed:
            self.current_color = self.bg_color
            self.Refresh()
        event.Skip()
    
    def SetLabel(self, label):
        """Set the button label."""
        self.label = label
        self.Refresh()
    
    def GetLabel(self):
        """Get the button label."""
        return self.label
    
    def SetBackgroundColour(self, color):
        """Set the button background color."""
        self.bg_color = color
        if not self.hover and not self.pressed:
            self.current_color = color
            self.Refresh()
    
    def SetHoverColour(self, color):
        """Set the button hover color."""
        self.hover_color = color
        if self.hover and not self.pressed:
            self.current_color = color
            self.Refresh()
    
    def SetTextColour(self, color):
        """Set the button text color."""
        self.text_color = color
        self.Refresh()
    
    def SetBorderColour(self, color):
        """Set the button border color."""
        self.border_color = color
        self.Refresh()
    
    def SetCornerRadius(self, radius):
        """Set the corner radius."""
        self.corner_radius = radius
        self.Refresh()
    
    def Enable(self, enable=True):
        """Enable or disable the button."""
        super().Enable(enable)
        if not enable:
            self.current_color = self.AdjustColor(self.bg_color, 30)  # Lighten the color
        else:
            self.current_color = self.bg_color
        self.Refresh()
    
    def Disable(self):
        """Disable the button."""
        self.Enable(False)
    
    @staticmethod
    def AdjustColor(hex_color, amount):
        """
        Adjust a hex color by the given amount.
        
        Args:
            hex_color: Hex color string (e.g., "#3498db")
            amount: Amount to adjust (-255 to 255)
            
        Returns:
            Adjusted hex color string
        """
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
            
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        
        return f"#{r:02x}{g:02x}{b:02x}"