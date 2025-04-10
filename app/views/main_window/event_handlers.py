"""
PaceKeeper Qt - 메인 윈도우 이벤트 핸들러
이벤트 및 시그널 처리 메서드 모음
"""

import atexit
import os
import sys
import threading
import time
import traceback
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QSystemTrayIcon

from app.utils.constants import SessionType, TimerState

def on_session_started(self, session_type):
    """
    세션 시작 이벤트 핸들러

    Args:
        session_type: 세션 타입
    """
    # 집중 모드 UI로 전환 (타이머 위젯만 표시)
    if session_type == SessionType.POMODORO:
        # 불필요한 UI 요소 숨기기
        self.contentSplitter.hide()
        self.menuBar.hide()
        self.toolBar.hide()
        self.statusBar.hide()

        # 타이머 위젯은 이미 표시되어 있으므로 별도로 처리할 필요 없음
        # 필요하다면 타이머 위젯을 집중 모드로 설정
        if hasattr(self, "timerWidget"):
            # 타이머 위젯이 집중 모드 메서드를 제공한다면 사용
            # self.timerWidget.setFocusMode(True)
            pass

        # 창 크기 최소화
        self.setFixedSize(300, 150)

    # UI 상태 업데이트
    self.updateUI()


def on_session_paused(self):
    """세션 일시정지 이벤트 핸들러"""
    self.updateUI()


def on_session_resumed(self):
    """세션 재개 이벤트 핸들러"""
    self.updateUI()


def on_session_stopped(self):
    """세션 중지 이벤트 핸들러"""
    # 일반 모드 UI로 복원
    # MainWindow 클래스의 _restore_normal_ui 메서드가 있다면 사용
    if hasattr(self, "_restore_normal_ui"):
        self._restore_normal_ui()
    else:
        # MainWindow 클래스에 메서드가 없는 경우 여기서 직접 처리
        if hasattr(self, "timerWidget"):
            # 타이머 위젯이 일반 모드 메서드를 제공한다면 사용
            pass

        # 일반 UI 요소 복원
        self.contentSplitter.show()
        self.menuBar.show()
        self.toolBar.show()
        self.statusBar.show()

        # 창 크기 복원
        self.setFixedSize(16777215, 16777215)  # 고정 크기 제거 (QWIDGETSIZE_MAX)
        self.resize(
            self.config.get("main_dlg_width", 800),
            self.config.get("main_dlg_height", 500),
        )

    # UI 상태 업데이트
    self.updateUI()


def on_session_finished(self, session_type):
    """
    세션 완료 이벤트 핸들러

    Args:
        session_type: 세션 타입
    """
    try:
        # 이전 세션이 휴식 타입이었다면 휴식 대화상자를 표시하지 않고 리턴
        if session_type != SessionType.POMODORO:
            self.updateUI()
            return

        # 뽀모도로 세션이 완료되면 일반 모드 UI로 복원
        # MainWindow 클래스의 _restore_normal_ui 메서드가 있다면 사용
        if hasattr(self, "_restore_normal_ui"):
            self._restore_normal_ui()
        else:
            # MainWindow 클래스에 메서드가 없는 경우 여기서 직접 처리
            if hasattr(self, "timerWidget"):
                # 타이머 위젯이 일반 모드 메서드를 제공한다면 사용
                pass

            # 일반 UI 요소 복원
            self.contentSplitter.show()
            self.menuBar.show()
            self.toolBar.show()
            self.statusBar.show()

            # 창 크기 복원
            self.setFixedSize(16777215, 16777215)  # 고정 크기 제거 (QWIDGETSIZE_MAX)
            self.resize(
                self.config.get("main_dlg_width", 800),
                self.config.get("main_dlg_height", 500),
            )

        self.updateUI()

        # 다음 세션 타입 결정
        next_session_type = SessionType.SHORT_BREAK
        pomodoro_count = self.main_controller.pomodoro_count
        if pomodoro_count % self.config.get("long_break_interval", 4) == 0:
            next_session_type = SessionType.LONG_BREAK

        print(
            f"Pomodoro session finished. Showing break dialog for {next_session_type}"
        )

        # 휴식 대화상자 표시
        # 메서드 이름 변경: showBreakDialog → show_break_dialog
        self.show_break_dialog(next_session_type)

    except Exception as e:
        # 예외 발생 시 로그 기록 및 안전한 처리
        print(f"Error in on_session_finished: {e}")
        # UI 업데이트를 시도해서 최소한 UI가 동작하도록 함
        try:
            self.updateUI()
        except Exception:
            pass


def on_text_submitted(self, text):
    """
    텍스트 제출 이벤트 핸들러

    Args:
        text: 제출된 텍스트
    """
    # 현재 입력 텍스트 설정
    self.main_controller.set_log_text(text)

    # 타이머가 실행 중이 아니면 로그 추가
    timer_state = self.timer_controller.get_state()
    if timer_state != TimerState.RUNNING:
        # 로그 생성 (0분 로그)
        self.log_service.create_log(message=text)

        # 최근 로그 업데이트
        self.updateRecentLogs()


def on_tag_selected(self, tag_name):
    """
    태그 선택 이벤트 핸들러

    Args:
        tag_name: 선택된 태그 이름
    """
    # 현재 입력 텍스트에 태그 추가
    current_text = self.textInputWidget.text()
    if current_text:
        # setText 메서드를 사용하여 태그 추가
        if not current_text.endswith(" "):
            current_text += " "
        self.textInputWidget.textInput.setText(f"{current_text}#{tag_name}")
    else:
        # 비어있을 경우 태그만 추가
        self.textInputWidget.textInput.setText(f"#{tag_name}")


def on_log_selected(self, log_text):
    """
    로그 선택 이벤트 핸들러

    Args:
        log_text: 선택된 로그 텍스트
    """
    # 로그 텍스트를 입력 필드에 설정
    if hasattr(self.textInputWidget, "textInput"):
        self.textInputWidget.textInput.setText(log_text)
    elif hasattr(self.textInputWidget, "setText"):
        self.textInputWidget.setText(log_text)
    else:
        print(f"[ERROR] TextInputWidget에 적절한 setText 메서드가 없습니다.")


def on_tray_icon_activated(self, reason):
    """
    트레이 아이콘 활성화 이벤트 핸들러

    Args:
        reason: 활성화 이유
    """
    if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
        self.showNormal()


def on_exit_from_tray(self):
    """
    트레이 메뉴에서 종료 이벤트 핸들러
    """
    # 종료 로그 기록
    try:
        log_file = os.path.join(os.path.expanduser("~"), "pacekeeper_shutdown.log")
        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - 트레이 메뉴에서 종료 요청됨\n")
    except:
        pass

    # 트레이 아이콘 제거
    try:
        if hasattr(self, "trayIcon") and self.trayIcon:
            try:
                self.trayIcon.hide()
                self.trayIcon.setVisible(False)

                # 메뉴 및 액션 제거
                if self.trayIcon.contextMenu():
                    menu = self.trayIcon.contextMenu()
                    self.trayIcon.setContextMenu(None)
                    menu.deleteLater()

                # 시그널 연결 해제
                if hasattr(self.trayIcon, "activated"):
                    try:
                        self.trayIcon.activated.disconnect()
                    except:
                        pass

                # 참조 제거
                self.trayIcon = None
            except:
                pass
    except:
        pass

    # 애플리케이션 종료 - 여러 방법으로 시도
    try:
        # 1. QCoreApplication.quit()
        QCoreApplication.quit()
        time.sleep(0.5)  # 짧은 지연

        # 2. sys.exit()
        sys.exit(0)
    except:
        pass

    # 3. 마지막 수단: os._exit()
    try:
        os._exit(0)
    except:
        pass


def close_event(self, event: QCloseEvent):
    """
    창 닫기 이벤트 처리 - 강화된 예외 처리와 안전한 종료

    Args:
        event: 닫기 이벤트
    """
    # 로깅 설정
    log_file = os.path.join(os.path.expanduser("~"), "pacekeeper_shutdown.log")

    def log_message(msg):
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} - {msg}\n")
        except:
            pass

    # 현재 스레드 정보 기록
    current_thread = threading.current_thread()
    log_message(f"========= 애플리케이션 종료 시작 ==========")
    log_message(f"현재 스레드: {current_thread.name} (ID: {current_thread.ident})")
    log_message(f"활성 스레드 수: {threading.active_count()}")
    log_message(f"활성 스레드 목록: {[t.name for t in threading.enumerate()]}")

    # 프로세스 ID 기록
    log_message(f"프로세스 ID: {os.getpid()}")

    # 종료 상태 추적 변수
    timer_state = None
    session_stopped = False
    tray_icon_cleaned = False

    try:
        # 트레이로 최소화 설정 확인
        if self.config.get("minimize_to_tray", True):
            log_message("트레이로 최소화 설정 활성화됨")
            # 트레이로 최소화 설정이 켜져 있으면
            event.ignore()  # 기본 닫기 동작(종료)을 무시하고
            self.hide()  # 창을 숨깁니다
            log_message("창을 숨김 (hide 호출됨)")

            # 트레이 메시지 표시 (아이콘 보이는 경우)
            if (
                hasattr(self, "trayIcon")
                and self.trayIcon
                and self.trayIcon.isVisible()
            ):
                try:
                    log_message("트레이 아이콘 메시지 표시 시도")
                    self.trayIcon.showMessage(
                        "PaceKeeper",
                        "앱이 시스템 트레이에서 계속 실행 중입니다.",
                        QSystemTrayIcon.MessageIcon.Information,
                        2000,
                    )
                    log_message("트레이 메시지 표시 성공")
                except Exception as e:
                    error_msg = f"Warning: Failed to show tray message: {e}"
                    print(error_msg)
                    log_message(error_msg)
                    log_message(traceback.format_exc())

            # 트레이로 최소화 시 여기서 종료 (아래 코드 실행하지 않음)
            log_message("트레이로 최소화 완료, close_event 메소드 종료")
            return

        # 여기서부터는 실제 프로그램 종료 로직 처리
        log_message("실제 종료 로직 시작 (트레이 최소화 아님)")

        # 1. 타이머 상태 확인 및 세션 중지
        try:
            if hasattr(self, "timer_controller") and self.timer_controller:
                log_message("타이머 컨트롤러 객체 확인됨")
                try:
                    # 타이머 상태 확인
                    timer_state = self.timer_controller.get_state()
                    log_message(f"현재 타이머 상태: {timer_state}")

                    # 세션 실행 중인 경우 중지
                    if timer_state is not None and timer_state != TimerState.IDLE:
                        if hasattr(self, "main_controller") and self.main_controller:
                            log_message("세션 중지 시도...")
                            self.main_controller.stop_session()
                            session_stopped = True
                            log_message("세션 중지 성공")
                    else:
                        # 이미 중지된 상태
                        session_stopped = True
                        log_message("중지할 활성 세션 없음")
                except Exception as e:
                    error_msg = f"Warning: Error when checking timer state or stopping session: {e}"
                    print(error_msg)
                    log_message(error_msg)
                    log_message(traceback.format_exc())
            else:
                log_message("타이머 컨트롤러 객체가 없거나 생성되지 않음")
        except Exception as e:
            error_msg = f"Warning: Critical error during session cleanup: {e}"
            print(error_msg)
            log_message(error_msg)
            log_message(traceback.format_exc())

        # 2. 트레이 아이콘 정리
        try:
            if hasattr(self, "trayIcon") and self.trayIcon:
                log_message("트레이 아이콘 객체 있음, 정리 시도")
                try:
                    # 트레이 아이콘 숨기기
                    log_message("트레이 아이콘 hide() 시도")
                    self.trayIcon.hide()
                    log_message("트레이 아이콘 setVisible(False) 시도")
                    self.trayIcon.setVisible(False)
                    log_message("트레이 아이콘 숨기기 성공")
                except Exception as e:
                    error_msg = f"Warning: Failed to hide tray icon: {e}"
                    print(error_msg)
                    log_message(error_msg)
                    log_message(traceback.format_exc())

                # 트레이 아이콘의 모든 시그널 연결 해제
                try:
                    log_message("트레이 아이콘 시그널 연결 해제 시도")
                    if hasattr(self.trayIcon, "activated"):
                        self.trayIcon.activated.disconnect()
                    log_message("트레이 아이콘 시그널 연결 해제 성공")
                except Exception as e:
                    log_message(f"트레이 아이콘 시그널 연결 해제 실패: {e}")

                # 트레이 메뉴 제거
                try:
                    if (
                        hasattr(self.trayIcon, "contextMenu")
                        and self.trayIcon.contextMenu()
                    ):
                        log_message("트레이 메뉴 제거 시도")
                        menu = self.trayIcon.contextMenu()
                        self.trayIcon.setContextMenu(None)
                        menu.deleteLater()
                        log_message("트레이 메뉴 제거 성공")
                except Exception as e:
                    log_message(f"트레이 메뉴 제거 실패: {e}")

                # 참조 제거 (가비지 콜렉션을 위해 중요)
                try:
                    log_message("트레이 아이콘 참조 제거 시도 (self.trayIcon = None)")
                    self.trayIcon = None
                    tray_icon_cleaned = True
                    log_message("트레이 아이콘 참조 제거 성공")
                except Exception as e:
                    error_msg = f"Warning: Failed to clear tray icon reference: {e}"
                    print(error_msg)
                    log_message(error_msg)
                    log_message(traceback.format_exc())
            else:
                log_message("트레이 아이콘 객체 없음")
        except Exception as e:
            error_msg = f"Warning: Critical error during tray icon cleanup: {e}"
            print(error_msg)
            log_message(error_msg)
            log_message(traceback.format_exc())

        # 종료 상태 로그 기록
        status_msg = f"Application closing: Session stopped={session_stopped}, Tray cleaned={tray_icon_cleaned}"
        print(status_msg)
        log_message(status_msg)

        # 3. 이벤트 수락 및 애플리케이션 종료
        try:
            log_message("이벤트 수락 및 애플리케이션 종료 시도...")
            log_message("event.accept() 호출")
            event.accept()

            # 종료 함수 등록
            def exit_handler():
                try:
                    with open(log_file, "a", encoding="utf-8") as f:
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"{timestamp} - atexit 핸들러 실행됨\n")
                        f.write(
                            f"{timestamp} - 핸들러 실행 시 활성 스레드 수: {threading.active_count()}\n"
                        )
                except:
                    pass

            atexit.register(exit_handler)

            # 강제 종료를 위한 타이머 설정 (5초 후)
            try:

                def force_exit():
                    try:
                        with open(log_file, "a", encoding="utf-8") as f:
                            f.write(
                                f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 강제 종료 시도 (os._exit)\n"
                            )
                    except:
                        pass
                    os._exit(0)

                # 스레드로 타이머 실행 (메인 스레드 블록 방지)
                threading.Timer(5.0, force_exit).start()
                log_message("5초 후 강제 종료 타이머 설정됨")
            except Exception as e:
                log_message(f"강제 종료 타이머 설정 실패: {e}")

            log_message("QCoreApplication.quit() 호출")
            QCoreApplication.quit()
            log_message("애플리케이션 종료 시그널 전송 완료")

            # 대기 후 로그 추가
            log_message("quit() 호출 후 스레드 상태:")
            log_message(f"활성 스레드 수: {threading.active_count()}")
            log_message(f"활성 스레드 목록: {[t.name for t in threading.enumerate()]}")

            # 시스템 종료 시도
            log_message("sys.exit(0) 호출 시도")
            sys.exit(0)
        except Exception as e:
            error_msg = f"Error during final quit: {e}"
            print(error_msg)
            log_message(error_msg)
            log_message(traceback.format_exc())
            # 마지막 수단으로 sys.exit 사용
            log_message("예외 발생 후 sys.exit(0) 시도")
            sys.exit(0)

    except Exception as e:
        # 어떤 상황에서도 프로그램이 종료되도록 예외 처리
        print(f"Critical error during application closing: {e}")
        try:
            log_message(f"심각한 오류 발생: {e}")
            log_message(traceback.format_exc())
        except:
            pass

        try:
            # 이벤트가 아직 처리되지 않았다면 수락
            event.accept()
        except Exception:
            pass

        try:
            # 애플리케이션 종료 시도
            QCoreApplication.quit()

            # 강제 종료 타이머 설정
            threading.Timer(3.0, lambda: os._exit(1)).start()
        except Exception:
            # 마지막 수단
            try:
                os._exit(1)
            except:
                sys.exit(1)
