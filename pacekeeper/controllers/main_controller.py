# controllers/main_controller.py

import wx
import json
import datetime
from pacekeeper.controllers.config_controller import ConfigController, AppStatus
from pacekeeper.controllers.sound_manager import SoundManager
from pacekeeper.controllers.timer_controller import TimerService
from pacekeeper.services.log_service import LogService
from pacekeeper.services.tag_service import TagService
from pacekeeper.services.category_service import CategoryService
from pacekeeper.repository.entities import Log
from pacekeeper.utils.functions import resource_path
from pacekeeper.consts.labels import load_language_resource
from icecream import ic

lang_res = load_language_resource(ConfigController().get_language())

MINUTE_TO_SECOND = 5

class MainController:
    """
    MainController: 애플리케이션의 비즈니스 로직 제어  
    책임: 타이머, 사운드, 사이클 관리 및 로그 DB 제어, 그리고 최근 로그 업데이트
    """
    def __init__(self, main_frame: 'MainFrame', config_ctrl: ConfigController):
        self.main_frame = main_frame
        self.config_ctrl = config_ctrl
        
        self.category_service = CategoryService()
        self.tag_service = TagService()
        self.log_service = LogService()
        self.sound_manager = SoundManager(config_ctrl)
        self.timer_service = TimerService(
            config_ctrl, 
            update_callback=self.main_frame.update_timer_label,
            on_finish=None  # 시작 시 동적으로 할당
        )
        self.paused = False
        
        # 앱 시작 시, 최근 로그를 UI에 업데이트합니다.
        self.refresh_recent_logs()

    def start_study_session(self):
        """학습 세션 시작 메소드 (기존 start_study() 대체)"""
        self.study_start_time = datetime.datetime.now()
        study_minutes = self.config_ctrl.get_setting("study_time", 25)
        total_seconds = study_minutes * MINUTE_TO_SECOND
        
        # 학습 세션 상태 설정 및 타이머 종료 시 수행할 콜백 할당
        self.config_ctrl.set_status(AppStatus.STUDY)
        self.timer_service.on_finish = self.on_study_session_finished

        # 타이머 시작 (내부적으로 기존 타이머 종료 후 새 타이머 스레드 시작)
        self.timer_service.start(total_seconds)

    def on_study_session_finished(self):
        """학습 세션 종료 후 실행될 로직 및 휴식 세션 전환"""
        self.timer_service.stop()
        
        # 학습 종료 시 로그 저장 (사용자 입력값)
        user_input = self.main_frame.log_input_panel.get_value().strip()
        if user_input:
            try:
                # 저장된 study_start_time을 create_study_log에 전달
                self.log_service.create_study_log(user_input, study_start_time=self.study_start_time)
            except Exception as e:
                wx.MessageBox(f"로그 저장 실패: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
        
        # 로그 추가 후 최신 로그 목록을 UI에 업데이트합니다.
        self.refresh_recent_logs()
        
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
            
        # 휴식 세션 시작 (UI 생성은 메인 스레드에서 관리)
        wx.CallAfter(self.start_break_session, break_min)

    def start_break_session(self, break_min: int):
        """휴식 세션 시작 메소드"""
        total_seconds = break_min * MINUTE_TO_SECOND

        # 휴식 종료 후 실행될 콜백 할당
        self.timer_service.on_finish = self.on_break_session_finished

        # 타이머 시작 (휴식 타이머)
        self.timer_service.start(total_seconds)
        # UI 창(다이얼로그 등)은 반드시 메인 스레드에서 생성되어야 하므로 wx.CallAfter 사용
        wx.CallAfter(self.main_frame.show_break_dialog, break_min)

    def on_break_session_finished(self):
        """휴식 세션 종료 후 실행될 로직"""
        self.timer_service.stop()

    def toggle_pause(self):
        """일시정지/재개 토글 메서드"""
        if self.timer_service.is_paused():
            self.timer_service.resume()
            self.paused = False
        else:
            self.timer_service.pause()
            self.paused = True

    def stop_study_timer(self):
        """공부 타이머 중단 메서드"""
        self.timer_service.stop()
        # 추가로 UI 갱신이나 상태 초기화 작업이 필요하면 이곳에 구현합니다.
        
    def cleanup(self):
        """앱 종료 시 모든 리소스 정리"""
        # 타이머 서비스 중지
        self.timer_service.stop()
        
        # 사운드 매니저 정리
        self.sound_manager.cleanup()
        
        # 기타 필요한 정리 작업 수행
        # ConfigController에는 save_settings() 메서드가 없지만 settings_model에는 있음
        self.config_ctrl.settings_model.save_settings()

    def refresh_recent_logs(self):
        """
        MainFrame의 recent_logs 컨트롤 및 TagButtonsPanel을 업데이트하여 최신 로그 목록과 태그 버튼을 반영하는 메서드.
        중복된 메시지는 하나만 보여주고, 최대 10개의 로그만 표시합니다.
        """
        logs:list[Log] = self.log_service.retrieve_recent_logs()
        unique_logs = []
        seen_messages = set()
        
        for log in logs:
            message = log.message
            if message in seen_messages:
                continue
            
            tag_text = self.tag_service.get_tag_text(log.tags)
            tag_str = json.dumps(tag_text)
            tag_list = tag_str.replace('[', '').replace(']', '').replace('"', '')
            setattr(log, "tag_text", tag_list)
            ic("tag_text", tag_list)
            
            log_dict = log.to_dict()
            log_dict["tag_text"] = tag_list
            ic("log_dict", log_dict)
            
            unique_logs.append(log_dict)
            seen_messages.add(message)
            if len(unique_logs) >= 10:
                break
            
            
        self.main_frame.recent_logs.update_logs(logs=unique_logs)

    def get_all_logs(self):
        """
        기록 보기 다이얼로그 등에서 사용하기 위한 함수로,
        중복 메시지 포함 모든 로그 데이터를 반환합니다.
        """
        return self.log_service.retrieve_all_logs()