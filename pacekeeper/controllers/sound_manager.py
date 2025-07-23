import logging
import os
import sys

from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QMessageBox

from pacekeeper.consts.labels import load_language_resource
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.utils.resource_path import resource_path

lang_res = load_language_resource()
logger = logging.getLogger(__name__)

class SoundManager:
    """알람 사운드 로직을 별도로 관리"""

    def __init__(self, config_ctrl: ConfigController):
        self.config_ctrl = config_ctrl
        self.current_sound = None
        logger.info("SoundManager initialized with QSound")

    def play_sound(self, sound_file: str):
        """사운드 재생"""
        try:
            # PyInstaller 환경에서 리소스 경로 처리
            original_path = sound_file
            if not os.path.exists(sound_file):
                sound_file = resource_path(sound_file)

            logger.info(f"Attempting to play sound: {sound_file}")
            logger.info(f"File exists: {os.path.exists(sound_file)}")

            # 이전 사운드가 재생 중이면 중지
            if self.current_sound is not None:
                self.current_sound.stop()

            # QSound 사용 (볼륨 조절은 불가능하지만 안정적)
            self.current_sound = QSound(sound_file)
            self.current_sound.play()
            logger.info("Sound played successfully using QSound")

        except Exception as e:
            logger.error(f"Failed to play sound {sound_file}: {e}")
            # 백업 방법으로 시스템 사운드 재생 (macOS)
            try:
                if sys.platform == 'darwin':
                    os.system(f'afplay "{sound_file}" &')
                    logger.info("Sound played using system command (afplay)")
            except Exception as e2:
                logger.error(f"System command also failed: {e2}")
                error_msg = lang_res.error_messages.get('ALARM_SOUND', '알람 재생 에러: {}').format(e)
                QMessageBox.critical(None, "Error", error_msg)

    def stop_sound(self):
        """사운드 정지"""
        if self.current_sound is not None:
            self.current_sound.stop()
            logger.info("Sound stopped")
