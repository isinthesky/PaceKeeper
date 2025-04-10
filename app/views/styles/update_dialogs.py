"""
객체 이름 설정과 테마 적용을 위한 함수
"""

import os

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import (QComboBox, QDialog, QFrame, QLabel,
                             QLineEdit, QListWidget, QPushButton, QWidget)


def set_object_names(dialog):
    """
    다이얼로그의 모든 위젯에 objectName을 설정하는 함수

    Args:
        dialog: 대상 다이얼로그
    """
    # 다이얼로그 자체에 이름 설정
    if isinstance(dialog, QDialog) and not dialog.objectName():
        class_name = dialog.__class__.__name__
        dialog.setObjectName(class_name)

    # 모든 자식 위젯에 이름 설정
    for child in dialog.findChildren(QObject):
        # 이미 objectName이 설정된 경우 건너뛰기
        if child.objectName():
            continue

        # 위젯 유형 확인 및 이름 설정
        if isinstance(child, QPushButton):
            text = child.text().lower().replace(" ", "")
            child.setObjectName(f"{text}Button")
        elif isinstance(child, QLineEdit):
            # 부모 위젯의 속성을 확인하거나 기본 이름 할당
            if hasattr(child, "_name"):
                child.setObjectName(f"{child._name}Input")
            else:
                child.setObjectName("textInput")
        elif isinstance(child, QLabel):
            text = child.text().lower().replace(" ", "")
            if text:
                child.setObjectName(f"{text}Label")
            else:
                child.setObjectName("label")
        elif isinstance(child, QListWidget):
            child.setObjectName("listWidget")
        elif isinstance(child, QComboBox):
            child.setObjectName("comboBox")
        elif isinstance(child, QFrame):
            child.setObjectName("frame")
        elif isinstance(child, QWidget) and child.layout() is not None:
            # 레이아웃이 있는 위젯은 패널로 간주
            if "left" in child.objectName().lower() or child.x() < dialog.width() / 2:
                child.setObjectName("leftPanel")
            elif (
                "right" in child.objectName().lower() or child.x() >= dialog.width() / 2
            ):
                child.setObjectName("rightPanel")
            elif "top" in child.objectName().lower() or child.y() < dialog.height() / 2:
                child.setObjectName("topArea")
            elif (
                "bottom" in child.objectName().lower()
                or child.y() >= dialog.height() / 2
            ):
                child.setObjectName("bottomArea")
            else:
                child.setObjectName("panel")


def apply_theme_change(dialog, theme_name, theme_manager):
    """
    테마 변경 시 다이얼로그에 테마를 적용하는 함수

    Args:
        dialog: 테마를 적용할 다이얼로그
        theme_name: 테마 이름
        theme_manager: 테마 관리자 인스턴스
    """
    if theme_manager:
        style_content = theme_manager.get_theme_style(theme_name)
        if style_content:
            print(f"[DEBUG] {dialog.__class__.__name__}에 테마 적용: {theme_name}")

            # 다이얼로그에 스타일시트 적용
            dialog.setStyleSheet(style_content)

            # 모든 자식 위젯의 개별 스타일시트 제거 - 안전한 방법으로 구현
            try:
                for widget in dialog.findChildren(QWidget):
                    try:
                        widget.setStyleSheet("")
                    except Exception as e:
                        print(f"[DEBUG] 위젯 스타일시트 제거 중 오류: {e}")
            except Exception as e:
                print(f"[DEBUG] 위젯 처리 중 오류: {e}")

            # 특수 처리가 필요한 위젯 업데이트 - 안전한 방법으로 구현
            try:
                for frame in dialog.findChildren(QFrame):
                    try:
                        # 색상 미리보기 처리
                        if frame.objectName() == "colorPreview" and hasattr(
                            dialog, "current_category"
                        ):
                            if dialog.current_category and hasattr(
                                dialog.current_category, "color"
                            ):
                                frame.setStyleSheet(
                                    f"background-color: {dialog.current_category.color}; "
                                    f"border-radius: 4px; border: 1px solid palette(mid);"
                                )
                    except Exception as e:
                        print(f"[DEBUG] 프레임 스타일 적용 중 오류: {e}")
            except Exception as e:
                print(f"[DEBUG] 프레임 처리 중 오류: {e}")

            # 다이얼로그 강제 업데이트
            dialog.update()
