#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modules
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QTabWidget, QWidget, QGroupBox, QCheckBox,
                             QRadioButton, QSlider, QGridLayout, QLabel, QSpacerItem, QSizePolicy)

# Import sources
from jsonTools import set_json, write_json
from utils import set_desktop

########################################################################################################################


# Class for settings dialog
class SettingDialog(QDialog):
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
            if self.windowState() & Qt.WindowMinimized:
                self.showMaximized()


########################################################################################################################


# Class for general configurations
class GeneralTab(QWidget):
    def __init__(self, *args, **kwargs):
        super(GeneralTab, self).__init__(*args, **kwargs)

        # Groups for separate options
        confApp = QGroupBox('Application')
        startUp = QGroupBox('Startup')

        # General options for interface
        self.autoStart = QCheckBox('Auto start on login')
        self.showTray = QCheckBox('Show tray icon')

        # Define checkbox for auto start
        if set_json('AutoStart') == 'True':
            self.autoStart.setChecked(True)

        # Define checkbox for tray icon
        if set_json('TrayIcon') == 'True':
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
        if set_json('StartUp') == 'Default':
            self.showDefault.setChecked(True)
        elif set_json('StartUp') == 'Maximized':
            self.showMaximize.setChecked(True)
        elif set_json('StartUp') == 'Minimized':
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

    # ### Functions ####################################################################################################

    # Set options for auto start in settings.json
    def setAutoStart(self):
        if self.autoStart.isChecked():
            write_json('AutoStart', 'True')
        else:
            write_json('AutoStart', 'False')
        st = set_desktop()
        if not st:
            self.autoStart.setChecked(False)

    # Set options for system tray in settings.json
    def setTrayIcon(self):
        if self.showTray.isChecked():
            write_json('TrayIcon', 'True')
        else:
            write_json('TrayIcon', 'False')
            if self.showMinimize.isChecked():
                self.showDefault.setChecked(True)

    # Set options for startup in settings.json
    def radioButtonState(self, button):
        if button.text() == self.msg_show and self.showDefault.isChecked():
            write_json('StartUp', 'Default')
        if button.text() == self.msg_max and self.showMaximize.isChecked():
            write_json('StartUp', 'Maximized')
        if button.text() == self.msg_min and self.showMinimize.isChecked():
            write_json('StartUp', 'Minimized')
            self.showTray.setChecked(True)


########################################################################################################################


# Class for custom configurations
class CustomTab(QWidget):
    def __init__(self, win, *args, **kwargs):
        self.main = win  # For modify status bar

        super(CustomTab, self).__init__(*args, **kwargs)
        customInterface = QGroupBox('Interface')
        customFont = QGroupBox('Font')

        # Options for set font
        self.font = QLabel('Window Size Font: ' + str(set_json('SizeFont')))
        self.fontSlider = QSlider(Qt.Horizontal)
        self.fontSlider.setRange(8, 18)
        self.fontSlider.setValue(set_json('SizeFont'))
        self.fontSlider.setTickPosition(QSlider.TicksAbove)
        self.fontSlider.setTickInterval(1)

        # Options for Custom interface
        self.showStatus = QCheckBox('Show status bar')
        self.frameLabel = QLabel('Opacity:')
        self.frameSlider = QSlider(Qt.Horizontal)
        self.frameSlider.setRange(20, 100)
        self.frameSlider.setValue(set_json('Opacity'))
        self.frameSlider.setTickPosition(QSlider.TicksAbove)
        self.frameSlider.setTickInterval(5)

        if set_json('StatusBar') == 'True':
            self.showStatus.setChecked(True)

        # Functions for modify values
        self.showStatus.toggled.connect(self.setStatusBar)
        self.frameSlider.valueChanged.connect(self.setOpacity)
        self.fontSlider.valueChanged.connect(self.setSizeFont)

        # Create grid for a good organization
        customLayout = QGridLayout()
        customLayout.addWidget(self.showStatus, 0, 0, 1, 2)
        customLayout.addWidget(QLabel(''), 1, 0, 1, 2)
        customLayout.addWidget(self.frameLabel, 2, 0)
        customLayout.addWidget(self.frameSlider, 2, 1)
        customInterface.setLayout(customLayout)

        # Create layout for font
        fontLayout = QVBoxLayout()
        fontLayout.addWidget(self.font)
        fontLayout.addWidget(self.fontSlider)
        customFont.setLayout(fontLayout)

        # Create layout for tab
        layout = QVBoxLayout()
        layout.addWidget(customInterface)
        layout.addWidget(customFont)
        self.setLayout(layout)

    # ### Functions ####################################################################################################

    # Set options for status bar in settings.json
    def setStatusBar(self):
        if self.showStatus.isChecked():
            write_json('StatusBar', 'True')
            self.main.statusBar().show()
        else:
            write_json('StatusBar', 'False')
            self.main.statusBar().hide()

    # Set value for opacity in settings.json
    def setOpacity(self):
        write_json('Opacity', self.frameSlider.value())
        if set_json('Opacity') == 100:
            self.main.setWindowOpacity(1)
        else:
            str_num = '0.' + str(self.frameSlider.value())
            self.main.setWindowOpacity(float(str_num))

    # Modify size font and write in settings.json
    def setSizeFont(self):
        self.font.setText('Window Size Font: ' + str(self.fontSlider.value()))
        write_json('SizeFont', self.fontSlider.value())
        self.main.view.settings().globalSettings().setFontSize(QWebEngineSettings.MinimumFontSize,
                                                               int(set_json('SizeFont')))

########################################################################################################################


# Class for network configurations
class NetworkTab(QWidget):
    def __init__(self, *args, **kwargs):
        super(NetworkTab, self).__init__(*args, **kwargs)
        connect = QGroupBox('Connection')
        self.autoReload = QCheckBox('Reload automatically in case of connection fail')
        self.autoReload.toggled.connect(self.setAutoReload)

        if set_json('AutoReload') == 'True':
            self.autoReload.setChecked(True)

        # Define layout for network options
        startLayout = QVBoxLayout()
        startLayout.addWidget(self.autoReload)
        connect.setLayout(startLayout)

        # Create layout for tab
        layout = QVBoxLayout()
        layout.addWidget(connect)
        self.setLayout(layout)
        self.layout().addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Add a vertical spacer.

    # Set options for auto reload in settings.json
    def setAutoReload(self):
        if self.autoReload.isChecked():
            write_json('AutoReload', 'True')
        else:
            write_json('AutoReload', 'False')

########################################################################################################################
