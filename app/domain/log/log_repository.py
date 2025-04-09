"""
PaceKeeper Qt - 로그 저장소
로그 데이터 액세스 및 조작 기능
"""

import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.config.db_manager import DBManager
from app.domain.category.category_repository import CategoryRepository
from app.domain.log.log_entity import LogEntity
from app.domain.tag.tag_repository import TagRepository


class LogRepository:
    """로그 데이터 저장소 클래스"""

    def __init__(
        self,
        db_manager: Optional[DBManager] = None,
        tag_repository: Optional[TagRepository] = None,
        category_repository: Optional[CategoryRepository] = None,
    ):
        """
        로그 저장소 초기화

        Args:
            db_manager: 데이터베이스 관리자 인스턴스
            tag_repository: 태그 저장소 인스턴스
            category_repository: 카테고리 저장소 인스턴스
        """
        self.db_manager = db_manager or DBManager()
        self.tag_repository = tag_repository or TagRepository(self.db_manager)
        self.category_repository = category_repository or CategoryRepository(
            self.db_manager
        )

    def create(self, log_entry: LogEntity) -> LogEntity:
        """
        새 로그 항목 생성

        Args:
            log_entry: 저장할 로그 항목 객체

        Returns:
            생성된 로그 항목 객체 (ID 포함)
        """
        # 문자열 형식의 시작/종료 날짜 사용

        # 로그 항목 저장
        query = """
        INSERT INTO logs (message, tags, start_date, end_date, state)
        VALUES (?, ?, ?, ?, ?)
        """
        log_id = self.db_manager.insert(
            query,
            (
                log_entry.message,
                log_entry.tags,
                log_entry.start_date,
                log_entry.end_date,
                log_entry.state,
            ),
        )
        log_entry.id = log_id

        # 이제 태그는 문자열로 직접 저장되므로 태그 관계 저장 불필요

        return log_entry

    def get_by_id(self, log_id: int) -> Optional[LogEntity]:
        """
        ID로 로그 항목 조회

        Args:
            log_id: 로그 항목 ID

        Returns:
            조회된 로그 항목 객체 또는 None
        """
        query = """
        SELECT id, message, tags, start_date, end_date, state
        FROM logs
        WHERE id = ?
        """
        result = self.db_manager.fetch_one(query, (log_id,))

        if not result:
            return None

        # 로그 항목 기본 정보
        log_entry = LogEntity(
            id=result["id"],
            message=result["message"],
            tags=result["tags"],
            start_date=result["start_date"],
            end_date=result["end_date"],
            state=result["state"],
        )

        # LogEntity는 태그와 카테고리를 직접 참조하지 않으므로 추가 조회 불필요

        return log_entry

    def get_all(self, limit: int = 100, offset: int = 0) -> List[LogEntity]:
        """
        모든 로그 항목 조회

        Args:
            limit: 반환할 최대 항목 수
            offset: 시작 오프셋

        Returns:
            로그 항목 객체 목록
        """
        query = """
        SELECT id, message, tags, start_date, end_date, state
        FROM logs
        ORDER BY start_date DESC
        LIMIT ? OFFSET ?
        """
        results = self.db_manager.fetch_all(query, (limit, offset))

        logs = []
        for result in results:
            # 로그 항목 기본 정보
            log_entry = LogEntity(
                id=result["id"],
                message=result["message"],
                tags=result["tags"],
                start_date=result["start_date"],
                end_date=result["end_date"],
                state=result["state"],
            )

            logs.append(log_entry)

        return logs

    def update(self, log_entry: LogEntity) -> bool:
        """
        로그 항목 정보 업데이트

        Args:
            log_entry: 업데이트할 로그 항목 객체

        Returns:
            성공 여부
        """
        if log_entry.id is None:
            return False

        # 로그 항목 업데이트
        query = """
        UPDATE logs
        SET message = ?, tags = ?, start_date = ?, end_date = ?, state = ?
        WHERE id = ?
        """
        self.db_manager.execute_query(
            query,
            (
                log_entry.message,
                log_entry.tags,
                log_entry.start_date,
                log_entry.end_date,
                log_entry.state,
                log_entry.id,
            ),
        )

        # 이제 태그는 문자열로 직접 저장되므로 태그 관계 관리 불필요

        return True

    def delete(self, log_id: int) -> bool:
        """
        로그 항목 삭제

        Args:
            log_id: 삭제할 로그 항목 ID

        Returns:
            성공 여부
        """
        query = """
        DELETE FROM logs
        WHERE id = ?
        """
        self.db_manager.execute_query(query, (log_id,))
        return True

    def search(self, search_term: str, limit: int = 100) -> List[LogEntity]:
        """
        로그 항목 검색

        Args:
            search_term: 검색어
            limit: 반환할 최대 항목 수

        Returns:
            검색 결과 로그 항목 목록
        """
        query = """
        SELECT id, message, tags, start_date, end_date, state
        FROM logs
        WHERE message LIKE ?
           OR tags LIKE ?
        ORDER BY start_date DESC
        LIMIT ?
        """
        # 검색어에 와일드카드 추가
        search_pattern = f"%{search_term}%"
        results = self.db_manager.fetch_all(
            query, (search_pattern, search_pattern, limit)
        )

        logs = []
        for result in results:
            # 로그 항목 기본 정보
            log_entry = LogEntity(
                id=result["id"],
                message=result["message"],
                tags=result["tags"],
                start_date=result["start_date"],
                end_date=result["end_date"],
                state=result["state"],
            )

            logs.append(log_entry)

        return logs

    def get_recent(self, limit: int = 10) -> List[LogEntity]:
        """
        최근 로그 항목 조회

        Args:
            limit: 반환할 최대 항목 수

        Returns:
            로그 항목 객체 목록
        """
        return self.get_all(limit=limit, offset=0)

    # 태그 관련 메서드는 이제 필요하지 않음 (tags가 문자열로 저장됨)
