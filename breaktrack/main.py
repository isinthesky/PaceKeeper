# main.py
import wx
import wx.adv  # TaskBarIcon을 위한 import 추가
import os
from breaktrack.controllers.config_controller import ConfigController
from breaktrack.controllers.main_controller import MainController
from breaktrack.views.main_frame import MainFrame
from breaktrack.utils import resource_path

def main():
    """메인 함수."""
    app = wx.App()

    # TaskBar 아이콘 설정
    icon_path = resource_path(os.path.join("assets", "icons", "BreakTrack.png"))
    print(icon_path)
    if os.path.exists(icon_path):
        app.SetAppDisplayName("Breaktrack")
        app_icon = wx.Icon(icon_path, wx.BITMAP_TYPE_PNG)
        taskbar = wx.adv.TaskBarIcon()
        taskbar.SetIcon(app_icon)

    # 설정/상태 관리 컨트롤러
    config_controller = ConfigController()

    # 메인 프레임 생성 + 메인 컨트롤러와 연결
    frame = MainFrame(None, title="Breaktrack", config_controller=config_controller)
    MainController(frame, config_controller)

    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
