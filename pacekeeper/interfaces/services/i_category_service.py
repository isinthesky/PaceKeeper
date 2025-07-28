# interfaces/services/i_category_service.py

from abc import ABC, abstractmethod

from pacekeeper.repository.entities import Category


class ICategoryService(ABC):
    """
    카테고리 Service 인터페이스

    카테고리 관련 비즈니스 로직을 위한 추상 인터페이스를 정의합니다.
    """


    @abstractmethod
    def create_category(self, name: str, description: str = "", color: str = "#FFFFFF") -> Category:
        """
        새로운 카테고리를 생성합니다.

        Args:
            name: 카테고리 이름
            description: 카테고리 설명
            color: 카테고리 색상

        Returns:
            생성된 카테고리 객체
        """
        pass

    @abstractmethod
    def update_category(self, category_id: int, name: str | None = None,
                       description: str | None = None, color: str | None = None) -> None:
        """
        카테고리를 업데이트합니다.

        Args:
            category_id: 업데이트할 카테고리 ID
            name: 새로운 카테고리 이름 (선택사항)
            description: 새로운 카테고리 설명 (선택사항)
            color: 새로운 카테고리 색상 (선택사항)
        """
        pass

    @abstractmethod
    def delete_category(self, category_id: int) -> None:
        """
        카테고리를 삭제합니다.

        Args:
            category_id: 삭제할 카테고리 ID
        """
        pass

    @abstractmethod
    def get_category_by_id(self, category_id: int) -> Category | None:
        """
        ID로 카테고리를 조회합니다.

        Args:
            category_id: 조회할 카테고리 ID

        Returns:
            찾은 카테고리 또는 None
        """
        pass

    @abstractmethod
    def get_category(self, category_id: int) -> Category | None:
        """
        ID로 카테고리를 조회합니다. (get_category_by_id의 단축형)

        Args:
            category_id: 조회할 카테고리 ID

        Returns:
            찾은 카테고리 또는 None
        """
        pass

    @abstractmethod
    def get_categories(self) -> list[Category]:
        """
        모든 활성 카테고리를 조회합니다.

        Returns:
            활성 카테고리 목록
        """
        pass
