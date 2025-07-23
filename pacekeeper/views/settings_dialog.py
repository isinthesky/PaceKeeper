# views/settings_dialog.py
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import (
    AVAILABLE_LANG_LABELS,
    AVAILABLE_LANGS,
    SET_ALARM_VOLUME,
    SET_BREAK_COLOR,
    SET_LANGUAGE,
    SET_LONG_BREAK_TIME,
    SET_POMODORO_CYCLES,
    SET_SHORT_BREAK_TIME,
    SET_SOUND_ENABLE,
    SET_STUDY_TIME,
    SET_TTS_ENABLE,
)
from pacekeeper.controllers.config_controller import ConfigController


class SettingsDialog(QDialog):
    """설정 다이얼로그"""
    def __init__(self, parent, config_ctrl: ConfigController):
        super().__init__(parent)
        self.config_ctrl = config_ctrl
        self.lang_res = load_language_resource(config_ctrl.get_language())

        self.setWindowTitle(self.lang_res.base_labels['SETTINGS'])
        self.setMinimumWidth(400)

        self.init_ui()
        self.load_settings()
        self.connect_events()

    def init_ui(self):
        """UI 구성요소 초기화"""
        main_layout = QVBoxLayout(self)

        # 탭 위젯 생성
        self.tab_widget = QTabWidget(self)

        # === 타이머 설정 탭 ===
        timer_tab = QWidget()
        timer_layout = QVBoxLayout(timer_tab)

        # 타이머 설정 그룹박스
        timer_group = QGroupBox(self.lang_res.group_labels['TIMER_SETTINGS'], timer_tab)
        timer_form = QFormLayout(timer_group)

        # 공부 시간 스핀박스
        self.study_time_spin = QSpinBox(timer_group)
        self.study_time_spin.setRange(1, 120)
        timer_form.addRow(self.lang_res.setting_labels['STUDY_TIME'], self.study_time_spin)

        # 짧은 휴식 시간 스핀박스
        self.short_break_spin = QSpinBox(timer_group)
        self.short_break_spin.setRange(1, 30)
        timer_form.addRow(self.lang_res.setting_labels['SHORT_BREAK'], self.short_break_spin)

        # 긴 휴식 시간 스핀박스
        self.long_break_spin = QSpinBox(timer_group)
        self.long_break_spin.setRange(1, 60)
        timer_form.addRow(self.lang_res.setting_labels['LONG_BREAK'], self.long_break_spin)

        # 뽀모도로 사이클 스핀박스
        self.cycles_spin = QSpinBox(timer_group)
        self.cycles_spin.setRange(1, 10)
        timer_form.addRow(self.lang_res.setting_labels['CYCLES'], self.cycles_spin)

        timer_layout.addWidget(timer_group)

        # === 소리 설정 탭 ===
        sound_tab = QWidget()
        sound_layout = QVBoxLayout(sound_tab)

        # 소리 설정 그룹박스
        sound_group = QGroupBox(self.lang_res.group_labels['SOUND_SETTINGS'], sound_tab)
        sound_form = QFormLayout(sound_group)

        # 소리 활성화 체크박스
        self.sound_enable_check = QCheckBox(sound_group)
        sound_form.addRow(self.lang_res.setting_labels['SOUND_ENABLE'], self.sound_enable_check)

        # TTS 활성화 체크박스
        self.tts_enable_check = QCheckBox(sound_group)
        sound_form.addRow(self.lang_res.setting_labels['TTS_ENABLE'], self.tts_enable_check)

        # 알람 볼륨 슬라이더
        volume_widget = QWidget(sound_group)
        volume_layout = QHBoxLayout(volume_widget)
        volume_layout.setContentsMargins(0, 0, 0, 0)

        self.volume_slider = QSlider(Qt.Horizontal, volume_widget)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.setTickInterval(10)

        self.volume_label = QLabel("50%", volume_widget)
        self.volume_label.setMinimumWidth(40)

        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)

        sound_form.addRow(self.lang_res.setting_labels['ALARM_VOLUME'], volume_widget)

        sound_layout.addWidget(sound_group)

        # === 시각 설정 탭 ===
        visual_tab = QWidget()
        visual_layout = QVBoxLayout(visual_tab)

        # 시각 설정 그룹박스
        visual_group = QGroupBox(self.lang_res.group_labels['VISUAL_SETTINGS'], visual_tab)
        visual_form = QFormLayout(visual_group)

        # 휴식 색상 버튼
        self.break_color_btn = QPushButton(visual_group)
        self.break_color_btn.setFixedSize(80, 25)
        visual_form.addRow(self.lang_res.setting_labels['BREAK_COLOR'], self.break_color_btn)

        visual_layout.addWidget(visual_group)

        # === 언어 설정 탭 ===
        lang_tab = QWidget()
        lang_layout = QVBoxLayout(lang_tab)

        # 언어 설정 그룹박스
        lang_group = QGroupBox(self.lang_res.group_labels['LANGUAGE_SETTINGS'], lang_tab)
        lang_form = QFormLayout(lang_group)

        # 언어 선택 콤보박스
        self.lang_combo = QComboBox(lang_group)
        for i, _lang in enumerate(AVAILABLE_LANGS):
            self.lang_combo.addItem(AVAILABLE_LANG_LABELS[i])

        lang_form.addRow(self.lang_res.setting_labels['LANGUAGE'], self.lang_combo)

        lang_layout.addWidget(lang_group)

        # 탭 추가
        self.tab_widget.addTab(timer_tab, self.lang_res.tab_labels['TIMER'])
        self.tab_widget.addTab(sound_tab, self.lang_res.tab_labels['SOUND'])
        self.tab_widget.addTab(visual_tab, self.lang_res.tab_labels['VISUAL'])
        self.tab_widget.addTab(lang_tab, self.lang_res.tab_labels['LANGUAGE'])

        main_layout.addWidget(self.tab_widget)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()

        # 저장 버튼
        self.save_btn = QPushButton(self.lang_res.button_labels['SAVE'], self)
        button_layout.addWidget(self.save_btn)

        # 취소 버튼
        self.cancel_btn = QPushButton(self.lang_res.button_labels['CANCEL'], self)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

    def load_settings(self):
        """설정 값을 UI에 로드"""
        # 타이머 설정
        self.study_time_spin.setValue(self.config_ctrl.get_setting(SET_STUDY_TIME, 25))
        self.short_break_spin.setValue(self.config_ctrl.get_setting(SET_SHORT_BREAK_TIME, 5))
        self.long_break_spin.setValue(self.config_ctrl.get_setting(SET_LONG_BREAK_TIME, 15))
        self.cycles_spin.setValue(self.config_ctrl.get_setting(SET_POMODORO_CYCLES, 4))

        # 소리 설정
        self.sound_enable_check.setChecked(self.config_ctrl.get_setting(SET_SOUND_ENABLE, True))
        self.tts_enable_check.setChecked(self.config_ctrl.get_setting(SET_TTS_ENABLE, False))

        volume = self.config_ctrl.get_setting(SET_ALARM_VOLUME, 50)
        self.volume_slider.setValue(volume)
        self.volume_label.setText(f"{volume}%")

        # 시각 설정
        break_color = self.config_ctrl.get_setting(SET_BREAK_COLOR, "#FDFFB6")
        self.break_color = QColor(break_color)
        self.break_color_btn.setStyleSheet(f"background-color: {break_color};")

        # 언어 설정
        lang_index = AVAILABLE_LANGS.index(self.config_ctrl.get_setting(SET_LANGUAGE, "en"))
        self.lang_combo.setCurrentIndex(lang_index)

    def connect_events(self):
        """이벤트 연결"""
        # 버튼 이벤트
        self.save_btn.clicked.connect(self.on_save)
        self.cancel_btn.clicked.connect(self.reject)

        # 볼륨 슬라이더 이벤트
        self.volume_slider.valueChanged.connect(self.on_volume_changed)

        # 색상 버튼 이벤트
        self.break_color_btn.clicked.connect(self.on_color_select)

    def on_volume_changed(self, value):
        """볼륨 슬라이더 값 변경 이벤트"""
        self.volume_label.setText(f"{value}%")

    def on_color_select(self):
        """색상 선택 다이얼로그 오픈"""
        color = QColorDialog.getColor(self.break_color, self)
        if color.isValid():
            self.break_color = color
            self.break_color_btn.setStyleSheet(f"background-color: {color.name()};")

    def on_save(self):
        """설정 저장 버튼 클릭 시 호출"""
        # 타이머 설정 저장
        self.config_ctrl.set_setting(SET_STUDY_TIME, self.study_time_spin.value())
        self.config_ctrl.set_setting(SET_SHORT_BREAK_TIME, self.short_break_spin.value())
        self.config_ctrl.set_setting(SET_LONG_BREAK_TIME, self.long_break_spin.value())
        self.config_ctrl.set_setting(SET_POMODORO_CYCLES, self.cycles_spin.value())

        # 소리 설정 저장
        self.config_ctrl.set_setting(SET_SOUND_ENABLE, self.sound_enable_check.isChecked())
        self.config_ctrl.set_setting(SET_TTS_ENABLE, self.tts_enable_check.isChecked())
        self.config_ctrl.set_setting(SET_ALARM_VOLUME, self.volume_slider.value())

        # 시각 설정 저장
        self.config_ctrl.set_setting(SET_BREAK_COLOR, self.break_color.name())

        # 언어 설정 저장
        selected_lang = AVAILABLE_LANGS[self.lang_combo.currentIndex()]
        self.config_ctrl.set_setting(SET_LANGUAGE, selected_lang)

        # 설정 저장
        self.config_ctrl.save_settings()

        # 다이얼로그 닫기
        self.accept()
