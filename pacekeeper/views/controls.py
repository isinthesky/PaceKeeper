# views/controls.py
import wx
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.services.category_service import CategoryService
from pacekeeper.repository.entities import Tag
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.styles import *  # 스타일 상수 가져오기
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
        
        # 배경색 설정
        self.SetBackgroundColour(PANEL_BACKGROUND)
        
        # StaticBox와 그 내부를 구성하는 StaticBoxSizer를 생성합니다.
        self.static_box = wx.StaticBox(self, label=lang_res.messages['RECENT_LOGS'])
        self.static_box.SetBackgroundColour(PANEL_BACKGROUND)
        self.static_box.SetForegroundColour(TEXT_COLOR)
        self.box_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
        # 외부 여백은 유지하면서 box_sizer를 추가합니다.
        self.sizer.Add(self.box_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        # 커스텀 스타일의 ListCtrl 생성
        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_NONE)
        self.list_ctrl.SetBackgroundColour(LIST_BACKGROUND)
        self.list_ctrl.SetForegroundColour(LIST_TEXT_COLOR)
        
        # 컬럼 설정
        self.list_ctrl.InsertColumn(0, "시간", width=150)
        self.list_ctrl.InsertColumn(1, "메시지", width=390)
        self.list_ctrl.InsertColumn(2, "태그", width=200)
        
        # 이벤트 바인딩
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
        
        # 배경색 설정
        self.SetBackgroundColour(PANEL_BACKGROUND)
        
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
                # 일반 버튼 대신 RoundButton 사용
                btn = RoundButton(
                    self, 
                    label=tag.name,
                    corner_radius=CORNER_RADIUS_SMALL
                )
                btn.Bind(wx.EVT_BUTTON, lambda event, t=tag: self.on_tag_selected(t))
            
                category = color_set.get(tag.category_id)
                if category:
                    # 카테고리 색상이 있으면 적용, 없으면 기본 파스텔 핑크 사용
                    btn.SetBackgroundColour(category.color)
                    # 어두운 색상의 경우 텍스트 색상을 흰색으로 변경
                    if self._is_dark_color(category.color):
                        btn.SetTextColour("#FFFFFF")
                    else:
                        btn.SetTextColour(TEXT_COLOR)
                else:
                    # 기본 파스텔 핑크 색상 사용
                    btn.SetBackgroundColour(BUTTON_BACKGROUND)
                    btn.SetTextColour(TEXT_COLOR)

                self.sizer.Add(btn, 0, wx.ALL, 5)
                
        self.Layout()
        
    def _is_dark_color(self, color_hex):
        """
        색상이 어두운지 확인하는 헬퍼 메서드
        """
        # 색상 코드에서 # 제거
        color = color_hex.lstrip('#')
        
        # RGB 값으로 변환
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        
        # 밝기 계산 (YIQ 공식 사용)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        
        # 밝기가 128보다 작으면 어두운 색상으로 간주
        return brightness < 128

class RoundTextCtrl(wx.TextCtrl):
    """
    둥근 모서리를 가진 텍스트 컨트롤
    """
    def __init__(self, parent, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
                 name=wx.TextCtrlNameStr, border_color=INPUT_BORDER, corner_radius=CORNER_RADIUS_SMALL):
        """
        둥근 모서리를 가진 텍스트 컨트롤 초기화
        
        Args:
            parent: 부모 윈도우
            id: 컨트롤 ID
            value: 초기 텍스트 값
            pos: 위치
            size: 크기
            style: 스타일
            validator: 유효성 검사기
            name: 이름
            border_color: 테두리 색상 (hex)
            corner_radius: 모서리 반경 (픽셀)
        """
        # 기본 테마에서는 기본 테두리 스타일 사용
        if not USE_ROUND_CORNERS:
            super().__init__(parent, id, value, pos, size, style, validator, name)
        else:
            super().__init__(parent, id, value, pos, size, style | wx.BORDER_NONE, validator, name)
        
        # 속성 설정
        self.border_color = border_color
        self.corner_radius = corner_radius
        self.use_round_corners = USE_ROUND_CORNERS  # 둥근 모서리 사용 여부
        
        # 배경색 및 텍스트 색상 설정
        self.SetBackgroundColour(INPUT_BACKGROUND)
        self.SetForegroundColour(TEXT_COLOR)
        
        # 둥근 모서리를 사용하는 경우에만 이벤트 바인딩
        if self.use_round_corners:
            self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def OnPaint(self, event):
        """
        텍스트 컨트롤 주변에 둥근 테두리를 그립니다.
        기본 이벤트 처리 후 테두리를 추가로 그립니다.
        """
        # 둥근 모서리를 사용하지 않으면 기본 그리기 사용
        if not self.use_round_corners:
            event.Skip()
            return
            
        # 기본 페인트 이벤트 처리
        event.Skip()
        
        # 테두리 그리기
        dc = wx.ClientDC(self)
        gc = wx.GraphicsContext.Create(dc)
        
        if not gc:
            return
            
        # 컨트롤 크기 가져오기
        width, height = self.GetSize()
        
        # 둥근 사각형 경로 생성
        path = gc.CreatePath()
        
        # 컨트롤 크기에 맞게 모서리 반경 조정
        corner_radius = min(self.corner_radius, width/2, height/2)
        
        # 둥근 사각형 그리기
        path.AddRoundedRectangle(0, 0, width, height, corner_radius)
        
        # 테두리만 그리기
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetPen(wx.Pen(self.border_color, 1))
        gc.DrawPath(path)

class TextInputPanel(wx.Panel):
    """텍스트 입력창과 (옵션) 버튼을 포함하는 패널"""
    def __init__(self, parent, text_style=wx.TE_PROCESS_ENTER):
        super().__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        # 패널 배경색 설정
        self.SetBackgroundColour(PANEL_BACKGROUND)
        
        self.static_box = wx.StaticBox(self, label=lang_res.messages['TODO_INPUT'])
        self.static_box.SetBackgroundColour(PANEL_BACKGROUND)
        self.static_box.SetForegroundColour(TEXT_COLOR)
        self.box_sizer = wx.StaticBoxSizer(self.static_box, wx.VERTICAL)
        self.sizer.Add(self.box_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 테마에 따라 일반 TextCtrl 또는 RoundTextCtrl 사용
        if USE_ROUND_CORNERS:
            self.input_ctrl = RoundTextCtrl(self, style=text_style)
        else:
            self.input_ctrl = wx.TextCtrl(self, style=text_style)
            self.input_ctrl.SetBackgroundColour(INPUT_BACKGROUND)
            
        # 텍스트 색상 설정
        self.input_ctrl.SetForegroundColour(TEXT_COLOR)
            
        self.box_sizer.Add(self.input_ctrl, flag=wx.EXPAND | wx.ALL, border=5)

    def get_value(self):
        """입력 값 반환"""
        return self.input_ctrl.GetValue()
        
    def set_value(self, value):
        """입력 값 설정"""
        self.input_ctrl.SetValue(value)
        
    def bind_text_change(self, handler):
        """텍스트 변경 이벤트 바인딩"""
        self.input_ctrl.Bind(wx.EVT_TEXT, handler)
        
    def bind_button(self, handler):
        """버튼 클릭 이벤트 바인딩 (버튼이 있는 경우)"""
        if hasattr(self, 'button'):
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

class RoundPanel(wx.Panel):
    """
    둥근 모서리를 가진 패널 컨트롤
    """
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, style=wx.TAB_TRAVERSAL, name=wx.PanelNameStr,
                 bg_color=PANEL_BACKGROUND, border_color=None, corner_radius=CORNER_RADIUS):
        """
        둥근 모서리를 가진 패널 초기화
        
        Args:
            parent: 부모 윈도우
            id: 패널 ID
            pos: 패널 위치
            size: 패널 크기
            style: 패널 스타일
            name: 패널 이름
            bg_color: 배경 색상 (hex)
            border_color: 테두리 색상 (hex), None이면 테두리 없음
            corner_radius: 모서리 반경 (픽셀)
        """
        super().__init__(parent, id, pos, size, style, name)
        
        # 패널 속성 설정
        self.bg_color = bg_color
        self.border_color = border_color
        self.corner_radius = corner_radius
        self.use_round_corners = USE_ROUND_CORNERS  # 둥근 모서리 사용 여부
        
        # 배경색 설정
        self.SetBackgroundColour(bg_color)
        
        # 배경 스타일 설정
        if self.use_round_corners:
            self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
            # 이벤트 바인딩
            self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def OnPaint(self, event):
        """둥근 모서리로 패널 그리기"""
        # 둥근 모서리를 사용하지 않으면 기본 그리기 사용
        if not self.use_round_corners:
            event.Skip()
            return
            
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        
        if not gc:
            dc.Clear()
            return
            
        # 패널 크기 가져오기
        width, height = self.GetSize()
        
        # 배경 지우기
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.Clear()
        
        # 둥근 사각형 경로 생성
        path = gc.CreatePath()
        
        # 패널 크기에 맞게 모서리 반경 조정
        corner_radius = min(self.corner_radius, width/2, height/2)
        
        # 둥근 사각형 그리기
        path.AddRoundedRectangle(0, 0, width, height, corner_radius)
        
        # 패널 채우기
        gc.SetBrush(wx.Brush(self.bg_color))
        if self.border_color:
            gc.SetPen(wx.Pen(self.border_color, 1))
        else:
            gc.SetPen(wx.TRANSPARENT_PEN)
            
        gc.DrawPath(path)

class RoundButton(wx.Control):
    """
    A custom button control with rounded corners, hover effects and customizable colors.
    """
    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, 
                 name="RoundButton", bg_color=BUTTON_BACKGROUND, hover_color=BUTTON_HOVER, 
                 text_color=TEXT_COLOR, border_color=BUTTON_BORDER, corner_radius=CORNER_RADIUS):
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
        # 기본 테마에서는 기본 버튼 사용
        if not USE_ROUND_CORNERS:
            self.use_default_button = True
            self.default_button = wx.Button(parent, id, label, pos, size, style, validator, name)
            super().__init__(parent, id, pos, size, style, validator, name)
            self.Bind(wx.EVT_PAINT, self.OnPaintDefault)
            
            # 기본 버튼 이벤트를 이 컨트롤로 전달
            self.default_button.Bind(wx.EVT_BUTTON, self.OnDefaultButtonClick)
            
            # 크기 설정
            self.SetSize(self.default_button.GetSize())
            self.SetMinSize(self.default_button.GetMinSize())
        else:
            self.use_default_button = False
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
    
    def OnPaintDefault(self, event):
        """기본 버튼 그리기"""
        # 아무것도 그리지 않음 (기본 버튼이 그려짐)
        pass
        
    def OnDefaultButtonClick(self, event):
        """기본 버튼 클릭 이벤트 처리"""
        # 이 컨트롤에서 버튼 이벤트 발생
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
        evt.SetEventObject(self)
        wx.PostEvent(self.GetEventHandler(), evt)
        
        # 원래 이벤트도 처리
        event.Skip()
    
    def OnPaint(self, event):
        """Paint the button with rounded corners."""
        # 기본 버튼을 사용하는 경우 기본 그리기 사용
        if self.use_default_button:
            event.Skip()
            return
            
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
        
        # Draw the label
        font = self.GetFont()
        gc.SetFont(font, self.text_color)
        
        # Calculate text position to center it
        text_width, text_height = gc.GetTextExtent(self.label)
        text_x = (width - text_width) / 2
        text_y = (height - text_height) / 2
        
        gc.DrawText(self.label, text_x, text_y)
        
        # Draw focus indicator if the button has focus
        if self.HasFocus():
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen(self.text_color, 1, wx.PENSTYLE_DOT))
            gc.DrawRoundedRectangle(2, 2, width-4, height-4, corner_radius-2)

    def OnLeftDown(self, event):
        """Handle left mouse button down event."""
        if self.use_default_button:
            self.default_button.SetFocus()
            return
            
        self.pressed = True
        self.current_color = self.AdjustColor(self.hover_color, -20)
        self.SetFocus()
        self.Refresh()
        event.Skip()

    def OnLeftUp(self, event):
        """Handle left mouse button up event."""
        if self.use_default_button:
            return
            
        if self.pressed:
            self.pressed = False
            
            # Check if the mouse is still over the button
            pos = event.GetPosition()
            rect = self.GetClientRect()
            
            if rect.Contains(pos):
                # Mouse is still over the button, trigger the click event
                self.current_color = self.hover_color
                
                # Create and post a button event
                evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
                evt.SetEventObject(self)
                wx.PostEvent(self.GetEventHandler(), evt)
            else:
                # Mouse moved away, just reset the color
                self.current_color = self.bg_color
                
            self.Refresh()
        event.Skip()

    def OnMouseEnter(self, event):
        """Handle mouse enter event."""
        if self.use_default_button:
            return
            
        self.hover = True
        if not self.pressed:
            self.current_color = self.hover_color
            self.Refresh()
        event.Skip()

    def OnMouseLeave(self, event):
        """Handle mouse leave event."""
        if self.use_default_button:
            return
            
        self.hover = False
        if not self.pressed:
            self.current_color = self.bg_color
            self.Refresh()
        event.Skip()

    def SetLabel(self, label):
        """Set the button label."""
        if self.use_default_button:
            self.default_button.SetLabel(label)
            return
            
        self.label = label
        self.Refresh()

    def GetLabel(self):
        """Get the button label."""
        if self.use_default_button:
            return self.default_button.GetLabel()
        return self.label

    def SetBackgroundColour(self, color):
        """Set the button background color."""
        if self.use_default_button:
            self.default_button.SetBackgroundColour(color)
            return
            
        self.bg_color = color
        self.current_color = color
        self.Refresh()

    def SetHoverColour(self, color):
        """Set the button hover color."""
        if self.use_default_button:
            return
            
        self.hover_color = color
        if self.hover:
            self.current_color = color
            self.Refresh()

    def SetTextColour(self, color):
        """Set the button text color."""
        if self.use_default_button:
            self.default_button.SetForegroundColour(color)
            return
            
        self.text_color = color
        self.Refresh()

    def SetBorderColour(self, color):
        """Set the button border color."""
        if self.use_default_button:
            return
            
        self.border_color = color
        self.Refresh()

    def SetCornerRadius(self, radius):
        """Set the button corner radius."""
        if self.use_default_button:
            return
            
        self.corner_radius = radius
        self.Refresh()

    def Enable(self, enable=True):
        """Enable or disable the button."""
        if self.use_default_button:
            self.default_button.Enable(enable)
            return
            
        super().Enable(enable)
        if not enable:
            self.current_color = self.AdjustColor(self.bg_color, 30)
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
        Positive values lighten the color, negative values darken it.
        """
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        
        # Adjust RGB values
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'