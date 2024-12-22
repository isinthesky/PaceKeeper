# models/settings_model.py
import json
import os

class SettingsModel:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.default_settings = {
            "study_time": 25,
            "short_break": 5,
            "long_break": 15,
            "cycles": 4,
            "break_dlg_padding_size": 70
        }
        self.settings = dict(self.default_settings)

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(f"설정 로드 오류: {e}. 기본값 사용.")
                self.settings = dict(self.default_settings)
        else:
            self.save_settings()

    def save_settings(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"설정 저장 오류: {e}")

    def update_settings(self, new_settings: dict):
        self.settings.update(new_settings)
        self.save_settings()
