# main.py
import wx
from breaktrack.controllers.config_controller import ConfigController
from breaktrack.controllers.main_controller import MainController
from breaktrack.views.main_frame import MainFrame

def main():
    """메인 함수."""
    app = wx.App()

    # 설정/상태 관리 컨트롤러
    config_controller = ConfigController()

    # 메인 프레임 생성 + 메인 컨트롤러와 연결
    frame = MainFrame(None, title="Breaktrack", config_controller=config_controller)
    MainController(frame, config_controller)

    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
