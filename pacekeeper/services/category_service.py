

from pacekeeper.interfaces.repositories.i_category_repository import ICategoryRepository
from pacekeeper.interfaces.services.i_category_service import ICategoryService
from pacekeeper.repository.entities import Category
from pacekeeper.utils.desktop_logger import DesktopLogger


class CategoryService(ICategoryService):
    """
    CategoryService: 카테고리 관련 비즈니스 로직을 처리하는 서비스 클래스입니다.

    주요 책임:
      - 새로운 카테고리 추가
      - 모든 활성 카테고리 조회
      - 카테고리 업데이트 (이름, 설명, 색상)
      - 카테고리 soft delete (state 업데이트)
    """

    def __init__(self, category_repository: ICategoryRepository) -> None:
        self.logger: DesktopLogger = DesktopLogger("PaceKeeper")
        self.repo: ICategoryRepository = category_repository
        self.logger.log_system_event("CategoryService 초기화됨.")

    def create_category(self, name: str, description: str = "", color: str = "#FFFFFF") -> Category:
        """
        새로운 카테고리를 추가하거나 이미 존재하는 경우 기존 카테고리를 반환합니다.

        매개변수:
            name (str): 카테고리 이름
            description (str, optional): 카테고리 설명
            color (str, optional): RGB 색상 값 (예: "#RRGGBB")

        반환값:
            Category: 추가되었거나 조회된 카테고리 객체
        """
        self.logger.log_system_event(
            f"카테고리 추가 요청: 이름 = {name}, 설명 = {description}, 색상 = {color}"
        )
        try:
            category = self.repo.create_category(name, description, color)
            self.logger.log_system_event(f"카테고리 추가 성공: {category.name}")
            return category
        except Exception as e:
            self.logger.log_error("카테고리 추가 실패", exc_info=True)
            raise e

    def get_category_by_id(self, category_id: int) -> Category | None:
        """
        지정된 ID의 카테고리를 조회합니다.
        """
        try:
            category = self.repo.get_category(category_id)
            self.logger.log_system_event(f"카테고리 조회 성공: {category.name}")
            return category
        except Exception:
            self.logger.log_error("카테고리 조회 실패", exc_info=True)
            return None

    def get_category(self, category_id: int) -> Category | None:
        """
        ID로 카테고리를 조회합니다. (get_category_by_id의 단축형)
        """
        return self.get_category_by_id(category_id)

    def get_categories(self) -> list[Category]:
        """
        모든 활성 카테고리들을 조회합니다.

        반환값:
            List[Category]: 활성 카테고리 목록
        """
        try:
            categories = self.repo.get_categories()
            self.logger.log_system_event(
                f"카테고리 조회 성공: {len(categories)}개 카테고리 조회됨."
            )
            return categories
        except Exception:
            self.logger.log_error("카테고리 조회 실패", exc_info=True)
            return []

    def get_all_categories(self) -> list[Category]:
        """
        모든 활성 카테고리들을 조회합니다. (get_categories 별칭)

        반환값:
            List[Category]: 활성 카테고리 목록
        """
        return self.get_categories()

    def update_category(
        self,
        category_id: int,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
    ) -> None:
        """
        지정된 카테고리의 이름, 설명 및 색상을 업데이트합니다.

        매개변수:
            category_id (int): 업데이트할 카테고리의 ID
            name (Optional[str]): 새 이름 (업데이트하지 않으려면 None)
            description (Optional[str]): 새 설명 (업데이트하지 않으려면 None)
            color (Optional[str]): 새 RGB 색상 값 (예: "#RRGGBB"), 업데이트하지 않으려면 None
        """
        self.logger.log_system_event(
            f"카테고리 업데이트 요청: ID = {category_id}, 이름 = {name}, 설명 = {description}, 색상 = {color}"
        )
        try:
            self.repo.update_category(category_id, name, description, color)
            self.logger.log_system_event("카테고리 업데이트 성공")
        except Exception:
            self.logger.log_error("카테고리 업데이트 실패", exc_info=True)

    def delete_category(self, category_id: int) -> None:
        """
        지정된 카테고리를 soft delete 처리합니다 (state 업데이트).

        매개변수:
            category_id (int): 삭제할 카테고리의 ID
        """
        self.logger.log_system_event(f"카테고리 삭제 요청: ID = {category_id}")
        try:
            self.repo.delete_category(category_id)
            self.logger.log_system_event("카테고리 삭제 성공")
        except Exception:
            self.logger.log_error("카테고리 삭제 실패", exc_info=True)
