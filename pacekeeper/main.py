#!/usr/bin/env python3
# main.py
import logging
import os
import sys
import traceback
from typing import NoReturn

# 디버그 로그 설정
debug_log_path: str = os.path.expanduser("~/Desktop/pacekeeper_debug.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(debug_log_path, mode="w"), logging.StreamHandler(sys.stdout)],
)

logger: logging.Logger = logging.getLogger(__name__)
logger.info("=== PaceKeeper 앱 시작 ===")
logger.info(f"Python 버전: {sys.version}")
logger.info(f"실행 경로: {sys.executable}")
logger.info(f"현재 디렉토리: {os.getcwd()}")
logger.info(f"sys.path: {sys.path}")

# PyInstaller 환경에서 추가 경로 설정
if getattr(sys, "frozen", False):
    # PyInstaller 실행 환경
    base_path = sys._MEIPASS
    # Qt 플러그인 경로 설정
    os.environ["QT_PLUGIN_PATH"] = os.path.join(base_path, "PyQt5", "Qt5", "plugins")
    logger.info(f"PyInstaller 환경 감지: base_path={base_path}")
    # 모듈 경로 추가
    if base_path not in sys.path:
        sys.path.insert(0, base_path)

try:
    logger.info("PyQt5 임포트 시도...")
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QApplication

    logger.info("PyQt5 임포트 성공")

    logger.info("앱 모듈 임포트 시도...")
    from pacekeeper.container import DIContainer, ServiceRegistry
    from pacekeeper.controllers.config_controller import ConfigController
    from pacekeeper.controllers.main_controller import MainController
    from pacekeeper.utils.logger import setup_logger
    from pacekeeper.views.main_window import MainWindow

    logger.info("앱 모듈 임포트 성공")

except Exception as e:
    logger.error(f"임포트 오류: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)


def main() -> NoReturn:
    """애플리케이션 메인 함수"""
    try:
        # 로깅 설정
        logger.info("애플리케이션 로거 설정...")
        setup_logger()
        logger.info("PaceKeeper 애플리케이션 시작")

        # QApplication 인스턴스 생성
        logger.info("QApplication 생성...")
        app = QApplication(sys.argv)

        # 애플리케이션 아이콘 설정
        app_icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        logger.info(f"아이콘 경로: {app_icon_path}")
        if os.path.exists(app_icon_path):
            app.setWindowIcon(QIcon(app_icon_path))
            logger.info("아이콘 설정 완료")
        else:
            logger.warning(f"아이콘 파일을 찾을 수 없음: {app_icon_path}")

        # DI 컨테이너 설정
        logger.info("DI 컨테이너 초기화...")
        container = DIContainer()
        ServiceRegistry.register_all_services(container)

        # 설정 컨트롤러 생성
        logger.info("ConfigController 생성...")
        config_ctrl = container.resolve(ConfigController)

        # 메인 윈도우 생성 (임시로 None 컨트롤러)
        logger.info("MainWindow 생성...")
        main_window = MainWindow(None, config_ctrl)

        # 메인 컨트롤러 생성 (DI 컨테이너를 통해)
        logger.info("MainController 생성...")
        # MainController는 MainWindow를 생성자 매개변수로 받으므로 수동으로 생성
        from pacekeeper.controllers.sound_manager import SoundManager
        from pacekeeper.controllers.timer_controller import TimerService
        from pacekeeper.interfaces.services.i_category_service import ICategoryService
        from pacekeeper.interfaces.services.i_log_service import ILogService
        from pacekeeper.interfaces.services.i_tag_service import ITagService

        category_service = container.resolve(ICategoryService)
        log_service = container.resolve(ILogService)
        tag_service = container.resolve(ITagService)
        sound_manager = SoundManager(config_ctrl)  # SoundManager는 수동 생성

        # TimerService는 콜백 함수가 필요하므로 수동 생성
        timer_service = TimerService(
            config_ctrl,
            update_callback=main_window.update_timer_label,
            on_finish=None  # 나중에 MainController에서 설정
        )

        main_ctrl = MainController(
            main_window,
            config_ctrl,
            category_service,
            tag_service,
            log_service,
            sound_manager,
            timer_service
        )
        
        # MainWindow에 MainController 설정 (의존성 주입 완료)
        main_window.set_main_controller(main_ctrl)

        # 메인 윈도우 표시
        logger.info("메인 윈도우 표시...")
        main_window.show()

        # 애플리케이션 실행
        logger.info("앱 이벤트 루프 시작...")
        sys.exit(app.exec_())

    except Exception as e:
        logger.error(f"애플리케이션 실행 중 오류 발생: {e}")
        logger.error(traceback.format_exc())

        # 오류를 파일에 기록
        error_log_path = os.path.expanduser("~/Desktop/pacekeeper_error.log")
        with open(error_log_path, "w") as f:
            f.write(f"Error: {e}\n")
            f.write(traceback.format_exc())

        sys.exit(1)


if __name__ == "__main__":
    main()
