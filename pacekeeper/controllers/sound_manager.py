import pygame
import wx
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.const import SETTINGS_BREAK_SOUND_VOLUME

class SoundManager:
    """알람 사운드 로직을 별도로 관리"""
    
    def __init__(self, config: ConfigController):
        self.config = config
        pygame.mixer.init()
        
    def play_sound(self, sound_file: str):
        """사운드 재생"""
        try:
            volume_percent = self.config.get_setting(SETTINGS_BREAK_SOUND_VOLUME)
            volume = volume_percent / 100.0
            
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()
        except Exception as e:
            wx.LogError(f"알람 재생 에러: {e}")
            
    def stop_sound(self):
        """사운드 정지"""
        pygame.mixer.music.stop() 