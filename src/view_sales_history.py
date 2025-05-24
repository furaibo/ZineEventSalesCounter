import flet as ft


# 頒布履歴表示用Viewの取得
class ViewSalesHistory(ft.View):
    # イニシャライザ定義
    def __init__(self, data_list: list):
        super().__init__()
        self.appbar = ft.AppBar(title=ft.Text("頒布履歴"))
        self.data_list = data_list
        self.define_view_components()

    # View内のUIオブジェクト定義
    # Note: 他のメソッドやイベントから呼び出されるものはselfつきで宣言
    def define_view_components(self):
        # DataTableの定義
        sales_history_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("商品名")),
                ft.DataColumn(ft.Text("頒布価格")),
                ft.DataColumn(ft.Text("頒布日時")),
            ]
        )

        for index, data in enumerate(self.data_list):
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(data["product"])),
                    ft.DataCell(ft.Text(f"￥{data["price"]:,}")),
                    ft.DataCell(ft.Text(data["sales_at"]))
                ],
            )
            sales_history_table.rows.append(row)

        # ListViewの設定
        list_view = ft.ListView(
            controls=[sales_history_table], width=900, height=700)

        # Viewに対する行の追加
        row_spacer = ft.Row(controls=[ft.Divider(height=5)])
        row_list_view = ft.Row(controls=[list_view])
        self.controls.append(row_spacer)
        self.controls.append(row_list_view)
