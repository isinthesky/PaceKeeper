"""
애플리케이션 전체에서 사용할 스타일 상수를 정의합니다.
"""
from pacekeeper.consts.settings import THEME_DEFAULT, THEME_PINK, THEME_DARK
from pacekeeper.controllers.config_controller import ConfigController

# 기본 색상 정의
PASTEL_PINK = "#FFD1DC"  # 기본 파스텔 핑크
PASTEL_PINK_DARK = "#FFAEC0"  # 어두운 파스텔 핑크 (호버 효과용)
PASTEL_PINK_LIGHT = "#FFEEF2"  # 밝은 파스텔 핑크 (배경용)
PASTEL_PINK_BORDER = "#FF8DA1"  # 테두리용 파스텔 핑크

# 다크 테마 색상 정의
DARK_BG = "#2D2D2D"  # 다크 테마 배경
DARK_CONTROL_BG = "#3D3D3D"  # 다크 테마 컨트롤 배경
DARK_HOVER = "#4D4D4D"  # 다크 테마 호버 색상
DARK_BORDER = "#5D5D5D"  # 다크 테마 테두리 색상
DARK_TEXT = "#FFFFFF"  # 다크 테마 텍스트 색상
DARK_TEXT_SECONDARY = "#CCCCCC"  # 다크 테마 보조 텍스트 색상
DARK_LIST_BG = "#333333"  # 다크 테마 리스트 배경
DARK_LIST_TEXT = "#FFFFFF"  # 다크 테마 리스트 텍스트

# 기본 테마 색상 정의 (하드코딩된 기본값)
DEFAULT_BG = "#F0F0F0"  # 기본 배경색
DEFAULT_CONTROL_BG = "#E0E0E0"  # 기본 컨트롤 배경색
DEFAULT_HOVER = "#D0D0D0"  # 기본 호버 색상
DEFAULT_BORDER = "#C0C0C0"  # 기본 테두리 색상
DEFAULT_TEXT = "#000000"  # 기본 텍스트 색상
DEFAULT_TEXT_SECONDARY = "#666666"  # 기본 보조 텍스트 색상
DEFAULT_LIST_BG = "#FFFFFF"  # 기본 리스트 배경
DEFAULT_LIST_TEXT = "#000000"  # 기본 리스트 텍스트

# 핑크 테마 리스트 색상
PINK_LIST_BG = "#FFF5F7"  # 핑크 테마 리스트 배경
PINK_LIST_TEXT = "#4A4A4A"  # 핑크 테마 리스트 텍스트

# 둥근 모서리 반경
CORNER_RADIUS = 10  # 기본 둥근 모서리 반경
CORNER_RADIUS_SMALL = 5  # 작은 컨트롤용 둥근 모서리 반경
CORNER_RADIUS_LARGE = 15  # 큰 컨트롤용 둥근 모서리 반경

# 테마별 스타일 정의
THEME_STYLES = {
    THEME_DEFAULT: {
        "PANEL_BACKGROUND": DEFAULT_BG,
        "BUTTON_BACKGROUND": DEFAULT_CONTROL_BG,
        "BUTTON_HOVER": DEFAULT_HOVER,
        "BUTTON_BORDER": DEFAULT_BORDER,
        "TEXT_COLOR": DEFAULT_TEXT,
        "TEXT_COLOR_LIGHT": DEFAULT_TEXT_SECONDARY,
        "INPUT_BACKGROUND": "#FFFFFF",
        "INPUT_BORDER": DEFAULT_BORDER,
        "LIST_BACKGROUND": DEFAULT_LIST_BG,
        "LIST_TEXT_COLOR": DEFAULT_LIST_TEXT,
        "USE_ROUND_CORNERS": False,  # 기본 테마는 둥근 모서리 사용 안 함
    },
    THEME_PINK: {
        "PANEL_BACKGROUND": PASTEL_PINK_LIGHT,
        "BUTTON_BACKGROUND": PASTEL_PINK,
        "BUTTON_HOVER": PASTEL_PINK_DARK,
        "BUTTON_BORDER": PASTEL_PINK_BORDER,
        "TEXT_COLOR": "#4A4A4A",
        "TEXT_COLOR_LIGHT": "#6E6E6E",
        "INPUT_BACKGROUND": "#FFFFFF",
        "INPUT_BORDER": PASTEL_PINK_BORDER,
        "LIST_BACKGROUND": PINK_LIST_BG,
        "LIST_TEXT_COLOR": PINK_LIST_TEXT,
        "USE_ROUND_CORNERS": True,  # 핑크 테마는 둥근 모서리 사용
    },
    THEME_DARK: {
        "PANEL_BACKGROUND": DARK_BG,
        "BUTTON_BACKGROUND": DARK_CONTROL_BG,
        "BUTTON_HOVER": DARK_HOVER,
        "BUTTON_BORDER": DARK_BORDER,
        "TEXT_COLOR": DARK_TEXT,
        "TEXT_COLOR_LIGHT": DARK_TEXT_SECONDARY,
        "INPUT_BACKGROUND": DARK_CONTROL_BG,
        "INPUT_BORDER": DARK_BORDER,
        "LIST_BACKGROUND": DARK_LIST_BG,
        "LIST_TEXT_COLOR": DARK_LIST_TEXT,
        "USE_ROUND_CORNERS": True,  # 다크 테마는 둥근 모서리 사용
    }
}

# 현재 테마 가져오기
def get_current_theme():
    config = ConfigController()
    return config.get_setting("theme", THEME_DEFAULT)

# 현재 테마의 스타일 가져오기
current_theme = get_current_theme()
current_style = THEME_STYLES.get(current_theme, THEME_STYLES[THEME_DEFAULT])

# 현재 테마 스타일 적용
PANEL_BACKGROUND = current_style["PANEL_BACKGROUND"]
BUTTON_BACKGROUND = current_style["BUTTON_BACKGROUND"]
BUTTON_HOVER = current_style["BUTTON_HOVER"]
BUTTON_BORDER = current_style["BUTTON_BORDER"]
TEXT_COLOR = current_style["TEXT_COLOR"]
TEXT_COLOR_LIGHT = current_style["TEXT_COLOR_LIGHT"]
INPUT_BACKGROUND = current_style["INPUT_BACKGROUND"]
INPUT_BORDER = current_style["INPUT_BORDER"]
LIST_BACKGROUND = current_style["LIST_BACKGROUND"]
LIST_TEXT_COLOR = current_style["LIST_TEXT_COLOR"]
USE_ROUND_CORNERS = current_style["USE_ROUND_CORNERS"]  # 둥근 모서리 사용 여부

# wx.App 생성 후 시스템 색상으로 업데이트하는 함수
def update_system_colors():
    """
    wx.App 생성 후 호출하여 시스템 색상으로 업데이트합니다.
    """
    import wx
    
    # 시스템 색상 가져오기
    system_bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
    system_ctrl_bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
    system_hover = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT)
    system_border = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNSHADOW)
    system_text = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT)
    system_text_secondary = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
    system_list_bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX)
    system_list_text = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOXTEXT)
    
    # 기본 테마 색상 업데이트
    if current_theme == THEME_DEFAULT:
        global PANEL_BACKGROUND, BUTTON_BACKGROUND, BUTTON_HOVER, BUTTON_BORDER, TEXT_COLOR, TEXT_COLOR_LIGHT, LIST_BACKGROUND, LIST_TEXT_COLOR
        
        PANEL_BACKGROUND = system_bg
        BUTTON_BACKGROUND = system_ctrl_bg
        BUTTON_HOVER = system_hover
        BUTTON_BORDER = system_border
        TEXT_COLOR = system_text
        TEXT_COLOR_LIGHT = system_text_secondary
        LIST_BACKGROUND = system_list_bg
        LIST_TEXT_COLOR = system_list_text 