import webview
from api import Api
api = Api()
window = webview.create_window(
    title="orm生成器",
    width=780,
    height=560,
    url="./web/index.html",
    js_api=api,
)
api._window = window
webview.start(icon="app.ico")