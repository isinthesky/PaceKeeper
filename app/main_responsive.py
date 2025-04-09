"""
PaceKeeper Qt - 메인 애플리케이션 (반응형)
애플리케이션 진입점 - 고급 테마 및 반응형 UI 적용
"""

import sys
import os
import atexit
import threading
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QLocale

from app.config.app_config import AppConfig
from app.views.main_window import MainWindow
from app.views.styles.advanced_theme_manager import AdvancedThemeManager
from app.views.styles.responsive_style_manager import ResponsiveStyleManager


def main():
    """애플리케이션 진입점"""
    # QApplication 인스턴스 생성
    app = QApplication(sys.argv)
    app.setApplicationName("PaceKeeper")
    app.setOrganizationName("PaceKeeper Team")
    app.setOrganizationDomain("pacekeeper.com")
    
    # 언어 설정
    locale = QLocale.system()
    QLocale.setDefault(locale)
    
    # 설정 로드
    config = AppConfig()
    
    # 테마 관리자 생성 및 테마 적용
    theme_manager = AdvancedThemeManager()
    
    # 고급 또는 일반 테마 적용 (설정에 따라)
    if config.get("use_advanced_theme", False):
        theme = "advanced"
    else:
        theme = config.get("theme", "default")
        
    theme_manager.apply_theme(app, theme)
    
    # 반응형 스타일 관리자 생성
    responsive_style_manager = ResponsiveStyleManager()
    
    # 메인 윈도우 생성 (반응형)
    window = MainWindow(config, theme_manager)
    
    # 초기 반응형 스타일 적용
    initial_width = window.width()
    responsive_style_manager.apply_responsive_style(window, initial_width)
    
    # 윈도우 표시
    window.show()
    
    # 종료 시 정리 작업
    def cleanup():
        """애플리케이션 종료 시 실행되는 정리 작업"""
        print("애플리케이션 종료 전 정리 작업을 수행합니다...")
        
        # 종료 로그 기록
        try:
            log_file = os.path.join(os.path.expanduser("~"), "pacekeeper_shutdown.log")
            with open(log_file, "a", encoding="utf-8") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} - 애플리케이션 aboutToQuit 시그널에서 cleanup 실행\n")
                f.write(f"{timestamp} - 활성 스레드 수: {threading.active_count()}\n")
                
                # 활성 스레드 목록 기록
                f.write(f"{timestamp} - 활성 스레드 목록:\n")
                for t in threading.enumerate():
                    f.write(f"{timestamp} - - 스레드: {t.name} (ID: {t.ident}, 데몬: {t.daemon})\n")
        except Exception as e:
            print(f"로그 기록 중 오류: {e}")
        
        # 강제 종료 타이머 설정
        try:
            def force_exit():
                """일정 시간 후 프로세스를 강제 종료"""
                print("애플리케이션 강제 종료 실행...")
                try:
                    # 종료 로그 기록
                    log_file = os.path.join(os.path.expanduser("~"), "pacekeeper_shutdown.log")
                    with open(log_file, "a", encoding="utf-8") as f:
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"{timestamp} - 애플리케이션 강제 종료 실행\n")
                except Exception as e:
                    print(f"강제 종료 로깅 중 오류: {e}")
                
                # 강제 종료 (마지막 수단)
                try:
                    os._exit(0)
                except:
                    pass
            
            # 8초 후 강제 종료 타이머 설정
            timer = threading.Timer(3.0, force_exit)
            timer.daemon = True  # 데몬 스레드로 설정
            timer.start()
            print("3초 후 강제 종료 타이머 설정됨")
        except Exception as e:
            print(f"종료 타이머 설정 중 오류: {e}")
    
    # 종료 시그널 연결
    app.aboutToQuit.connect(cleanup)
    
    # atexit 핸들러 등록
    def atexit_handler():
        """프로세스 종료 시 실행되는 핸들러"""
        try:
            log_file = os.path.join(os.path.expanduser("~"), "pacekeeper_shutdown.log")
            with open(log_file, "a", encoding="utf-8") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} - atexit 핸들러 실행됨\n")
        except:
            pass
    
    atexit.register(atexit_handler)
    
    # 애플리케이션 실행
    return app.exec()


if __name__ == "__main__":
    try:
        # 종료 코드 반환
        exit_code = main()
        
        # 정상 종료 기록
        try:
            log_file = os.path.join(os.path.expanduser("~"), "pacekeeper_shutdown.log")
            with open(log_file, "a", encoding="utf-8") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} - main() 함수 종료, 반환 코드: {exit_code}\n")
        except:
            pass
        
        # 종료 코드 반환
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n애플리케이션이 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"애플리케이션 실행 중 예외 발생: {e}")
        # 치명적인 오류 로깅
        try:
            import traceback
            log_file = os.path.join(os.path.expanduser("~"), "pacekeeper_shutdown.log")
            with open(log_file, "a", encoding="utf-8") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} - 심각한 오류 발생: {e}\n")
                f.write(f"{timestamp} - {traceback.format_exc()}\n")
        except:
            pass
        sys.exit(1)
