# views/track_dialog.py
import wx
from datetime import date, datetime, timedelta
from pacekeeper.const import (
    DIALOG_TRACK, MSG_ERROR_DATAMODEL, BTN_SEARCH, LABEL_SEARCH_DATE,
    LABEL_TAG, LABEL_ERROR, MSG_ERROR_SEARCH_DATE, CONFIG_DATA_MODEL,
)

class TrackDialog(wx.Dialog):
    def __init__(self, parent, config_controller):
        super().__init__(parent, title=DIALOG_TRACK, size=(800, 800),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        self.config = config_controller

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
        title_label = wx.StaticText(panel, label=DIALOG_TRACK, style=wx.ALIGN_CENTER)
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
            # days를 클로저로 캡처하기 위해 람다 대신 함수 사용
            btn.Bind(wx.EVT_BUTTON, lambda evt, d=days: self.on_period_button(evt, d))
            search_sizer.Add(btn, 0, wx.RIGHT, 5)

        # 종료일 (기본값: 오늘)
        search_sizer.Add(wx.StaticText(search_panel, label=f"{LABEL_SEARCH_DATE}"),
                         0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        today_str = date.today().strftime("%Y-%m-%d")
        self.end_date_tc = wx.TextCtrl(search_panel, value=today_str, size=(100, -1), style=wx.TE_CENTER)
        search_sizer.Add(self.end_date_tc, 0, wx.RIGHT, 10)

        # 태그
        search_sizer.Add(wx.StaticText(search_panel, label=LABEL_TAG),
                         0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.tag_tc = wx.TextCtrl(search_panel, size=(100, -1))
        search_sizer.Add(self.tag_tc, 0, wx.RIGHT, 10)

        # 검색 버튼
        search_btn = wx.Button(search_panel, label=BTN_SEARCH)
        search_btn.Bind(wx.EVT_BUTTON, self.on_search)
        search_sizer.Add(search_btn, 0, wx.RIGHT, 10)

        search_panel.SetSizer(search_sizer)
        vbox.Add(search_panel, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)

        # ListCtrl: 테이블 형태로 로그 표시
        self.list_ctrl = wx.ListCtrl(panel, style=wx.LC_REPORT)
        self.list_ctrl.InsertColumn(0, "ID", width=50, format=wx.LIST_FORMAT_RIGHT)
        self.list_ctrl.InsertColumn(1, "Timestamp", width=180, format=wx.LIST_FORMAT_CENTER)
        self.list_ctrl.InsertColumn(2, "Message", width=340, format=wx.LIST_FORMAT_LEFT)
        self.list_ctrl.InsertColumn(3, "Tags", width=140, format=wx.LIST_FORMAT_LEFT)

        vbox.Add(self.list_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        panel.SetSizer(vbox)

        self.load_all_logs()

    def load_all_logs(self):
        """
        DB에서 전체 로그를 가져와서 ListCtrl에 표시
        """
        if hasattr(self.config, "data_model"):
            rows = self.config.data_model.get_logs()
        else:
            rows = []
        self.load_rows(rows)

    def load_rows(self, rows):
        """
        ListCtrl 초기화 후, rows 데이터(ID, created_date, timestamp, message, tags) 출력
        """
        self.list_ctrl.DeleteAllItems()  # 기존 내용 초기화

        for row in rows:
            # row 예: (id, created_date, timestamp, message, tags)
            # 인덱스별로 컬럼에 매핑
            idx = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), str(row[0]))
            self.list_ctrl.SetItem(idx, 1, str(row[2]))  # timestamp
            self.list_ctrl.SetItem(idx, 2, str(row[3]))  # message
            self.list_ctrl.SetItem(idx, 3, str(row[4]))  # tags

    def on_period_button(self, event, days):
        """
        기간 버튼(1년, 3달, 1달, 1주, 1일) 클릭 시:
        종료일에서 days만큼 빼서 start_date를 결정하고 검색을 실행
        """
        end_date_str = self.end_date_tc.GetValue().strip()
        if not end_date_str:
            # 종료일이 비어있다면, 오늘 날짜로 설정
            end_date_str = date.today().strftime("%Y-%m-%d")
            self.end_date_tc.SetValue(end_date_str)

        # 종료일 파싱
        try:
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            wx.MessageBox(MSG_ERROR_SEARCH_DATE, LABEL_ERROR, wx.OK | wx.ICON_ERROR)
            return

        # 종료일에서 days일 전을 시작일로
        start_dt = end_dt - timedelta(days=days)
        self.selected_start_date = start_dt.strftime("%Y-%m-%d")

        # 곧바로 검색 로직 실행
        self.on_search(None)


    def on_search(self, event):
        """
        '검색' 버튼 클릭 시 날짜 범위 + 태그 검색을 수행
        """
        start_date = self.selected_start_date
        end_date = self.selected_end_date
        tag_keyword = self.tag_tc.GetValue().strip()        # 예: "#rest"

        # 데이터 모델이 있는지 확인
        if not hasattr(self.config, CONFIG_DATA_MODEL):
            wx.MessageBox(MSG_ERROR_DATAMODEL, LABEL_ERROR, wx.OK | wx.ICON_ERROR)
            return

        data_model = self.config.data_model

        # (A) 날짜 범위가 둘 다 입력된 경우 => get_logs_by_period
        #     아니면 => get_logs
        rows_date = None
        if start_date and end_date:
            rows_date = set(data_model.get_logs_by_period(start_date, end_date))
        else:
            # 날짜 범위가 주어지지 않았다면 전체 조회
            rows_date = set(data_model.get_logs())

        # (B) 태그가 입력된 경우 => get_logs_by_tag
        rows_tag = None
        if tag_keyword:
            rows_tag = set(data_model.get_logs_by_tag(tag_keyword))
        else:
            # 태그가 없으면 전체 조회
            rows_tag = set(data_model.get_logs())

        # (C) 날짜/태그 교집합
        #     두 조건이 모두 주어지면, 그 결과를 intersection
        intersect_rows = rows_date.intersection(rows_tag)

        # 리스트를 id DESC 순으로 정렬 (row[0] = id)
        sorted_rows = sorted(list(intersect_rows), key=lambda x: x[0], reverse=True)

        # 리스트에 표시
        self.load_rows(sorted_rows)

    def on_close(self, event):
        # 다이얼로그 종료
        self.Destroy()
