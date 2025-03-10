# models/settings_model.py
import json
import os
from pacekeeper.consts.settings import CONFIG_FILE, DEFAULT_SETTINGS
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.utils.functions import resource_path

lang_res = load_language_resource()

class SettingsModel:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.default_settings = dict(DEFAULT_SETTINGS)
        self.settings = dict(self.default_settings)
        self.load_settings()  # 초기화 시 설정 로드

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # 기본 설정에 로드된 설정 병합
                    self.settings = dict(self.default_settings)
                    self.settings.update(loaded_settings)
            except Exception as e:
                print(lang_res.error_messages['SETTINGS_LOAD'].format(e))
                self.settings = dict(self.default_settings)
                self.save_settings()  # 오류 발생 시 기본 설정으로 저장
        else:
            # 설정 파일이 없으면 기본 설정으로 저장
            self.settings = dict(self.default_settings)
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
