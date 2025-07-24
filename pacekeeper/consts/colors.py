# consts/colors.py

"""
PaceKeeper 애플리케이션의 통합 색상 팔레트

이 파일은 모든 UI 컴포넌트에서 사용되는 색상을 중앙화하여 관리합니다.
테마 변경이나 브랜딩 업데이트 시 이 파일만 수정하면 전체 애플리케이션에 반영됩니다.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ColorPalette:
    """색상 팔레트 데이터 클래스"""

    # Primary Colors
    PRIMARY: str = "#2196F3"  # Material Blue
    PRIMARY_HOVER: str = "#1976D2"
    PRIMARY_PRESSED: str = "#1565C0"

    # Secondary Colors
    SECONDARY: str = "#9CA3AF"  # Medium gray

    # Success Colors
    SUCCESS: str = "#10B981"  # Soft emerald
    SUCCESS_HOVER: str = "#059669"
    SUCCESS_PRESSED: str = "#047857"

    # Warning Colors
    WARNING: str = "#F59E0B"  # Soft amber
    WARNING_HOVER: str = "#D97706"
    WARNING_PRESSED: str = "#B45309"

    # Text Colors
    TEXT_PRIMARY: str = "#374151"  # Soft dark gray
    TEXT_SECONDARY: str = "#6B7280"  # Medium gray
    TEXT_HINT: str = "#9CA3AF"  # Light gray

    # Background Colors
    BACKGROUND: str = "#F8F9FA"  # Light gray
    SURFACE: str = "#FFFFFF"  # White
    SURFACE_HOVER: str = "#F9FAFB"
    SURFACE_PRESSED: str = "#F3F4F6"

    # Border Colors
    BORDER: str = "#E5E7EB"  # Very light gray
    BORDER_HOVER: str = "#D1D5DB"
    BORDER_FOCUS: str = "#2196F3"

    # Input Colors
    INPUT_BACKGROUND: str = "#FBFCFD"
    INPUT_FOCUS: str = "#FFFFFF"
    INPUT_DISABLED: str = "#F9FAFB"

    # Special Colors
    BREAK_COLOR: str = "#FDFFB6"  # Default break notification color
    WHITE: str = "#FFFFFF"  # Default category color

    # Scroll Bar Colors
    SCROLLBAR_HANDLE: str = "#D0D0D0"
    SCROLLBAR_HANDLE_HOVER: str = "#B0B0B0"
    SCROLLBAR_HANDLE_PRESSED: str = "#9E9E9E"


# 전역 색상 팔레트 인스턴스
COLORS = ColorPalette()


def get_theme_colors() -> dict[str, str]:
    """
    테마 시스템에서 사용할 색상 딕셔너리 반환
    
    Returns:
        Dict[str, str]: 색상 이름과 값의 매핑
    """
    return {
        # Primary
        'primary': COLORS.PRIMARY,
        'primary_hover': COLORS.PRIMARY_HOVER,
        'primary_pressed': COLORS.PRIMARY_PRESSED,

        # Secondary
        'secondary': COLORS.SECONDARY,

        # Success
        'success': COLORS.SUCCESS,
        'success_hover': COLORS.SUCCESS_HOVER,
        'success_pressed': COLORS.SUCCESS_PRESSED,

        # Warning
        'warning': COLORS.WARNING,
        'warning_hover': COLORS.WARNING_HOVER,
        'warning_pressed': COLORS.WARNING_PRESSED,

        # Text
        'text_primary': COLORS.TEXT_PRIMARY,
        'text_secondary': COLORS.TEXT_SECONDARY,
        'text_hint': COLORS.TEXT_HINT,

        # Background
        'background': COLORS.BACKGROUND,
        'surface': COLORS.SURFACE,
        'surface_hover': COLORS.SURFACE_HOVER,
        'surface_pressed': COLORS.SURFACE_PRESSED,

        # Border
        'border': COLORS.BORDER,
        'border_hover': COLORS.BORDER_HOVER,
        'border_focus': COLORS.BORDER_FOCUS,

        # Input
        'input_background': COLORS.INPUT_BACKGROUND,
        'input_focus': COLORS.INPUT_FOCUS,
        'input_disabled': COLORS.INPUT_DISABLED,

        # Special
        'break_color': COLORS.BREAK_COLOR,
        'white': COLORS.WHITE,
    }


def get_category_default_color() -> str:
    """
    카테고리의 기본 색상 반환
    
    Returns:
        str: 기본 카테고리 색상 (흰색)
    """
    return COLORS.WHITE


def get_break_default_color() -> str:
    """
    휴식 알림의 기본 색상 반환
    
    Returns:
        str: 기본 휴식 색상
    """
    return COLORS.BREAK_COLOR


def is_valid_hex_color(color: str) -> bool:
    """
    유효한 헥스 색상 코드인지 확인
    
    Args:
        color: 확인할 색상 코드
        
    Returns:
        bool: 유효한 헥스 색상 코드 여부
    """
    if not color or not color.startswith('#'):
        return False

    # #RGB 또는 #RRGGBB 형식 확인
    if len(color) == 4:  # #RGB
        return all(c in '0123456789ABCDEFabcdef' for c in color[1:])
    elif len(color) == 7:  # #RRGGBB
        return all(c in '0123456789ABCDEFabcdef' for c in color[1:])

    return False


# normalize_hex_color 함수 제거됨 - 현재 코드베이스에서 사용되지 않음
