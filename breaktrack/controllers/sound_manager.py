import pygame
import wx

class SoundManager:
    """알람 사운드 로직을 별도로 관리"""
    
    def __init__(self):
        pygame.mixer.init()
        
    def play_sound(self, sound_file: str):
        """사운드 재생"""
        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
        except Exception as e:
            wx.LogError(f"알람 재생 에러: {e}")
            
    def stop_sound(self):
        """사운드 정지"""
        pygame.mixer.music.stop() 