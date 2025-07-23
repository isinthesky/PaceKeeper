# interfaces/services/i_log_service.py

from abc import ABC, abstractmethod
from datetime import datetime

from pacekeeper.repository.entities import Log


class ILogService(ABC):
    """
    로그 Service 인터페이스

    로그 관련 비즈니스 로직을 위한 추상 인터페이스를 정의합니다.
    """

    @abstractmethod
    def create_study_log(self, message: str, study_start_time: datetime | None = None) -> None:
        """
        학습 로그를 생성합니다.

        Args:
            message: 로그 메시지
            study_start_time: 학습 시작 시간 (선택사항)
        """
        pass

    @abstractmethod
    def retrieve_all_logs(self) -> list[Log]:
        """
        모든 활성 로그를 조회합니다.

        Returns:
            활성 로그 목록
        """
        pass

    @abstractmethod
    def retrieve_logs_by_period(self, start_date: str, end_date: str) -> list[Log]:
        """
        지정한 기간 동안의 활성 로그를 조회합니다.

        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            기간 내의 활성 로그 목록
        """
        pass

    @abstractmethod
    def retrieve_logs_by_tag(self, tag_keyword: str) -> list[Log]:
        """
        지정한 태그를 포함하는 활성 로그를 조회합니다.

        Args:
            tag_keyword: 태그 키워드

        Returns:
            태그가 포함된 활성 로그 목록
        """
        pass

    @abstractmethod
    def retrieve_recent_logs(self, limit: int = 20) -> list[Log]:
        """
        최근 활성 로그들을 조회합니다.

        Args:
            limit: 조회할 최대 로그 수

        Returns:
            최근 활성 로그 목록
        """
        pass

    @abstractmethod
    def remove_logs_by_ids(self, log_ids: list[int]) -> None:
        """
        지정한 로그 ID 리스트에 해당하는 로그들을 soft delete 처리합니다.

        Args:
            log_ids: 삭제할 로그 ID 목록
        """
        pass
