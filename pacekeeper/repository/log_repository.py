# repositories/sqlite_log_repository.py
import os
import sqlite3
from datetime import datetime
from typing import List, Tuple
from pacekeeper.consts.settings import LOG_FILE, DB_FILE, DB_CREATE_TABLE
from pacekeeper.utils import extract_tags
from pacekeeper.consts.labels import load_language_resource
from icecream import ic

lang_res = load_language_resource()

class SQLiteLogRepository:
    def __init__(self, log_file=LOG_FILE, db_file=DB_FILE):
        self.log_file = log_file
        self.db_file = db_file

        # 텍스트 로그 파일 초기화
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"{lang_res.messages['PACEKEEPER_LOGS']}\n")
                f.write("====================\n")
        
        # DB 초기화
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute(DB_CREATE_TABLE)
            conn.commit()

    def add_study_log(self, message: str) -> None:
        """
        학습 로그 추가 메서드
        """
        
        ic(f"add_study_log: {message}")
        now = datetime.now()
        created_date = now.strftime("%Y-%m-%d")
        full_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        tags: list[str] = extract_tags(message)

        # 텍스트 로그 기록
        with open(self.log_file, 'a', encoding='utf-8') as f:
            tag_info = f" [{', '.join(tags)}]" if tags else ""
            f.write(f"{full_timestamp}{tag_info} - {message}\n")

        # DB INSERT
        with sqlite3.connect(self.db_file) as conn:
            ic(f"DB INSERT: {created_date}, {full_timestamp}, {message}, {', '.join(tags)}")
            c = conn.cursor()
            c.execute('''
                INSERT INTO pace_logs (created_date, timestamp, message, tags)
                VALUES (?, ?, ?, ?)
            ''', (created_date, full_timestamp, message, ', '.join(tags)))
            conn.commit()

    def _format_tags(self, tags_str: str) -> str:
        """
        태그 문자열을 쉼표를 기준으로 분리한 후, 각 태그 앞에 '#'가 붙어있지 않으면 추가하여 다시 문자열로 반환합니다.
        """
        if not tags_str:
            return ""
        # 쉼표로 분리하고 공백 제거 후, 각각의 태그 앞에 '#' 접두어 추가
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        formatted_tags = [tag if tag.startswith('#') else '#' + tag for tag in tags]
        return ", ".join(formatted_tags)

    def _process_rows(self, rows: List[Tuple]) -> List[Tuple]:
        """
        조회된 로그 튜플 리스트의 각 항목에 대해, 태그 정보를 형식화 처리합니다.
        각 튜플의 구조: (id, created_date, timestamp, message, tags)
        """
        processed = []
        for row in rows:
            new_tags = self._format_tags(row[4])
            processed.append((row[0], row[1], row[2], row[3], new_tags))
        return processed

    def get_logs(self) -> List[Tuple]:
        """
        모든 로그 조회 메서드 (state가 1 이상인 활성 로그만 조회)
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, created_date, timestamp, message, tags
                FROM pace_logs
                WHERE state >= 1
                ORDER BY id DESC
            """)
            rows = c.fetchall()
        return self._process_rows(rows)

    def get_logs_by_period(self, start_date: str, end_date: str) -> List[Tuple]:
        """
        기간 내의 활성 로그 조회 메서드 (state가 1 이상인 로그만 조회)
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, created_date, timestamp, message, tags
                FROM pace_logs
                WHERE created_date BETWEEN ? AND ? AND state >= 1
                ORDER BY id DESC
            """, (start_date, end_date))
            rows = c.fetchall()
        return self._process_rows(rows)

    def get_logs_by_tag(self, tag_keyword: str) -> List[Tuple]:
        """
        지정된 태그를 포함하는 활성 로그 조회 메서드 (state가 1 이상인 로그만 조회)
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, created_date, timestamp, message, tags
                FROM pace_logs
                WHERE tags LIKE ? AND state >= 1
                ORDER BY id DESC
            """, (f"%{tag_keyword}%",))
            rows = c.fetchall()
        return self._process_rows(rows)

    def get_last_logs(self, limit: int = 20) -> List[Tuple]:
        """
        최근 활성 로그들을 조회하는 메서드 (state가 1 이상인 로그만 조회)
        """
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, created_date, timestamp, message, tags
                FROM pace_logs
                WHERE state >= 1
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = c.fetchall()
        return self._process_rows(rows)

    def delete_logs_by_ids(self, ids: List[int]) -> None:
        """
        주어진 로그 ID 리스트에 해당하는 로그들의 state를 0으로 업데이트 (soft delete)
        """
        if not ids:
            return
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            placeholders = ",".join("?" for _ in ids)
            query = f"UPDATE pace_logs SET state=0 WHERE id IN ({placeholders})"
            c.execute(query, ids)
            conn.commit()