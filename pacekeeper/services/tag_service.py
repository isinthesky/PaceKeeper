import json

from icecream import ic

from pacekeeper.interfaces.repositories.i_tag_repository import ITagRepository
from pacekeeper.interfaces.services.i_tag_service import ITagService
from pacekeeper.repository.entities import Tag
from pacekeeper.utils.desktop_logger import DesktopLogger


class TagService(ITagService):
    def __init__(self, tag_repository: ITagRepository) -> None:
        self.logger: DesktopLogger = DesktopLogger("PaceKeeper")
        self.repository: ITagRepository = tag_repository
        self.logger.log_system_event("TagService 초기화됨.")

    def get_tag_text(self, tag_ids: list[int] | str) -> list[str]:
        """
        태그 ID 목록을 받아 태그 이름을 문자열로 변환합니다.

        Args:
            tag_ids: 태그 ID 목록 (정수 리스트 또는 JSON 문자열)

        Returns:
            태그 이름 목록
        """
        # 입력이 문자열인 경우 JSON 파싱
        if isinstance(tag_ids, str):
            try:
                tag_ids = json.loads(tag_ids)
            except json.JSONDecodeError as e:
                ic(f"JSON 파싱 오류: {e} - 입력: {tag_ids}")
                return []

        # 입력이 리스트가 아닌 경우 빈 리스트 반환
        if not isinstance(tag_ids, list):
            ic(f"태그 ID가 리스트가 아닙니다: {type(tag_ids)}")
            return []

        tag_names = []
        for tag_id in tag_ids:
            try:
                tag: Tag = self.repository.get_tag(tag_id)
                if tag and tag.name:
                    # 직접 태그 이름을 추가하여 불필요한 중간 과정 제거
                    # 명시적으로 str() 변환하여 인코딩 처리 보장
                    tag_names.append(str(tag.name))
            except Exception as e:
                ic(f"태그 조회 오류: {e} - 태그 ID: {tag_id}")

        return tag_names

    def get_tag(self, tag_id: int) -> Tag | None:
        """
        지정된 ID의 태그를 조회합니다.

        Args:
            tag_id: 조회할 태그 ID

        Returns:
            태그 객체 또는 None (조회 실패 시)
        """
        try:
            tag: Tag = self.repository.get_tag(tag_id)
            return tag
        except Exception as e:
            self.logger.log_error(f"태그 조회 실패: {e}", exc_info=True)
            return None

    def get_tags(self) -> list[dict]:
        """
        모든 태그를 딕셔너리 형태로 반환합니다.

        Returns:
            태그 딕셔너리 목록 (UI에서 사용)
        """
        try:
            tag_entities = self.repository.get_tags()
            return [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "description": tag.description,
                    "category_id": tag.category_id or 1  # 기본 카테고리 ID
                }
                for tag in tag_entities
            ]
        except Exception as e:
            self.logger.log_error(f"태그 목록 조회 실패: {e}", exc_info=True)
            return []

    def get_all_tags(self) -> list[Tag]:
        """
        모든 활성 태그를 조회합니다.

        Returns:
            활성 태그 목록
        """
        return self.repository.get_tags()

    def create_tag(self, name: str, description: str = "") -> Tag:
        """
        새로운 태그를 생성합니다.

        Args:
            name: 태그 이름
            description: 태그 설명

        Returns:
            생성된 태그 객체
        """
        try:
            return self.repository.add_tag(name, description)
        except Exception as e:
            self.logger.log_error(f"태그 생성 실패: {e}", exc_info=True)
            raise e

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
        try:
            return self.repository.update_tag(tag_id, name, description)
        except Exception as e:
            self.logger.log_error(f"태그 업데이트 실패: {e}", exc_info=True)
            return None

    def delete_tag(self, tag_id: int) -> None:
        """
        태그를 삭제합니다.

        Args:
            tag_id: 삭제할 태그 ID
        """
        try:
            self.repository.delete_tag(tag_id)
        except Exception as e:
            self.logger.log_error(f"태그 삭제 실패: {e}", exc_info=True)
            raise e
