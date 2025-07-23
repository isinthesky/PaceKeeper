# database/unit_of_work.py


from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from pacekeeper.utils.desktop_logger import DesktopLogger

from .session_manager import DatabaseSessionManager


class UnitOfWork:
    """
    Unit of Work 패턴 구현

    복수의 Repository 작업을 하나의 트랜잭션으로 묶어서 처리합니다.
    """

    def __init__(self, session_manager: DatabaseSessionManager | None = None) -> None:
        self.session_manager = session_manager or DatabaseSessionManager()
        self.logger = DesktopLogger("PaceKeeper")
        self._session: Session | None = None
        self._committed = False

    def __enter__(self) -> 'UnitOfWork':
        """
        컨텍스트 매니저 진입 시 세션 시작
        """
        self._session = self.session_manager.get_session()
        self._committed = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        컨텍스트 매니저 종료 시 세션 정리
        """
        if self._session:
            if exc_type is None and not self._committed:
                # 예외가 없고 아직 커밋하지 않았다면 커밋
                self.commit()
            elif exc_type is not None:
                # 예외가 발생했다면 롤백
                self.rollback()

            self._session.close()
            self._session = None

    @property
    def session(self) -> Session:
        """
        현재 활성 세션 반환

        Returns:
            SQLAlchemy 세션 객체

        Raises:
            RuntimeError: UnitOfWork가 활성화되지 않은 경우
        """
        if self._session is None:
            raise RuntimeError("UnitOfWork는 컨텍스트 매니저로 사용되어야 합니다")
        return self._session

    def commit(self) -> None:
        """
        현재 트랜잭션 커밋
        """
        if self._session and not self._committed:
            try:
                self._session.commit()
                self._committed = True
                self.logger.log_system_event("UnitOfWork 트랜잭션 커밋됨")
            except SQLAlchemyError as e:
                self.logger.log_error("UnitOfWork 커밋 실패", exc_info=True)
                self.rollback()
                raise e

    def rollback(self) -> None:
        """
        현재 트랜잭션 롤백
        """
        if self._session:
            try:
                self._session.rollback()
                self.logger.log_system_event("UnitOfWork 트랜잭션 롤백됨")
            except SQLAlchemyError as e:
                self.logger.log_error("UnitOfWork 롤백 실패", exc_info=True)
                raise e

    def flush(self) -> None:
        """
        변경사항을 데이터베이스에 플러시 (커밋 없이)
        """
        if self._session:
            try:
                self._session.flush()
                self.logger.log_debug("UnitOfWork 세션 플러시됨")
            except SQLAlchemyError as e:
                self.logger.log_error("UnitOfWork 플러시 실패", exc_info=True)
                raise e
