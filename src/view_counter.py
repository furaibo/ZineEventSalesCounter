import flet as ft
from flet.core.textfield import NumbersOnlyInputFilter
from pathlib import Path
from datetime import datetime

from report import generate_excel_report


# 定数定義
PRODUCT_COUNT_LIMIT = 6
PRODUCT_NAME_LIST = ["本", "DLカード", "ポストカード", "色紙", "アクリルスタンド", "キーホルダー"]


# 頒布履歴表示用Viewの取得
class ViewCounter(ft.View):
    # イニシャライザ定義
    def __init__(self, data_dict: dict):
        super().__init__()
        self.appbar = ft.AppBar(title=ft.Text("頒布数カウント"))
        self.data_dict = data_dict
        self.sales_history_dict = {i: [] for i in range(PRODUCT_COUNT_LIMIT)}
        self.define_view_components()

    #
    # 内部メソッド・イベント定義
    #

    # 頒布数集計結果の作成
    def get_sales_tally_data_list(self):
        sales_tally_list = []
        product_dict = {i: x.value for i, x in enumerate(self.text_field_product_list)}

        # 集計結果のリストを作成
        for index, item_list in self.sales_history_dict.items():
            product = product_dict[index]
            if len(product) > 0:
                item = {
                    "product": product,
                    "sales_count": len(item_list),
                    "sales_amount": sum([x["price"] for x in item_list])
                }
                sales_tally_list.append(item)

        return sales_tally_list

    # 履歴表示用データの取得
    def get_sales_history_data_list(self):
        sales_history_list = []
        product_dict = {i: x.value for i, x in enumerate(self.text_field_product_list)}

        # 履歴情報のリストを作成
        for index, item_list in self.sales_history_dict.items():
            product = product_dict[index]
            for item in item_list:
                item["product"] = product
                sales_history_list.append(item)

        # ソート処理(頒布日時の降順)
        sales_history_list = sorted(sales_history_list, key=lambda x: x["sales_at"], reverse=True)

        return sales_history_list

    # 頒布履歴情報の追加
    def add_sales_history_item(self, index: int):
        sales_at_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        price = int(self.text_field_price_list[index].value)
        history_item = {
            "price": price,
            "sales_at": sales_at_str
        }
        self.sales_history_dict[index].append(history_item)

    # 全体レポートexcelの保存
    def save_report_excel_file(self, save_file_path: Path):
        # 共有dict内に履歴情報データを格納
        self.data_dict["zine_event"] = {
            "name": self.text_field_zine_event_name.value,
            "desc": self.text_field_zine_event_desc.value,
            "date": self.text_field_zine_event_date.value
        }

        # 頒布数集計結果・履歴情報データの作成処理
        self.data_dict["sales_tally"] = self.get_sales_tally_data_list()
        self.data_dict["sales_history"] = self.get_sales_history_data_list()

        # Excelファイル生成処理の呼び出し
        generate_excel_report(save_file_path, self.data_dict)

    # snackbarの表示(頒布数加算処理時を想定)
    def show_snack_bar_sales_history(self, index: int):
        time_str = datetime.now().strftime("%H:%M:%S")
        product = self.text_field_product_list[index].value
        price = int(self.text_field_price_list[index].value)
        self.page.open(ft.SnackBar(ft.Text(f"{time_str} - {product}(価格: ￥{price:,}) 追加")))

    # イベント開催日指定時の処理
    def event_change_zine_event_date(self, e):
        dt_str = e.control.value.strftime("%Y/%m/%d")
        self.text_field_zine_event_date.value = dt_str
        self.text_field_zine_event_date.update()

    # チェックボックスの値が変更された時の処理
    def event_toggle_checkbox_product(self, e):
        # チェックボックスの値の確認
        index = e.control.data
        value = e.control.value
        disabled_flag = not value
        lock_flag = self.switch_product_lock_list[index].value

        # 各入力項目のdisabledフラグの切り替え
        self.dropdown_product_type_list[index].disabled = disabled_flag or lock_flag
        self.text_field_product_list[index].disabled = disabled_flag
        self.text_field_price_list[index].disabled = disabled_flag
        self.switch_product_lock_list[index].disabled = disabled_flag

        # 全体の更新
        self.update()

    # 編集ロック制御用のswitchの状態が変更されたときの処理
    def event_switch_product_lock(self, e):
        # ボタンの値の確認
        index = e.control.data
        value = e.control.value
        read_only_flag = value
        disabled_flag = not value

        # 各入力項目のread_only/disabledフラグの切り替え
        self.text_field_product_list[index].read_only = read_only_flag
        self.text_field_price_list[index].read_only = read_only_flag
        self.dropdown_product_type_list[index].disabled = read_only_flag

        self.icon_button_minus_list[index].disabled = disabled_flag
        self.text_field_count_list[index].disabled = disabled_flag
        self.icon_button_plus_list[index].disabled = disabled_flag

        # 全体の更新
        self.update()

    # '-'ボタン押下/頒布数減算時の処理
    def event_count_minus(self, e):
        # 頒布数の値の更新処理
        index = e.control.data
        text_field = self.text_field_count_list[index]
        value = int(text_field.value)
        if value > 0:
            text_field.value = str(value - 1)
            text_field.update()

        # 頒布履歴からの削除
        if len(self.sales_history_dict[index]) > 0:
            self.sales_history_dict[index].pop()

    # '+'ボタン押下/頒布数加算時の処理
    def event_count_plus(self, e):
        # 頒布数の値の更新処理
        index = e.control.data
        text_field = self.text_field_count_list[index]
        value = int(text_field.value)
        if value < 1000:
            text_field.value = str(value + 1)
            text_field.update()
            # 履歴追加処理およびページ下部バー表示
            self.add_sales_history_item(index)
            self.show_snack_bar_sales_history(index)

    # 頒布履歴確認ボタン押下時の処理
    def event_click_go_sales_history(self):
        # 共有dict内に履歴情報データを格納
        self.data_dict["sales_history"] = self.get_sales_history_data_list()
        self.page.go("/sales_history")

    # レポートExcelファイル保存先パスの指定
    def event_report_excel_save_path(self, e):
        if e.path:
            # ファイルパスの取得
            save_file_path = Path(e.path)
            self.save_report_excel_file(save_file_path)
        else:
            print("Notice: Excelファイル保存がキャンセルされました")

    # View内のUIオブジェクト定義
    # Note: 他のメソッドやイベントから呼び出されるものはselfつきで宣言
    def define_view_components(self):
        # DatePickerの定義
        picker_zine_event_date = ft.DatePicker(
            first_date=datetime(year=2025, month=1, day=1),
            on_change=self.event_change_zine_event_date
        )

        # FilePickerの定義
        # Note: appendによるpage/viewへの追加がないとエラー発生
        dialog_select_report_excel_save_path = ft.FilePicker(
            on_result=self.event_report_excel_save_path)
        self.controls.append(dialog_select_report_excel_save_path)

        # イベント情報入力部分の定義
        self.text_field_zine_event_name = ft.TextField(
            label="イベント名", width=300)
        self.text_field_zine_event_desc = ft.TextField(
            label="イベント説明", width=650, multiline=True, min_lines=2)
        self.text_field_zine_event_date = ft.TextField(
            label="開催日", value="----/--/--", width=200, read_only=True)
        button_zine_event_date = ft.ElevatedButton(
            "日付選択",
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=lambda e: self.page.open(picker_zine_event_date)
        )

        # 商品および頒布数情報部分の定義
        self.checkbox_product_enable_list = [
            ft.Checkbox(value=False, data=i,
                        on_change=self.event_toggle_checkbox_product)
            for i in range(PRODUCT_COUNT_LIMIT)
        ]

        self.dropdown_product_type_list = [
            ft.Dropdown(
                label=f"商品種別",
                width=180, disabled=True,
                options=[ft.DropdownOption(x) for x in PRODUCT_NAME_LIST]
            ) for _ in range(PRODUCT_COUNT_LIMIT)
        ]

        self.text_field_product_list = [
            ft.TextField(label=f"商品名({i+1})",
                         width=350, disabled=True)
            for i in range(PRODUCT_COUNT_LIMIT)
        ]
        self.text_field_price_list = [
            ft.TextField(
                label=f"頒布価格({i+1})", value="0",
                width=120, disabled=True,
                input_filter=NumbersOnlyInputFilter())
            for i in range(PRODUCT_COUNT_LIMIT)
        ]
        self.text_field_count_list = [
            ft.TextField(label=f"頒布数({i+1})", value="0",
                         width=120,  read_only=True, disabled=True)
            for i in range(PRODUCT_COUNT_LIMIT)
        ]

        self.icon_button_minus_list = [
            ft.IconButton(ft.Icons.REMOVE, data=i, disabled=True,
                          on_click=lambda e: self.event_count_minus(e))
            for i in range(PRODUCT_COUNT_LIMIT)
        ]
        self.icon_button_plus_list = [
            ft.IconButton(ft.Icons.ADD, data=i, disabled=True,
                          on_click=lambda e: self.event_count_plus(e))
            for i in range(PRODUCT_COUNT_LIMIT)
        ]

        self.switch_product_lock_list = [
            ft.Switch(label="編集ロック", data=i, disabled=True,
                      on_change=self.event_switch_product_lock)
            for i in range(PRODUCT_COUNT_LIMIT)
        ]

        # 各種操作ボタン
        button_go_sales_history = ft.CupertinoFilledButton(
            "頒布履歴の確認",
            on_click=lambda _: self.event_click_go_sales_history()
        )
        button_save_report_excel = ft.CupertinoFilledButton(
            "集計レポートExcelの保存",
            on_click=lambda _: dialog_select_report_excel_save_path.save_file(
                "集計レポートExcel保存先の指定",
                allowed_extensions=["xlsx"],
                initial_directory=str(Path.home() / "Downloads"),
            )
        )

        # 表示間隔調整用のDivider定義
        row_spacer_small = ft.Row(controls=[ft.Divider(height=5)])
        row_spacer_large = ft.Row(controls=[ft.Divider(height=10)])
        col_spacer = ft.VerticalDivider(width=40)

        # イベント情報入力部分の作成
        row_zine_event_header = ft.Row(controls=[ft.Text("イベント情報", size=20)])
        row_zine_event_name = ft.Row(controls=[
            self.text_field_zine_event_name,
            self.text_field_zine_event_date,
            button_zine_event_date
        ])
        row_zine_event_desc = ft.Row(controls=[self.text_field_zine_event_desc])

        # Viewに対する行の追加
        self.controls.extend([
            row_zine_event_header,
            row_spacer_small,
            row_zine_event_name,
            row_zine_event_desc,
            row_spacer_large
        ])

        # 頒布商品入力部分の作成
        # ヘッダ行の追加
        product_header_row = ft.Row(controls=[ft.Text("商品一覧", size=20)])
        self.controls.append(product_header_row)

        # 商品カウント用の行データ作成
        for i in range(PRODUCT_COUNT_LIMIT):
            row_product = ft.Row(controls=[
                self.checkbox_product_enable_list[i],
                self.dropdown_product_type_list[i],
                self.text_field_product_list[i],
                self.text_field_price_list[i],
                self.switch_product_lock_list[i],
                col_spacer,
                self.icon_button_minus_list[i],
                self.text_field_count_list[i],
                self.icon_button_plus_list[i]
            ])
            self.controls.extend([row_spacer_small, row_product])

        # 履歴確認・レポート出力ボタンの追加
        row_ops_buttons = ft.Row(controls=[
            button_go_sales_history, button_save_report_excel])
        self.controls.extend([row_spacer_large, row_ops_buttons])
