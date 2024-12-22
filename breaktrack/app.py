# breaktrack/app.py
import wx
from breaktrack.views.main_frame import MainFrame
from breaktrack.models.setting_model import SettingsModel
from breaktrack.utils import resource_path

class BreaktrackApp(wx.App):
    """
    Breaktrack 애플리케이션 클래스
    """
    def OnInit(self):
        """
        애플리케이션 초기화 메서드
        """
        # 설정 로드

        config_path = resource_path("config.json")
        print(config_path)
        self.settings = SettingsModel(config_path)
        self.settings.load_settings()

        self.frame = MainFrame(None, title="Breaktrack", settings=self.settings)
        self.frame.Show()
        return True