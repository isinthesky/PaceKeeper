# interfaces/services/__init__.py

from .i_category_service import ICategoryService
from .i_log_service import ILogService
from .i_tag_service import ITagService

__all__ = [
    "ILogService",
    "ITagService",
    "ICategoryService",
]
