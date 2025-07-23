#!/usr/bin/env python
"""
한글 태그 테스트 스크립트
이 스크립트는 태그 서비스와 로그 다이얼로그에서 한글 태그가 올바르게 표시되는지 테스트합니다.
"""

import json
import sys

from icecream import ic
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.repository.tag_repository import TagRepository

# 앱 모듈 임포트
from pacekeeper.services.tag_service import TagService
from pacekeeper.views.log_dialog import LogDialog


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("한글 태그 테스트")
        self.resize(300, 200)

        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 상태 라벨
        self.status_label = QLabel("테스트 준비 완료")
        layout.addWidget(self.status_label)

        # 태그 서비스 테스트 버튼
        test_tag_service_btn = QPushButton("태그 서비스 테스트")
        test_tag_service_btn.clicked.connect(self.test_tag_service)
        layout.addWidget(test_tag_service_btn)

        # 로그 다이얼로그 테스트 버튼
        test_log_dialog_btn = QPushButton("로그 다이얼로그 테스트")
        test_log_dialog_btn.clicked.connect(self.test_log_dialog)
        layout.addWidget(test_log_dialog_btn)

        # 태그 서비스와 저장소 초기화
        self.tag_service = TagService()
        self.repository = TagRepository()
        self.config = ConfigController()

    def test_tag_service(self):
        """태그 서비스의 get_tag_text 메서드를 테스트합니다."""
        self.status_label.setText("태그 서비스 테스트 중...")

        try:
            # 1. 데이터베이스에서 태그 가져오기
            tags = self.tag_service.get_tags()
            if not tags:
                self.status_label.setText("태그가 없습니다. 먼저 태그를 생성하세요.")
                return

            ic(f"태그 총 {len(tags)}개 조회됨")

            # 2. 태그 ID 목록 만들기
            tag_ids = [tag["id"] for tag in tags[:3]]  # 처음 3개만 사용

            # 3. 일반 리스트로 테스트
            result1 = self.tag_service.get_tag_text(tag_ids)
            ic("일반 리스트 테스트 결과:", result1)

            # 4. JSON 문자열로 테스트
            json_tag_ids = json.dumps(tag_ids)
            result2 = self.tag_service.get_tag_text(json_tag_ids)
            ic("JSON 문자열 테스트 결과:", result2)

            self.status_label.setText(f"테스트 성공: {', '.join(result1)}")

        except Exception as e:
            ic("테스트 실패:", e)
            self.status_label.setText(f"테스트 실패: {str(e)}")

    def test_log_dialog(self):
        """로그 다이얼로그를 열어 태그 표시를 테스트합니다."""
        self.status_label.setText("로그 다이얼로그 테스트 중...")

        try:
            # 로그 다이얼로그 열기
            dialog = LogDialog(self, self.config)
            dialog.show()
            self.status_label.setText("로그 다이얼로그 테스트 중... 다이얼로그 확인")

        except Exception as e:
            ic("다이얼로그 열기 실패:", e)
            self.status_label.setText(f"다이얼로그 열기 실패: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
