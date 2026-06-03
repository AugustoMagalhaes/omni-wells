import sys
import threading
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow

from hi_lo_wells.app import _find_free_port, app


def run_flask(port: int):
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def handle_download(download: QWebEngineDownloadRequest, view: QWebEngineView):
    import json

    suggested = download.suggestedFileName()
    path, _ = QFileDialog.getSaveFileName(None, "Save file", suggested)
    if path:
        download.setDownloadDirectory(str(Path(path).parent))
        download.setDownloadFileName(Path(path).name)
        download.accept()
        download.isFinishedChanged.connect(
            lambda: view.page().runJavaScript(
                f"showToast({json.dumps('✓ Saved as ' + Path(path).name)})"
            )
        )
    else:
        download.cancel()


def main():
    port = _find_free_port()

    flask_thread = threading.Thread(target=run_flask, args=[port], daemon=True)
    flask_thread.start()

    qt_app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("hi-lo-wells")
    window.resize(1280, 800)

    view = QWebEngineView()
    view.page().profile().downloadRequested.connect(
        lambda dl: handle_download(dl, view)
    )
    view.setUrl(QUrl(f"http://127.0.0.1:{port}"))
    window.setCentralWidget(view)
    window.show()

    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
