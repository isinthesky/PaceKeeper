# interfaces/repositories/i_tag_repository.py

from abc import ABC, abstractmethod

from pacekeeper.repository.entities import Tag


class ITagRepository(ABC):
    """
    태그 Repository 인터페이스

    태그 데이터 접근을 위한 추상 인터페이스를 정의합니다.
    """

    @abstractmethod
    def init_db(self) -> None:
        """데이터베이스 초기화"""
        pass

    @abstractmethod
    def add_tag(self, name: str, description: str = "") -> Tag:
        """
        새로운 태그를 추가하거나 이미 존재하는 태그를 반환

        Args:
            name: 태그 이름
            description: 태그 설명 (선택사항)

        Returns:
            추가되거나 기존 태그 객체
        """
        pass

    @abstractmethod
    def get_tag(self, tag_id: int) -> Tag | None:
        """
        태그 ID로 태그 조회

        Args:
            tag_id: 조회할 태그 ID

        Returns:
            찾은 태그 또는 None
        """
        pass

    @abstractmethod
    def get_tags(self) -> list[Tag]:
        """
        모든 활성 태그를 조회

        Returns:
            활성 태그 목록
        """
        pass

    @abstractmethod
    def update_tag(self, tag_id: int, name: str | None = None,
                  description: str | None = None, category_id: int | None = None) -> Tag | None:
        """
        태그 업데이트

        Args:
            tag_id: 업데이트할 태그 ID
            name: 새로운 태그 이름 (선택사항)
            description: 새로운 태그 설명 (선택사항)
            category_id: 새로운 카테고리 ID (선택사항)

        Returns:
            업데이트된 태그 또는 None
        """
        pass

    @abstractmethod
    def delete_tag(self, tag_id: int) -> None:
        """
        태그 삭제 (soft delete)

        Args:
            tag_id: 삭제할 태그 ID
        """
        pass
