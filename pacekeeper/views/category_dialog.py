# views/track_dialog.py
import wx
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.controllers.category_controls import CategoryControlsPanel, TagButtonsPanel
from pacekeeper.services.tag_service import TagService
from pacekeeper.services.category_service import CategoryService
from pacekeeper.consts.labels import load_language_resource
from icecream import ic

lang_res = load_language_resource(ConfigController().get_language())

class CategoryDialog(wx.Dialog):
    def __init__(self, parent, config_controller):
        super().__init__(parent, title=lang_res.base_labels['CATEGORY'], size=(660, 500),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        self.config = config_controller
        self.tag_service = TagService()
        self.category_service = CategoryService()
        self.selected_tag = None
        self.InitUI()
        self.Center()
        # 초기 데이터 로드
        self.refresh_data()

    def refresh_data(self):
        """
        카테고리 목록과 태그 목록을 새로고침합니다.
        이 메서드는 카테고리나 태그가 변경될 때마다 호출해야 합니다.
        """
        # 카테고리 목록 갱신
        self.controls_panel.update_category_list()
        # 태그 목록 갱신
        tags = self.tag_service.get_tags()
        self.tag_panel.update_tags(tags)

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 타이틀 레이블 추가
        title_label = wx.StaticText(panel, label=lang_res.base_labels['CATEGORY'], style=wx.ALIGN_CENTER)
        font = title_label.GetFont()
        font = font.Bold()
        title_label.SetFont(font)
        vbox.Add(title_label, flag=wx.EXPAND | wx.ALL, border=10)

        # 좌우 영역용 Horizontal BoxSizer 생성
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # CategoryControlsPanel: 왼쪽에 배치 (인스턴스 변수로 저장)
        self.controls_panel = CategoryControlsPanel(panel)
        hbox.Add(self.controls_panel, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # TagButtonsPanel: 오른쪽에 배치
        self.tag_panel = TagButtonsPanel(panel, on_tag_selected=self.add_tag_to_input)
        hbox.Add(self.tag_panel, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # 좌우 영역을 vbox에 추가 (비율 1로 지정하여 공간을 동일하게 나눔)
        vbox.Add(hbox, proportion=1, flag=wx.EXPAND)

        # 닫기 버튼 영역 추가
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        close_btn = wx.Button(panel, label="닫기")
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        btn_sizer.Add(close_btn, flag=wx.ALIGN_CENTER)
        vbox.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        panel.SetSizer(vbox)
        self.SetSize((660, 500))
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        # 키 입력 이벤트 처리를 위한 바인딩 추가 (다이얼로그 내에서 키 입력을 캡처)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        
    def add_tag_to_input(self, tag):
        self.selected_tag = tag
        
    def on_key_down(self, event):
        """
        다이얼로그에서 키 입력 이벤트를 처리하는 핸들러입니다.
        - Ctrl + 숫자 키: 선택된 태그의 카테고리 ID를 업데이트합니다.
        - 일반 키 입력: 텍스트 컨트롤에 입력되도록 이벤트를 전달합니다.
        """
        keycode = event.GetKeyCode()
        ctrl_down = event.ControlDown()
        
        if keycode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
            return
        
        if ctrl_down and keycode >= 48 and keycode <= 57:
            select_number = keycode - 48
            ic("Ctrl + 숫자 키 입력:", select_number)
            
            if not self.selected_tag:
                ic("selected_tag가 없습니다.")
                event.Skip()
                return
                
            category = self.category_service.get_category(select_number)
            ic("category", category)
            
            if not category:
                ic("category가 없습니다.")
                event.Skip()
                return
            
            tag = self.tag_service.get_tag(self.selected_tag.id)
            ic("tag", tag)
            
            tag.category_id = category.id
            
            updated_tag = self.tag_service.update_tag(tag)
            ic("updated_tag", updated_tag)
            
            # 갱신된 태그 정보를 반영하여 버튼 색상 업데이트
            self.refresh_data()
        else:
            # 일반 키 입력은 기본 처리로 전달 (텍스트 컨트롤 등에 입력)
            event.Skip()
        
    def on_close(self, event):
        self.EndModal(wx.ID_CANCEL)
