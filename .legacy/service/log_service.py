"""
PaceKeeper Qt - 로그 서비스
로그 관련 비즈니스 로직 처리
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal

from models.entities import LogEntry, Tag, Category
from models.repository.log_repository import LogRepository
from models.service.tag_service import TagService


class LogService(QObject):
    """로그 서비스 클래스"""
    
    # 시그널 정의
    logCreated = pyqtSignal(LogEntry)
    logUpdated = pyqtSignal(LogEntry)
    logDeleted = pyqtSignal(int)  # 로그 ID
    logsChanged = pyqtSignal()  # 로그 목록 변경
    
    def __init__(self, log_repository: Optional[LogRepository] = None,
                 tag_service: Optional[TagService] = None):
        """
        로그 서비스 초기화
        
        Args:
            log_repository: 로그 저장소 인스턴스
            tag_service: 태그 서비스 인스턴스
        """
        super().__init__()
        self.repository = log_repository or LogRepository()
        self.tag_service = tag_service or TagService()
    
    def create_log(self, message: str, category_id: Optional[int] = None,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  duration: int = 0) -> LogEntry:
        """
        새 로그 항목 생성
        
        Args:
            message: 로그 메시지
            category_id: 카테고리 ID
            start_time: 시작 시간
            end_time: 종료 시간
            duration: 지속 시간 (초)
            
        Returns:
            생성된 로그 항목 객체
        """
        # 메시지 정제 (양쪽 공백 제거)
        clean_message = message.strip()
        
        if not clean_message:
            raise ValueError("로그 메시지는 공백일 수 없습니다.")
        
        # 시간 정보 처리
        if start_time is None:
            start_time = datetime.now()
        
        if end_time is None and duration > 0:
            end_time = start_time + timedelta(seconds=duration)
        
        if end_time is not None and duration == 0:
            duration = int((end_time - start_time).total_seconds())
        
        # 메시지에서 태그 추출
        tags = self.tag_service.parse_tags_from_text(clean_message)
        
        # 로그 항목 생성
        log_entry = LogEntry(
            message=clean_message,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            category_id=category_id,
            tags=tags
        )
        
        # 저장소에 저장
        created_log = self.repository.create(log_entry)
        
        # 시그널 발생
        self.logCreated.emit(created_log)
        self.logsChanged.emit()
        
        return created_log
    
    def get_log(self, log_id: int) -> Optional[LogEntry]:
        """
        ID로 로그 항목 조회
        
        Args:
            log_id: 로그 항목 ID
            
        Returns:
            조회된 로그 항목 객체 또는 None
        """
        return self.repository.get_by_id(log_id)
    
    def get_all_logs(self, limit: int = 100, offset: int = 0) -> List[LogEntry]:
        """
        모든 로그 항목 조회
        
        Args:
            limit: 반환할 최대 항목 수
            offset: 시작 오프셋
            
        Returns:
            로그 항목 객체 목록
        """
        return self.repository.get_all(limit, offset)
    
    def get_recent_logs(self, limit: int = 10) -> List[LogEntry]:
        """
        최근 로그 항목 조회
        
        Args:
            limit: 반환할 최대 항목 수
            
        Returns:
            로그 항목 객체 목록
        """
        return self.repository.get_recent(limit)
    
    def update_log(self, log_entry: LogEntry) -> bool:
        """
        로그 항목 정보 업데이트
        
        Args:
            log_entry: 업데이트할 로그 항목 객체
            
        Returns:
            성공 여부
        """
        if log_entry.id is None:
            return False
        
        # 메시지 정제 (양쪽 공백 제거)
        log_entry.message = log_entry.message.strip()
        
        if not log_entry.message:
            raise ValueError("로그 메시지는 공백일 수 없습니다.")
        
        # 메시지에서 태그 추출 (기존 태그 유지)
        existing_tag_names = {tag.name for tag in log_entry.tags}
        new_tags = self.tag_service.parse_tags_from_text(log_entry.message)
        
        # 중복 없이 태그 합치기
        for tag in new_tags:
            if tag.name not in existing_tag_names:
                log_entry.tags.append(tag)
                existing_tag_names.add(tag.name)
        
        # 업데이트 실행
        success = self.repository.update(log_entry)
        
        if success:
            # 시그널 발생
            self.logUpdated.emit(log_entry)
            self.logsChanged.emit()
        
        return success
    
    def delete_log(self, log_id: int) -> bool:
        """
        로그 항목 삭제
        
        Args:
            log_id: 삭제할 로그 항목 ID
            
        Returns:
            성공 여부
        """
        success = self.repository.delete(log_id)
        
        if success:
            # 시그널 발생
            self.logDeleted.emit(log_id)
            self.logsChanged.emit()
        
        return success
    
    def search_logs(self, search_term: str, limit: int = 100) -> List[LogEntry]:
        """
        로그 항목 검색
        
        Args:
            search_term: 검색어
            limit: 반환할 최대 항목 수
            
        Returns:
            검색 결과 로그 항목 목록
        """
        return self.repository.search(search_term, limit)
    
    def get_stats_by_day(self, days: int = 7) -> Dict[str, Any]:
        """
        일별 로그 통계 조회
        
        Args:
            days: 조회할 일 수
            
        Returns:
            일별 통계 정보
        """
        # 시작일과 종료일 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
        
        # 모든 로그 가져오기
        logs = self.get_all_logs(limit=1000)  # 충분히 큰 숫자
        
        # 일별 데이터 초기화
        daily_stats = {}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_stats[date_str] = {
                'total_duration': 0,
                'log_count': 0,
                'categories': {},
                'tags': {}
            }
            current_date += timedelta(days=1)
        
        # 로그 분석
        for log in logs:
            # 로그 날짜가 범위 내에 있는지 확인
            if log.start_time and start_date <= log.start_time <= end_date:
                date_str = log.start_time.strftime('%Y-%m-%d')
                
                # 지속 시간 추가
                daily_stats[date_str]['total_duration'] += log.duration
                daily_stats[date_str]['log_count'] += 1
                
                # 카테고리 통계
                if log.category:
                    category_name = log.category.name
                    if category_name not in daily_stats[date_str]['categories']:
                        daily_stats[date_str]['categories'][category_name] = {
                            'duration': 0,
                            'count': 0,
                            'color': log.category.color
                        }
                    daily_stats[date_str]['categories'][category_name]['duration'] += log.duration
                    daily_stats[date_str]['categories'][category_name]['count'] += 1
                
                # 태그 통계
                for tag in log.tags:
                    if tag.name not in daily_stats[date_str]['tags']:
                        daily_stats[date_str]['tags'][tag.name] = {
                            'count': 0,
                            'color': tag.color
                        }
                    daily_stats[date_str]['tags'][tag.name]['count'] += 1
        
        return daily_stats
    
    def get_total_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        종합 통계 조회
        
        Args:
            days: 조회할 일 수
            
        Returns:
            종합 통계 정보
        """
        # 시작일 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 모든 로그 가져오기
        logs = self.get_all_logs(limit=1000)  # 충분히 큰 숫자
        
        # 통계 데이터 초기화
        stats = {
            'total_duration': 0,
            'log_count': 0,
            'categories': {},
            'tags': {},
            'average_duration': 0,
            'period_days': days
        }
        
        # 로그 분석
        for log in logs:
            # 로그 날짜가 범위 내에 있는지 확인
            if log.start_time and start_date <= log.start_time <= end_date:
                # 지속 시간 추가
                stats['total_duration'] += log.duration
                stats['log_count'] += 1
                
                # 카테고리 통계
                if log.category:
                    category_name = log.category.name
                    if category_name not in stats['categories']:
                        stats['categories'][category_name] = {
                            'duration': 0,
                            'count': 0,
                            'color': log.category.color
                        }
                    stats['categories'][category_name]['duration'] += log.duration
                    stats['categories'][category_name]['count'] += 1
                
                # 태그 통계
                for tag in log.tags:
                    if tag.name not in stats['tags']:
                        stats['tags'][tag.name] = {
                            'count': 0,
                            'color': tag.color
                        }
                    stats['tags'][tag.name]['count'] += 1
        
        # 평균 계산
        if stats['log_count'] > 0:
            stats['average_duration'] = stats['total_duration'] // stats['log_count']
        
        return stats
