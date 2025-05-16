# controllers/main_controller.py

import json
import datetime
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMessageBox

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

MINUTE_TO_SECOND = 5  # 테스트용으로 분당 5초로 설정. 실제로는 60초로 변경 필요

class MainController:
    """
    MainController: 애플리케이션의 비즈니스 로직 제어  
    책임: 타이머, 사운드, 사이클 관리 및 로그 DB 제어, 그리고 최근 로그 업데이트
    """
    def __init__(self, main_window: 'MainWindow', config_ctrl: ConfigController):
        self.main_window = main_window
        self.config_ctrl = config_ctrl
        
        self.category_service = CategoryService()
        self.tag_service = TagService()
        self.log_service = LogService()
        self.sound_manager = SoundManager(config_ctrl)
        self.timer_service = TimerService(
            config_ctrl, 
            update_callback=self.main_window.update_timer_label,
            on_finish=None  # 시작 시 동적으로 할당
        )
        self.paused = False
        self.current_tag = None
        self.current_description = ""
        
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
        user_input = self.main_window.text_input_panel.get_value().strip()
        if user_input:
            try:
                # 저장된 study_start_time을 create_study_log에 전달
                self.log_service.create_study_log(user_input, study_start_time=self.study_start_time)
            except Exception as e:
                QMessageBox.critical(self.main_window, "Error", f"로그 저장 실패: {str(e)}")
        
        # 로그 추가 후 최신 로그 목록을 UI에 업데이트합니다.
        self.refresh_recent_logs()
        
        # 사이클 증가 및 휴식 시간 결정
        cycle = self.config_ctrl.increment_cycle()
        if cycle % self.config_ctrl.get_setting("cycles", 4) == 0:
            break_min = self.config_ctrl.get_setting("long_break", 15)
            self.config_ctrl.set_status(AppStatus.LONG_BREAK)
            self.sound_manager.play_sound("pacekeeper/assets/sounds/long_brk.wav")
        else:
            break_min = self.config_ctrl.get_setting("short_break", 5)
            self.config_ctrl.set_status(AppStatus.SHORT_BREAK)
            self.sound_manager.play_sound("pacekeeper/assets/sounds/short_brk.wav")
            
        # 휴식 세션 시작
        # Qt에서는 wx.CallAfter 대신 QTimer.singleShot 사용
        QTimer.singleShot(0, lambda: self.start_break_session(break_min))

    def start_break_session(self, break_min: int):
        """휴식 세션 시작 메소드"""
        total_seconds = break_min * MINUTE_TO_SECOND

        # 휴식 종료 후 실행될 콜백 할당
        self.timer_service.on_finish = self.on_break_session_finished

        # 타이머 시작 (휴식 타이머)
        self.timer_service.start(total_seconds)
        
        # 현재 상태에 따라 휴식 타입 결정
        break_type = AppStatus.LONG_BREAK if self.config_ctrl.get_status() == AppStatus.LONG_BREAK else AppStatus.SHORT_BREAK
        
        # PyQt에서는 직접 show_break_dialog 호출 (Qt의 이벤트 루프가 자동으로 처리)
        self.main_window.show_break_dialog(break_type, break_min, self.on_break_session_finished)

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

    def refresh_recent_logs(self):
        """
        MainWindow의 recent_logs 컨트롤 및 TagButtonsPanel을 업데이트하여 최신 로그 목록과 태그 버튼을 반영하는 메서드.
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
            tag_list = ', '.join(tag_text) if tag_text else ''
            setattr(log, "tag_text", tag_list)
            
            unique_logs.append(log)
            seen_messages.add(message)
            if len(unique_logs) >= 10:
                break
                        
        # 최근 로그 UI 컨트롤 업데이트
        self.main_window.recent_logs_control.update_logs(logs=unique_logs)


    def get_all_logs(self):
        """
        기록 보기 다이얼로그 등에서 사용하기 위한 함수로,
        중복 메시지 포함 모든 로그 데이터를 반환합니다.
        """
        return self.log_service.retrieve_all_logs()

    def set_current_tag(self, tag):
        """현재 태그 설정"""
        self.current_tag = tag
        
    def set_current_description(self, description):
        """현재 설명 설정"""
        self.current_description = description
        
    def start_timer(self):
        """타이머 시작"""
        self.start_study_session()
        
    def pause_timer(self):
        """타이머 일시정지"""
        self.toggle_pause()
        
    def resume_timer(self):
        """타이머 재개"""
        self.toggle_pause()
        
    def stop_timer(self):
        """타이머 중지"""
        self.stop_study_timer()