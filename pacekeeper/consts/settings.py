# App strings
APP_NAME = 'PaceKeeper'
APP_TITLE = APP_NAME

# Asset files
ICON_NAME = 'pacekeeper'
ICON_PNG = f'{ICON_NAME}.png'
ICON_ICO = f'{ICON_NAME}.ico'
ICON_ICNS = f'{ICON_NAME}.icns'
LONG_BREAK_SOUND = 'long_brk.wav'
SHORT_BREAK_SOUND = 'short_brk.wav'

# File paths and names
CONFIG_FILE = 'config.json'
LOG_FILE = 'pace_log.txt'
DB_FILE = 'pace_log.db'
ASSETS_DIR = 'assets'
ICONS_DIR = 'icons'
SOUNDS_DIR = 'sounds'

# Database
CATEGORY_CREATE_TABLE = '''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        state SMALLINT DEFAULT 1
    )
'''

TAG_CREATE_TABLE = '''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category_id INTEGER NOT NULL,
        state SMALLINT DEFAULT 1
    )
'''

LOG_CREATE_TABLE = '''
    CREATE TABLE IF NOT EXISTS pace_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        message TEXT NOT NULL,
        tags TEXT CHECK( json_valid(tags) ),
        state SMALLINT DEFAULT 1
    )
'''

# Settings keys
SET_STUDY_TIME = 'study_time'
SET_SHORT_BREAK_TIME = 'short_break_time'
SET_LONG_BREAK_TIME = 'long_break_time'
SET_POMODORO_CYCLES = 'pomodoro_cycles'
SET_PADDING_SIZE = 'padding_size'
SET_SOUND_ENABLE = 'sound_enable'
SET_TTS_ENABLE = 'tts_enable'
SET_ALARM_VOLUME = 'alarm_volume'
SET_BREAK_COLOR = 'break_color'
SET_LANGUAGE = 'language'
SET_MAIN_DLG_WIDTH = 'main_dlg_width'
SET_MAIN_DLG_HEIGHT = 'main_dlg_height'

# Default settings
DEFAULT_SETTINGS = {
    SET_STUDY_TIME: 25,
    SET_SHORT_BREAK_TIME: 5,
    SET_LONG_BREAK_TIME: 15,
    SET_POMODORO_CYCLES: 4,
    SET_PADDING_SIZE: 100,
    SET_SOUND_ENABLE: True,
    SET_TTS_ENABLE: False,
    SET_ALARM_VOLUME: 80,
    SET_BREAK_COLOR: '#FDFFB6',
    SET_LANGUAGE: 'ko',
    SET_MAIN_DLG_WIDTH: 800,
    SET_MAIN_DLG_HEIGHT: 550
}

# 사용 가능한 언어 설정
AVAILABLE_LANGS = ['ko', 'en']
AVAILABLE_LANG_LABELS = ['한국어', 'English']
