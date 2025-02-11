# views/break_dialog.py
import wx
from pacekeeper.controllers.config_controller import ConfigController, AppStatus
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import SET_PADDING_SIZE, CONFIG_DATA_MODEL
from pacekeeper.views.controls import BreakDialogPanel

lang_res = load_language_resource()

class BreakDialog(wx.Dialog):
    """
    휴식 시간을 카운트다운하는 모달 다이얼로그  
    UI는 BreakDialogPanel을 사용하고, 타이머 제어는 MainController의 기능을 호출하도록 함.
    """
    def __init__(self, parent, config_controller: ConfigController, break_minutes=5, on_break_end=None):
        display_width, display_height = wx.GetDisplaySize()
        self.config = config_controller
        self.break_minutes = break_minutes
        self.on_break_end = on_break_end
        self._destroyed = False  # 종료 상태 추적
        
        super().__init__(
            parent,
            title=lang_res.title_labels['BREAK_DIALOG_TITLE'],
            size=(display_width - self.config.get_setting(SET_PADDING_SIZE, 100),
                  display_height - self.config.get_setting(SET_PADDING_SIZE, 100)),
            style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP
        )

        # UI: BreakDialogPanel를 사용하여 레이아웃 구성
        self.panel = BreakDialogPanel(
            self,
            config_ctrl=self.config,
            on_item_double_click=self.on_item_double_click,
            on_tag_selected=self.add_tag_to_input,
            on_text_change=self.on_text_change,
            on_submit=self.on_submit
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.CenterOnScreen()

        # 타이머 제어: MainController에서 제공하는 함수(start_timer_func, stop_timer_func)를 할당받아 사용
        # 예를 들어, 외부에서 아래와 같이 할당할 수 있습니다.
        #   break_dialog.start_timer_func = main_controller.start_break_timer
        #   break_dialog.stop_timer_func = main_controller.stop_timer
        if hasattr(self, 'start_timer_func') and callable(self.start_timer_func):
            total_seconds = self.break_minutes * 60  # 분 → 초 변환
            self.start_timer_func(total_seconds, self.panel.break_label, self.on_break_finish)
        else:
            print("start_timer_func not provided to BreakDialog.")

    def on_break_finish(self):
        """타이머 종료 후 호출될 콜백 (MainController에서 호출)"""
        if not self._destroyed and self.on_break_end:
            wx.CallAfter(self.on_break_end)
        if not self._destroyed:
            wx.CallAfter(self.EndModal, wx.ID_OK)

    def on_item_double_click(self, event):
        index = event.GetIndex()
        message = self.panel.recent_logs.list_ctrl.GetItemText(index, 1)
        tags = self.panel.recent_logs.list_ctrl.GetItemText(index, 2)
        full_text = f"{tags} {message}".strip() if tags else message
        self.panel.input_panel.set_value(full_text)
        if self.panel.input_panel.button:
            self.panel.input_panel.button.Enable(True)

    def on_text_change(self, event):
        user_text = self.panel.input_panel.get_value().strip()
        if self.panel.input_panel.button:
            self.panel.input_panel.button.Enable(bool(user_text))

    def on_submit(self, event):
        self._destroyed = True
        # 타이머 중지 함수는 MainController에서 할당받은 stop_timer_func를 사용
        if hasattr(self, 'stop_timer_func') and callable(self.stop_timer_func):
            self.stop_timer_func()
        user_text = self.panel.input_panel.get_value().strip()
        if hasattr(self.config, CONFIG_DATA_MODEL) and user_text:
            self.config.data_model.log_study(user_text)
            self.panel.recent_logs.load_data()
        if self.on_break_end:
            self.on_break_end(manual_submit=True)
        self.EndModal(wx.ID_OK)
        
    def add_tag_to_input(self, tag):
        current = self.panel.input_panel.get_value()
        if tag not in current:
            new_text = f"{current} {tag}" if current else f"{tag}"
            self.panel.input_panel.set_value(new_text.strip())