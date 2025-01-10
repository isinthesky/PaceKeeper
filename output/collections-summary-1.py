# File: ./breaktrack/__init__.py



# File: ./breaktrack/utils.py

# utils.py
import os
import sys
import re
def resource_path(relative_path: str) -> str:
    """
    PyInstaller 환경 등에서 리소스 절대 경로를 반환
    """
    try:
        base_path = sys._MEIPASS  # PyInstaller 임시 폴더
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def extract_tags(message: str) -> list[str]:
    """
    message에서 태그 추출
    """
    tags = re.findall(r'#(\w+)', message)
    return tags


# File: ./breaktrack/main.py

# main.py
import wx
import wx.adv  # TaskBarIcon을 위한 import 추가
import os
from breaktrack.controllers.config_controller import ConfigController
from breaktrack.controllers.main_controller import MainController
from breaktrack.views.main_frame import MainFrame
from breaktrack.utils import resource_path
from breaktrack.const import ASSETS_DIR, ICONS_DIR, ICON_PNG, APP_NAME, APP_TITLE

def main():
    """메인 함수."""
    app = wx.App()

    # TaskBar 아이콘 설정
    icon_path = resource_path(os.path.join(ASSETS_DIR, ICONS_DIR, ICON_PNG))
    if os.path.exists(icon_path):
        app.SetAppDisplayName(APP_NAME)
        app_icon = wx.Icon(icon_path, wx.BITMAP_TYPE_PNG)
        taskbar = wx.adv.TaskBarIcon()
        taskbar.SetIcon(app_icon)

    # 설정/상태 관리 컨트롤러
    config_controller = ConfigController()

    # 메인 프레임 생성 + 메인 컨트롤러와 연결
    frame = MainFrame(None, title=APP_TITLE, config_controller=config_controller)
    MainController(frame, config_controller)

    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()


# File: ./breaktrack/const.py

# File paths and names
CONFIG_FILE = 'config.json'
LOG_FILE = 'break_log.txt'
DB_FILE = 'break_log.db'
ASSETS_DIR = '/assets'
ICONS_DIR = 'icons'
SOUNDS_DIR = 'sounds'

# Asset files
ICON_NAME = 'BreakTrack'
ICON_PNG = f'{ICON_NAME}.png'
ICON_ICO = f'{ICON_NAME}.ico'
ICON_ICNS = f'{ICON_NAME}.icns'
LONG_BREAK_SOUND = 'long_brk.wav'
SHORT_BREAK_SOUND = 'short_brk.wav'

# App strings
APP_NAME = 'Breaktrack'
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
MSG_BREAKTRACK_LOGS = 'Breaktrack Logs'

# Database
DB_CREATE_TABLE = '''
    CREATE TABLE IF NOT EXISTS break_logs (
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

# settings
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

# config.data_model
CONFIG_DATA_MODEL = 'data_model'


# File: ./breaktrack/models/setting_model.py

# models/settings_model.py
import json
import os
from breaktrack.const import CONFIG_FILE, DEFAULT_SETTINGS, MSG_ERROR_SETTINGS_LOAD, MSG_ERROR_SETTINGS_SAVE

class SettingsModel:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        print(self.config_file)
        self.default_settings = dict(DEFAULT_SETTINGS)
        self.settings = dict(self.default_settings)

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(MSG_ERROR_SETTINGS_LOAD.format(e))
                self.settings = dict(self.default_settings)
        else:
            self.save_settings()

    def save_settings(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(MSG_ERROR_SETTINGS_SAVE.format(e))

    def update_settings(self, new_settings: dict):
        self.settings.update(new_settings)
        self.save_settings()


# File: ./breaktrack/models/data_model.py

# breaktrack/models/data_model.py
import os
import sqlite3
from datetime import datetime
from breaktrack.utils import extract_tags
from breaktrack.const import LOG_FILE, DB_FILE, MSG_BREAKTRACK_LOGS, DB_CREATE_TABLE

class DataModel:
    """
    SQLite DB + 텍스트 파일 로그를 함께 관리하는 데이터 모델
    (기간 검색, 태그 검색을 대비해 테이블 구조 개선)
    """
    def __init__(self, log_file=LOG_FILE, db_file=DB_FILE):
        self.log_file = log_file
        self.db_file = db_file

        # 텍스트 로그 파일 초기화
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"{MSG_BREAKTRACK_LOGS}\n")
                f.write("====================\n")

        # DB 초기화
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute(DB_CREATE_TABLE)
            conn.commit()

    def log_break(self, message: str, tags: str=None):
        """
        새 로그를 DB와 텍스트 파일에 기록.
        tags: 쉼표로 구분된 태그 문자열 (예: "#rest,#study")
        """
        now = datetime.now()
        created_date = now.strftime("%Y-%m-%d")        # YYYY-MM-DD
        full_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        # message에서 태그 추출
        tags : list[str] = extract_tags(message)

        # 텍스트 로그
        with open(self.log_file, 'a', encoding='utf-8') as f:
            tag_info = f" [{', '.join(tags)}]" if tags else ""
            f.write(f"{full_timestamp}{tag_info} - {message}\n")

        # DB INSERT
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO break_logs (created_date, timestamp, message, tags)
                VALUES (?, ?, ?, ?)
            ''', (created_date, full_timestamp, message, ', '.join(tags)))
            conn.commit()

    def get_logs(self):
        """
        break_logs 테이블의 모든 로그 레코드를 최신순으로 가져온다.
        [(id, created_date, timestamp, message, tags), ...]
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, created_date, timestamp, message, tags
                FROM break_logs
                ORDER BY id DESC
            """)
            rows = c.fetchall()
        return rows

    def get_logs_by_period(self, start_date, end_date):
        """
        특정 기간(YYYY-MM-DD) 사이의 로그를 조회한다.
        ex) get_logs_by_period('2024-01-01', '2024-01-31')
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, created_date, timestamp, message, tags
                FROM break_logs
                WHERE created_date BETWEEN ? AND ?
                ORDER BY id DESC
            """, (start_date, end_date))
            rows = c.fetchall()
        return rows

    def get_logs_by_tag(self, tag_keyword):
        """
        태그 검색. 예) tag_keyword = '#rest'
        LIKE 검색으로 '#rest' 포함 여부를 체크.
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, created_date, timestamp, message, tags
                FROM break_logs
                WHERE tags LIKE ?
                ORDER BY id DESC
            """, (f"%{tag_keyword}%",))
            rows = c.fetchall()
        return rows

    def get_last_logs(self, limit=20):
        """
        DB에서 최신순으로 limit개 로그를 가져온다.
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, created_date, timestamp, message, tags
                FROM break_logs
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = c.fetchall()
        return rows

# File: ./breaktrack/controllers/timer_thread.py

import threading
import time
import wx

class TimerThread(threading.Thread):
    """메인 '작업 시간' 카운트다운을 담당하는 쓰레드"""
    
    def __init__(self, config_controller, main_frame, total_seconds):
        super().__init__()
        self.config = config_controller
        self.main_frame = main_frame
        self.total_seconds = total_seconds
        self._running = True

    def run(self):
        for remaining in range(self.total_seconds, -1, -1):
            if not self.config.is_running or not self._running:
                break

            mins, secs = divmod(remaining, 60)
            time_label = f"{mins:02d}:{secs:02d}"

            try:
                wx.CallAfter(self.main_frame.timer_label.SetLabel, time_label)
            except Exception:
                break

            time.sleep(1)

    def stop(self):
        self._running = False 

# File: ./breaktrack/controllers/main_controller.py

import time
import wx
import threading
from breaktrack.controllers.config_controller import ConfigController, AppStatus
from breaktrack.views.break_dialog import BreakDialog
from breaktrack.models.data_model import DataModel
from breaktrack.controllers.sound_manager import SoundManager
from breaktrack.controllers.timer_thread import TimerThread
from breaktrack.utils import resource_path
from breaktrack.const import CONFIG_DATA_MODEL, DIALOG_BREAK
class MainController:
    """
    메인 프레임과 상호작용하며,
    (1) Pomodoro cycle(공부->휴식->공부...) 흐름 제어
    (2) UI 이벤트 바인딩
    (3) 타이머 쓰레드 관리
    """

    def __init__(self, main_frame, config_controller: ConfigController):
        self.main_frame = main_frame
        self.config = config_controller
        self.sound_manager = SoundManager(self.config)

        # 사운드 파일 정의
        self.long_break_sound = resource_path("assets/sounds/long_brk.wav")
        self.short_break_sound = resource_path("assets/sounds/short_brk.wav")

        # 이벤트 바인딩
        self.main_frame.start_button.Bind(wx.EVT_BUTTON, self.toggle_timer)
        self.main_frame.Bind(wx.EVT_CLOSE, self.on_close)

        # TimerThread 초기값
        self.timer_thread = None

    def toggle_timer(self, event):
        """
        '시작' 또는 '중지' 버튼을 누를 때 실행.
        """
        if not self.config.is_running:
            self.start_timer()
        else:
            self.stop_timer()

    def start_timer(self):
        """
        타이머 시작 (공부 시간 -> 휴식 -> 반복)
        """
        self.config.start_app()
        self.main_frame.menu_bar.Enable(wx.ID_PREFERENCES, False)
        self.main_frame.start_button.SetLabel("중지")

        # Pomodoro 사이클 관리
        # 메인 쓰레드에서 진행하면 GUI가 멈출 수 있으므로 별도 쓰레드 사용
        self.cycle_thread = threading.Thread(target=self.run_pomodoro_cycle, daemon=True)
        self.cycle_thread.start()

    def stop_timer(self):
        """
        타이머 중지
        """
        self.config.stop_app()
        self.main_frame.menu_bar.Enable(wx.ID_PREFERENCES, True)
        self.main_frame.start_button.SetLabel("시작")

        # 메인 타이머 쓰레드 중지
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.stop()
            self.timer_thread.join(timeout=2)

        # UI 라벨 초기화
        wx.CallAfter(self.main_frame.timer_label.SetLabel, "00:00")

    def run_pomodoro_cycle(self):
        """
        - (1) '공부 시간' 카운트다운
        - (2) 사이클 횟수에 따라 '짧은 휴식' 또는 '긴 휴식' 결정
        - (3) 휴식 다이얼로그 표시
        - (4) 사용자 종료 또는 모든 사이클 반복
        """
        while self.config.is_running:
            self.config.increment_cycle()  # 사이클 증가

            # (A) 공부 시간 카운트다운
            study_time_min = self.config.get_setting("study_time", 25)
            total_seconds = study_time_min * 60
            self.start_study_countdown(total_seconds)

            if not self.config.is_running:
                break

            # (B) 휴식 시간 결정 (짧은 or 긴)
            if self.config.get_cycle() % self.config.get_setting("cycles", 4) == 0:
                # 긴 휴식
                self.sound_manager.play_sound(self.long_break_sound)
                break_min = self.config.get_setting("long_break", 15)
                self.config.set_status(AppStatus.LONG_BREAK)
            else:
                # 짧은 휴식
                self.sound_manager.play_sound(self.short_break_sound)
                break_min = self.config.get_setting("short_break", 5)
                self.config.set_status(AppStatus.SHORT_BREAK)

            # (C) 휴식 다이얼로그(모달) 표시
            wx.CallAfter(self.show_break_dialog, break_min)

            # 휴식 다이얼로그가 닫힐 때까지 대기
            while self.config.is_running and AppStatus.is_break(self.config.get_status()):
                time.sleep(1)

    def start_study_countdown(self, total_seconds):
        """
        공부 시간 카운트다운을 별도 TimerThread로 처리
        """
        self.timer_thread = TimerThread(
            config_controller=self.config,
            main_frame=self.main_frame,
            total_seconds=total_seconds
        )
        self.timer_thread.start()

        # 스레드 종료 대기
        self.timer_thread.join()

    def show_break_dialog(self, break_min):
        """
        휴식 다이얼로그 표시. 모달로 열림.
        """
        dlg = BreakDialog(
            parent=self.main_frame,
            title=DIALOG_BREAK,
            break_minutes=break_min,
            config_controller=self.config
        )

        dlg.ShowModal()
        dlg.Destroy()

        # 휴식 후 상태를 다시 STUDY로 복원
        if self.config.is_running:
            self.config.set_status(AppStatus.STUDY)

    def on_close(self, event):
        """
        메인 윈도우 닫기 처리
        """
        self.stop_timer()
        self.main_frame.Destroy()

# File: ./breaktrack/controllers/sound_manager.py

import pygame
import wx
from breaktrack.controllers.config_controller import ConfigController
from breaktrack.const import SETTINGS_BREAK_SOUND_VOLUME

class SoundManager:
    """알람 사운드 로직을 별도로 관리"""
    
    def __init__(self, config: ConfigController):
        self.config = config
        pygame.mixer.init()
        
    def play_sound(self, sound_file: str):
        """사운드 재생"""
        try:
            volume_percent = self.config.get_setting(SETTINGS_BREAK_SOUND_VOLUME)
            volume = volume_percent / 100.0
            
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()
        except Exception as e:
            wx.LogError(f"알람 재생 에러: {e}")
            
    def stop_sound(self):
        """사운드 정지"""
        pygame.mixer.music.stop() 

# File: ./breaktrack/controllers/config_controller.py

# controllers/config_controller.py
from enum import Enum
from dataclasses import dataclass
from breaktrack.models.setting_model import SettingsModel
from breaktrack.models.data_model import DataModel
from breaktrack.const import STATUS_WAIT, STATUS_STUDY, STATUS_SHORT_BREAK, STATUS_LONG_BREAK
from breaktrack.utils import resource_path

@dataclass
class StatusInfo:
    """상태 정보를 담는 데이터 클래스"""
    label: str
    value: int

class AppStatus(Enum):
    WAIT = StatusInfo(label=STATUS_WAIT, value=0)
    STUDY = StatusInfo(label=STATUS_STUDY, value=1)
    SHORT_BREAK = StatusInfo(label=STATUS_SHORT_BREAK, value=2)
    LONG_BREAK = StatusInfo(label=STATUS_LONG_BREAK, value=3)

    @property
    def label(self):
        return self.value.label

    @property
    def value_int(self):
        return self.value.value

    @classmethod
    def is_break(cls, status: 'AppStatus') -> bool:
        return status in [cls.SHORT_BREAK, cls.LONG_BREAK]

class ConfigController:
    """
    앱의 전역 상태 및 설정을 관리.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 한 번만 초기화
        if not hasattr(self, 'initialized'):
            self.settings_model = SettingsModel(resource_path("../assets/config.json"))
            self.settings_model.load_settings()
            self.data_model = DataModel()
            self.data_model.init_db()

            self._status = AppStatus.WAIT
            self.is_running = False
            self.current_cycle = 0

            self.initialized = True

    # --- 설정 접근/수정 ---
    def get_setting(self, key: str, default=None):
        return self.settings_model.settings.get(key, default)

    def update_settings(self, new_settings: dict):
        self.settings_model.update_settings(new_settings)

    # --- 상태/작업 흐름 ---
    def get_status(self) -> AppStatus:
        return self._status

    def set_status(self, status: AppStatus):
        self._status = status

    def start_app(self):
        self.is_running = True
        self.set_status(AppStatus.STUDY)

    def stop_app(self):
        self.is_running = False
        self.set_status(AppStatus.WAIT)
        self.current_cycle = 0

    def increment_cycle(self):
        self.current_cycle += 1

    def get_cycle(self):
        return self.current_cycle


# File: ./breaktrack/views/break_dialog.py

# views/break_dialog.py
import wx
import threading
import time
from breaktrack.controllers.config_controller import ConfigController
from breaktrack.const import DIALOG_BREAK, MSG_START_BREAK, MSG_ERROR_DEFAULT, BTN_SUBMIT, CONFIG_DATA_MODEL, SETTINGS_BREAK_DLG_PADDING_SIZE

class BreakDialog(wx.Dialog):
    """
    휴식 시간을 카운트다운하는 모달 다이얼로그.
    """
    def __init__(self, parent, title=DIALOG_BREAK, message=MSG_START_BREAK,
                 break_minutes=5, config_controller=None, on_break_end=None):
        """
        break_minutes: 휴식 시간 (분)
        config_controller: ConfigController 인스턴스
        """
        display_width, display_height = wx.GetDisplaySize()
        self.config :ConfigController = config_controller
        self._destroyed = False  # 객체 삭제 상태 추적

        super().__init__(
            parent,
            title=title,
            size=(display_width - self.config.get_setting(SETTINGS_BREAK_DLG_PADDING_SIZE, 70),
                  display_height - self.config.get_setting(SETTINGS_BREAK_DLG_PADDING_SIZE, 70)),
            style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP
        )

        self.break_minutes = break_minutes
        self.on_break_end = on_break_end
        self._running = True

        # UI 초기화
        self.init_ui(message)
        self.CenterOnScreen()

        # 카운트다운 스레드 시작
        self.break_thread = threading.Thread(target=self.run_countdown)
        self.break_thread.start()

    def init_ui(self, message):
        """
        UI 컴포넌트 배치
        1) 안내 문구
        2) 남은 휴식 시간 라벨
        3) 최근 5개 로그 표시 (신규 추가)
        4) 메시지 입력창 + 제출 버튼
        """
        self.SetBackgroundColour('#a3cca3')
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.tag_buttons_panel = wx.Panel(self)
        self.tag_buttons_sizer = wx.WrapSizer()
        self.tag_buttons_panel.SetSizer(self.tag_buttons_sizer)

        # (1) 안내 문구
        st = wx.StaticText(self, label=message, style=wx.ALIGN_CENTER)
        main_sizer.Add(st, flag=wx.ALIGN_CENTER | wx.TOP, border=20)

        # (2) 남은 시간 표시
        self.break_label = wx.StaticText(self, label="00:00", style=wx.ALIGN_CENTER)
        font = self.break_label.GetFont()
        font.PointSize += 10
        self.break_label.SetFont(font)
        main_sizer.Add(self.break_label, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)

        # (3) 최근 5개 로그 보여주기
        main_sizer.Add(self.create_recent_logs_ctrl(self), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)

        # (4) 태그 버튼들
        main_sizer.Add(self.tag_buttons_panel, flag=wx.EXPAND | wx.ALL, border=10)

        # (4) 사용자 입력 필드 + 종료 버튼
        self.user_input = wx.TextCtrl(self, value="", style=wx.TE_PROCESS_ENTER)
        self.user_input.Bind(wx.EVT_TEXT, self.on_text_change)
        main_sizer.Add(self.user_input, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=20)

        self.submit_btn = wx.Button(self, label=BTN_SUBMIT)
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit)
        self.submit_btn.Enable(False)  # 초기 비활성화
        main_sizer.Add(self.submit_btn, flag=wx.ALIGN_CENTER | wx.ALL, border=20)

        self.SetSizer(main_sizer)

    def create_recent_logs_ctrl(self, parent) -> wx.StaticBoxSizer:
        """
        '최근 5개 기록' 섹션(StaticBox + ListCtrl) 만들기
        """
        box = wx.StaticBox(parent, label="최근 5개 기록")
        box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        # ListCtrl 생성 (보고서 스타일)
        self.recent_logs_lc = wx.ListCtrl(
            box,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN,
        )
        
        # 컬럼 추가
        self.recent_logs_lc.InsertColumn(0, "시간", format=wx.LIST_FORMAT_CENTER, width=160)
        self.recent_logs_lc.InsertColumn(1, "메시지", format=wx.LIST_FORMAT_LEFT, width=500)
        self.recent_logs_lc.InsertColumn(2, "태그", format=wx.LIST_FORMAT_LEFT, width=300)
        
        # 데이터 로드
        self.load_recent_logs()
        
        self.recent_logs_lc.SetMinSize((300, 250))
        box_sizer.Add(self.recent_logs_lc, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        return box_sizer

    def load_recent_logs(self):
        """
        DB에서 최근 5개 로그를 조회하여 ListCtrl에 표시
        """
        if self.config and hasattr(self.config, CONFIG_DATA_MODEL):
            # 기존 항목 삭제
            self.recent_logs_lc.DeleteAllItems()

            # 태그 집합 초기화
            unique_tags = set()
            
            rows = self.config.data_model.get_last_logs(10)
            rows.reverse()
            for idx, row in enumerate(rows):
                log_time = row[2]   # timestamp
                log_msg = row[3]    # message
                log_tags = row[4]   # tags

                # ListCtrl에 항목 추가
                index = self.recent_logs_lc.InsertItem(idx, log_time)
                self.recent_logs_lc.SetItem(index, 1, log_msg)
                self.recent_logs_lc.SetItem(index, 2, log_tags or "")

                # 태그 추출 및 집합에 추가
                if log_tags:
                    tags = [tag.strip() for tag in log_tags.split(',')]
                    unique_tags.update(tags)
            
            # 기존 태그 버튼들 제거
            for child in self.tag_buttons_panel.GetChildren():
                child.Destroy()
            
            # 새로운 태그 버튼들 생성
            for tag in sorted(unique_tags):
                if tag:  # 빈 태그 제외
                    btn = self.create_tag_button(tag)
                    self.tag_buttons_sizer.Add(btn, 0, wx.ALL, 5)
            
            self.tag_buttons_panel.Layout()
        
    def create_tag_button(self, tag: str) -> wx.Button:
        """
        둥근 모서리의 태그 버튼 생성
        """
        btn = wx.Button(self.tag_buttons_panel, label=tag)
                
        # 클릭 이벤트 바인딩
        btn.Bind(wx.EVT_BUTTON, lambda evt, t=tag: self.on_tag_button_click(evt, t))
        
        return btn
    
    def on_tag_button_click(self, event, tag: str):
        """
        태그 버튼 클릭 시 입력창에 태그 추가
        """
        current_text = self.user_input.GetValue()
        if not tag.startswith('#'):
            tag = f"#{tag}"
        
        # 이미 해당 태그가 있는지 확인
        if tag not in current_text:
            # 입력창이 비어있지 않고 마지막 문자가 공백이 아니면 공백 추가
            if current_text and not current_text.endswith(' '):
                current_text += ' '
            current_text += f"{tag} "
            self.user_input.SetValue(current_text)

    def run_countdown(self):
        """
        휴식 시간 카운트다운 (break_minutes * 60초)
        """
        remaining = self.break_minutes * 60
        while remaining >= 0 and self._running:
            mins, secs = divmod(remaining, 60)
            if not self._destroyed:  # 객체가 살아있을 때만 UI 업데이트
                try:
                    wx.CallAfter(self.break_label.SetLabel, f"{mins:02d}:{secs:02d}")
                except Exception as e:
                    self.config.data_model.log_break(MSG_ERROR_DEFAULT.format(e))
                    break
            time.sleep(1)
            remaining -= 1

    def on_text_change(self, event):
        """
        텍스트 입력창에 내용이 있어야만 '종료' 버튼 활성화
        """
        user_text = self.user_input.GetValue().strip()
        self.submit_btn.Enable(bool(user_text))

    def on_submit(self, event):
        """
        사용자가 '종료' 버튼을 누르면:
        1) 카운트다운 스레드 종료
        2) DB에 메시지 로그 기록
        3) 로그 목록 갱신
        4) 다이얼로그 닫기
        """
        self._running = False
        self._destroyed = True  # 객체가 곧 삭제될 것임을 표시
        user_text = self.user_input.GetValue().strip()

        # DB 저장
        if hasattr(self.config, CONFIG_DATA_MODEL) and user_text:
            self.config.data_model.log_break(user_text)
            self.load_recent_logs()  # 로그 목록 갱신

        if self.on_break_end:
            self.on_break_end()

        # 스레드가 완전히 종료될 때까지 잠시 대기
        if self.break_thread and self.break_thread.is_alive():
            self.break_thread.join(timeout=1)

        self.EndModal(wx.ID_OK)

# File: ./breaktrack/views/main_frame.py

# views/main_frame.py
import wx
import os
from breaktrack.views.settings_dialog import SettingsDialog
from breaktrack.views.track_dialog import TrackDialog
from breaktrack.utils import resource_path
from breaktrack.const import (
    APP_TITLE, ASSETS_DIR, ICONS_DIR, ICON_ICO,
    MENU_FILE, MENU_SETTINGS, MENU_VIEW_LOGS, MENU_EXIT,
    BTN_START
)

class MainFrame(wx.Frame):
    def __init__(self, parent, title=APP_TITLE, config_controller=None):
        super().__init__(parent, title=title, size=(300, 200))
        self.config_controller = config_controller

        icon_path = resource_path(os.path.join(ASSETS_DIR, ICONS_DIR, ICON_ICO))
        if os.path.exists(icon_path):
            self.SetIcon(wx.Icon(icon_path))

        self.init_menu()

        # 메인 패널
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 타이머 라벨
        self.timer_label = wx.StaticText(panel, label="00:00", style=wx.ALIGN_CENTER)
        font = self.timer_label.GetFont()
        font.PointSize += 20
        font = font.Bold()
        self.timer_label.SetFont(font)
        vbox.Add(self.timer_label, flag=wx.EXPAND | wx.ALL, border=20)

        # 시작/중지 버튼
        self.start_button = wx.Button(panel, label=BTN_START)
        vbox.Add(self.start_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=20)

        panel.SetSizer(vbox)

    def init_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        settings_item = file_menu.Append(wx.ID_PREFERENCES, f"{MENU_SETTINGS}\tCtrl+S")
        track_item = file_menu.Append(wx.ID_ANY, f"{MENU_VIEW_LOGS}\tCtrl+L")
        exit_item = file_menu.Append(wx.ID_EXIT, f"{MENU_EXIT}\tCtrl+Q")

        menu_bar.Append(file_menu, MENU_FILE)
        self.SetMenuBar(menu_bar)
        self.menu_bar = menu_bar

        # 이벤트 바인딩
        self.Bind(wx.EVT_MENU, self.on_open_settings, settings_item)
        self.Bind(wx.EVT_MENU, self.on_show_track, track_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)

    def on_open_settings(self, event):
        dialog = SettingsDialog(self, self.config_controller)
        if dialog.ShowModal() == wx.ID_OK:
            pass
        dialog.Destroy()

    def on_show_track(self, event):
        dlg = TrackDialog(self, self.config_controller)
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, event):
        self.Close()


# File: ./breaktrack/views/settings_dialog.py

# views/settings_dialog.py
import wx
from breaktrack.const import (
    MENU_SETTINGS, BTN_SAVE, BTN_CANCEL,
    SETTINGS_LABEL_STUDY_TIME, SETTINGS_LABEL_SHORT_BREAK, SETTINGS_LABEL_LONG_BREAK, SETTINGS_LABEL_CYCLES, 
    SETTINGS_STUDY_TIME, SETTINGS_SHORT_BREAK, SETTINGS_LONG_BREAK, SETTINGS_CYCLES,
    SETTINGS_BREAK_SOUND_VOLUME
)

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, config_controller):
        super().__init__(parent, title=MENU_SETTINGS, size=(350, 350),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        self.config = config_controller
        self.InitUI()
        self.Center()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # study_time
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.StaticText(panel, label=SETTINGS_LABEL_STUDY_TIME), flag=wx.RIGHT, border=8)
        self.study_time = wx.SpinCtrl(
            panel, value=str(self.config.get_setting(SETTINGS_STUDY_TIME, 25)),
            min=1, max=120
        )
        hbox1.Add(self.study_time, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND | wx.ALL, border=10)

        # short_break
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(wx.StaticText(panel, label=SETTINGS_LABEL_SHORT_BREAK), flag=wx.RIGHT, border=8)
        self.short_break = wx.SpinCtrl(
            panel, value=str(self.config.get_setting(SETTINGS_SHORT_BREAK, 5)),
            min=1, max=60
        )
        hbox2.Add(self.short_break, proportion=1)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.ALL, border=10)

        # long_break
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(wx.StaticText(panel, label=SETTINGS_LABEL_LONG_BREAK), flag=wx.RIGHT, border=8)
        self.long_break = wx.SpinCtrl(
            panel, value=str(self.config.get_setting(SETTINGS_LONG_BREAK, 15)),
            min=1, max=120
        )
        hbox3.Add(self.long_break, proportion=1)
        vbox.Add(hbox3, flag=wx.EXPAND | wx.ALL, border=10)

        # cycles
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(wx.StaticText(panel, label=SETTINGS_LABEL_CYCLES), flag=wx.RIGHT, border=8)
        self.cycles = wx.SpinCtrl(
            panel, value=str(self.config.get_setting(SETTINGS_CYCLES, 4)),
            min=1, max=20
        )
        hbox4.Add(self.cycles, proportion=1)
        vbox.Add(hbox4, flag=wx.EXPAND | wx.ALL, border=10)

        # --- break_sound_volume ---
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        volume_label = wx.StaticText(panel, label="알람 볼륨 (0 ~ 100):")
        hbox5.Add(volume_label, flag=wx.RIGHT, border=8)
        current_volume = self.config.get_setting(SETTINGS_BREAK_SOUND_VOLUME, 50)  # 기본값 50
        self.break_sound_volume_slider = wx.Slider(
            panel, value=current_volume, minValue=0, maxValue=100,
            style=wx.SL_HORIZONTAL | wx.SL_LABELS
        )
        hbox5.Add(self.break_sound_volume_slider, proportion=1)
        vbox.Add(hbox5, flag=wx.EXPAND | wx.ALL, border=10) 
        
        # 버튼
        hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, wx.ID_OK, label=BTN_SAVE)
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, label=BTN_CANCEL)
        hbox_btn.Add(btn_ok)
        hbox_btn.Add(btn_cancel, flag=wx.LEFT, border=10)
        vbox.Add(hbox_btn, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        panel.SetSizer(vbox)

        # 이벤트
        btn_ok.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event):
        new_settings = {
            SETTINGS_STUDY_TIME: self.study_time.GetValue(),
            SETTINGS_SHORT_BREAK: self.short_break.GetValue(),
            SETTINGS_LONG_BREAK: self.long_break.GetValue(),
            SETTINGS_CYCLES: self.cycles.GetValue(),
            SETTINGS_BREAK_SOUND_VOLUME: self.break_sound_volume_slider.GetValue()
        }
        self.config.update_settings(new_settings)
        self.EndModal(wx.ID_OK)


# File: ./breaktrack/views/track_dialog.py

# views/track_dialog.py
import wx
from datetime import date, datetime, timedelta
from breaktrack.const import (
    DIALOG_TRACK, MSG_ERROR_DATAMODEL, BTN_SEARCH, LABEL_SEARCH_DATE,
    LABEL_TAG, LABEL_ERROR, MSG_ERROR_SEARCH_DATE, CONFIG_DATA_MODEL,
)

class TrackDialog(wx.Dialog):
    def __init__(self, parent, config_controller):
        super().__init__(parent, title=DIALOG_TRACK, size=(800, 800),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        self.config = config_controller

        # 종료일 기본값: 오늘
        end_dt = date.today()
        start_dt = end_dt - timedelta(days=90)
        self.selected_start_date = start_dt.strftime("%Y-%m-%d")
        self.selected_end_date = end_dt.strftime("%Y-%m-%d")

        self.InitUI()
        self.Center()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 레이블
        title_label = wx.StaticText(panel, label=DIALOG_TRACK, style=wx.ALIGN_CENTER)
        font = title_label.GetFont()
        font = font.Bold()
        title_label.SetFont(font)
        vbox.Add(title_label, flag=wx.EXPAND | wx.ALL, border=10)

        # ---------------------------------------------------------------------
        # (1) 검색 영역: 날짜 범위 + 태그 + 검색 버튼
        # ---------------------------------------------------------------------
        search_panel = wx.Panel(panel)
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # -- 기간 선택 버튼들 --
        # 1년 / 3달 / 1달 / 1주 / 1일
        period_buttons = [
            ("1년", 365),
            ("3달", 90),
            ("1달", 30),
            ("1주", 7),
            ("1일", 1),
        ]
        for label, days in period_buttons:
            btn = wx.Button(search_panel, label=label, size=(40, -1))
            # days를 클로저로 캡처하기 위해 람다 대신 함수 사용
            btn.Bind(wx.EVT_BUTTON, lambda evt, d=days: self.on_period_button(evt, d))
            search_sizer.Add(btn, 0, wx.RIGHT, 5)

        # 종료일 (기본값: 오늘)
        search_sizer.Add(wx.StaticText(search_panel, label=f"{LABEL_SEARCH_DATE}"),
                         0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        today_str = date.today().strftime("%Y-%m-%d")
        self.end_date_tc = wx.TextCtrl(search_panel, value=today_str, size=(100, -1), style=wx.TE_CENTER)
        search_sizer.Add(self.end_date_tc, 0, wx.RIGHT, 10)

        # 태그
        search_sizer.Add(wx.StaticText(search_panel, label=LABEL_TAG),
                         0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.tag_tc = wx.TextCtrl(search_panel, size=(100, -1))
        search_sizer.Add(self.tag_tc, 0, wx.RIGHT, 10)

        # 검색 버튼
        search_btn = wx.Button(search_panel, label=BTN_SEARCH)
        search_btn.Bind(wx.EVT_BUTTON, self.on_search)
        search_sizer.Add(search_btn, 0, wx.RIGHT, 10)

        search_panel.SetSizer(search_sizer)
        vbox.Add(search_panel, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)

        # ListCtrl: 테이블 형태로 로그 표시
        self.list_ctrl = wx.ListCtrl(panel, style=wx.LC_REPORT)
        self.list_ctrl.InsertColumn(0, "ID", width=50, format=wx.LIST_FORMAT_RIGHT)
        self.list_ctrl.InsertColumn(1, "Timestamp", width=180, format=wx.LIST_FORMAT_CENTER)
        self.list_ctrl.InsertColumn(2, "Message", width=340, format=wx.LIST_FORMAT_LEFT)
        self.list_ctrl.InsertColumn(3, "Tags", width=140, format=wx.LIST_FORMAT_LEFT)

        vbox.Add(self.list_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        panel.SetSizer(vbox)

        self.load_all_logs()

    def load_all_logs(self):
        """
        DB에서 전체 로그를 가져와서 ListCtrl에 표시
        """
        if hasattr(self.config, "data_model"):
            rows = self.config.data_model.get_logs()
        else:
            rows = []
        self.load_rows(rows)

    def load_rows(self, rows):
        """
        ListCtrl 초기화 후, rows 데이터(ID, created_date, timestamp, message, tags) 출력
        """
        self.list_ctrl.DeleteAllItems()  # 기존 내용 초기화

        for row in rows:
            # row 예: (id, created_date, timestamp, message, tags)
            # 인덱스별로 컬럼에 매핑
            idx = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), str(row[0]))
            self.list_ctrl.SetItem(idx, 1, str(row[2]))  # timestamp
            self.list_ctrl.SetItem(idx, 2, str(row[3]))  # message
            self.list_ctrl.SetItem(idx, 3, str(row[4]))  # tags

    def on_period_button(self, event, days):
        """
        기간 버튼(1년, 3달, 1달, 1주, 1일) 클릭 시:
        종료일에서 days만큼 빼서 start_date를 결정하고 검색을 실행
        """
        end_date_str = self.end_date_tc.GetValue().strip()
        if not end_date_str:
            # 종료일이 비어있다면, 오늘 날짜로 설정
            end_date_str = date.today().strftime("%Y-%m-%d")
            self.end_date_tc.SetValue(end_date_str)

        # 종료일 파싱
        try:
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            wx.MessageBox(MSG_ERROR_SEARCH_DATE, LABEL_ERROR, wx.OK | wx.ICON_ERROR)
            return

        # 종료일에서 days일 전을 시작일로
        start_dt = end_dt - timedelta(days=days)
        self.selected_start_date = start_dt.strftime("%Y-%m-%d")

        # 곧바로 검색 로직 실행
        self.on_search(None)


    def on_search(self, event):
        """
        '검색' 버튼 클릭 시 날짜 범위 + 태그 검색을 수행
        """
        start_date = self.selected_start_date
        end_date = self.selected_end_date
        tag_keyword = self.tag_tc.GetValue().strip()        # 예: "#rest"

        # 데이터 모델이 있는지 확인
        if not hasattr(self.config, CONFIG_DATA_MODEL):
            wx.MessageBox(MSG_ERROR_DATAMODEL, LABEL_ERROR, wx.OK | wx.ICON_ERROR)
            return

        data_model = self.config.data_model

        # (A) 날짜 범위가 둘 다 입력된 경우 => get_logs_by_period
        #     아니면 => get_logs
        rows_date = None
        if start_date and end_date:
            rows_date = set(data_model.get_logs_by_period(start_date, end_date))
        else:
            # 날짜 범위가 주어지지 않았다면 전체 조회
            rows_date = set(data_model.get_logs())

        # (B) 태그가 입력된 경우 => get_logs_by_tag
        rows_tag = None
        if tag_keyword:
            rows_tag = set(data_model.get_logs_by_tag(tag_keyword))
        else:
            # 태그가 없으면 전체 조회
            rows_tag = set(data_model.get_logs())

        # (C) 날짜/태그 교집합
        #     두 조건이 모두 주어지면, 그 결과를 intersection
        intersect_rows = rows_date.intersection(rows_tag)

        # 리스트를 id DESC 순으로 정렬 (row[0] = id)
        sorted_rows = sorted(list(intersect_rows), key=lambda x: x[0], reverse=True)

        # 리스트에 표시
        self.load_rows(sorted_rows)

    def on_close(self, event):
        # 다이얼로그 종료
        self.Destroy()
