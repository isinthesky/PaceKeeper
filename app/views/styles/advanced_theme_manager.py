"""
PaceKeeper Qt - 고급 테마 관리자 (개선된 버전)
Qt 스타일 시트(QSS)를 사용한 테마 관리 및 동적 스타일 적용
"""

import json
import os

from PyQt6.QtCore import QFile, QObject, QTextStream, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget


class AdvancedThemeManager(QObject):
    """고급 테마 관리 및 적용 클래스 (위젯 자동 등록 및 효율적 관리 기능 추가)"""

    # 싱글톤 인스턴스
    _instance = None
    _app = None  # QApplication 인스턴스 저장

    # 사용자 정의 시그널
    themeChanged = pyqtSignal(str)

    @classmethod
    def get_instance(cls, theme_dir=None, app=None):
        """싱글톤 패턴으로 테마 관리자의 단일 인스턴스 반환

        Args:
            theme_dir: 테마 디렉토리 경로 (첫 인스턴스 생성 시에만 사용)
            app: QApplication 인스턴스

        Returns:
            AdvancedThemeManager: 단일 테마 관리자 인스턴스
        """
        if cls._instance is None:
            cls._instance = cls(theme_dir, app)
        elif app is not None and cls._app is None:
            # 기존 인스턴스가 있지만 앱이 설정되지 않은 경우
            cls._app = app
        return cls._instance

    def __init__(self, theme_dir=None, app=None):
        """
        고급 테마 관리자 초기화

        Args:
            theme_dir: 테마 디렉토리 경로 (기본값: 'themes')
            app: QApplication 인스턴스
        """
        super().__init__()

        # QApplication 인스턴스 저장
        if app is not None:
            AdvancedThemeManager._app = app

        if theme_dir:
            self.themes_dir = theme_dir
        else:
            # 기본 테마 디렉토리 설정
            self.themes_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "themes"
            )

        self.current_theme = "default"
        self.theme_cache = {}  # 테마 캐싱
        self.managed_widgets = set()  # 관리할 위젯 세트 (리스트 → 세트로 변경)

        # 사용 가능한 테마 목록 초기화
        self.available_themes = self._detect_themes()

        # 위젯 모니터링 설정 여부
        self._monitoring_setup = False

    def _detect_themes(self):
        """
        테마 디렉토리에서 사용 가능한 테마 감지

        Returns:
            dict: {테마 이름: 파일 경로} 형태의 딕셔너리
        """
        themes = {}
        print(f"\n[DEBUG] 테마 감지 시작 - 테마 디렉토리: {self.themes_dir}")

        # 기본 테마 추가 (항상 존재해야 함)
        default_path = os.path.join(self.themes_dir, "default.qss")
        if os.path.exists(default_path):
            themes["default"] = default_path
            print(f"[DEBUG] 기본 테마 감지: {default_path}")
        else:
            print(f"[DEBUG] 경고: 기본 테마 파일을 찾을 수 없습니다: {default_path}")

        # 테마 디렉토리에서 모든 .qss 파일 검색
        if os.path.exists(self.themes_dir):
            print(f"[DEBUG] 테마 디렉토리 확인: {self.themes_dir}")
            for file in os.listdir(self.themes_dir):
                if file.endswith(".qss") and file != "default.qss":
                    name = os.path.splitext(file)[0]
                    path = os.path.join(self.themes_dir, file)
                    themes[name] = path
                    print(f"[DEBUG] 테마 감지: {name} => {path}")
        else:
            print(f"[DEBUG] 경고: 테마 디렉토리가 존재하지 않습니다: {self.themes_dir}")

        print(f"[DEBUG] 총 {len(themes)} 개의 테마 감지\n")
        return themes

    def setup_widget_monitoring(self, app):
        """
        애플리케이션 내 모든 위젯을 자동으로 모니터링하고 등록

        Args:
            app: QApplication 인스턴스
        """
        # 중복 설정 방지
        if self._monitoring_setup:
            return

        # 원래 QWidget 초기화 메서드 저장
        original_init = QWidget.__init__
        theme_manager = self  # 클로저에서 self 참조

        # QWidget 초기화 메서드 재정의
        def custom_init(self, *args, **kwargs):
            # 원래 초기화 메서드 호출
            original_init(self, *args, **kwargs)

            # 위젯이 Dialog, Window 또는 주요 UI 컴포넌트인 경우만 등록
            if self.__class__.__name__.endswith(
                ("Dialog", "Window", "Widget")
            ) and not self.objectName().startswith("qt_"):
                theme_manager.register_widget(self)

        # QWidget 초기화 메서드 교체
        QWidget.__init__ = custom_init

        # 애플리케이션 종료 시 원래 메서드 복원
        def restore_widget_init():
            QWidget.__init__ = original_init

        app.aboutToQuit.connect(restore_widget_init)
        self._monitoring_setup = True

    def get_available_themes(self):
        """
        사용 가능한 테마 목록 반환

        Returns:
            list: 테마 이름 목록
        """
        return list(self.available_themes.keys())

    def get_current_theme(self):
        """
        현재 테마 이름 반환

        Returns:
            str: 현재 테마 이름
        """
        return self.current_theme

    def _load_theme_file(self, theme_path):
        """
        테마 파일 로드

        Args:
            theme_path: 테마 파일 경로

        Returns:
            str: 테마 스타일시트 내용
        """
        print(f"[DEBUG] 테마 파일 로드 시도: {theme_path}")

        # 캐시 확인
        if theme_path in self.theme_cache:
            print(f"[DEBUG] 캐시에서 테마 로드: {theme_path}")
            return self.theme_cache[theme_path]

        # 파일에서 로드
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                content = f.read()
                # 캐시에 저장
                self.theme_cache[theme_path] = content
                print(
                    f"[DEBUG] 테마 로드 성공: {theme_path}\n테마 내용 길이: {len(content)} 바이트"
                )
                return content
        except Exception as e:
            print(f"[DEBUG] 테마 로드 실패: {e}")
            return ""

    def register_widget(self, widget):
        """
        테마 변경 시 자동으로 업데이트할 위젯 등록

        Args:
            widget: 등록할 위젯 인스턴스
        """
        # 세트에 추가 (중복 자동 처리)
        self.managed_widgets.add(widget)

        # 위젯 삭제 이벤트 연결
        try:
            widget.destroyed.connect(
                lambda obj=None, w=widget: self.unregister_widget(w)
            )
        except (RuntimeError, TypeError):
            # 이미 위젯이 소멸 중이거나 시그널 연결 불가 시
            pass

    def unregister_widget(self, widget):
        """
        등록된 위젯 제거

        Args:
            widget: 제거할 위젯 인스턴스
        """
        # 세트에서 제거 (존재하지 않는 요소 제거 시 오류 없음)
        self.managed_widgets.discard(widget)

    def update_all_widgets(self):
        """등록된 모든 위젯에 현재 테마 적용 - 안전하게 구현"""
        style_content = self.get_theme_style(self.current_theme)
        if not style_content:
            print(f"[DEBUG] 테마 스타일을 가져올 수 없음, 위젯 업데이트 건너뜀")
            return

        # 유효한 위젯만 저장할 임시 세트
        valid_widgets = set()

        print(f"[DEBUG] 관리 중인 위젯 수: {len(self.managed_widgets)}")
        processed = 0
        updated = 0
        errors = 0

        for widget in self.managed_widgets:
            processed += 1
            try:
                # 폐기된 QObject에 접근하지 않도록 안전하게 처리
                if widget is None:
                    print(f"[DEBUG] 위젯 {processed}가 None입니다.")
                    continue

                try:
                    # 위젯 메타클래스 확인 (QObject인지 확인)
                    widget_class = widget.__class__
                except RuntimeError as e:
                    print(
                        f"[DEBUG] 위젯 {processed}에 접근할 수 없음 (RuntimeError): {e}"
                    )
                    errors += 1
                    continue

                # QDialog가 이미 닫힌 경우 확인
                try:
                    from PyQt6.QtWidgets import QDialog

                    if isinstance(widget, QDialog) and not widget.isVisible():
                        print(f"[DEBUG] QDialog 위젯이 더 이상 표시되지 않음, 건너뜀")
                        continue
                except Exception as e:
                    print(f"[DEBUG] QDialog 체크 중 오류: {e}")

                # 스타일시트 적용 시도
                try:
                    print(f"[DEBUG] 위젯에 테마 적용: {type(widget).__name__}")
                    widget.setStyleSheet(style_content)
                    updated += 1
                    valid_widgets.add(widget)
                except Exception as e:
                    errors += 1
                    print(f"[DEBUG] 스타일시트 설정 중 오류: {e}")
            except RuntimeError as e:
                errors += 1
                # C++ 객체가 삭제된 경우
                print(f"[DEBUG] 위젯 {processed}가 이미 삭제됨 (RuntimeError): {e}")
            except Exception as e:
                errors += 1
                print(f"[DEBUG] 위젯 업데이트 중 오류 발생: {e}")

        # 관리 위젯 세트 업데이트 (유효한 위젯만 유지)
        self.managed_widgets = valid_widgets
        print(
            f"[DEBUG] 위젯 업데이트 완료: 처리={processed}, 성공={updated}, 오류={errors}"
        )

    def set_application(self, app):
        """QApplication 인스턴스 설정

        Args:
            app: QApplication 인스턴스
        """
        AdvancedThemeManager._app = app
        print(f"[DEBUG] QApplication 인스턴스 설정 완료")

    def apply_theme(self, target=None, theme_name="default"):
        """
        애플리케이션 또는 특정 위젯에 테마 적용

        Args:
            target: QApplication 인스턴스 또는 테마를 적용할 QWidget (기본값: None이면 저장된 앱 인스턴스 사용)
            theme_name: 적용할 테마 이름

        Returns:
            bool: 성공 여부
        """
        # target이 None이면 저장된 앱 인스턴스 사용
        if target is None:
            target = AdvancedThemeManager._app
            print(
                f"\n[DEBUG] apply_theme 시작: 저장된 앱 인스턴스 사용, theme_name={theme_name}"
            )
        else:
            print(
                f"\n[DEBUG] apply_theme 시작: target={type(target)}, theme_name={theme_name}"
            )

        # 타겟이 여전히 None인지 확인
        if target is None:
            print(
                f"[DEBUG] 경고: 대상이 None입니다. 저장된 앱 인스턴스도 없습니다. 테마 변경을 무시합니다."
            )
            return False

        # 테마 존재 확인
        if theme_name not in self.available_themes:
            print(f"[DEBUG] 경고: 테마 '{theme_name}'을(를) 찾을 수 없습니다.")
            return False

        theme_path = self.available_themes[theme_name]
        style_content = self._load_theme_file(theme_path)

        if not style_content:
            print(f"[DEBUG] 테마 내용이 비어있습니다. 테마 적용 실패.")
            return False

        previous_theme = self.current_theme

        try:
            if isinstance(target, QApplication):
                # 애플리케이션 전체에 적용
                print(f"[DEBUG] 전체 애플리케이션에 테마 적용 시도: {theme_name}")
                target.setStyleSheet(style_content)
                print(f"[DEBUG] 스타일시트 적용 완료: 길이={len(style_content)}")
                self.current_theme = theme_name  # 전체 테마 변경 시에만 업데이트

                # 테마가 변경되었을 때만 시그널 발생 (중요 - 순서를 변경해서 먼저 시그널을 보냄)
                if previous_theme != theme_name:
                    print(
                        f"[DEBUG] 테마 변경 시그널 발생: {previous_theme} -> {theme_name}"
                    )
                    self.themeChanged.emit(theme_name)

                # 등록된 모든 위젯 업데이트 (시그널 발생 후 실행)
                print(
                    f"[DEBUG] 등록된 모든 위젯 업데이트 시도, 위젯 수: {len(self.managed_widgets)}"
                )
                self.update_all_widgets()

                # 추가: 현재 열려있는 모든 대화상자에 대한 특별 처리
                print(f"[DEBUG] 현재 열려있는 대화상자 찾기 시도")
                try:
                    from PyQt6.QtWidgets import QDialog

                    # 테마 적용을 위한 함수를 가져옵니다.
                    try:
                        from app.views.styles.update_dialogs import (
                            apply_theme_change, set_object_names)

                        has_dialog_helpers = True
                        print(f"[DEBUG] 대화상자 테마 헬퍼 함수 가져오기 성공")
                    except ImportError:
                        has_dialog_helpers = False
                        print(
                            f"[DEBUG] update_dialogs 모듈을 가져올 수 없습니다. 기본 방식으로 테마 적용"
                        )

                    # 안전하게 모든 위젯 검사
                    all_widgets = []
                    try:
                        all_widgets = target.allWidgets()
                    except Exception as e:
                        print(f"[DEBUG] allWidgets 호출 중 오류: {e}")

                    for widget in all_widgets:
                        try:
                            # 대화상자 및 관리되지 않는지 확인
                            is_dialog = isinstance(widget, QDialog)
                            is_visible = widget.isVisible()
                            is_managed = widget in self.managed_widgets

                            if is_dialog and is_visible and not is_managed:
                                dialog_name = widget.__class__.__name__
                                print(
                                    f"[DEBUG] 관리되지 않는 대화상자 발견: {dialog_name}"
                                )

                                # set_object_names 호출 후 테마 적용
                                if has_dialog_helpers:
                                    # objectName이 없는 경우 설정
                                    if not widget.objectName():
                                        widget.setObjectName(dialog_name)

                                    # 다이얼로그에 객체 이름 설정 및 테마 적용
                                    set_object_names(widget)
                                    apply_theme_change(widget, theme_name, self)
                                else:
                                    # 대화상자에 스타일 직접 적용
                                    widget.setStyleSheet(style_content)
                        except Exception as e:
                            print(f"[DEBUG] 개별 대화상자 처리 중 오류: {e}")
                except Exception as e:
                    print(f"[DEBUG] 대화상자 처리 중 오류: {e}")

            elif isinstance(target, QWidget):
                # 특정 위젯에만 적용
                print(f"[DEBUG] 특정 위젯에 테마 적용: {type(target).__name__}")
                target.setStyleSheet(style_content)
            else:
                print(f"[DEBUG] 경고: 지원되지 않는 대상 타입입니다: {type(target)}")
                return False

            print(f"[DEBUG] 테마 적용 성공: {theme_name}\n")
            return True

        except Exception as e:
            print(f"[DEBUG] 테마 적용 중 오류 발생: {e}")
            return False

    def get_theme_style(self, theme_name="default"):
        """
        테마 스타일시트 내용 반환

        Args:
            theme_name: 테마 이름

        Returns:
            str: 테마 스타일시트 내용
        """
        if theme_name in self.available_themes:
            return self._load_theme_file(self.available_themes[theme_name])
        return ""

    def create_custom_theme(
        self, theme_name, base_theme="default", customizations=None
    ):
        """
        기존 테마를 기반으로 사용자 정의 테마 생성

        Args:
            theme_name: 새 테마 이름
            base_theme: 기반 테마 이름
            customizations: CSS 규칙 사전

        Returns:
            bool: 성공 여부
        """
        # 기반 테마 존재 확인
        if base_theme not in self.available_themes:
            return False

        # 기반 테마 로드
        base_style = self._load_theme_file(self.available_themes[base_theme])

        # 사용자 정의 적용
        if customizations:
            for selector, rules in customizations.items():
                # CSS 규칙 문자열로 변환
                rules_str = "; ".join([f"{prop}: {val}" for prop, val in rules.items()])

                # 선택자가 이미 스타일시트에 있는지 확인
                selector_pos = base_style.find(selector + " {")
                if selector_pos != -1:
                    # 기존 규칙 블록 찾기
                    block_start = base_style.find("{", selector_pos) + 1
                    block_end = base_style.find("}", block_start)

                    # 규칙 블록 교체
                    if block_start != 0 and block_end != -1:
                        base_style = (
                            base_style[:block_start]
                            + " "
                            + rules_str
                            + "; "
                            + base_style[block_end:]
                        )
                else:
                    # 선택자 규칙 추가
                    base_style += f"\n{selector} {{ {rules_str}; }}"

        # 새 테마 파일 저장
        theme_path = os.path.join(self.themes_dir, f"{theme_name}.qss")
        try:
            with open(theme_path, "w", encoding="utf-8") as f:
                f.write(base_style)

            # 사용 가능한 테마 목록 업데이트
            self.available_themes[theme_name] = theme_path
            return True
        except Exception as e:
            print(f"테마 저장 실패: {e}")
            return False

    def apply_responsive_styles(self, app, width, height=None):
        """
        창 크기에 따른 반응형 스타일 적용

        Args:
            app: QApplication 인스턴스
            width: 창 너비
            height: 창 높이 (선택 사항)
        """
        # 기본 반응형 스타일 생성
        responsive_style = self._get_responsive_style(width, height)

        # 현재 스타일시트 가져오기
        current_style = app.styleSheet()

        # 반응형 스타일 적용 (기존 스타일 유지)
        if current_style:
            # 간단한 구현을 위해 새 스타일을 추가하는 방식 사용
            app.setStyleSheet(current_style + "\n" + responsive_style)

    def _get_responsive_style(self, width, height=None):
        """
        창 크기에 따른 반응형 스타일 생성

        Args:
            width: 창 너비
            height: 창 높이 (선택 사항)

        Returns:
            str: 반응형 스타일 문자열
        """
        # 창 크기에 따른 스타일 생성
        if width < 500:
            return """
                QToolBar { font-size: 9pt; }
                QToolBar QToolButton { padding: 3px; }
                QStatusBar { font-size: 9pt; }
                QLabel#timerLabel { font-size: 28pt; }
                QPushButton { min-width: 70px; min-height: 25px; padding: 3px 6px; }
            """
        elif width < 800:
            return """
                QToolBar { font-size: 10pt; }
                QToolBar QToolButton { padding: 4px; }
                QStatusBar { font-size: 10pt; }
                QLabel#timerLabel { font-size: 36pt; }
                QPushButton { min-width: 80px; min-height: 28px; padding: 4px 8px; }
            """
        else:
            return """
                QToolBar { font-size: 11pt; }
                QToolBar QToolButton { padding: 5px; }
                QStatusBar { font-size: 10pt; }
                QLabel#timerLabel { font-size: 48pt; }
                QPushButton { min-width: 90px; min-height: 30px; padding: 5px 10px; }
            """
