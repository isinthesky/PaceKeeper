# interfaces/services/i_tag_service.py

from abc import ABC, abstractmethod

from pacekeeper.repository.entities import Tag


class ITagService(ABC):
    """
    태그 Service 인터페이스

    태그 관련 비즈니스 로직을 위한 추상 인터페이스를 정의합니다.
    """

    @abstractmethod
    def get_tag_text(self, tags_json: str) -> list[str]:
        """
        태그 JSON에서 태그 텍스트 목록을 추출합니다.

        Args:
            tags_json: 태그 ID가 저장된 JSON 문자열

        Returns:
            태그 이름 문자열 목록
        """
        pass

    @abstractmethod
    def get_all_tags(self) -> list[Tag]:
        """
        모든 활성 태그를 조회합니다.

        Returns:
            활성 태그 목록
        """
        pass

    @abstractmethod
    def create_tag(self, name: str, description: str = "") -> Tag:
        """
        새로운 태그를 생성합니다.

        Args:
            name: 태그 이름
            description: 태그 설명

        Returns:
            생성된 태그 객체
        """
        pass

    @abstractmethod
    def update_tag(self, tag_id: int, name: str | None = None,
                   description: str | None = None) -> Tag | None:
        """
        태그를 업데이트합니다.

        Args:
            tag_id: 업데이트할 태그 ID
            name: 새로운 태그 이름 (선택사항)
            description: 새로운 태그 설명 (선택사항)

        Returns:
            업데이트된 태그 객체 또는 None
        """
        pass

    @abstractmethod
    def delete_tag(self, tag_id: int) -> None:
        """
        태그를 삭제합니다.

        Args:
            tag_id: 삭제할 태그 ID
        """
        pass
