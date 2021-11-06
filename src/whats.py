#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modules
from os.path import isfile
from time import sleep
from sys import argv

########################################################################################################################

# Verify installed modules
try:
    # noinspection PyUnresolvedReferences
    from PyQt5.QtGui import QIcon, QDesktopServices, QFont
    # noinspection PyUnresolvedReferences
    from PyQt5.QtCore import QUrl, QFileInfo, pyqtSlot, QMargins, Qt, QEvent
    # noinspection PyUnresolvedReferences
    from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QSystemTrayIcon, QMenu, QAction
except ImportError as msg:
    from logging import error
    exit(error('%s. Please install PyQt5 and QtWebEngine.', msg))

########################################################################################################################

# Verify installed QtWebEngine module
try:
    # noinspection PyUnresolvedReferences
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineDownloadItem, QWebEngineSettings
except ImportError:
    from warning import WarnDialog
    warn = QApplication(argv)
    msg = WarnDialog()
    msg.show()
    exit(warn.exec_())

########################################################################################################################

# Import sources
from about import AboutDialog
from setting import SettingDialog
from agent import user_agent
from utils import set_icon, desk
import jsonTools as j

########################################################################################################################


# Global variables
capture_url = None
w_url = 'https://web.whatsapp.com/'


# Verify manual change in auto start
if isfile(desk) and j.set_json('AutoStart') == 'False':
    j.write_json('AutoStart', 'True')
elif not isfile(desk) and j.set_json('AutoStart') == 'True':
    j.write_json('AutoStart', 'False')


# Class for application interface
class MainWindow(QMainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self):
        super(MainWindow, self).__init__()
        self.start = 0

        # Properties window
        self.setWindowTitle('Whats - WhatsApp Desktop')
        self.setWindowIcon(QIcon(set_icon()))
        self.setMinimumSize(800, 600)

        # View whatapp web page
        self.view = Browser(self)
        self.view.setPage(WhatsApp(self.view))
        self.view.page().linkHovered.connect(self.link_hovered)
        self.view.load(QUrl(w_url))
        self.setCentralWidget(self.view)

        # Define first value for size font
        if j.set_json('SizeFont') == 'Default':
            j.write_json('SizeFont', float(str(self.font().key()).split(',')[1]))

        # Settings for active options
        self.view.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.view.settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)
        self.view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.view.settings().globalSettings().setFontSize(QWebEngineSettings.MinimumFontSize,
                                                          int(j.set_json('SizeFont')))

        # Define opacity options
        if j.set_json('Opacity') != 100:
            str_num = '0.' + str(j.set_json('Opacity'))
            self.setWindowOpacity(float(str_num))

        # Create status bar
        if j.set_json('StatusBar') == 'True':
            self.statusBar().show()

        # Active icon on system tray
        if j.set_json('TrayIcon') == 'True':
            self.view.titleChanged.connect(lambda: self.change_title(self.view.page().title()))

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
            self.trayExit.triggered.connect(whats.quit)

            # Menu for system tray
            self.trayMenu = QMenu()
            self.trayMenu.addAction(self.trayHide)
            self.trayMenu.addAction(self.trayExit)
            self.tray.setContextMenu(self.trayMenu)
            self.tray.show()

            # Options for show window por start minimized on tray
            if j.set_json('StartUp') == 'Minimized':
                self.trayMenu.clear()
                self.trayMenu.addAction(self.trayShow)
                self.trayMenu.addAction(self.trayExit)

    # ### Functions ####################################################################################################

    # Show links mouse hover and capture link
    def link_hovered(self, link):
        if j.set_json('StatusBar') == 'True':
            self.statusBar().showMessage(link)
        global capture_url
        capture_url = link

    # Action for modify title
    def change_title(self, title):
        if title == 'web.whatsapp.com':
            self.tray.setIcon(QIcon(set_icon('error')))
            if j.set_json('AutoReload') == 'True':  # Auto reconnect
                self.view.setUrl(QUrl(w_url))
                sleep(1)
        elif title == 'WhatsApp Web':
            self.tray.setIcon(QIcon(set_icon('warning')))
        elif title == 'WhatsApp':
            self.tray.setIcon(QIcon(set_icon('original')))
        else:
            self.tray.setIcon(QIcon(set_icon('withmsg')))  # Found messages

    # Action case press hide
    def on_hide(self):
        self.hide()

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

        # Show maximized when start minimized to tray
        if self.start == 0 and j.set_json('StartUp') == 'Minimized':
            self.showMaximized()
            self.start = 1

        # change attributes of system tray menu
        self.trayMenu.clear()
        self.trayMenu.addAction(self.trayHide)
        self.trayMenu.addAction(self.trayExit)

    # Capture event when close window
    def closeEvent(self, event):
        event.ignore()

        # Tray icon verification
        if j.set_json('TrayIcon') == 'True':
            self.on_hide()
        else:
            whats.quit()


########################################################################################################################


# Class for custom browser
# noinspection PyUnresolvedReferences
class Browser(QWebEngineView):
    def __init__(self, win, *args, **kwargs):
        self.main = win      # For modify status bar
        self.menu = QMenu()  # For create context menu

        super().__init__(*args, **kwargs)
        self.save_url = None

        # Necessary to map mouse event
        QApplication.instance().installEventFilter(self)
        self.setMouseTracking(True)

        # Define items for create custom menu
        self.menuExternal = QAction('Open link in the browser')
        self.menuLinkClip = QAction('Copy link to clipboard')
        self.menuReload = QAction('Reload')
        self.menuConfig = QAction('Preferencies')
        self.menuAbout = QAction('About')

        # Add functions for options menu
        self.menuExternal.triggered.connect(self.external_browser)
        self.menuLinkClip.triggered.connect(lambda: clipboard.setText(self.save_url, mode=clipboard.Clipboard))
        self.menuReload.triggered.connect(lambda: self.setUrl(QUrl(w_url)))  # Good reload method
        self.menuConfig.triggered.connect(self.show_settings)
        self.menuAbout.triggered.connect(self.show_about)

    # ### Functions ####################################################################################################

    # View settings window
    def show_settings(self):
        sett = SettingDialog(self.main)
        sett.exec_()

    # View about message
    @staticmethod
    def show_about():
        about = AboutDialog()
        about.exec_()

    # Open select link in a external browser
    def external_browser(self):
        global capture_url
        if not capture_url:  # For press right button
            capture_url = self.save_url

        if capture_url:
            QDesktopServices.openUrl(QUrl(capture_url))
        capture_url = None

    # Create custom menu
    def contextMenuEvent(self, event):
        global capture_url
        if capture_url:  # Menu for link mouse hover
            self.menu.addAction(self.menuExternal)
            self.menu.addAction(self.menuLinkClip)
        else:
            self.menu.addAction(self.menuReload)
            self.menu.addSeparator()
            self.menu.addAction(self.menuConfig)
            self.menu.addAction(self.menuAbout)
        self.menu.popup(event.globalPos())

    # Execute event on click mouse
    def mousePressEvent(self, event):
        global capture_url
        if event.button() == Qt.LeftButton:  # Left button is clicked
            if capture_url:
                self.external_browser()
        if event.button() == Qt.RightButton:  # Right button is clicked
            self.save_url = capture_url

    def eventFilter(self, obj, event):
        if obj.parent() == self:
            if event.type() == QEvent.MouseButtonPress:
                self.mousePressEvent(event)
        return False


########################################################################################################################


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


########################################################################################################################


# Start application
if __name__ == '__main__':
    whats = QApplication(argv)
    clipboard = whats.clipboard()
    main = MainWindow()
    if j.set_json('StartUp') == 'Default':
        main.show()
    elif j.set_json('StartUp') == 'Maximized':
        main.showMaximized()
    elif j.set_json('StartUp') == 'Minimized':
        main.hide()
    whats.exec_()

########################################################################################################################
