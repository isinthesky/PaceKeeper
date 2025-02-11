# controllers/main_controller.py
from pacekeeper.controllers.config_controller import ConfigController, AppStatus
from pacekeeper.controllers.sound_manager import SoundManager
from pacekeeper.controllers.timer_controller import TimerService
from pacekeeper.utils import resource_path
from pacekeeper.consts.labels import load_language_resource
from icecream import ic

lang_res = load_language_resource()

class MainController:
    """
    MainController: 애플리케이션의 비즈니스 로직 제어  
    책임: 타이머, 사운드, 사이클 관리 등 UI(MainFrame)와 분리하여 처리
    """
    def __init__(self, main_frame: 'MainFrame', config_ctrl: ConfigController):
        self.main_frame = main_frame
        self.config_ctrl = config_ctrl
        self.sound_manager = SoundManager(config_ctrl)
        self.timer_service = TimerService(
            config_ctrl, 
            update_callback=self.main_frame.update_timer_label,
            on_finish=self.on_study_timer_finish
        )
        self.paused = False

    def start_study_timer(self):
        """공부 타이머 시작 메서드"""
        study_minutes = self.config_ctrl.get_setting("study_time", 25)
        total_seconds = study_minutes * 60
        self.timer_service.start(total_seconds)
        
    def stop_study_timer(self):
        """공부 타이머 중단 메서드"""
        self.timer_service.stop()
        # 추가로 UI 갱신이나 상태 초기화 작업이 필요하면 이곳에 구현합니다.
    
    def toggle_pause(self):
        """일시정지/재개 토글 메서드"""
        if self.timer_service.is_paused():
            self.timer_service.resume()
            self.paused = False
        else:
            self.timer_service.pause()
            self.paused = True

    def on_study_timer_finish(self):
        """공부 타이머 종료 후 휴식 시작 로직"""
        # UI 스레드에서 안전하게 실행
        self.start_break()

    def start_break(self):
        """휴식 로직 실행 메서드"""
        # 사이클 증가 및 휴식 시간 결정
        cycle = self.config_ctrl.increment_cycle()
        if cycle % self.config_ctrl.get_setting("cycles", 4) == 0:
            break_min = self.config_ctrl.get_setting("long_break", 15)
            self.config_ctrl.set_status(AppStatus.LONG_BREAK)
            self.sound_manager.play_sound(resource_path("assets/sounds/long_brk.wav"))
        else:
            break_min = self.config_ctrl.get_setting("short_break", 5)
            self.config_ctrl.set_status(AppStatus.SHORT_BREAK)
            self.sound_manager.play_sound(resource_path("assets/sounds/short_brk.wav"))
            
        self.main_frame.show_break_dialog(break_min)