# main.py
import wx
import wx.adv
import os
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.controllers.main_controller import MainController
from pacekeeper.views.main_frame import MainFrame
from pacekeeper.utils.functions import resource_path
from pacekeeper.consts.settings import ASSETS_DIR, ICONS_DIR, ICON_PNG, APP_NAME, DB_FILE
from pacekeeper.repository.entities import Base

from sqlalchemy import create_engine

def init_database(db_uri=f"sqlite:///{DB_FILE}"):
    """
    데이터베이스 엔진을 생성하고, 모든 테이블을 생성합니다.
    """
    engine = create_engine(db_uri, echo=True)
    Base.metadata.create_all(engine)
    return engine

def main():
    """메인 함수."""
    # 데이터베이스 및 테이블 새로 생성
    engine = init_database()  # 데이터베이스가 없거나, 테이블이 없는 경우 새로 생성됩니다.
    
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
