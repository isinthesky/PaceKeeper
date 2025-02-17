import logging
import logging.handlers
import os
import sys

class DesktopLogger:
    def __init__(self, app_name="PaceKeeper"):
        self.app_name = app_name

        # OS별 표준 로그 경로 설정
        if sys.platform == 'win32':
            base_dir = os.getenv('APPDATA')
        else:
            base_dir = os.path.expanduser("~")
        
        # Windows: APPDATA\PaceKeeper\logs, 기타 OS: ~/.pacekeeper/logs
        if sys.platform == 'win32':
            self.log_dir = os.path.join(base_dir, app_name, 'logs')
        else:
            self.log_dir = os.path.join(base_dir, f".{app_name.lower()}", "logs")
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
        
        # 로거 초기화 및 파일 핸들러 설정
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger(self.app_name)
        # 이미 핸들러가 등록된 경우 중복 등록 방지
        if logger.hasHandlers():
            return logger

        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 로그 파일은 최대 1MB 크기로 제한, 최대 7개 백업
        log_file = os.path.join(self.log_dir, f"{self.app_name}.log")
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=7,
            encoding='utf-8'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def log_error(self, error_msg, exc_info=None):
        """치명적인 오류 로깅"""
        if exc_info:
            self.logger.error(f"{error_msg}", exc_info=True)
        else:
            self.logger.error(f"{error_msg}")

    def log_user_action(self, action):
        """주요 사용자 액션 로깅"""
        self.logger.info(f"User Action: {action}")

    def log_system_event(self, event):
        """시스템 이벤트 로깅"""
        self.logger.info(f"System Event: {event}") 