# repository/log_repository.py


from sqlalchemy import and_, desc, or_
from sqlalchemy.exc import SQLAlchemyError

from pacekeeper.consts.labels import load_language_resource
from pacekeeper.database import DatabaseSessionManager
from pacekeeper.interfaces.repositories.i_log_repository import ILogRepository
from pacekeeper.repository.entities import Category, Log
from pacekeeper.utils.desktop_logger import DesktopLogger

lang_res = load_language_resource()


class LogRepository(ILogRepository):
    """
    로그 데이터 액세스 클래스

    로그 엔티티의 CRUD 작업 및 조회 기능을 제공합니다.
    SQLAlchemy ORM을 사용하여 데이터베이스와 상호작용합니다.
    """
    def __init__(self, session_manager: DatabaseSessionManager) -> None:
        """LogRepository 초기화 및 데이터베이스 초기화"""
        self.session_manager = session_manager
        self.desktop_logger = DesktopLogger("PaceKeeper")
        self.desktop_logger.log_system_event("LogRepository 초기화됨.")

        # DB 및 테이블 초기화: 기본적으로 엔티티에 의해 생성
        self.initialize_database()

    def initialize_database(self) -> None:
        """
        SQLAlchemy ORM을 통해 데이터베이스 및 테이블 초기화

        DatabaseSessionManager에서 이미 초기화하므로 별도 처리 불필요
        """
        # DatabaseSessionManager에서 이미 초기화됨
        self.desktop_logger.log_system_event("LogRepository DB 초기화 완료")

    def get_category_by_name(self, category_name: str) -> Category | None:
        """
        카테고리 이름으로 카테고리 조회

        Args:
            category_name: 조회할 카테고리 이름

        Returns:
            찾은 카테고리 또는 None
        """
        with self.session_manager.readonly_session_scope() as session:
            try:
                category = session.query(Category).filter(
                    Category.name == category_name,
                    Category.state >= 1
                ).first()
                return category
            except SQLAlchemyError:
                return None

    def save_category(self, category: Category) -> Category:
        """
        카테고리 저장/갱신

        Args:
            category: 저장할 카테고리 객체

        Returns:
            저장된 카테고리 객체

        Raises:
            SQLAlchemyError: 저장 실패 시
        """
        with self.session_manager.session_scope() as session:
            session.add(category)
            session.flush()  # ID 생성을 위해
            session.refresh(category)
            return category

    def save_log(self, log: Log) -> Log:
        """
        로그 저장/갱신

        Args:
            log: 저장할 로그 객체

        Returns:
            저장된 로그 객체

        Raises:
            SQLAlchemyError: 저장 실패 시
        """
        with self.session_manager.session_scope() as session:
            session.add(log)
            session.flush()  # ID 생성을 위해
            session.refresh(log)
            return log

    def get_all_logs(self) -> list[Log]:
        """
        모든 활성 로그 조회 (state가 1 이상)

        Returns:
            활성 로그 목록
        """
        with self.session_manager.readonly_session_scope() as session:
            try:
                logs = session.query(Log).filter(Log.state >= 1).order_by(desc(Log.id)).all()

                # 세션이 닫히기 전에 모든 로그 객체의 속성을 미리 로드하여 세션과 분리된 객체 목록 생성
                detached_logs = []
                for log in logs:
                    detached_log = Log(
                        id=log.id,
                        start_date=log.start_date,
                        end_date=log.end_date,
                        message=log.message,
                        tags=log.tags,
                        state=log.state
                    )
                    detached_logs.append(detached_log)

                self.desktop_logger.log_system_event("전체 로그 조회 성공")
                return detached_logs
            except SQLAlchemyError as e:
                self.desktop_logger.log_error(f"전체 로그 조회 실패: {e}", exc_info=True)
                return []

    def get_logs_by_period(self, start_date: str, end_date: str) -> list[Log]:
        """
        기간 내의 활성 로그 조회 (state가 1 이상)

        Args:
            start_date: 시작 날짜/시간 (YYYY-MM-DD 또는 YYYY-MM-DD HH:MM:SS 형식)
            end_date: 종료 날짜/시간 (YYYY-MM-DD 또는 YYYY-MM-DD HH:MM:SS 형식)

        Returns:
            기간 내의 활성 로그 목록
        """
        with self.session_manager.readonly_session_scope() as session:
            try:
                # 날짜 형식이 YYYY-MM-DD인 경우 시간 정보 추가
                if len(start_date) == 10:  # YYYY-MM-DD 형식
                    start_date = f"{start_date} 00:00:00"
                if len(end_date) == 10:  # YYYY-MM-DD 형식
                    end_date = f"{end_date} 23:59:59"

                logs = session.query(Log).filter(
                    and_(
                        Log.start_date >= start_date,
                        Log.start_date <= end_date,
                        Log.state >= 1
                    )
                ).order_by(desc(Log.id)).all()

                # 세션이 닫히기 전에 모든 로그 객체의 속성을 미리 로드하여 세션과 분리된 객체 목록 생성
                detached_logs = []
                for log in logs:
                    detached_log = Log(
                        id=log.id,
                        start_date=log.start_date,
                        end_date=log.end_date,
                        message=log.message,
                        tags=log.tags,
                        state=log.state
                    )
                    detached_logs.append(detached_log)

                self.desktop_logger.log_system_event(f"기간({start_date} ~ {end_date}) 로그 조회 성공")
                return detached_logs
            except SQLAlchemyError as e:
                self.desktop_logger.log_error(f"기간 로그 조회 실패: {e}", exc_info=True)
                return []

    def get_logs_by_tag(self, tag_keyword: str) -> list[Log]:
        """
        지정된 태그를 포함하는 활성 로그 조회 (state가 1 이상)

        태그 키워드는 메시지 내용(#태그명)과 태그 ID 모두에서 검색됩니다.

        Args:
            tag_keyword: 검색할 태그 키워드

        Returns:
            태그가 포함된 활성 로그 목록
        """
        with self.session_manager.readonly_session_scope() as session:
            try:
                # 메시지 내용에서 태그 검색 (예: #test)
                message_filter = Log.message.like(f"%#{tag_keyword}%")

                # 태그 ID에서 검색 (태그 이름이 저장된 태그 ID 검색)
                tag_filter = Log.tags.like(f"%{tag_keyword}%")

                # 두 조건 중 하나라도 만족하는 로그 검색
                logs = session.query(Log).filter(
                    and_(
                        or_(message_filter, tag_filter),
                        Log.state >= 1
                    )
                ).order_by(desc(Log.id)).all()

                # 세션이 닫히기 전에 모든 로그 객체의 속성을 미리 로드하여 세션과 분리된 객체 목록 생성
                detached_logs = []
                for log in logs:
                    detached_log = Log(
                        id=log.id,
                        start_date=log.start_date,
                        end_date=log.end_date,
                        message=log.message,
                        tags=log.tags,
                        state=log.state
                    )
                    detached_logs.append(detached_log)

                self.desktop_logger.log_system_event(f"태그({tag_keyword}) 로그 조회 성공")
                return detached_logs
            except SQLAlchemyError as e:
                self.desktop_logger.log_error(f"태그 로그 조회 실패: {e}", exc_info=True)
                return []

    def get_recent_logs(self, limit: int = 20) -> list[Log]:
        """
        최근 활성 로그들을 조회 (state가 1 이상)

        Args:
            limit: 조회할 최대 로그 수 (기본값: 20)

        Returns:
            최근 활성 로그 목록 (최대 limit개)
        """
        with self.session_manager.readonly_session_scope() as session:
            try:
                logs = session.query(Log).filter(Log.state >= 1).order_by(desc(Log.id)).limit(limit).all()

                # 세션이 닫히기 전에 모든 로그 객체의 속성을 미리 로드하여 세션과 분리된 객체 목록 생성
                detached_logs = []
                for log in logs:
                    detached_log = Log(
                        id=log.id,
                        start_date=log.start_date,
                        end_date=log.end_date,
                        message=log.message,
                        tags=log.tags,
                        state=log.state
                    )
                    detached_logs.append(detached_log)

                self.desktop_logger.log_system_event(f"최근 {limit}개의 로그 조회 성공")
                return detached_logs
            except SQLAlchemyError as e:
                self.desktop_logger.log_error(f"최근 로그 조회 실패: {e}", exc_info=True)
                return []

    def soft_delete_logs(self, log_ids: list[int]) -> int:
        """
        주어진 로그 ID 리스트에 해당하는 로그들의 state를 0으로 업데이트 (soft delete)

        Args:
            log_ids: 삭제할 로그 ID 목록

        Returns:
            삭제된 로그 수

        Raises:
            SQLAlchemyError: 삭제 실패 시
        """
        if not log_ids:
            return 0

        with self.session_manager.session_scope() as session:
            logs = session.query(Log).filter(Log.id.in_(log_ids)).all()
            deleted_count = 0
            for log in logs:
                log.state = 0
                deleted_count += 1
            self.desktop_logger.log_system_event(f"로그 삭제 (IDs: {log_ids}) 성공")
            return deleted_count
