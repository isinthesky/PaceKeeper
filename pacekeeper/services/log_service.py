import json
from datetime import datetime

from icecream import ic

from pacekeeper.interfaces.repositories.i_log_repository import ILogRepository
from pacekeeper.interfaces.repositories.i_tag_repository import ITagRepository
from pacekeeper.interfaces.services.i_log_service import ILogService
from pacekeeper.repository.entities import Log
from pacekeeper.utils.desktop_logger import DesktopLogger
from pacekeeper.utils.functions import extract_tags


class LogService(ILogService):
    def __init__(self, log_repository: ILogRepository, tag_repository: ITagRepository) -> None:
        self.logger: DesktopLogger = DesktopLogger("PaceKeeper")
        self.repository: ILogRepository = log_repository
        self.tag_repo: ITagRepository = tag_repository
        self.logger.log_system_event("LogService 초기화됨.")

    def create_study_log(self, message: str, study_start_time: datetime | None = None) -> None:
        """
        메시지와 선택적 study_start_time을 이용해 학습 로그를 생성합니다.
        study_start_time이 제공되면 이를 시작 시간으로 사용하고, 그렇지 않으면 현재 시간을 사용합니다.
        """
        self.logger.log_user_action(f"학습 로그 생성 요청: {message}")

        now = datetime.now()
        if study_start_time:
            start_date = study_start_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            start_date = now.strftime("%Y-%m-%d %H:%M:%S")
        end_date = now.strftime("%Y-%m-%d %H:%M:%S")

        # 메시지에서 태그 추출 및 태그 테이블에 추가하여 태그 ID 수집
        tag_ids: list[int] = []
        tags_list: list[str] = extract_tags(message)
        if tags_list:
            for tag in tags_list:
                try:
                    tag_entity = self.tag_repo.add_tag(tag)
                    ic("tag_entity", tag_entity)
                    tag_ids.append(tag_entity.id)
                    ic("tag_ids", tag_ids)
                except Exception:
                    self.logger.log_error("태그 추가 실패", exc_info=True)

        # 태그 ID 리스트를 JSON 형식으로 변환하여 저장
        tags_json = json.dumps(tag_ids, ensure_ascii=False)

        ic(tags_json)

        new_log = Log(start_date=start_date, end_date=end_date, message=message, tags=tags_json)
        try:
            self.repository.save_log(new_log)
            self.logger.log_system_event("학습 로그 저장 성공")
        except Exception:
            self.logger.log_error("학습 로그 저장 실패", exc_info=True)

    def retrieve_all_logs(self) -> list[Log]:
        """
        모든 활성 로그를 조회합니다.
        """
        try:
            logs = self.repository.get_all_logs()
            self.logger.log_system_event("전체 로그 조회 성공")
            return logs
        except Exception:
            self.logger.log_error("전체 로그 조회 실패", exc_info=True)
            return []

    def retrieve_logs_by_period(self, start_date: str, end_date: str) -> list[Log]:
        """
        지정한 기간 동안의 활성 로그를 조회합니다.
        """
        try:
            logs = self.repository.get_logs_by_period(start_date, end_date)
            self.logger.log_system_event(f"기간({start_date} ~ {end_date}) 로그 조회 성공")
            return logs
        except Exception:
            self.logger.log_error("기간 로그 조회 실패", exc_info=True)
            return []

    def retrieve_logs_by_tag(self, tag_keyword: str) -> list[Log]:
        """
        지정한 태그를 포함하는 활성 로그를 조회합니다.
        """
        try:
            logs = self.repository.get_logs_by_tag(tag_keyword)
            self.logger.log_system_event(f"태그({tag_keyword}) 로그 조회 성공")
            return logs
        except Exception:
            self.logger.log_error("태그 로그 조회 실패", exc_info=True)
            return []

    def retrieve_recent_logs(self, limit: int = 20) -> list[Log]:
        """
        최근 활성 로그들을 조회합니다.
        """
        try:
            logs = self.repository.get_recent_logs(limit)
            for log in logs:
                ic("log", log.__dict__)
            self.logger.log_system_event(f"최근 {limit}개의 로그 조회 성공")
            return logs
        except Exception:
            self.logger.log_error("최근 로그 조회 실패", exc_info=True)
            return []

    def remove_logs_by_ids(self, log_ids: list[int]) -> None:
        """
        지정한 로그 ID 리스트에 해당하는 로그들을 soft delete 처리합니다.
        """
        if not log_ids:
            return
        try:
            self.repository.soft_delete_logs(log_ids)
            self.logger.log_system_event(f"로그 삭제 (IDs: {log_ids}) 성공")
        except Exception:
            self.logger.log_error("로그 삭제 실패", exc_info=True)
