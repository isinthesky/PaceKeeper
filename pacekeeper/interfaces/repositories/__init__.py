# interfaces/repositories/__init__.py

from .i_category_repository import ICategoryRepository
from .i_log_repository import ILogRepository
from .i_tag_repository import ITagRepository

__all__ = [
    "ILogRepository",
    "ITagRepository",
    "ICategoryRepository",
]
