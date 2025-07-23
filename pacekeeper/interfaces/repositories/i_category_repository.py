# interfaces/repositories/i_category_repository.py

from abc import ABC, abstractmethod

from pacekeeper.repository.entities import Category


class ICategoryRepository(ABC):
    """
    카테고리 Repository 인터페이스

    카테고리 데이터 접근을 위한 추상 인터페이스를 정의합니다.
    """

    @abstractmethod
    def init_db(self) -> None:
        """데이터베이스 초기화"""
        pass

    @abstractmethod
    def create_category(self, name: str, description: str = "", color: str = "#FFFFFF") -> Category:
        """
        새로운 카테고리를 추가하거나 이미 존재하는 카테고리를 반환

        Args:
            name: 카테고리 이름
            description: 카테고리 설명 (선택사항)
            color: 카테고리 색상 (선택사항)

        Returns:
            추가되거나 기존 카테고리 객체
        """
        pass

    @abstractmethod
    def get_category(self, category_id: int) -> Category | None:
        """
        카테고리 ID로 카테고리 조회

        Args:
            category_id: 조회할 카테고리 ID

        Returns:
            찾은 카테고리 또는 None
        """
        pass

    @abstractmethod
    def get_categories(self) -> list[Category]:
        """
        모든 활성 카테고리를 조회

        Returns:
            활성 카테고리 목록
        """
        pass

    @abstractmethod
    def update_category(self, category_id: int, name: str | None = None,
                       description: str | None = None, color: str | None = None) -> None:
        """
        카테고리 업데이트

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
        카테고리 삭제 (soft delete)

        Args:
            category_id: 삭제할 카테고리 ID
        """
        pass
