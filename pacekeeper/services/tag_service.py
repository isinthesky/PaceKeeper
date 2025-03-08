import json
from datetime import datetime
from typing import List, Optional

from pacekeeper.repository.log_repository import LogRepository
from pacekeeper.repository.entities import Log, Category, Tag
from pacekeeper.repository.tag_repository import TagRepository
from pacekeeper.utils.functions import extract_tags
from pacekeeper.utils.desktop_logger import DesktopLogger
from icecream import ic

class TagService:
    def __init__(self):
        self.logger = DesktopLogger("PaceKeeper")
        self.repository = TagRepository()
        self.logger.log_system_event("TagService 초기화됨.")

    def get_tag_text(self, tag_ids: list[int]) -> list[str]:
        """
        태그 ID 목록을 받아 태그 이름을 문자열로 변환합니다.
        """
        tag_texts = []
        for tag_id in tag_ids:
            tag:Tag = self.repository.get_tag(tag_id)
            if tag:
                tag_texts.append(tag)
                
        ic("tag_texts", tag_texts)
          
        return [tag.name for tag in tag_texts]
    
    def get_tag(self, tag_id: int) -> Optional[Tag]:
        """
        지정된 ID의 태그를 조회합니다.
        """
        try:
            tag: Tag = self.repository.get_tag(tag_id)
            return tag
        except Exception as e:
            self.logger.log_error("태그 조회 실패", exc_info=True)
            return None

    def get_tags(self) -> list[Tag]:
        """
        모든 태그 목록을 반환합니다.
        """
        return self.repository.get_tags()

    def update_tag(self, tag: Tag) -> Optional[Tag]:
        """
        태그 업데이트
        """
        try:
            updated_tag = self.repository.update_tag(tag.id, tag.name, tag.description, tag.category_id)
            if updated_tag:
                return updated_tag
            else:
                self.logger.log_error("태그 업데이트 실패", exc_info=True)
                return None
        except Exception as e:
            self.logger.log_error("태그 업데이트 실패", exc_info=True)
            raise e
    