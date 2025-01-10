# File paths and names
CONFIG_FILE = 'config.json'
LOG_FILE = 'pace_log.txt'
DB_FILE = 'pace_log.db'
ASSETS_DIR = 'assets'
ICONS_DIR = 'icons'
SOUNDS_DIR = 'sounds'

# Asset files
ICON_NAME = 'PaceKeeper'
ICON_PNG = f'{ICON_NAME}.png'
ICON_ICO = f'{ICON_NAME}.ico'
ICON_ICNS = f'{ICON_NAME}.icns'
LONG_BREAK_SOUND = 'long_brk.wav'
SHORT_BREAK_SOUND = 'short_brk.wav'

# App strings
APP_NAME = 'PaceKeeper'
APP_TITLE = APP_NAME

# Menu items
MENU_FILE = '파일'
MENU_SETTINGS = '설정'
MENU_VIEW_LOGS = '기록 보기'
MENU_EXIT = '종료'

# Status labels
STATUS_WAIT = '대기'
STATUS_STUDY = '작업'
STATUS_SHORT_BREAK = '짧은 휴식'
STATUS_LONG_BREAK = '긴 휴식' 

# Button labels
BTN_START = '시작'
BTN_STOP = '중지'
BTN_SUBMIT = '종료'
BTN_SEARCH = '검색'
LABEL_SEARCH_DATE = '종료일 (YYYY-MM-DD)'
LABEL_TAG = '태그: '

# Dialog titles
DIALOG_SETTINGS = '설정'
DIALOG_BREAK = '휴식'
DIALOG_TRACK = '기록'

# Error messages
LABEL_ERROR = '오류'
MSG_ERROR_SEARCH_DATE = '종료일 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력하세요.'
MSG_ERROR_DEFAULT = '오류 발생: {}'
MSG_ERROR_DATAMODEL = 'DataModel이 설정되지 않았습니다.'
MSG_ERROR_SETTINGS_LOAD = '설정 로드 오류: {}. 기본값 사용.'
MSG_ERROR_SETTINGS_SAVE = '설정 저장 오류: {}'
MSG_ERROR_ALARM_SOUND = '알람 재생 에러: {}'

# Messages
MSG_START_BREAK = '휴식을 시작하세요!'
MSG_BREAKTRACK_LOGS = 'PaceKeeper 기록'

# Database
DB_CREATE_TABLE = '''
    CREATE TABLE IF NOT EXISTS pace_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_date TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        message TEXT NOT NULL,
        tags TEXT
    )
'''

# Settings dialog labels
SETTINGS_LABEL_STUDY_TIME = "작업 시간(분):"
SETTINGS_LABEL_SHORT_BREAK = "짧은 휴식(분):"
SETTINGS_LABEL_LONG_BREAK = "긴 휴식(분):"
SETTINGS_LABEL_CYCLES = "사이클 수:"
BTN_SAVE = "저장"
BTN_CANCEL = "취소"

# Settings keys
SETTINGS_STUDY_TIME = 'study_time'
SETTINGS_SHORT_BREAK = 'short_break'
SETTINGS_LONG_BREAK = 'long_break'
SETTINGS_CYCLES = 'cycles'
SETTINGS_BREAK_DLG_PADDING_SIZE = 'break_dlg_padding_size'
SETTINGS_BREAK_SOUND_VOLUME = 'break_sound_volume'

# Default settings
DEFAULT_SETTINGS = {
    'study_time': 25,
    'short_break': 5,
    'long_break': 15,
    'cycles': 4,
    'break_dlg_padding_size': 70,
    'break_sound_volume': 80
}

# Config keys
CONFIG_DATA_MODEL = 'data_model'
