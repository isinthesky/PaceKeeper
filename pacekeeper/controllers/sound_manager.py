import pygame
import os
import sys
import logging
from PyQt5.QtWidgets import QMessageBox
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.consts.settings import SET_ALARM_VOLUME
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.utils.resource_path import resource_path

lang_res = load_language_resource()
logger = logging.getLogger(__name__)

class SoundManager:
    """알람 사운드 로직을 별도로 관리"""
    
    def __init__(self, config_ctrl: ConfigController):
        self.config_ctrl = config_ctrl
        try:
            # PyInstaller 환경에서는 더 명시적인 초기화 필요
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            logger.info("Pygame mixer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")
            # 재시도 - 기본 설정으로
            try:
                pygame.mixer.init()
                logger.info("Pygame mixer initialized with defaults")
            except Exception as e2:
                logger.error(f"Failed to initialize pygame mixer (retry): {e2}")
        
    def play_sound(self, sound_file: str):
        """사운드 재생"""
        try:
            volume = (self.config_ctrl.get_setting(SET_ALARM_VOLUME, 70) or 70) / 100
            
            # PyInstaller 환경에서 리소스 경로 처리
            original_path = sound_file
            if not os.path.exists(sound_file):
                sound_file = resource_path(sound_file)
            
            logger.info(f"Attempting to play sound: {sound_file}")
            logger.info(f"File exists: {os.path.exists(sound_file)}")
            
            # PyInstaller 환경에서는 pygame.mixer.Sound 사용이 더 안정적
            if getattr(sys, 'frozen', False):
                try:
                    sound = pygame.mixer.Sound(sound_file)
                    sound.set_volume(volume)
                    sound.play()
                    logger.info("Sound played using mixer.Sound")
                except Exception as se:
                    logger.error(f"mixer.Sound failed: {se}, trying mixer.music")
                    pygame.mixer.music.load(sound_file)
                    pygame.mixer.music.set_volume(volume)
                    pygame.mixer.music.play()
            else:
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play()
                
            logger.info("Sound played successfully")
        except Exception as e:
            logger.error(f"Failed to play sound {sound_file}: {e}")
            error_msg = lang_res.error_messages.get('ALARM_SOUND', '알람 재생 에러: {}').format(e)
            QMessageBox.critical(None, "Error", error_msg)
            
    def stop_sound(self):
        """사운드 정지"""
        pygame.mixer.music.stop() 