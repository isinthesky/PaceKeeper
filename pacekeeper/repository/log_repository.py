# repositories/sqlite_log_repository.py

from datetime import datetime
from typing import List, Optional

from sqlalchemy import create_engine, desc, and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from pacekeeper.repository.entities import Base, Category, Log
from pacekeeper.utils.functions import extract_tags
from pacekeeper.utils.desktop_logger import DesktopLogger
from pacekeeper.consts.settings import DB_FILE
from pacekeeper.consts.labels import load_language_resource
from icecream import ic

lang_res = load_language_resource()

# SQLite를 사용한다고 가정 (파일 기반 DB)
DATABASE_URI = f"sqlite:///{DB_FILE}"
engine = create_engine(DATABASE_URI, echo=False, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

class LogRepository:
    def __init__(self):
        self.desktop_logger = DesktopLogger("PaceKeeper")
        self.desktop_logger.log_system_event("LogRepository 초기화됨.")
        
        # DB 및 테이블 초기화: 기본적으로 엔티티에 의해 생성
        self.initialize_database()
        
    def initialize_database(self) -> None:
        try:
            Base.metadata.create_all(engine)
            self.desktop_logger.log_system_event("SQLAlchemy 기반 DB 초기화 완료")
        except SQLAlchemyError as e:
            self.desktop_logger.log_error("SQLAlchemy DB 초기화 실패", exc_info=True)
            raise Exception("DB 초기화 실패") from e
    
    def get_category_by_name(self, category_name: str) -> Optional[Category]:
        session = Session()
        try:
            category = session.query(Category).filter(
                Category.name == category_name,
                Category.state >= 1
            ).first()
            return category
        except SQLAlchemyError:
            return None
        finally:
            session.close()
    
    def save_category(self, category: Category) -> Category:
        session = Session()
        try:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_log(self, log: Log) -> None:
        session = Session()
        try:
            session.add(log)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_logs(self) -> List[Log]:
        """
        모든 활성 로그 조회 메서드 (state가 1 이상)
        """
        session = Session()
        try:
            logs = session.query(Log).filter(Log.state >= 1).order_by(desc(Log.id)).all()
            
            # 세션이 닫히기 전에 모든 로그 객체의 속성을 미리 로드하여 새 객체 목록 생성
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
        finally:
            session.close()
    
    def get_logs_by_period(self, start_date: str, end_date: str) -> List[Log]:
        """
        기간 내의 활성 로그 조회 메서드 (state가 1 이상)
        """
        session = Session()
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
            
            # 세션이 닫히기 전에 모든 로그 객체의 속성을 미리 로드하여 새 객체 목록 생성
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
        finally:
            session.close()
    
    def get_logs_by_tag(self, tag_keyword: str) -> List[Log]:
        """
        지정된 태그를 포함하는 활성 로그 조회 메서드 (state가 1 이상)
        태그 키워드는 메시지 내용과 태그 ID 모두에서 검색됩니다.
        """
        session = Session()
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
            
            # 세션이 닫히기 전에 모든 로그 객체의 속성을 미리 로드하여 새 객체 목록 생성
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
        finally:
            session.close()
    
    def get_recent_logs(self, limit: int = 20) -> List[Log]:
        """
        최근 활성 로그들을 조회하는 메서드 (state가 1 이상)
        """
        session = Session()
        try:
            logs = session.query(Log).filter(Log.state >= 1).order_by(desc(Log.id)).limit(limit).all()
            
            # 세션이 닫히기 전에 모든 로그 객체의 속성을 미리 로드하여 새 객체 목록 생성
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
        finally:
            session.close()
    
    def soft_delete_logs(self, log_ids: List[int]) -> None:
        """
        주어진 로그 ID 리스트에 해당하는 로그들의 state를 0으로 업데이트 (soft delete)
        """
        if not log_ids:
            return
        
        session = Session()
        try:
            logs = session.query(Log).filter(Log.id.in_(log_ids)).all()
            for log in logs:
                log.state = 0
            session.commit()
            self.desktop_logger.log_system_event(f"로그 삭제 (IDs: {log_ids}) 성공")
        except SQLAlchemyError as e:
            session.rollback()
            self.desktop_logger.log_error("로그 삭제 실패", exc_info=True)
            raise e
        finally:
            session.close()