"""
PaceKeeper Qt - 태그 서비스
태그 관련 비즈니스 로직 처리
"""

from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from app.domain.tag.tag_entity import TagEntity
from app.domain.tag.tag_repository import TagRepository


class TagService(QObject):
    """태그 서비스 클래스"""

    # 시그널 정의
    tagCreated = pyqtSignal(TagEntity)
    tagUpdated = pyqtSignal(TagEntity)
    tagDeleted = pyqtSignal(int)  # 태그 ID
    tagsChanged = pyqtSignal()  # 태그 목록 변경

    def __init__(self, tag_repository: Optional[TagRepository] = None):
        """
        태그 서비스 초기화

        Args:
            tag_repository: 태그 저장소 인스턴스
        """
        super().__init__()
        self.repository = tag_repository or TagRepository()

    def create_tag(
        self, name: str, category_id: int = 0, description: str = ""
    ) -> TagEntity:
        """
        새 태그 생성

        Args:
            name: 태그 이름
            color: 태그 색상 (기본값: 파란색)

        Returns:
            생성된 태그 객체
        """
        # 이름 정제 (공백 제거, # 제거)
        clean_name = name.strip().lstrip("#")

        if not clean_name:
            raise ValueError("태그 이름은 공백일 수 없습니다.")

        # 이미 존재하는 태그인지 확인
        existing_tag = self.repository.get_by_name(clean_name)
        if existing_tag:
            return existing_tag

        # 새 태그 생성
        tag = TagEntity(
            name=clean_name, category_id=category_id, description=description
        )
        created_tag = self.repository.create(tag)

        # 시그널 발생
        self.tagCreated.emit(created_tag)
        self.tagsChanged.emit()

        return created_tag

    def get_tag(self, tag_id: int) -> Optional[TagEntity]:
        """
        ID로 태그 조회

        Args:
            tag_id: 태그 ID

        Returns:
            조회된 태그 객체 또는 None
        """
        return self.repository.get_by_id(tag_id)

    def get_tag_by_name(self, name: str) -> Optional[TagEntity]:
        """
        이름으로 태그 조회

        Args:
            name: 태그 이름

        Returns:
            조회된 태그 객체 또는 None
        """
        # 이름 정제 (공백 제거, # 제거)
        clean_name = name.strip().lstrip("#")

        if not clean_name:
            return None

        return self.repository.get_by_name(clean_name)

    def get_all_tags(self) -> List[TagEntity]:
        """
        모든 태그 조회

        Returns:
            태그 객체 목록
        """
        return self.repository.get_all()

    def update_tag(self, tag: TagEntity) -> bool:
        """
        태그 정보 업데이트

        Args:
            tag: 업데이트할 태그 객체

        Returns:
            성공 여부
        """
        if tag.id is None:
            return False

        # 이름 정제 (공백 제거, # 제거)
        tag.name = tag.name.strip().lstrip("#")

        if not tag.name:
            raise ValueError("태그 이름은 공백일 수 없습니다.")

        # 업데이트 실행
        success = self.repository.update(tag)

        if success:
            # 시그널 발생
            self.tagUpdated.emit(tag)
            self.tagsChanged.emit()

        return success

    def delete_tag(self, tag_id: int) -> bool:
        """
        태그 삭제

        Args:
            tag_id: 삭제할 태그 ID

        Returns:
            성공 여부
        """
        success = self.repository.delete(tag_id)

        if success:
            # 시그널 발생
            self.tagDeleted.emit(tag_id)
            self.tagsChanged.emit()

        return success

    def parse_tags_from_text(self, text: str) -> List[TagEntity]:
        """
        텍스트에서 태그 추출

        Args:
            text: 분석할 텍스트

        Returns:
            추출된 태그 객체 목록
        """
        import re

        # 정규식으로 #태그 형식 추출
        tag_pattern = r"#(\w+)"
        matches = re.findall(tag_pattern, text)

        tags = []
        for match in matches:
            # 태그가 존재하면 가져오고, 없으면 생성
            tag = self.repository.get_by_name(match)
            if not tag:
                tag = self.create_tag(match)

            tags.append(tag)

        return tags
