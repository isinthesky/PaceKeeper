from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker, Session as SessionType
from sqlalchemy import create_engine

from pacekeeper.repository.entities import Base, Tag
from pacekeeper.consts.settings import DB_FILE
from pacekeeper.utils.desktop_logger import DesktopLogger
from icecream import ic

DATABASE_URI = f"sqlite:///{DB_FILE}"
engine = create_engine(DATABASE_URI, echo=False, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

class TagRepository:
    def __init__(self):
        self.desktop_logger = DesktopLogger("PaceKeeper")
        self.desktop_logger.log_system_event("TagRepository 초기화됨.")
        self.init_db()
        
    def init_db(self):
        try:
            Base.metadata.create_all(engine)
            self.desktop_logger.log_system_event("태그 DB 초기화 완료")
        except Exception as e:
            self.desktop_logger.log_error("태그 DB 초기화 실패", exc_info=True)
    
    def add_tag(self, name: str, description: str = "") -> Tag:
        """
        새로운 태그를 추가하거나 이미 존재하는 태그를 반환합니다.
        """
        session: SessionType = Session()
        try:
            tag = session.query(Tag).filter(
                Tag.name == name,
                Tag.state >= 1
            ).first()
            
            if not tag:
                tag = Tag(name=name, description=description)
                session.add(tag)
                session.commit()
                session.refresh(tag)
                self.desktop_logger.log_system_event(f"태그 추가 완료: {name}")
            else:
                self.desktop_logger.log_system_event(f"태그 이미 존재함: {name}")
                
            return tag
        except Exception as e:
            session.rollback()
            self.desktop_logger.log_error("태그 추가 실패", exc_info=True)
            raise e
        finally:
            session.close()
            
    def get_tag(self, tag_id: int) -> Optional[Tag]:
        """
        태그 ID 목록을 받아 태그 이름을 문자열로 변환합니다.
        """
        session: SessionType = Session()
        try:
            tag = session.query(Tag).filter(Tag.id == tag_id).first()
            return tag
        except Exception as e:
            self.desktop_logger.log_error(f"태그 조회 실패: {e}", exc_info=True)
            return None
        finally:
            session.close()
    
    def get_tags(self) -> list[Tag]:
        """
        모든 활성 태그를 조회합니다.
        """
        session: SessionType = Session()
        try:
            tags = session.query(Tag).filter(Tag.state >= 1).order_by(desc(Tag.id)).all()
            self.desktop_logger.log_system_event("전체 태그 조회 성공")
            return tags
        except Exception as e:
            self.desktop_logger.log_error("태그 조회 실패", exc_info=True)
            return []
        finally:
            session.close()
            
    def update_tag(self, tag_id: int, name: Optional[str] = None, description: Optional[str] = None, category_id: Optional[int] = None) -> Optional[Tag]:
        """
        태그 업데이트 (이름, 설명)
        """
        session: SessionType = Session()
        try:
            tag = session.query(Tag).filter(Tag.id == tag_id, Tag.state >= 1).first()
            if tag:
                if name is not None:
                    tag.name = name
                if description is not None:
                    tag.description = description
                if category_id is not None:
                    tag.category_id = category_id
                session.commit()
                session.refresh(tag)
                self.desktop_logger.log_system_event(f"태그 업데이트 완료: ID {tag_id}")
                return tag
            else:
                self.desktop_logger.log_system_event(f"업데이트할 태그가 존재하지 않음: ID {tag_id}")
                return None
        except Exception as e:
            session.rollback()
            self.desktop_logger.log_error("태그 업데이트 실패", exc_info=True)
        finally:
            session.close()
    
    def delete_tag(self, tag_id: int) -> None:
        """
        태그 삭제 (soft delete: state를 0으로 업데이트)
        """
        session: SessionType = Session()
        try:
            tag = session.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                tag.state = 0
                session.commit()
                self.desktop_logger.log_system_event(f"태그 삭제 완료: ID {tag_id}")
            else:
                self.desktop_logger.log_system_event(f"삭제할 태그가 존재하지 않음: ID {tag_id}")
        except Exception as e:
            session.rollback()
            self.desktop_logger.log_error("태그 삭제 실패", exc_info=True)
        finally:
            session.close() 