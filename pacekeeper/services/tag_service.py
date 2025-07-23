import json

from icecream import ic

from pacekeeper.repository.entities import Tag
from pacekeeper.repository.tag_repository import TagRepository
from pacekeeper.utils.desktop_logger import DesktopLogger


class TagService:
    def __init__(self) -> None:
        self.logger: DesktopLogger = DesktopLogger("PaceKeeper")
        self.repository: TagRepository = TagRepository()
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
        모든 태그 목록을 반환합니다.

        Returns:
            태그 딕셔너리 목록
        """
        tags: list[Tag] = self.repository.get_tags()
        # 명시적으로 문자열 변환하여 인코딩 보장
        tag_dicts = []
        for tag in tags:
            tag_dict = tag.to_dict()
            tag_dict["name"] = str(tag_dict["name"])  # 명시적 문자열 변환
            tag_dicts.append(tag_dict)
        return tag_dicts

    def update_tag(self, tag: Tag) -> Tag | None:
        """
        태그 업데이트

        Args:
            tag: 업데이트할 태그 객체

        Returns:
            업데이트된 태그 객체 또는 None (업데이트 실패 시)
        """
        try:
            updated_tag = self.repository.update_tag(
                tag.id, tag.name, tag.description, tag.category_id
            )
            if updated_tag:
                return updated_tag
            else:
                self.logger.log_error("태그 업데이트 실패", exc_info=True)
                return None
        except Exception as e:
            self.logger.log_error(f"태그 업데이트 실패: {e}", exc_info=True)
            raise e
