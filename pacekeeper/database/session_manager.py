# database/session_manager.py

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from pacekeeper.repository.db_config import DATABASE_URI
from pacekeeper.repository.entities import Base
from pacekeeper.utils.desktop_logger import DesktopLogger


class DatabaseSessionManager:
    """
    데이터베이스 세션 관리를 중앙화하는 클래스

    모든 Repository가 공통으로 사용할 세션 관리 기능을 제공합니다.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self.logger = DesktopLogger("PaceKeeper")
            self.engine = create_engine(
                DATABASE_URI,
                echo=False,
                connect_args={"check_same_thread": False}
            )
            self.SessionLocal = sessionmaker(bind=self.engine)
            self._initialize_database()
            DatabaseSessionManager._initialized = True
            self.logger.log_system_event("DatabaseSessionManager 초기화됨.")

    def _initialize_database(self) -> None:
        """
        데이터베이스 및 테이블 초기화
        """
        try:
            Base.metadata.create_all(self.engine)
            self.logger.log_system_event("데이터베이스 초기화 완료")
        except SQLAlchemyError as e:
            self.logger.log_error("데이터베이스 초기화 실패", exc_info=True)
            raise Exception("데이터베이스 초기화 실패") from e

    def get_session(self) -> Session:
        """
        새로운 데이터베이스 세션 생성

        Returns:
            SQLAlchemy 세션 객체
        """
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        트랜잭션 관리를 포함한 세션 컨텍스트 매니저

        자동으로 커밋/롤백을 처리하고 세션을 정리합니다.

        Yields:
            SQLAlchemy 세션 객체
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def readonly_session_scope(self) -> Generator[Session, None, None]:
        """
        읽기 전용 세션 컨텍스트 매니저

        커밋 없이 세션을 자동으로 정리합니다.

        Yields:
            SQLAlchemy 세션 객체
        """
        session = self.get_session()
        try:
            yield session
        finally:
            session.close()

    def close_all_sessions(self) -> None:
        """
        모든 세션 정리 및 엔진 종료
        """
        try:
            self.engine.dispose()
            self.logger.log_system_event("모든 데이터베이스 세션 종료됨")
        except Exception as e:
            self.logger.log_error(f"세션 종료 중 오류: {e}", exc_info=True)
