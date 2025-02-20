import wx
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.services.category_service import CategoryService
from pacekeeper.repository.entities import Tag
from pacekeeper.consts.labels import load_language_resource
from icecream import ic


lang_res = load_language_resource(ConfigController().get_language())

class CategoryControlsPanel(wx.Panel):
    """
    CategoryControlsPanel: 카테고리 목록을 보여주고
    새로운 카테고리 생성, 선택된 카테고리 수정 및 삭제 기능을 제공하는 패널.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.service = CategoryService()
        self.InitUI()
        self.update_category_list()

    def InitUI(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 카테고리 목록을 표시할 ListCtrl 생성 (ID, 이름, 설명, 색상)
        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, "ID", width=30)
        self.list_ctrl.InsertColumn(1, "이름", width=120)
        self.list_ctrl.InsertColumn(2, "설명", width=50)
        self.list_ctrl.InsertColumn(3, "색상", width=70)
        main_sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        # 카테고리 정보 입력용 폼 (이름, 설명, 색상)
        form_sizer = wx.FlexGridSizer(3, 2, 5, 5)
        name_label = wx.StaticText(self, label="이름:")
        self.name_text = wx.TextCtrl(self)
        description_label = wx.StaticText(self, label="설명:")
        self.description_text = wx.TextCtrl(self)
        color_label = wx.StaticText(self, label="색상:")
        self.color_picker = wx.ColourPickerCtrl(self, colour=wx.Colour(255, 255, 255))
        form_sizer.AddMany([name_label, self.name_text,
                            description_label, self.description_text,
                            color_label, self.color_picker])
        main_sizer.Add(form_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # 버튼 영역: 생성, 수정, 삭제
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.create_btn = wx.Button(self, label="생성")
        self.modify_btn = wx.Button(self, label="수정")
        self.delete_btn = wx.Button(self, label="삭제")
        btn_sizer.Add(self.create_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self.modify_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self.delete_btn, 0, wx.ALL, 5)
        main_sizer.Add(btn_sizer, 0, wx.CENTER)

        self.SetSizer(main_sizer)

        # 이벤트 바인딩
        self.create_btn.Bind(wx.EVT_BUTTON, self.on_create)
        self.modify_btn.Bind(wx.EVT_BUTTON, self.on_modify)
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected)

    def update_category_list(self):
        """카테고리 목록을 서비스로부터 조회하여 ListCtrl에 업데이트합니다."""
        self.list_ctrl.DeleteAllItems()
        categories = self.service.get_categories()
        for category in categories:
            idx = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), str(category.id))
            self.list_ctrl.SetItem(idx, 1, category.name)
            self.list_ctrl.SetItem(idx, 2, category.description)
            self.list_ctrl.SetItem(idx, 3, category.color)

    def on_create(self, event):
        """새 카테고리를 생성합니다."""
        name = self.name_text.GetValue().strip()
        description = self.description_text.GetValue().strip()
        color = self.color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        if not name:
            wx.MessageBox("이름을 입력하세요.", "오류", wx.OK | wx.ICON_ERROR)
            return
        try:
            self.service.add_category(name, description, color)
            wx.MessageBox(f"카테고리 생성 완료 {name}", "정보", wx.OK | wx.ICON_INFORMATION)
            self.clear_form()
            self.update_category_list()
        except Exception as e:
            wx.MessageBox(f"카테고리 생성 실패 {e}", "오류", wx.OK | wx.ICON_ERROR)

    def on_modify(self, event):
        """선택한 카테고리의 정보를 수정합니다."""
        selected_index = self.list_ctrl.GetFirstSelected()
        if selected_index == -1:
            wx.MessageBox("수정할 카테고리를 선택하세요.", "알림", wx.OK | wx.ICON_INFORMATION)
            return
        category_id = int(self.list_ctrl.GetItemText(selected_index))
        new_name = self.name_text.GetValue().strip()
        new_description = self.description_text.GetValue().strip()
        new_color = self.color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        if not new_name:
            wx.MessageBox("이름을 입력하세요.", "오류", wx.OK | wx.ICON_ERROR)
            return
        try:
            self.service.update_category(category_id, new_name, new_description, new_color)
            wx.MessageBox("카테고리 수정 완료", "정보", wx.OK | wx.ICON_INFORMATION)
            self.clear_form()
            self.update_category_list()
        except Exception as e:
            wx.MessageBox(f"카테고리 수정 실패 {e}", "오류", wx.OK | wx.ICON_ERROR)

    def on_delete(self, event):
        """선택한 카테고리를 삭제(soft delete)합니다."""
        selected_index = self.list_ctrl.GetFirstSelected()
        if selected_index == -1:
            wx.MessageBox("삭제할 카테고리를 선택하세요.", "알림", wx.OK | wx.ICON_INFORMATION)
            return
        category_id = int(self.list_ctrl.GetItemText(selected_index))
        answer = wx.MessageBox("선택한 카테고리를 삭제하시겠습니까?", "확인", wx.YES_NO | wx.ICON_QUESTION)
        if answer != wx.YES:
            return
        try:
            self.service.delete_category(category_id)
            wx.MessageBox("카테고리 삭제 완료", "정보", wx.OK | wx.ICON_INFORMATION)
            self.clear_form()
            self.update_category_list()
        except Exception as e:
            wx.MessageBox(f"카테고리 삭제 실패 {e}", "오류", wx.OK | wx.ICON_ERROR)

    def on_item_selected(self, event):
        """
        목록에서 항목이 선택되면 해당 카테고리의 이름, 설명 및 색상을 입력 폼에 채웁니다.
        선택된 카테고리의 저장된 색상 값 (#RRGGBB 형식)이 색상 선택 박스에 반영됩니다.
        """
        selected_index = event.GetIndex()
        name = self.list_ctrl.GetItemText(selected_index, 1)
        description = self.list_ctrl.GetItemText(selected_index, 2)
        color_text = self.list_ctrl.GetItemText(selected_index, 3)
        
        self.name_text.SetValue(name)
        self.description_text.SetValue(description)

        # 저장된 색상 값이 올바른 형식인지 확인 후 색상 박스 업데이트
        if color_text and color_text.startswith("#") and len(color_text) == 7:
            try:
                r = int(color_text[1:3], 16)
                g = int(color_text[3:5], 16)
                b = int(color_text[5:7], 16)
                self.color_picker.SetColour(wx.Colour(r, g, b))
            except Exception:
                self.color_picker.SetColour(wx.Colour(255, 255, 255))
        else:
            self.color_picker.SetColour(wx.Colour(255, 255, 255))

    def clear_form(self):
        """입력 폼 초기화 및 리스트 선택 해제."""
        self.name_text.SetValue("")
        self.description_text.SetValue("")
        self.color_picker.SetColour(wx.Colour(255, 255, 255))
        # 모든 항목의 선택 해제: 한 번에 해제하는 기능이 없으므로 모든 항목의 선택을 해제합니다.
        idx = self.list_ctrl.GetFirstSelected()
        while idx != -1:
            self.list_ctrl.Select(idx, on=0)
            idx = self.list_ctrl.GetNextSelected(idx) 
            
class TagButtonsPanel(wx.Panel):
    """태그 버튼들을 관리하는 패널"""
    def __init__(self, parent, on_tag_selected =  None):
        super().__init__(parent)
        self.on_tag_selected = on_tag_selected
        self.sizer = wx.WrapSizer()
        self.SetSizer(self.sizer)
        self.service = CategoryService()
        self.selected_tag = None
            
    def update_tags(self, tags:list[dict]):
        """
        태그 버튼 업데이트 메서드.
        """
        for child in self.GetChildren():
            child.Destroy()
        
        categories = self.service.get_categories()
        color_set = {category.id: category for category in categories}
                
        for tag in tags:
            if tag:
                btn = wx.Button(self, label=tag["name"])
                btn.Bind(wx.EVT_BUTTON, lambda event, t=tag: self.on_tag_selected(t))
                
                category = color_set.get(tag["category_id"])
                if category:
                    btn.SetBackgroundColour(category.color)
                    
                self.sizer.Add(btn, 0, wx.ALL, 5)
                
        self.Layout()