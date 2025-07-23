

from sqlalchemy import desc

from pacekeeper.database import DatabaseSessionManager
from pacekeeper.interfaces.repositories.i_tag_repository import ITagRepository
from pacekeeper.repository.entities import Tag
from pacekeeper.utils.desktop_logger import DesktopLogger


class TagRepository(ITagRepository):
    def __init__(self, session_manager: DatabaseSessionManager):
        self.session_manager = session_manager
        self.desktop_logger = DesktopLogger("PaceKeeper")
        self.desktop_logger.log_system_event("TagRepository 초기화됨.")
        self.init_db()

    def init_db(self) -> None:
        # DatabaseSessionManager에서 이미 초기화됨
        self.desktop_logger.log_system_event("TagRepository DB 초기화 완료")

    def add_tag(self, name: str, description: str = "") -> Tag:
        """
        새로운 태그를 추가하거나 이미 존재하는 태그를 반환합니다.
        """
        with self.session_manager.session_scope() as session:
            tag = session.query(Tag).filter(
                Tag.name == name,
                Tag.state >= 1
            ).first()

            if not tag:
                tag = Tag(name=name, description=description)
                session.add(tag)
                session.flush()
                session.refresh(tag)
                self.desktop_logger.log_system_event(f"태그 추가 완료: {name}")
            else:
                self.desktop_logger.log_system_event(f"태그 이미 존재함: {name}")

            return tag

    def get_tag(self, tag_id: int) -> Tag | None:
        """
        태그 ID 목록을 받아 태그 이름을 문자열로 변환합니다.
        """
        with self.session_manager.readonly_session_scope() as session:
            try:
                tag = session.query(Tag).filter(Tag.id == tag_id).first()
                return tag
            except Exception as e:
                self.desktop_logger.log_error(f"태그 조회 실패: {e}", exc_info=True)
                return None

    def get_tags(self) -> list[Tag]:
        """
        모든 활성 태그를 조회합니다.
        """
        with self.session_manager.readonly_session_scope() as session:
            try:
                tags = session.query(Tag).filter(Tag.state >= 1).order_by(desc(Tag.id)).all()
                self.desktop_logger.log_system_event("전체 태그 조회 성공")
                return tags
            except Exception:
                self.desktop_logger.log_error("태그 조회 실패", exc_info=True)
                return []

    def update_tag(self, tag_id: int, name: str | None = None, description: str | None = None, category_id: int | None = None) -> Tag | None:
        """
        태그 업데이트 (이름, 설명)
        """
        with self.session_manager.session_scope() as session:
            tag = session.query(Tag).filter(Tag.id == tag_id, Tag.state >= 1).first()
            if tag:
                if name is not None:
                    tag.name = name
                if description is not None:
                    tag.description = description
                if category_id is not None:
                    tag.category_id = category_id
                session.flush()
                session.refresh(tag)
                self.desktop_logger.log_system_event(f"태그 업데이트 완료: ID {tag_id}")
                return tag
            else:
                self.desktop_logger.log_system_event(f"업데이트할 태그가 존재하지 않음: ID {tag_id}")
                return None

    def delete_tag(self, tag_id: int) -> None:
        """
        태그 삭제 (soft delete: state를 0으로 업데이트)
        """
        with self.session_manager.session_scope() as session:
            tag = session.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                tag.state = 0
                self.desktop_logger.log_system_event(f"태그 삭제 완료: ID {tag_id}")
            else:
                self.desktop_logger.log_system_event(f"삭제할 태그가 존재하지 않음: ID {tag_id}")
