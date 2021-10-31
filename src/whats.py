#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modules
from os import remove
from sys import argv

# Verify installed modules
try:
    # noinspection PyUnresolvedReferences
    from PyQt5.QtGui import QIcon, QDesktopServices
    # noinspection PyUnresolvedReferences
    from PyQt5.QtCore import QUrl, QFileInfo, pyqtSlot, QMargins, Qt, QEvent
    # noinspection PyUnresolvedReferences
    from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QSystemTrayIcon, QMenu, QAction
except ImportError as msg:
    from logging import error
    exit(error('%s. Please install PyQt5 and QtWebEngine.', msg))

# Verify installed QtWebEngine module
try:
    # noinspection PyUnresolvedReferences
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineDownloadItem
except ImportError:
    from warning import WarnDialog
    warn = QApplication(argv)
    msg = WarnDialog()
    msg.show()
    exit(warn.exec_())

# Import sources
from about import AboutDialog
from setting import SettingDialog
from warning import LinkDialog
from agent import user_agent
from utils import set_icon, run_map_link, run_exit_map_link, set_link, name_map_ext


# Class for application interface
# noinspection PyUnresolvedReferences
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Properties window
        self.setWindowTitle('Whats - WhatsApp Desktop')
        self.setWindowIcon(QIcon(set_icon()))
        self.setMinimumSize(800, 600)

        # View whatapp web page
        self.view = Browser()
        self.view.setPage(WhatsApp(self.view))
        self.view.titleChanged.connect(lambda: self.change_title(self.view.page().title()))
        self.view.load(QUrl("https://web.whatsapp.com"))
        # noinspection PyTypeChecker
        self.setCentralWidget(self.view)

        # Create system tray
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(set_icon('warning')))

        # Items for create menu in system tray
        self.trayHide = QAction('Hide', self)
        self.trayShow = QAction('Show', self)
        self.trayExit = QAction('Exit', self)

        # Add functions for options menu in system tray
        self.trayHide.triggered.connect(self.on_hide)
        self.trayShow.triggered.connect(self.on_show)
        self.trayExit.triggered.connect(self.exit_app)

        # Menu for system tray
        self.trayMenu = QMenu()
        self.trayMenu.addAction(self.trayHide)
        self.trayMenu.addAction(self.trayExit)
        self.tray.setContextMenu(self.trayMenu)
        self.tray.show()

    # Action for modify title
    def change_title(self, title):
        if title == 'WhatsApp Web':
            self.tray.setIcon(QIcon(set_icon('warning')))
        elif title == 'WhatsApp':
            self.tray.setIcon(QIcon(set_icon()))
        else:
            self.tray.setIcon(QIcon(set_icon('withmsg')))  # Found messages

    # Action case press hide
    def on_hide(self):
        self.hide()
        run_exit_map_link()

        # change attributes of system tray menu
        self.trayMenu.clear()
        self.trayMenu.addAction(self.trayShow)
        self.trayMenu.addAction(self.trayExit)

    # Action case press show
    def on_show(self):
        margin = QMargins(0, 0, 0, 1)  # Hack for hide a window and let it appear at the same position
        self.setGeometry(self.geometry() + margin)
        self.show()
        self.setGeometry(self.geometry() - margin)
        run_map_link()

        # change attributes of system tray menu
        self.trayMenu.clear()
        self.trayMenu.addAction(self.trayHide)
        self.trayMenu.addAction(self.trayExit)

    # Close applications
    @staticmethod
    def exit_app():
        run_exit_map_link()
        whats.quit()

    # Capture event when close window
    def closeEvent(self, event):
        event.ignore()
        self.on_hide()
        run_exit_map_link()

    # Monitore minimize event
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            # noinspection PyTypeChecker
            if self.windowState() & Qt.WindowMinimized:
                run_exit_map_link()
            else:
                run_exit_map_link()
                run_map_link()


# Class for custom browser
# noinspection PyUnresolvedReferences
class Browser(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Define items for create custom menu
        self.menuReload = QAction('Reload')
        self.menuExternal = QAction('External Link')
        self.menuConfig = QAction('Preferencies')
        self.menuAbout = QAction('About')

        # Add functions for options menu
        self.menuReload.triggered.connect(self.reload)
        self.menuExternal.triggered.connect(self.external_link)
        # self.menuConfig.triggered.connect(self.show_settings)
        self.menuAbout.triggered.connect(self.show_about)

    # View settings window
    @staticmethod
    def show_settings():
        sett = SettingDialog()
        sett.exec_()

    # View about message
    @staticmethod
    def show_about():
        about = AboutDialog()
        about.exec_()

    # Open select link in a external browser
    @staticmethod
    def external_link():
        url = set_link()
        if url is not None:
            remove(name_map_ext())
            QDesktopServices.openUrl(QUrl(url))
        else:
            no_link = LinkDialog()
            no_link.exec_()

    # Create custom menu
    def contextMenuEvent(self, event):
        # noinspection PyAttributeOutsideInit
        self.menu = QMenu()
        self.menu.addAction(self.menuReload)
        self.menu.addSeparator()
        self.menu.addAction(self.menuExternal)
        self.menu.addSeparator()
        self.menu.addAction(self.menuConfig)
        self.menu.addAction(self.menuAbout)
        self.menu.popup(event.globalPos())


# Class for whatsapp web page
class WhatsApp(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)
        self.profile().defaultProfile().setHttpUserAgent(user_agent())
        self.profile().downloadRequested.connect(self.download)
        self.featurePermissionRequested.connect(self.permission)

    # Function for download file
    @pyqtSlot(QWebEngineDownloadItem)
    def download(self, download):
        old_path = download.path()
        suffix = QFileInfo(old_path).suffix()
        path = QFileDialog.getSaveFileName(self.view(), "Save File", old_path, "*." + suffix)[0]
        if path:
            download.setPath(path)
            download.accept()

    def permission(self, frame, feature):
        self.setFeaturePermission(frame, feature, QWebEnginePage.PermissionGrantedByUser)


# Start application
if __name__ == '__main__':
    run_map_link()
    whats = QApplication(argv)
    main = MainWindow()
    main.showMaximized()
    whats.exec_()
