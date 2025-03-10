# repositories/sqlite_log_repository.py

from datetime import datetime
from typing import List, Optional
import os

from sqlalchemy import create_engine, desc, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from pacekeeper.repository.entities import Base, Category, Log
from pacekeeper.utils.functions import extract_tags, resource_path
from pacekeeper.utils.desktop_logger import DesktopLogger
from pacekeeper.consts.settings import DB_FILE
from pacekeeper.consts.labels import load_language_resource
from icecream import ic

lang_res = load_language_resource()

# SQLite를 사용한다고 가정 (파일 기반 DB)
DATABASE_URI = f"sqlite:///{DB_FILE}"

# 데이터베이스 파일 디렉토리 확인 및 생성
db_dir = os.path.dirname(DB_FILE)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir)

engine = create_engine(DATABASE_URI, echo=False, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

class LogRepository:
    def __init__(self):
        self.desktop_logger = DesktopLogger("PaceKeeper")
        self.desktop_logger.log_system_event(f"LogRepository 초기화됨. DB 경로: {DB_FILE}")
        
        # DB 및 테이블 초기화: 기본적으로 엔티티에 의해 생성
        self.initialize_database()
        
    def initialize_database(self) -> None:
        try:
            Base.metadata.create_all(engine)
            self.desktop_logger.log_system_event("SQLAlchemy 기반 DB 초기화 완료")
        except SQLAlchemyError as e:
            self.desktop_logger.log_error(f"SQLAlchemy DB 초기화 실패: {str(e)}", exc_info=True)
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
            self.desktop_logger.log_system_event("전체 로그 조회 성공")
            return logs
        except SQLAlchemyError:
            return []
        finally:
            session.close()
    
    def get_logs_by_period(self, start_date: str, end_date: str) -> List[Log]:
        """
        기간 내의 활성 로그 조회 메서드 (state가 1 이상)
        """
        session = Session()
        try:
            logs = session.query(Log).filter(
                and_(
                    Log.start_date >= start_date,
                    Log.start_date <= end_date,
                    Log.state >= 1
                )
            ).order_by(desc(Log.id)).all()
            self.desktop_logger.log_system_event(f"기간({start_date} ~ {end_date}) 로그 조회 성공")
            return logs
        except SQLAlchemyError:
            return []
        finally:
            session.close()
    
    def get_logs_by_tag(self, tag_keyword: str) -> List[Log]:
        """
        지정된 태그를 포함하는 활성 로그 조회 메서드 (state가 1 이상)
        """
        session = Session()
        try:
            logs = session.query(Log).filter(
                Log.tags.like(f"%{tag_keyword}%"),
                Log.state >= 1
            ).order_by(desc(Log.id)).all()
            self.desktop_logger.log_system_event(f"태그({tag_keyword}) 로그 조회 성공")
            return logs
        except SQLAlchemyError:
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
            self.desktop_logger.log_system_event(f"최근 {limit}개의 로그 조회 성공")
            return logs
        except SQLAlchemyError:
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