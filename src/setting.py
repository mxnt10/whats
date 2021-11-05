#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modules
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QTabWidget, QWidget, QGroupBox, QCheckBox,
                             QRadioButton, QSlider, QGridLayout, QLabel)

# Import sources
import jsonTools as j
from utils import set_desktop

########################################################################################################################


# Class for settings dialog
class SettingDialog(QDialog):
    # noinspection PyUnresolvedReferences
    def __init__(self, win, *args, **kwargs):
        self.main = win  # For modify status bar

        super(SettingDialog, self).__init__(*args, **kwargs)

        # Properties window
        self.setWindowTitle('Settings')
        self.setFixedSize(0, 0)

        # Widgets for add tabs
        tabWidget = QTabWidget()
        tabWidget.addTab(GeneralTab(), 'General')
        tabWidget.addTab(CustomTab(self.main), 'Custom')
        tabWidget.addTab(NetworkTab(), 'Network')

        # Define button OK
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)

        # Create layout
        layout = QVBoxLayout()
        layout.addWidget(tabWidget)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    # Capture event on minimize
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            # noinspection PyTypeChecker
            if self.windowState() & Qt.WindowMinimized:
                self.showMaximized()


########################################################################################################################


# Class for general configurations
class GeneralTab(QWidget):
    # noinspection PyUnresolvedReferences
    def __init__(self, *args, **kwargs):
        super(GeneralTab, self).__init__(*args, **kwargs)

        # Groups for separate options
        confApp = QGroupBox('Application')
        startUp = QGroupBox('Startup')

        # General options for interface
        self.autoStart = QCheckBox('Auto start on login')
        self.showTray = QCheckBox('Show tray icon')

        # Define checkbox for auto start
        if j.set_json('AutoStart') == 'True':
            self.autoStart.setChecked(True)

        # Define checkbox for tray icon
        if j.set_json('TrayIcon') == 'True':
            self.showTray.setChecked(True)

        # Messages for raio buttons
        self.msg_show = 'Standard startup'
        self.msg_max = 'Open maximized'
        self.msg_min = 'Open minimized to system tray'

        # StartUp options
        self.showDefault = QRadioButton(self.msg_show)
        self.showMaximize = QRadioButton(self.msg_max)
        self.showMinimize = QRadioButton(self.msg_min)

        # Define selection for startup
        if j.set_json('StartUp') == 'Default':
            self.showDefault.setChecked(True)
        elif j.set_json('StartUp') == 'Maximized':
            self.showMaximize.setChecked(True)
        elif j.set_json('StartUp') == 'Minimized':
            self.showMinimize.setChecked(True)

        # Instructions for execute action with press a checkbox
        self.autoStart.toggled.connect(self.setAutoStart)
        self.showTray.toggled.connect(self.setTrayIcon)

        # Instructions for execute action with press a radio button
        self.showDefault.toggled.connect(lambda: self.radioButtonState(self.showDefault))
        self.showMaximize.toggled.connect(lambda: self.radioButtonState(self.showMaximize))
        self.showMinimize.toggled.connect(lambda: self.radioButtonState(self.showMinimize))

        # Set layout for general options
        startLayout = QVBoxLayout()
        startLayout.addWidget(self.autoStart)
        startLayout.addWidget(self.showTray)
        confApp.setLayout(startLayout)

        # Set layout for startup options
        showLayout = QVBoxLayout()
        showLayout.addWidget(self.showDefault)
        showLayout.addWidget(self.showMaximize)
        showLayout.addWidget(self.showMinimize)
        startUp.setLayout(showLayout)

        # Create layout for tab
        layout = QVBoxLayout()
        layout.addWidget(confApp)
        layout.addWidget(startUp)
        self.setLayout(layout)

    # Set options for auto start in settings.json
    def setAutoStart(self):
        if self.autoStart.isChecked():
            j.write_json('AutoStart', 'True')
        else:
            j.write_json('AutoStart', 'False')
        st = set_desktop()
        if not st:
            self.autoStart.setChecked(False)

    # Set options for system tray in settings.json
    def setTrayIcon(self):
        if self.showTray.isChecked():
            j.write_json('TrayIcon', 'True')
        else:
            j.write_json('TrayIcon', 'False')
            if self.showMinimize.isChecked():
                self.showDefault.setChecked(True)

    # Set options for startup in settings.json
    def radioButtonState(self, button):
        if button.text() == self.msg_show and self.showDefault.isChecked():
            j.write_json('StartUp', 'Default')
        if button.text() == self.msg_max and self.showMaximize.isChecked():
            j.write_json('StartUp', 'Maximized')
        if button.text() == self.msg_min and self.showMinimize.isChecked():
            j.write_json('StartUp', 'Minimized')
            self.showTray.setChecked(True)


########################################################################################################################


# Class for custom configurations
class CustomTab(QWidget):
    def __init__(self, win, *args, **kwargs):
        self.main = win  # For modify status bar

        super(CustomTab, self).__init__(*args, **kwargs)
        customInterface = QGroupBox('Interface')

        # Options for Custom interface
        self.showStatus = QCheckBox('Show status bar')
        frameLabel = QLabel('Opacity:')
        frameSlider = QSlider(Qt.Horizontal)
        frameSlider.setRange(20, 100)
        frameSlider.setValue(int(j.set_json('Opacity')))

        if j.set_json('StatusBar') == 'True':
            self.showStatus.setChecked(True)

        # noinspection PyUnresolvedReferences
        self.showStatus.toggled.connect(self.setStatusBar)

        # Create grid for a good organization
        customLayout = QGridLayout()
        customLayout.addWidget(self.showStatus, 0, 0, 1, 2)
        customLayout.addWidget(frameLabel, 1, 0)
        customLayout.addWidget(frameSlider, 1, 1)
        customInterface.setLayout(customLayout)

        # Create layout for tab
        layout = QVBoxLayout()
        layout.addWidget(customInterface)
        self.setLayout(layout)

    # Set options for status bar in settings.json
    def setStatusBar(self):
        if self.showStatus.isChecked():
            j.write_json('StatusBar', 'True')
            self.main.statusBar().show()
        else:
            j.write_json('StatusBar', 'False')
            self.main.statusBar().hide()


########################################################################################################################


# Class for network configurations
class NetworkTab(QWidget):
    def __init__(self, *args, **kwargs):
        super(NetworkTab, self).__init__(*args, **kwargs)
        connect = QGroupBox('Connection')
        self.autoReload = QCheckBox('Reload automatically in case of connection fail')

        if j.set_json('AutoReload') == 'True':
            self.autoReload.setChecked(True)

        # Define layout for network options
        startLayout = QVBoxLayout()
        startLayout.addWidget(self.autoReload)
        connect.setLayout(startLayout)

        # noinspection PyUnresolvedReferences
        self.autoReload.toggled.connect(self.setAutoReload)

        # Create layout for tab
        layout = QVBoxLayout()
        layout.addWidget(connect)
        self.setLayout(layout)

    # Set options for auto reload in settings.json
    def setAutoReload(self):
        if self.autoReload.isChecked():
            j.write_json('AutoReload', 'True')
        else:
            j.write_json('AutoReload', 'False')

########################################################################################################################
