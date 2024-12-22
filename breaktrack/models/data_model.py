# breaktrack/models/data_model.py
import os
import sqlite3
from datetime import datetime
from breaktrack.utils import extract_tags

class DataModel:
    """
    SQLite DB + 텍스트 파일 로그를 함께 관리하는 데이터 모델
    (기간 검색, 태그 검색을 대비해 테이블 구조 개선)
    """
    def __init__(self, log_file='break_log.txt', db_file='break_log.db'):
        self.log_file = log_file
        self.db_file = db_file

        # 텍스트 로그 파일 초기화
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("Breaktrack Logs\n")
                f.write("====================\n")

        # DB 초기화
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()

            # 1) 테이블이 없으면 생성
            c.execute('''
                CREATE TABLE IF NOT EXISTS break_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_date TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    message TEXT NOT NULL,
                    tags TEXT
                )
            ''')
            conn.commit()

            # # 2) 혹시 기존 테이블 구조에 tags 컬럼이 없으면 추가 (이미 있으면 무시)
            # try:
            #     c.execute("SELECT tags FROM break_logs LIMIT 1")  
            # except sqlite3.OperationalError:
            #     # 'tags' 컬럼이 없는 경우
            #     c.execute("ALTER TABLE break_logs ADD COLUMN tags TEXT")
            #     conn.commit()

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