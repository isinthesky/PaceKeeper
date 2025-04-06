"""
PaceKeeper Qt - 고급 테마 관리자
Qt 스타일 시트(QSS)를 사용한 테마 관리 및 동적 스타일 적용
"""

from PyQt6.QtCore import QObject, pyqtSignal, QFile, QTextStream
import os
import json


class AdvancedThemeManager(QObject):
    """고급 테마 관리 및 적용 클래스"""
    
    # 사용자 정의 시그널
    themeChanged = pyqtSignal(str)
    
    def __init__(self, theme_dir=None):
        """
        고급 테마 관리자 초기화
        
        Args:
            theme_dir: 테마 디렉토리 경로 (기본값: 'themes')
        """
        super().__init__()
        
        if theme_dir:
            self.themes_dir = theme_dir
        else:
            # 기본 테마 디렉토리 설정
            self.themes_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "themes"
            )
        
        self.current_theme = "default"
        self.theme_cache = {}  # 테마 캐싱
        
        # 사용 가능한 테마 목록 초기화
        self.available_themes = self._detect_themes()
    
    def _detect_themes(self):
        """
        테마 디렉토리에서 사용 가능한 테마 감지
        
        Returns:
            dict: {테마 이름: 파일 경로} 형태의 딕셔너리
        """
        themes = {}
        
        # 기본 테마 추가 (항상 존재해야 함)
        default_path = os.path.join(self.themes_dir, "default.qss")
        if os.path.exists(default_path):
            themes["default"] = default_path
        
        # 테마 디렉토리에서 모든 .qss 파일 검색
        if os.path.exists(self.themes_dir):
            for file in os.listdir(self.themes_dir):
                if file.endswith(".qss") and file != "default.qss":
                    name = os.path.splitext(file)[0]
                    path = os.path.join(self.themes_dir, file)
                    themes[name] = path
        
        return themes
    
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
        # 캐시 확인
        if theme_path in self.theme_cache:
            return self.theme_cache[theme_path]
        
        # 파일에서 로드
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                content = f.read()
                # 캐시에 저장
                self.theme_cache[theme_path] = content
                return content
        except Exception as e:
            print(f"테마 로드 실패: {e}")
            return ""
    
    def apply_theme(self, app, theme_name="default"):
        """
        애플리케이션에 테마 적용
        
        Args:
            app: QApplication 인스턴스
            theme_name: 적용할 테마 이름
            
        Returns:
            bool: 성공 여부
        """
        # 테마 존재 확인
        if theme_name in self.available_themes:
            theme_path = self.available_themes[theme_name]
            style_content = self._load_theme_file(theme_path)
            
            if style_content:
                # 현재 테마 업데이트
                self.current_theme = theme_name
                
                # 애플리케이션에 스타일 적용
                if app:
                    app.setStyleSheet(style_content)
                
                # 테마 변경 시그널 발생
                self.themeChanged.emit(theme_name)
                return True
        
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
    
    def create_custom_theme(self, theme_name, base_theme="default", customizations=None):
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
                            base_style[:block_start] + 
                            " " + rules_str + "; " + 
                            base_style[block_end:]
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
