# models/settings_model.py
import json
import os
from pacekeeper.consts.settings import CONFIG_FILE, DEFAULT_SETTINGS
from pacekeeper.consts.labels import load_language_resource

lang_res = load_language_resource()

class SettingsModel:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.default_settings = dict(DEFAULT_SETTINGS)
        self.settings = dict(self.default_settings)

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
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
