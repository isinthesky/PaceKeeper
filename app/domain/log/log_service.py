"""
PaceKeeper Qt - 로그 서비스
로그 관련 비즈니스 로직 처리
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from app.domain.log.log_entity import LogEntity
from app.domain.log.log_repository import LogRepository
from app.domain.tag.tag_service import TagService


class LogService(QObject):
    """로그 서비스 클래스"""

    # 시그널 정의
    logCreated = pyqtSignal(LogEntity)
    logUpdated = pyqtSignal(LogEntity)
    logDeleted = pyqtSignal(int)  # 로그 ID
    logsChanged = pyqtSignal()  # 로그 목록 변경

    def __init__(
        self,
        log_repository: Optional[LogRepository] = None,
        tag_service: Optional[TagService] = None,
    ):
        """
        로그 서비스 초기화

        Args:
            log_repository: 로그 저장소 인스턴스
            tag_service: 태그 서비스 인스턴스
        """
        super().__init__()
        self.repository = log_repository or LogRepository()
        self.tag_service = tag_service or TagService()

    def create_log(
        self,
        message: str,
        tags: str = "",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> LogEntity:
        """
        새 로그 항목 생성

        Args:
            message: 로그 메시지
            tags: 태그 문자열
            start_date: 시작 날짜 문자열
            end_date: 종료 날짜 문자열

        Returns:
            생성된 로그 항목 객체
        """
        # 메시지 정제 (양쪽 공백 제거)
        clean_message = message.strip()

        if not clean_message:
            raise ValueError("로그 메시지는 공백일 수 없습니다.")

        # 시간 정보 처리
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 메시지에서 태그 추출 및 태그 문자열 업데이트
        if not tags:
            tags = self._extract_tags_from_message(clean_message)

        # 로그 항목 생성
        log_entry = LogEntity(
            message=clean_message,
            tags=tags,
            start_date=start_date,
            end_date=end_date,
            state=1,
        )

        # 저장소에 저장
        created_log = self.repository.create(log_entry)

        # 시그널 발생
        self.logCreated.emit(created_log)
        self.logsChanged.emit()

        return created_log

    def get_log(self, log_id: int) -> Optional[LogEntity]:
        """
        ID로 로그 항목 조회

        Args:
            log_id: 로그 항목 ID

        Returns:
            조회된 로그 항목 객체 또는 None
        """
        return self.repository.get_by_id(log_id)

    def get_all_logs(self, limit: int = 100, offset: int = 0) -> List[LogEntity]:
        """
        모든 로그 항목 조회

        Args:
            limit: 반환할 최대 항목 수
            offset: 시작 오프셋

        Returns:
            로그 항목 객체 목록
        """
        return self.repository.get_all(limit, offset)

    def get_recent_logs(self, limit: int = 10) -> List[LogEntity]:
        """
        최근 로그 항목 조회

        Args:
            limit: 반환할 최대 항목 수

        Returns:
            로그 항목 객체 목록
        """
        return self.repository.get_recent(limit)

    def update_log(self, log_entry: LogEntity) -> bool:
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

        # 메시지에서 태그 추출하여 태그 문자열 업데이트
        if not log_entry.tags:
            log_entry.tags = self._extract_tags_from_message(log_entry.message)

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

    def search_logs(self, search_term: str, limit: int = 100) -> List[LogEntity]:
        """
        로그 항목 검색

        Args:
            search_term: 검색어
            limit: 반환할 최대 항목 수

        Returns:
            검색 결과 로그 항목 목록
        """
        return self.repository.search(search_term, limit)

    def _extract_tags_from_message(self, message: str) -> str:
        """
        메시지에서 태그 추출하여 문자열로 반환

        Args:
            message: 로그 메시지

        Returns:
            추출된 태그 문자열 (쉼표로 구분)
        """
        import re

        # 정규식으로 #태그 형식 추출
        tag_pattern = r"#(\w+)"
        matches = re.findall(tag_pattern, message)

        # 태그 목록을 쉼표로 구분된 문자열로 변환
        if matches:
            return ",".join(matches)
        return ""

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
        start_date = end_date - timedelta(days=days - 1)
        start_date_str = start_date.strftime("%Y-%m-%d")

        # 모든 로그 가져오기
        logs = self.get_all_logs(limit=1000)  # 충분히 큰 숫자

        # 일별 데이터 초기화
        daily_stats = {}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            daily_stats[date_str] = {"log_count": 0, "tags": {}}
            current_date += timedelta(days=1)

        # 로그 분석
        for log in logs:
            # 로그 날짜가 범위 내에 있는지 확인
            if log.start_date and log.start_date.startswith(start_date_str):
                date_str = log.start_date.split(" ")[0]  # YYYY-MM-DD 부분만 추출

                # 일별 카운트 증가
                daily_stats[date_str]["log_count"] += 1

                # 태그 통계
                if log.tags:
                    tag_list = log.tags.split(",")
                    for tag_name in tag_list:
                        tag_name = tag_name.strip()
                        if tag_name:
                            if tag_name not in daily_stats[date_str]["tags"]:
                                daily_stats[date_str]["tags"][tag_name] = {"count": 0}
                            daily_stats[date_str]["tags"][tag_name]["count"] += 1

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
        start_date_str = start_date.strftime("%Y-%m-%d")

        # 모든 로그 가져오기
        logs = self.get_all_logs(limit=1000)  # 충분히 큰 숫자

        # 통계 데이터 초기화
        stats = {"log_count": 0, "tags": {}, "period_days": days}

        # 로그 분석
        for log in logs:
            # 로그 날짜가 범위 내에 있는지 확인
            if log.start_date and log.start_date.startswith(start_date_str):
                # 로그 카운트 증가
                stats["log_count"] += 1

                # 태그 통계
                if log.tags:
                    tag_list = log.tags.split(",")
                    for tag_name in tag_list:
                        tag_name = tag_name.strip()
                        if tag_name:
                            if tag_name not in stats["tags"]:
                                stats["tags"][tag_name] = {"count": 0}
                            stats["tags"][tag_name]["count"] += 1

        return stats
