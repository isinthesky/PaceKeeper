"""
PaceKeeper Qt - 상수 모듈
애플리케이션 전반에서 사용할 상수 정의
"""

from enum import Enum, auto


class TimerState(Enum):
    """타이머 상태 열거형"""

    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()
    BREAK = auto()


class SessionType(Enum):
    """세션 타입 열거형"""

    POMODORO = auto()
    SHORT_BREAK = auto()
    LONG_BREAK = auto()


# 애플리케이션 정보
APP_NAME = "PaceKeeper"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Simple and effective time management tool"
APP_AUTHOR = "PaceKeeper Team"

# 타이머 관련 상수
DEFAULT_POMODORO_TIME = 25  # 기본 뽀모도로 시간 (분)
DEFAULT_SHORT_BREAK_TIME = 5  # 기본 짧은 휴식 시간 (분)
DEFAULT_LONG_BREAK_TIME = 15  # 기본 긴 휴식 시간 (분)
DEFAULT_LONG_BREAK_INTERVAL = 4  # 긴 휴식 간격 (뽀모도로 세션 수)

# 파일 경로 관련 상수
CONFIG_FILENAME = "config.json"
LOG_DB_FILENAME = "pace_log.db"

# UI 관련 상수
UI_DEFAULT_WIDTH = 800
UI_DEFAULT_HEIGHT = 500
UI_MIN_WIDTH = 400
UI_MIN_HEIGHT = 300

# 색상 코드 (QSS에서 사용)
COLOR_PRIMARY = "#4a86e8"
COLOR_SECONDARY = "#6c757d"
COLOR_SUCCESS = "#4caf50"
COLOR_DANGER = "#f44336"
COLOR_WARNING = "#ff9800"
COLOR_INFO = "#17a2b8"
COLOR_LIGHT = "#f8f9fa"
COLOR_DARK = "#343a40"
