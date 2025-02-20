from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker, Session as SessionType
from sqlalchemy import create_engine

from pacekeeper.repository.entities import Base, Category
from pacekeeper.consts.settings import DB_FILE
from pacekeeper.utils.desktop_logger import DesktopLogger

DATABASE_URI = f"sqlite:///{DB_FILE}"
engine = create_engine(DATABASE_URI, echo=False, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

class CategoryRepository:
    def __init__(self):
        self.desktop_logger = DesktopLogger("PaceKeeper")
        self.desktop_logger.log_system_event("SQLAlchemyCategoryRepository 초기화됨.")
        self.init_db()
        
    def init_db(self):
        try:
            Base.metadata.create_all(engine)
            self.desktop_logger.log_system_event("카테고리 DB 초기화 완료")
        except Exception as e:
            self.desktop_logger.log_error("카테고리 DB 초기화 실패", exc_info=True)
            
    def add_category(self, name: str, description: str = "", color: str = "#FFFFFF") -> Category:
        """
        새로운 카테고리를 추가하거나 이미 존재하는 카테고리를 반환합니다.
        """
        session: SessionType = Session()
        try:
            category = session.query(Category).filter(
                Category.name == name,
                Category.state >= 1
            ).first()
            if not category:
                category = Category(name=name, description=description, color=color, state=1)
                session.add(category)
                session.commit()
                self.desktop_logger.log_system_event(f"카테고리 추가 완료: {name}")
            else:
                self.desktop_logger.log_system_event(f"카테고리 이미 존재함: {name}")
            return category
        except Exception as e:
            session.rollback()
            self.desktop_logger.log_error("카테고리 추가 실패", exc_info=True)
            raise e
        finally:
            session.close()
            
    def get_category(self, category_id: int) -> Category:
        """
        지정된 ID의 카테고리를 조회합니다.
        """
        session: SessionType = Session()
        try:
            category = session.query(Category).filter(Category.id == category_id, Category.state >= 1).first()
            if category:
                self.desktop_logger.log_system_event(f"카테고리 조회 성공: {category.name}")
                return category
            else:
                self.desktop_logger.log_system_event(f"카테고리 조회 실패: ID {category_id}")
                return None
        except Exception as e:
            self.desktop_logger.log_error("카테고리 조회 실패", exc_info=True)
            return None
        finally:
            session.close()
            
    def get_categories(self) -> List[Category]:
        """
        모든 활성 카테고리를 조회합니다.
        """
        session: SessionType = Session()
        try:
            categories = session.query(Category).filter(Category.state >= 1).order_by(Category.id).all()
            self.desktop_logger.log_system_event("전체 카테고리 조회 성공")
            return categories
        except Exception as e:
            self.desktop_logger.log_error("카테고리 조회 실패", exc_info=True)
            return []
        finally:
            session.close()
            
    def update_category(self, category_id: int, name: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None) -> None:
        """
        카테고리 업데이트 (이름, 설명, 색상)
        """
        session: SessionType = Session()
        try:
            category = session.query(Category).filter(Category.id == category_id, Category.state >= 1).first()
            if category:
                if name is not None:
                    category.name = name
                if description is not None:
                    category.description = description
                if color is not None:
                    category.color = color
                session.commit()
                self.desktop_logger.log_system_event(f"카테고리 업데이트 완료: ID {category_id}")
            else:
                self.desktop_logger.log_system_event(f"업데이트할 카테고리가 존재하지 않음: ID {category_id}")
        except Exception as e:
            session.rollback()
            self.desktop_logger.log_error("카테고리 업데이트 실패", exc_info=True)
        finally:
            session.close()
            
    def delete_category(self, category_id: int) -> None:
        """
        카테고리 삭제 (soft delete: state를 0으로 업데이트)
        """
        session: SessionType = Session()
        try:
            category = session.query(Category).filter(Category.id == category_id).first()
            if category:
                category.state = 0
                session.commit()
                self.desktop_logger.log_system_event(f"카테고리 삭제 완료: ID {category_id}")
            else:
                self.desktop_logger.log_system_event(f"삭제할 카테고리가 존재하지 않음: ID {category_id}")
        except Exception as e:
            session.rollback()
            self.desktop_logger.log_error("카테고리 삭제 실패", exc_info=True)
        finally:
            session.close() 