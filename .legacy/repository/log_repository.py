"""
PaceKeeper Qt - 로그 저장소
로그 데이터 액세스 및 조작 기능
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import sqlite3

from models.entities import LogEntry, Tag, Category
from models.repository.db_manager import DBManager
from models.repository.tag_repository import TagRepository
from models.repository.category_repository import CategoryRepository


class LogRepository:
    """로그 데이터 저장소 클래스"""
    
    def __init__(self, 
                 db_manager: Optional[DBManager] = None,
                 tag_repository: Optional[TagRepository] = None,
                 category_repository: Optional[CategoryRepository] = None):
        """
        로그 저장소 초기화
        
        Args:
            db_manager: 데이터베이스 관리자 인스턴스
            tag_repository: 태그 저장소 인스턴스
            category_repository: 카테고리 저장소 인스턴스
        """
        self.db_manager = db_manager or DBManager()
        self.tag_repository = tag_repository or TagRepository(self.db_manager)
        self.category_repository = category_repository or CategoryRepository(self.db_manager)
    
    def create(self, log_entry: LogEntry) -> LogEntry:
        """
        새 로그 항목 생성
        
        Args:
            log_entry: 저장할 로그 항목 객체
            
        Returns:
            생성된 로그 항목 객체 (ID 포함)
        """
        # 시작/종료 시간을 ISO 형식 문자열로 변환
        start_time_str = log_entry.start_time.isoformat() if log_entry.start_time else None
        end_time_str = log_entry.end_time.isoformat() if log_entry.end_time else None
        
        # 로그 항목 저장
        query = """
        INSERT INTO logs (message, start_time, end_time, duration, category_id)
        VALUES (?, ?, ?, ?, ?)
        """
        log_id = self.db_manager.insert(
            query, 
            (log_entry.message, start_time_str, end_time_str, log_entry.duration, log_entry.category_id)
        )
        log_entry.id = log_id
        
        # 태그 관계 저장
        if log_entry.tags:
            for tag in log_entry.tags:
                # 태그가 없으면 생성
                if tag.id is None:
                    tag = self.tag_repository.get_or_create(tag.name, tag.color)
                
                # 로그-태그 관계 저장
                self._add_tag_to_log(log_id, tag.id)
        
        return log_entry
    
    def get_by_id(self, log_id: int) -> Optional[LogEntry]:
        """
        ID로 로그 항목 조회
        
        Args:
            log_id: 로그 항목 ID
            
        Returns:
            조회된 로그 항목 객체 또는 None
        """
        query = """
        SELECT id, message, start_time, end_time, duration, category_id
        FROM logs
        WHERE id = ?
        """
        result = self.db_manager.fetch_one(query, (log_id,))
        
        if not result:
            return None
        
        # 로그 항목 기본 정보
        log_entry = LogEntry(
            id=result['id'],
            message=result['message'],
            start_time=datetime.fromisoformat(result['start_time']) if result['start_time'] else None,
            end_time=datetime.fromisoformat(result['end_time']) if result['end_time'] else None,
            duration=result['duration'],
            category_id=result['category_id']
        )
        
        # 카테고리 정보 조회
        if log_entry.category_id:
            log_entry.category = self.category_repository.get_by_id(log_entry.category_id)
        
        # 태그 정보 조회
        log_entry.tags = self._get_tags_for_log(log_id)
        
        return log_entry
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[LogEntry]:
        """
        모든 로그 항목 조회
        
        Args:
            limit: 반환할 최대 항목 수
            offset: 시작 오프셋
            
        Returns:
            로그 항목 객체 목록
        """
        query = """
        SELECT id, message, start_time, end_time, duration, category_id
        FROM logs
        ORDER BY start_time DESC
        LIMIT ? OFFSET ?
        """
        results = self.db_manager.fetch_all(query, (limit, offset))
        
        logs = []
        for result in results:
            # 로그 항목 기본 정보
            log_entry = LogEntry(
                id=result['id'],
                message=result['message'],
                start_time=datetime.fromisoformat(result['start_time']) if result['start_time'] else None,
                end_time=datetime.fromisoformat(result['end_time']) if result['end_time'] else None,
                duration=result['duration'],
                category_id=result['category_id']
            )
            
            # 카테고리 정보 조회
            if log_entry.category_id:
                log_entry.category = self.category_repository.get_by_id(log_entry.category_id)
            
            # 태그 정보 조회
            log_entry.tags = self._get_tags_for_log(log_entry.id)
            
            logs.append(log_entry)
        
        return logs
    
    def update(self, log_entry: LogEntry) -> bool:
        """
        로그 항목 정보 업데이트
        
        Args:
            log_entry: 업데이트할 로그 항목 객체
            
        Returns:
            성공 여부
        """
        if log_entry.id is None:
            return False
        
        # 시작/종료 시간을 ISO 형식 문자열로 변환
        start_time_str = log_entry.start_time.isoformat() if log_entry.start_time else None
        end_time_str = log_entry.end_time.isoformat() if log_entry.end_time else None
        
        # 로그 항목 업데이트
        query = """
        UPDATE logs
        SET message = ?, start_time = ?, end_time = ?, duration = ?, category_id = ?
        WHERE id = ?
        """
        self.db_manager.execute_query(
            query, 
            (log_entry.message, start_time_str, end_time_str, 
             log_entry.duration, log_entry.category_id, log_entry.id)
        )
        
        # 기존 태그 관계 삭제
        self._remove_all_tags_from_log(log_entry.id)
        
        # 새 태그 관계 추가
        for tag in log_entry.tags:
            # 태그가 없으면 생성
            if tag.id is None:
                tag = self.tag_repository.get_or_create(tag.name, tag.color)
            
            # 로그-태그 관계 저장
            self._add_tag_to_log(log_entry.id, tag.id)
        
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
    
    def search(self, search_term: str, limit: int = 100) -> List[LogEntry]:
        """
        로그 항목 검색
        
        Args:
            search_term: 검색어
            limit: 반환할 최대 항목 수
            
        Returns:
            검색 결과 로그 항목 목록
        """
        query = """
        SELECT DISTINCT l.id, l.message, l.start_time, l.end_time, l.duration, l.category_id
        FROM logs l
        LEFT JOIN log_tags lt ON l.id = lt.log_id
        LEFT JOIN tags t ON lt.tag_id = t.id
        LEFT JOIN categories c ON l.category_id = c.id
        WHERE l.message LIKE ?
           OR t.name LIKE ?
           OR c.name LIKE ?
        ORDER BY l.start_time DESC
        LIMIT ?
        """
        # 검색어에 와일드카드 추가
        search_pattern = f"%{search_term}%"
        results = self.db_manager.fetch_all(
            query, 
            (search_pattern, search_pattern, search_pattern, limit)
        )
        
        logs = []
        for result in results:
            # 로그 항목 기본 정보
            log_entry = LogEntry(
                id=result['id'],
                message=result['message'],
                start_time=datetime.fromisoformat(result['start_time']) if result['start_time'] else None,
                end_time=datetime.fromisoformat(result['end_time']) if result['end_time'] else None,
                duration=result['duration'],
                category_id=result['category_id']
            )
            
            # 카테고리 정보 조회
            if log_entry.category_id:
                log_entry.category = self.category_repository.get_by_id(log_entry.category_id)
            
            # 태그 정보 조회
            log_entry.tags = self._get_tags_for_log(log_entry.id)
            
            logs.append(log_entry)
        
        return logs
    
    def get_recent(self, limit: int = 10) -> List[LogEntry]:
        """
        최근 로그 항목 조회
        
        Args:
            limit: 반환할 최대 항목 수
            
        Returns:
            로그 항목 객체 목록
        """
        return self.get_all(limit=limit, offset=0)
    
    def _get_tags_for_log(self, log_id: int) -> List[Tag]:
        """
        로그 항목의 태그 목록 조회
        
        Args:
            log_id: 로그 항목 ID
            
        Returns:
            태그 객체 목록
        """
        query = """
        SELECT t.id, t.name, t.color
        FROM tags t
        JOIN log_tags lt ON t.id = lt.tag_id
        WHERE lt.log_id = ?
        """
        results = self.db_manager.fetch_all(query, (log_id,))
        
        return [
            Tag(
                id=result['id'],
                name=result['name'],
                color=result['color']
            )
            for result in results
        ]
    
    def _add_tag_to_log(self, log_id: int, tag_id: int) -> bool:
        """
        로그 항목에 태그 추가
        
        Args:
            log_id: 로그 항목 ID
            tag_id: 태그 ID
            
        Returns:
            성공 여부
        """
        try:
            query = """
            INSERT OR IGNORE INTO log_tags (log_id, tag_id)
            VALUES (?, ?)
            """
            self.db_manager.execute_query(query, (log_id, tag_id))
            return True
        except sqlite3.Error:
            return False
    
    def _remove_all_tags_from_log(self, log_id: int) -> bool:
        """
        로그 항목의 모든 태그 관계 삭제
        
        Args:
            log_id: 로그 항목 ID
            
        Returns:
            성공 여부
        """
        query = """
        DELETE FROM log_tags
        WHERE log_id = ?
        """
        self.db_manager.execute_query(query, (log_id,))
        return True
