# PaceKeeper UI 개선 가이드

본 문서는 PaceKeeper 앱의 UI를 개선하기 위한 가이드입니다. 현재 구현된 개선 사항과 앞으로의 개선 방향을 담고 있습니다.

## 1. 개선 개요

PaceKeeper의 UI 개선 작업은 사용자 경험과 시각적 품질을 높이는 것을 목표로 합니다. 주요 개선 사항은 다음과 같습니다:

- 일관된 디자인 시스템 적용
- 카드 기반 레이아웃으로 시각적 계층 구조 강화
- 현대적인 컨트롤 스타일 적용
- 반응형 디자인 구현
- 사용성 및 접근성 개선

## 2. 구현된 개선 사항

### 2.1 테마 및 스타일

- `improved/dark.qss`: 개선된 다크 테마 스타일시트
- 모든 UI 컨트롤에 대한 일관된 스타일 정의 (버튼, 입력 필드, 리스트 등)
- 카드 스타일의 그룹박스 및 패널 디자인

### 2.2 다이얼로그 개선

다음 다이얼로그들이 개선되었습니다:

- `settings_dialog.py`: 설정 다이얼로그 (기존 파일 수정)
- `category_dialog_improved.py`: 카테고리 관리 다이얼로그 (새 파일)
- `tag_dialog_improved.py`: 태그 관리 다이얼로그 (새 파일)
- `log_dialog_improved.py`: 로그 조회 다이얼로그 (새 파일)

주요 개선 사항:
- 카드 기반 레이아웃
- 여백 및 내부 간격 최적화
- 컨트롤 크기 및 상호작용 영역 확대
- 시각적 계층 구조 강화

### 2.3 반응형 디자인

`responsive_style_manager.py`를 통해 창 크기에 따른 UI 요소 자동 조정을 구현:

- 작은 화면: 500px 미만
- 중간 화면: 500px ~ 800px
- 큰 화면: 800px 이상

## 3. 적용 방법

### 3.1 개선된 다이얼로그 사용

`main_window_methods_improved.py`에 구현된 메서드를 메인 윈도우 클래스에 적용하여 개선된 다이얼로그를 사용할 수 있습니다:

```python
# main_window.py에서 메서드 추가
from app.views.main_window.main_window_methods_improved import (
    show_settings_dialog,
    show_log_dialog,
    show_category_dialog,
    show_tag_dialog,
    on_settings_changed
)

# 메서드를 클래스에 추가
MainWindow.show_settings_dialog = show_settings_dialog
MainWindow.show_log_dialog = show_log_dialog
MainWindow.show_category_dialog = show_category_dialog
MainWindow.show_tag_dialog = show_tag_dialog
MainWindow.on_settings_changed = on_settings_changed
```

### 3.2 개선된 테마 사용

`advanced_theme_manager.py`에 개선된 테마 경로를 추가:

```python
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

    # 개선된 테마 추가
    improved_dir = os.path.join(self.themes_dir, "improved")
    if os.path.exists(improved_dir):
        for file in os.listdir(improved_dir):
            if file.endswith(".qss"):
                name = "improved_" + os.path.splitext(file)[0]
                path = os.path.join(improved_dir, file)
                themes[name] = path

    # 기존 테마 추가
    if os.path.exists(self.themes_dir):
        for file in os.listdir(self.themes_dir):
            if file.endswith(".qss") and file != "default.qss":
                name = os.path.splitext(file)[0]
                path = os.path.join(self.themes_dir, file)
                themes[name] = path

    return themes
```

## 4. 향후 개선 방향

### 4.1 추가 UI 개선 항목

- 메인 타이머 위젯 개선
- 상태 바 및 도구 모음 개선
- 애니메이션 및 전환 효과 추가
- 접근성 및 키보드 탐색 개선

### 4.2 필요한 리소스

다음 리소스들이 UI 개선을 위해 필요합니다:

- SVG 아이콘 세트: 버튼, 메뉴 항목에 사용
- 체크박스, 라디오 버튼 등을 위한 커스텀 이미지
- 고품질 폰트 (예: Noto Sans, Roboto)

## 5. 구현 예시

### 5.1 카드 스타일 그룹 박스

```python
group = QGroupBox("그룹 제목")
group.setStyleSheet("""
    QGroupBox {
        background-color: palette(base);
        border-radius: 6px;
        border: 1px solid palette(mid);
        margin-top: 12px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
""")
```

### 5.2 현대적인 버튼

```python
button = QPushButton("버튼")
button.setMinimumWidth(100)
button.setMinimumHeight(36)
button.setStyleSheet("""
    QPushButton {
        background-color: #4a86e8;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #5a96f8;
    }
    QPushButton:pressed {
        background-color: #3a76d8;
    }
""")
```

### 5.3 개선된 입력 필드

```python
lineEdit = QLineEdit()
lineEdit.setMinimumHeight(32)
lineEdit.setPlaceholderText("입력하세요...")
lineEdit.setStyleSheet("""
    QLineEdit {
        border-radius: 4px;
        padding: 4px 8px;
        background-color: palette(base);
        border: 1px solid palette(mid);
    }
    QLineEdit:focus {
        border: 1px solid palette(highlight);
    }
""")
```

## 6. 테스트 및 검증

UI 개선 사항을 적용한 후에는 다음 사항을 확인해주세요:

1. 다양한 화면 크기에서 테스트
2. 다크 모드와 라이트 모드 테스트
3. 모든 대화상자 및 컨트롤이 일관된 디자인 언어로 표시되는지 확인
4. 접근성 및 사용성 테스트

---

작성자: PaceKeeper 개발팀
최종 업데이트: 2025-04-10
