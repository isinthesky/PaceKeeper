"""
PaceKeeper Qt - 데이터베이스 관리자
SQLite 데이터베이스 연결 및 기본 스키마 관리
"""

import os
import sqlite3
from contextlib import contextmanager
from typing import Optional, Tuple


class DBManager:
    """데이터베이스 관리 클래스"""

    def __init__(self, db_path: Optional[str] = None):
        """
        데이터베이스 관리자 초기화

        Args:
            db_path: 데이터베이스 파일 경로 (None일 경우 기본 경로 사용)
        """
        if db_path is None:
            # 기본 데이터베이스 파일 경로 설정
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            self.db_path = os.path.join(base_dir, "pace_log.db")
        else:
            self.db_path = db_path

        # 데이터베이스 초기화
        self.init_db()

    def init_db(self):
        """데이터베이스 초기화 및 테이블 생성"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 카테고리 테이블
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                color TEXT DEFAULT '#4a86e8',
                state INTEGER DEFAULT 1
            )
            """
            )

            # 태그 테이블
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                category_id INTEGER DEFAULT 0,
                state INTEGER DEFAULT 1
            )
            """
            )

            # 로그 테이블
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                tags TEXT DEFAULT '',
                start_date TEXT NOT NULL,
                end_date TEXT,
                state INTEGER DEFAULT 1
            )
            """
            )

            # 기본 카테고리 추가
            cursor.execute(
                """
            INSERT OR IGNORE INTO categories (id, name, description, color, state)
            VALUES (1, 'Work', 'Work related tasks', '#f44336', 1),
                   (2, 'Study', 'Study and learning activities', '#4a86e8', 1),
                   (3, 'Personal', 'Personal activities', '#4caf50', 1)
            """
            )

            conn.commit()

    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            # 외래 키 제약 조건 활성화
            conn.execute("PRAGMA foreign_keys = ON")
            # 열 이름으로 결과 접근 가능하도록 설정
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """
        쿼리 실행 및 결과 반환

        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터

        Returns:
            실행된 커서 객체
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def fetch_all(self, query: str, params: Tuple = ()) -> list:
        """
        쿼리 실행 후 모든 결과 반환

        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터

        Returns:
            실행 결과 목록
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """
        쿼리 실행 후 첫 번째 결과 반환

        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터

        Returns:
            실행 결과의 첫 번째 행 또는 None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def insert(self, query: str, params: Tuple = ()) -> int:
        """
        삽입 쿼리 실행 후 마지막 행 ID 반환

        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터

        Returns:
            마지막으로 삽입된 행의 ID, 삽입 실패 시 0
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            # lastrowid가 None일 수 있으니 기본값 0으로 설정
            return cursor.lastrowid or 0
