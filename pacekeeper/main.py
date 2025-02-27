#!/usr/bin/env python3
# main.py
import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.controllers.main_controller import MainController
from pacekeeper.views.main_window import MainWindow
from pacekeeper.utils.logger import setup_logger

def main():
    """애플리케이션 메인 함수"""
    # 로깅 설정
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("PaceKeeper 애플리케이션 시작")
    
    try:
        # QApplication 인스턴스 생성
        app = QApplication(sys.argv)
        
        # 애플리케이션 아이콘 설정
        app_icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.png')
        if os.path.exists(app_icon_path):
            app.setWindowIcon(QIcon(app_icon_path))
        
        # 설정 컨트롤러 생성
        config_ctrl = ConfigController()
        
        # 메인 윈도우 생성
        main_window = MainWindow(None, config_ctrl)
        
        # 메인 컨트롤러 생성 및 메인 윈도우에 연결
        main_ctrl = MainController(main_window, config_ctrl)
        
        # 메인 윈도우에 메인 컨트롤러 설정
        main_window.main_ctrl = main_ctrl
        
        # 메인 윈도우 표시
        main_window.show()
        
        # 애플리케이션 실행
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"애플리케이션 실행 중 오류 발생: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
