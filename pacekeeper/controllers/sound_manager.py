import wx
import pygame
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.consts.settings import SET_SOUND_VOLUME
from pacekeeper.consts.labels import load_language_resource

lang_res = load_language_resource()

class SoundManager:
    """알람 사운드 로직을 별도로 관리"""
    
    def __init__(self, config_ctrl: ConfigController):
        self.config_ctrl = config_ctrl
        pygame.mixer.init()
        
    def play_sound(self, sound_file: str):
        """사운드 재생"""
        try:
            volume = (self.config_ctrl.get_setting(SET_SOUND_VOLUME, 70) or 70) / 100
            
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()
        except Exception as e:
            wx.LogError(lang_res.error_messages['ALARM_SOUND'].format(e))
            
    def stop_sound(self):
        """사운드 정지"""
        pygame.mixer.music.stop()
        
    def cleanup(self):
        """리소스 정리"""
        try:
            self.stop_sound()
            pygame.mixer.quit()
        except Exception as e:
            wx.LogError(f"Sound cleanup error: {e}") 