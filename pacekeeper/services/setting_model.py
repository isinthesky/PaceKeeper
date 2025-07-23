# models/settings_model.py
import json
import os

from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import CONFIG_FILE, DEFAULT_SETTINGS

lang_res = load_language_resource()

class SettingsModel:
    def __init__(self, config_file=CONFIG_FILE):
        # 사용자 홈 디렉토리에 .pacekeeper 폴더 생성
        self.config_dir = os.path.join(os.path.expanduser('~'), '.pacekeeper')
        os.makedirs(self.config_dir, exist_ok=True)

        # 설정 파일 경로 설정
        self.config_file = os.path.join(self.config_dir, config_file)
        self.default_settings = dict(DEFAULT_SETTINGS)
        self.settings = dict(self.default_settings)

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, encoding='utf-8') as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(lang_res.error_messages['SETTINGS_LOAD'].format(e))
                self.settings = dict(self.default_settings)
        else:
            self.save_settings()

    def save_settings(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(lang_res.error_messages['SETTINGS_SAVE'].format(e))

    def update_settings(self, new_settings: dict):
        self.settings.update(new_settings)
        self.save_settings()
