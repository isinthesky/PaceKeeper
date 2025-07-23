# container/service_registration.py

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .di_container import DIContainer


class ServiceRegistry:
    """
    서비스 등록을 위한 레지스트리 클래스

    모든 서비스 등록 로직을 중앙화하여 관리합니다.
    """

    @staticmethod
    def register_all_services(container: "DIContainer") -> None:
        """
        모든 서비스를 컨테이너에 등록

        Args:
            container: DI 컨테이너 인스턴스
        """
        # Repository 인터페이스 및 구현체 등록
        ServiceRegistry._register_repositories(container)

        # Service 인터페이스 및 구현체 등록
        ServiceRegistry._register_services(container)

        # Controller 등록
        ServiceRegistry._register_controllers(container)

        # 기타 컴포넌트 등록
        ServiceRegistry._register_infrastructure(container)

    @staticmethod
    def _register_repositories(container: "DIContainer") -> None:
        """Repository 레이어 서비스 등록"""
        from pacekeeper.interfaces.repositories.i_category_repository import ICategoryRepository
        from pacekeeper.interfaces.repositories.i_log_repository import ILogRepository
        from pacekeeper.interfaces.repositories.i_tag_repository import ITagRepository
        from pacekeeper.repository.category_repository import CategoryRepository
        from pacekeeper.repository.log_repository import LogRepository
        from pacekeeper.repository.tag_repository import TagRepository

        # Repository 인터페이스와 구현체 등록
        container.register_singleton(ILogRepository, LogRepository)
        container.register_singleton(ITagRepository, TagRepository)
        container.register_singleton(ICategoryRepository, CategoryRepository)

    @staticmethod
    def _register_services(container: "DIContainer") -> None:
        """Service 레이어 서비스 등록"""
        from pacekeeper.interfaces.services.i_category_service import ICategoryService
        from pacekeeper.interfaces.services.i_log_service import ILogService
        from pacekeeper.interfaces.services.i_tag_service import ITagService
        from pacekeeper.services.category_service import CategoryService
        from pacekeeper.services.log_service import LogService
        from pacekeeper.services.tag_service import TagService

        # Service 인터페이스와 구현체 등록
        container.register_singleton(ILogService, LogService)
        container.register_singleton(ITagService, TagService)
        container.register_singleton(ICategoryService, CategoryService)

    @staticmethod
    def _register_controllers(container: "DIContainer") -> None:
        """Controller 레이어 서비스 등록"""
        from pacekeeper.controllers.config_controller import ConfigController
        from pacekeeper.controllers.main_controller import MainController
        from pacekeeper.controllers.sound_manager import SoundManager
        from pacekeeper.controllers.timer_controller import TimerService

        # ConfigController는 특별히 처리 (기존 싱글톤 유지)
        container.register_singleton(ConfigController, lambda: ConfigController())

        # 다른 Controller들
        container.register_singleton(SoundManager, SoundManager)
        container.register_singleton(TimerService, TimerService)
        container.register_transient(MainController, MainController)

    @staticmethod
    def _register_infrastructure(container: "DIContainer") -> None:
        """인프라스트럭처 서비스 등록"""
        from pacekeeper.database import DatabaseSessionManager

        # 데이터베이스 세션 관리자 등록
        container.register_singleton(DatabaseSessionManager, DatabaseSessionManager)
