# main.py
import wx
import wx.adv
import os
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.controllers.main_controller import MainController
from pacekeeper.views.main_frame import MainFrame
from pacekeeper.utils import resource_path
from pacekeeper.consts.settings import ASSETS_DIR, ICONS_DIR, ICON_PNG, APP_NAME, APP_TITLE

def main():
    """메인 함수."""
    app = wx.App()

    # TaskBar 아이콘 설정
    icon_path = resource_path(os.path.join(ASSETS_DIR, ICONS_DIR, ICON_PNG))
    if os.path.exists(icon_path):
        app.SetAppDisplayName(APP_NAME)
        app_icon = wx.Icon(icon_path, wx.BITMAP_TYPE_PNG)
        taskbar = wx.adv.TaskBarIcon()
        taskbar.SetIcon(app_icon)

    # 설정 컨트롤러 싱글톤 인스턴스 초기화
    config_ctrl = ConfigController()
    
    # 메인 프레임 생성
    frame = MainFrame(None, config_ctrl=config_ctrl)

    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
