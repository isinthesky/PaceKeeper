# interfaces/__init__.py

# Repository interfaces
from .repositories.i_category_repository import ICategoryRepository
from .repositories.i_log_repository import ILogRepository
from .repositories.i_tag_repository import ITagRepository
from .services.i_category_service import ICategoryService

# Service interfaces
from .services.i_log_service import ILogService
from .services.i_tag_service import ITagService

__all__ = [
    "ILogRepository",
    "ITagRepository",
    "ICategoryRepository",
    "ILogService",
    "ITagService",
    "ICategoryService",
]
