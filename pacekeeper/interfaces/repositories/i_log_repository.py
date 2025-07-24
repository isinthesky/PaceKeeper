# interfaces/repositories/i_log_repository.py

from abc import ABC, abstractmethod

from pacekeeper.repository.entities import Log


class ILogRepository(ABC):
    """
    로그 Repository 인터페이스

    로그 데이터 접근을 위한 추상 인터페이스를 정의합니다.
    """

    @abstractmethod
    def initialize_database(self) -> None:
        """데이터베이스 및 테이블 초기화"""
        pass

    # get_category_by_name 메서드 제거됨 - LogRepository에서 카테고리 로직 분리

    # save_category 메서드 제거됨 - LogRepository에서 카테고리 로직 분리

    @abstractmethod
    def save_log(self, log: Log) -> Log:
        """
        로그 저장/갱신

        Args:
            log: 저장할 로그 객체

        Returns:
            저장된 로그 객체
        """
        pass

    @abstractmethod
    def get_all_logs(self) -> list[Log]:
        """
        모든 활성 로그 조회 (state가 1 이상)

        Returns:
            활성 로그 목록
        """
        pass

    @abstractmethod
    def get_logs_by_period(self, start_date: str, end_date: str) -> list[Log]:
        """
        기간 내의 활성 로그 조회

        Args:
            start_date: 시작 날짜/시간
            end_date: 종료 날짜/시간

        Returns:
            기간 내의 활성 로그 목록
        """
        pass

    @abstractmethod
    def get_logs_by_tag(self, tag_keyword: str) -> list[Log]:
        """
        지정된 태그를 포함하는 활성 로그 조회

        Args:
            tag_keyword: 검색할 태그 키워드

        Returns:
            태그가 포함된 활성 로그 목록
        """
        pass

    @abstractmethod
    def get_recent_logs(self, limit: int = 20) -> list[Log]:
        """
        최근 활성 로그들을 조회

        Args:
            limit: 조회할 최대 로그 수

        Returns:
            최근 활성 로그 목록
        """
        pass

    @abstractmethod
    def soft_delete_logs(self, log_ids: list[int]) -> int:
        """
        로그들을 soft delete 처리

        Args:
            log_ids: 삭제할 로그 ID 목록

        Returns:
            삭제된 로그 수
        """
        pass
