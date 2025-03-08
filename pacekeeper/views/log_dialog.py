# views/track_dialog.py
import wx
import json
from typing import List
from datetime import date, datetime, timedelta
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.services.log_service import LogService
from pacekeeper.services.tag_service import TagService
from pacekeeper.repository.entities import Log
from pacekeeper.consts.labels import load_language_resource
from icecream import ic

lang_res = load_language_resource(ConfigController().get_language())

class LogDialog(wx.Dialog):
    def __init__(self, parent, config_controller):
        super().__init__(parent, title=lang_res.base_labels['LOGS'], size=(800, 800),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        self.config = config_controller
        self.log_service = LogService()
        self.tag_service = TagService()
        # 종료일 기본값: 오늘
        end_dt = date.today()
        start_dt = end_dt - timedelta(days=90)
        self.selected_start_date = start_dt.strftime("%Y-%m-%d")
        self.selected_end_date = end_dt.strftime("%Y-%m-%d")

        self.InitUI()
        self.Center()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 레이블
        title_label = wx.StaticText(panel, label=lang_res.base_labels['LOGS'], style=wx.ALIGN_CENTER)
        font = title_label.GetFont()
        font = font.Bold()
        title_label.SetFont(font)
        vbox.Add(title_label, flag=wx.EXPAND | wx.ALL, border=10)

        # ---------------------------------------------------------------------
        # (1) 검색 영역: 날짜 범위 + 태그 + 검색 버튼
        # ---------------------------------------------------------------------
        search_panel = wx.Panel(panel)
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # -- 기간 선택 버튼들 --
        # 1년 / 3달 / 1달 / 1주 / 1일
        period_buttons = [
            ("1년", 365),
            ("3달", 90),
            ("1달", 30),
            ("1주", 7),
            ("1일", 1),
        ]
        
        for label, days in period_buttons:
            btn = wx.Button(search_panel, label=label, size=(40, -1))
            btn.Bind(wx.EVT_BUTTON, lambda evt, d=days: self.on_period_button(evt, d))
            search_sizer.Add(btn, flag=wx.ALL, border=5)
            
        # ESC 키 이벤트 바인딩 추가
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)

        # 종료일 (기본값: 오늘)
        search_sizer.Add(wx.StaticText(search_panel, label=lang_res.base_labels['SEARCH_DATE']),
                         0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        today_str = date.today().strftime("%Y-%m-%d")
        self.end_date_tc = wx.TextCtrl(search_panel, value=today_str, size=(100, -1), style=wx.TE_CENTER)
        search_sizer.Add(self.end_date_tc, 0, wx.RIGHT, 10)

        # 태그
        search_sizer.Add(wx.StaticText(search_panel, label=lang_res.base_labels['TAG']),
                         0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.tag_tc = wx.TextCtrl(search_panel, size=(100, -1))
        search_sizer.Add(self.tag_tc, 0, wx.RIGHT, 10)

        # 검색 버튼
        search_btn = wx.Button(search_panel, label=lang_res.button_labels['SEARCH'])
        search_btn.Bind(wx.EVT_BUTTON, self.on_search)
        search_sizer.Add(search_btn, 0, wx.RIGHT, 10)

        search_panel.SetSizer(search_sizer)
        vbox.Add(search_panel, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)

        # ---------------------------------------------------------------------
        # (2) ListCtrl: 로그를 테이블 형태로 표시
        # ---------------------------------------------------------------------
        # ID 컬럼은 내부 참조용으로 사용하고, 사용자에게는 보이지 않도록 너비 0 설정
        self.list_ctrl = wx.ListCtrl(panel, style=wx.LC_REPORT)
        self.list_ctrl.InsertColumn(0, "ID", width=0, format=wx.LIST_FORMAT_RIGHT)
        self.list_ctrl.InsertColumn(1, "Start Time", width=180, format=wx.LIST_FORMAT_CENTER)
        self.list_ctrl.InsertColumn(2, "End Time", width=180, format=wx.LIST_FORMAT_CENTER)
        self.list_ctrl.InsertColumn(3, "Message", width=300, format=wx.LIST_FORMAT_LEFT)
        self.list_ctrl.InsertColumn(4, "Tags", width=200, format=wx.LIST_FORMAT_LEFT)
        vbox.Add(self.list_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # ---------------------------------------------------------------------
        # (3) 삭제 버튼: 선택한 로그 항목들을 삭제
        # ---------------------------------------------------------------------
        btn_panel = wx.Panel(panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        delete_btn = wx.Button(btn_panel, label="선택 삭제")
        delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        btn_sizer.Add(delete_btn, 0, wx.ALL, 5)
        btn_panel.SetSizer(btn_sizer)
        vbox.Add(btn_panel, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(vbox)
        self.load_all_logs()

    def load_all_logs(self):
        """
        DB에서 전체 로그를 가져와서 ListCtrl에 표시
        """
        rows: List[Log] = self.log_service.retrieve_all_logs()
        rows  = rows if rows else []
        self.load_rows(rows)

    def load_rows(self, logs: List[Log]):
        self.list_ctrl.DeleteAllItems()
        
        tags = self.tag_service.get_tags()
        tag_dict = {tag.id: tag.name for tag in tags}
        
        ic("태그 사전:", tag_dict)
        
        for row in logs:
            idx = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), str(row.id))
            # 생성 일시를 올바른 필드 created_at으로 변경
            self.list_ctrl.SetItem(idx, 1, str(row.start_date))  # timestamp
            self.list_ctrl.SetItem(idx, 2, str(row.end_date))  
            self.list_ctrl.SetItem(idx, 3, str(row.message))
            
            ic("로그 태그:", row.tags)
            
            # 태그 ID 목록 처리
            tag_names = []
            
            try:
                # 문자열을 리스트로 변환 시도
                import ast
                tag_ids = ast.literal_eval(row.tags)
                if isinstance(tag_ids, list):
                    for tag_id in tag_ids:
                        if tag_id in tag_dict:
                            tag_names.append(tag_dict[tag_id])
            except (ValueError, SyntaxError):
                # 쉼표로 구분된 문자열로 처리
                tag_ids = [tid.strip() for tid in row.tags.replace('[', '').replace(']', '').split(',')]
                for tag_id in tag_ids:
                    if tag_id and tag_id.isdigit() and int(tag_id) in tag_dict:
                        tag_names.append(tag_dict[int(tag_id)])
            
            # 태그 이름을 쉼표로 구분하여 표시
            tag_names_str = ", ".join(tag_names)
            ic("태그 이름:", tag_names_str)
            self.list_ctrl.SetItem(idx, 4, tag_names_str)

    def on_period_button(self, event, days):
        """
        기간 버튼 클릭 시 종료일에서 days일 만큼 빼서 시작일을 결정하고 검색 실행
        """
        end_date_str = self.end_date_tc.GetValue().strip()
        if not end_date_str:
            end_date_str = date.today().strftime("%Y-%m-%d")
            self.end_date_tc.SetValue(end_date_str)
        try:
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            wx.MessageBox(lang_res.error_messages['SEARCH_DATE'], lang_res.base_labels['ERROR'], wx.OK | wx.ICON_ERROR)
            return

        start_dt = end_dt - timedelta(days=days)
        self.selected_start_date = start_dt.strftime("%Y-%m-%d")
        self.on_search(None)

    def on_search(self, event):
        """
        '검색' 버튼 클릭 시 날짜 범위와 태그 검색을 수행
        """
        start_date = self.selected_start_date
        end_date = self.selected_end_date
        tag_keyword = self.tag_tc.GetValue().strip()
    
        # 날짜 범위 조건 처리
        rows_date = set(self.log_service.retrieve_logs_by_period(start_date, end_date)) if start_date and end_date else set(self.log_service.retrieve_all_logs())
        # 태그 조건 처리
        rows_tag = set(self.log_service.retrieve_logs_by_tag(tag_keyword)) if tag_keyword else set(self.log_service.retrieve_all_logs())
        intersect_rows = rows_date.intersection(rows_tag)
        sorted_rows = sorted(list(intersect_rows), key=lambda x: x[0], reverse=True)
        self.load_rows(sorted_rows)

    def on_delete(self, event):
        """
        선택된 로그 항목들을 삭제하는 이벤트 핸들러
        """
        # 선택된 항목 인덱스를 가져옴
        selected_indices = []
        index = self.list_ctrl.GetFirstSelected()
        while index != -1:
            selected_indices.append(index)
            index = self.list_ctrl.GetNextSelected(index)

        if not selected_indices:
            wx.MessageBox("삭제할 로그를 선택하세요.", "알림", wx.OK | wx.ICON_INFORMATION)
            return

        answer = wx.MessageBox("선택한 로그를 삭제하시겠습니까?", "확인", wx.YES_NO | wx.ICON_QUESTION)
        if answer != wx.YES:
            return

        ids_to_delete = []
        for idx in selected_indices:
            id_str = self.list_ctrl.GetItemText(idx, 0)
            try:
                log_id = int(id_str)
                ids_to_delete.append(log_id)
            except ValueError:
                continue

        self.log_service.remove_logs_by_ids(ids_to_delete)
        wx.MessageBox("선택한 로그가 삭제되었습니다.", "정보", wx.OK | wx.ICON_INFORMATION)
        self.load_all_logs()

    def on_close(self, event):
        self.Destroy()

    def on_key_down(self, event):
        """
        키 입력 이벤트를 처리하는 핸들러입니다.
        ESC 키를 누르면 다이얼로그를 닫습니다.
        """
        keycode = event.GetKeyCode()
        
        if keycode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()  # 다른 키 입력은 기본 처리로 전달
