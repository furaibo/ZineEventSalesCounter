import flet as ft
from view_counter import ViewCounter
from view_sales_history import ViewSalesHistory


# main関数
def main(page: ft.Page):
    # ページ設定
    page.title = "頒布数・売上管理ツール"
    page.appbar = ft.AppBar(title=ft.Text("頒布数・売上管理ツール"))

    # ウィンドウサイズの指定
    page.window.width = 1200
    page.window.height = 1000

    # アプリ全体でのデータ保持用のdict
    app_data_dict = {}
    app_view_dict = {}

    # Window用イベント
    def window_on_event(e):
        # 閉じるボタンが押されたときの動作
        if e.data == "close":
            dialog = ft.AlertDialog(
                content=ft.Text("アプリを終了しますか？"),
                actions=[
                    ft.TextButton("Yes", on_click=lambda _: page.window.destroy()),
                    ft.TextButton("No", on_click=lambda _: page.close(dialog))
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER
            )
            page.open(dialog)

    # routeごとの分岐処理
    def route_change(route: str):
        if page.route == "/":
            root_view = page.views[0]
            page.views.clear()
            page.views.append(root_view)
        elif page.route == "/count":
            # Note: 入力済み情報が消去されないよう、作成済みのViewを再利用する
            if "count" in app_view_dict:
                view_counter = app_view_dict["count"]
                page.views.append(view_counter)
            else:
                view_counter = ViewCounter(app_data_dict)
                app_view_dict["count"] = view_counter
                page.views.append(view_counter)
        elif page.route == "/sales_history":
            history_data_list = app_data_dict["sales_history"]
            view_sales_history = ViewSalesHistory(history_data_list)
            page.views.append(view_sales_history)

        page.update()

    # Viewで戻るボタンを押した際の処理
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        view.page.go(top_view.route)

    # Windowクローズ時の処理
    # Note: xボタン押下は即時クローズせずに確認ウィンドウ表示
    page.window.prevent_close = True
    page.window.on_event = window_on_event

    # ルート変更時・戻る際のロジックを設定
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # トップのUI定義
    button_to_count = ft.Button(text="入力へ進む", on_click=lambda _: page.go("/count"))
    row_button_to_count = ft.Row(controls=[button_to_count])

    # pageへの追加
    page.controls.append(row_button_to_count)
    page.update()


# アプリの実行
if __name__ == "__main__":
    ft.app(target=main)

