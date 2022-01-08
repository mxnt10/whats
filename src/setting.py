# -*- coding: utf-8 -*-

# Módulos do PyQt5
from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QTabWidget, QWidget, QGroupBox, QCheckBox,
                             QRadioButton, QSlider, QGridLayout, QLabel, QSpacerItem, QSizePolicy, QToolTip, QSpinBox,
                             QComboBox)

# Modulos integrados (src)
from jsonTools import set_json, write_json
from utils import setDesktop, listSound

# Variáveis globais
enable_dark_mode_option = False

########################################################################################################################


# Classe para o painel de configurações
class SettingDialog(QDialog):
    # Definição dos sinais a serem emitidos
    statusbar_emit = pyqtSignal()
    font_emit = pyqtSignal()
    opacity_emit = pyqtSignal()
    tray_emit = pyqtSignal()

    def __init__(self):
        super(SettingDialog, self).__init__()

        # Propriedades gerais
        self.setWindowTitle('Settings')
        self.setFixedSize(0, 0)

        # Definindo a aba de configuração geral que vai receber os sinais
        generalTab = GeneralTab()
        generalTab.tray_emit.connect(self.tray_emit)

        # Definindo a aba de personalização que vai receber os sinais
        customTab = CustomTab()
        customTab.statusbar_emit.connect(self.statusbar_emit)
        customTab.font_emit.connect(self.font_emit)
        customTab.opacity_emit.connect(self.opacity_emit)

        # Widget para adicionar as abas
        tabWidget = QTabWidget()
        tabWidget.addTab(generalTab, 'General')
        tabWidget.addTab(customTab, 'Custom')
        tabWidget.addTab(NotifyTab(), 'Notify')
        tabWidget.addTab(NetworkTab(), 'Network')

        # Botão OK
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)

        # Criando o layout
        layout = QVBoxLayout()
        layout.addWidget(tabWidget)
        layout.addWidget(buttonBox)
        self.setLayout(layout)


    # Evento para impedir a minimização da janela.
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.showMaximized()


########################################################################################################################


# Classe para configurações gerais
class GeneralTab(QWidget):
    # Sinal a ser emitido
    tray_emit = pyqtSignal()

    def __init__(self):
        super(GeneralTab, self).__init__()

        # Grupos para separar as opções
        confApp = QGroupBox('Application')
        startUp = QGroupBox('Startup')

        # Opções gerais para interface
        self.autoStart = QCheckBox('Auto start on login')
        self.showTray = QCheckBox('Show tray icon')

        # Definir checkbox para autoinicialização
        if set_json('AutoStart'):
            self.autoStart.setChecked(True)

        # Definir checkbox para system tray
        if set_json('TrayIcon'):
            self.showTray.setChecked(True)

        # Messagens para os radio buttons
        self.msg_show = 'Standard startup'
        self.msg_max = 'Open maximized'
        self.msg_min = 'Open minimized to system tray'

        # Opções de inicialização
        self.showDefault = QRadioButton(self.msg_show)
        self.showMaximize = QRadioButton(self.msg_max)
        self.showMinimize = QRadioButton(self.msg_min)

        # definir seleção para inicialização
        if set_json('StartUp') == 'Normal':
            self.showDefault.setChecked(True)
        elif set_json('StartUp') == 'Maximized':
            self.showMaximize.setChecked(True)
        elif set_json('StartUp') == 'Minimized':
            self.showMinimize.setChecked(True)

        # Instructions for execute action with press a checkbox
        self.autoStart.toggled.connect(self.setAutoStart)
        self.showTray.toggled.connect(self.setTrayIcon)

        # Instruções para executar ações ao pressionar nos radio buttons
        self.showDefault.toggled.connect(lambda: self.radioButtonState(self.showDefault))
        self.showMaximize.toggled.connect(lambda: self.radioButtonState(self.showMaximize))
        self.showMinimize.toggled.connect(lambda: self.radioButtonState(self.showMinimize))

        # Layout para as opções gerais
        startLayout = QVBoxLayout()
        startLayout.addWidget(self.autoStart)
        startLayout.addWidget(self.showTray)
        confApp.setLayout(startLayout)

        # Layout para as opções de inicialização
        showLayout = QVBoxLayout()
        showLayout.addWidget(self.showDefault)
        showLayout.addWidget(self.showMaximize)
        showLayout.addWidget(self.showMinimize)
        startUp.setLayout(showLayout)

        # Layout geral
        layout = QVBoxLayout()
        layout.addWidget(confApp)
        layout.addWidget(startUp)
        layout.addItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Espaço por precaução
        self.setLayout(layout)


########################################################################################################################


    # Definindo opções para autoinicialização em 'settings.json'.
    def setAutoStart(self):
        if self.autoStart.isChecked():
            write_json('AutoStart', True)
        else:
            write_json('AutoStart', False)
        st = setDesktop()
        if not st:  # Prevenindo caso o arquivo desktop não exista
            self.autoStart.setChecked(False)


    # Alterando opções para o system tray em 'settings.json'.
    def setTrayIcon(self):
        if self.showTray.isChecked():
            write_json('TrayIcon', True)
        else:
            write_json('TrayIcon', False)
            if self.showMinimize.isChecked():
                self.showDefault.setChecked(True)
        self.tray_emit.emit()


    # Alterando opções para inicialização em 'settings.json'.
    def radioButtonState(self, button):
        if button.text() == self.msg_show and self.showDefault.isChecked():
            write_json('StartUp', 'Normal')
        if button.text() == self.msg_max and self.showMaximize.isChecked():
            write_json('StartUp', 'Maximized')
        if button.text() == self.msg_min and self.showMinimize.isChecked():
            write_json('StartUp', 'Minimized')
            self.showTray.setChecked(True)


########################################################################################################################


# Classe para exibir rapidamente uma mensagem para o modo dark.
class BoxToolTip(QCheckBox):
    def __init__(self, parent=None):
        super(BoxToolTip, self).__init__(parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        pos = self.mapToGlobal(event.pos())
        QToolTip.showText(pos, 'Dark mode will only have effect on next program startup')


# Classe para configurações de customização do programa.
class CustomTab(QWidget):
    # Definição dos sinais a serem emitidos
    statusbar_emit = pyqtSignal()
    font_emit = pyqtSignal()
    opacity_emit = pyqtSignal()

    def __init__(self):
        super(CustomTab, self).__init__()

        # Grupos para separar as opções
        customInterface = QGroupBox('Interface')
        customFont = QGroupBox('Font')

        # Opções para definir a fonte
        self.font = QLabel('Window Size Font: ' + str(set_json('SizeFont')))
        self.fontSlider = QSlider(Qt.Horizontal)
        self.fontSlider.setRange(6, 20)
        self.fontSlider.setValue(set_json('SizeFont'))
        self.fontSlider.setTickPosition(QSlider.TicksAbove)
        self.fontSlider.setTickInterval(1)

        # Opções para customizar a interface
        self.showStatus = QCheckBox('Show status bar')
        self.darkMode = BoxToolTip('Dark mode')
        self.darkMode.setFixedWidth(160)
        self.frameLabel = QLabel('Opacity:')
        self.frameSlider = QSlider(Qt.Horizontal)
        self.frameSlider.setRange(20, 100)
        self.frameSlider.setValue(set_json('Opacity'))
        self.frameSlider.setTickPosition(QSlider.TicksAbove)
        self.frameSlider.setTickInterval(5)

        # Verificando se o statusbar está ativo
        if set_json('StatusBar'):
            self.showStatus.setChecked(True)

        # Verificando se o modo dark está ativo
        if set_json('DarkMode'):
            self.darkMode.setChecked(True)

        # Instruções para modificação dos valores
        self.showStatus.toggled.connect(self.setStatusBar)
        self.darkMode.toggled.connect(self.setDarkMode)
        self.frameSlider.valueChanged.connect(self.setOpacity)
        self.fontSlider.valueChanged.connect(self.setSizeFont)

        # usando grid para uma melhor organização
        customLayout = QGridLayout()
        customLayout.addWidget(self.showStatus, 0, 0, 1, 2)
        customLayout.addWidget(self.darkMode, 1, 0, 1, 2)
        customLayout.addWidget(QLabel(''), 2, 0, 1, 2)
        customLayout.addWidget(self.frameLabel, 3, 0)
        customLayout.addWidget(self.frameSlider, 3, 1)
        customInterface.setLayout(customLayout)

        # Não são todos os webapps que precisam do modo dark
        if not enable_dark_mode_option:
            self.darkMode.hide()

        # Layout para fonte
        fontLayout = QVBoxLayout()
        fontLayout.addWidget(self.font)
        fontLayout.addWidget(self.fontSlider)
        customFont.setLayout(fontLayout)

        # Layout geral
        layout = QVBoxLayout()
        layout.addWidget(customInterface)
        layout.addWidget(customFont)
        layout.addItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Espaço por precaução
        self.setLayout(layout)


########################################################################################################################


    # Definindo opções para o statusbar em 'settings.json'.
    def setStatusBar(self):
        if self.showStatus.isChecked():
            write_json('StatusBar', True)
        else:
            write_json('StatusBar', False)
        self.statusbar_emit.emit()


    # Alterar as opções do modo dark em 'settings.json'.
    def setDarkMode(self):
        if self.darkMode.isChecked():
            write_json('DarkMode', True)
        else:
            write_json('DarkMode', False)


    # Alteração dos valores para opacidade em 'settings.json'.
    def setOpacity(self):
        write_json('Opacity', self.frameSlider.value())
        self.opacity_emit.emit()


    # Alterar valores da fonte em 'settings.json'.
    def setSizeFont(self):
        self.font.setText('Size Font: ' + str(self.fontSlider.value()))
        write_json('SizeFont', self.fontSlider.value())
        self.font_emit.emit()


########################################################################################################################


# Classe para configuração de opções para mensagens de notificação.
class NotifyTab(QWidget):
    def __init__(self):
        super(NotifyTab, self).__init__()

        # Grupos para separar as opções
        messageNotify = QGroupBox('Message options')
        soundNotify = QGroupBox('Sound options')

        # Opções para opções de notificação
        self.optionMessage = QCheckBox('View notification messages')
        self.optionSound = QCheckBox('Emit notification sounds')

        # Tempo de exibição de notificação
        self.timeMessage = QSpinBox()
        self.timeMessage.setFixedWidth(60)
        self.timeMessage.setMinimum(2)
        self.timeMessage.setMaximum(15)
        self.timeMessage.setValue(set_json('TimeMessage') / 1000)
        self.timeMessage.valueChanged.connect(lambda: write_json('TimeMessage', self.timeMessage.value() * 1000))
        labelMessage = QLabel('Showtime (s):')
        labelMessage.setAlignment(Qt.AlignRight)

        # Temas para o som de notificação
        self.soundTheme = QComboBox()
        labelSound = QLabel('Sound Theme:')
        labelSound.setAlignment(Qt.AlignRight)
        self.soundTheme.addItems(listSound())
        self.soundTheme.setCurrentIndex(listSound().index(set_json('SoundTheme')))
        self.soundTheme.currentIndexChanged.connect(lambda: write_json('SoundTheme', self.soundTheme.currentText()))

        # Verificando se o statusbar está ativo
        if set_json('NotifyMessage'):
            self.optionMessage.setChecked(True)

        # Verificando se o modo dark está ativo
        if set_json('NotifySound'):
            self.optionSound.setChecked(True)

        # Instruções para modificação dos valores
        self.optionMessage.toggled.connect(self.setNotifyMessage)
        self.optionSound.toggled.connect(self.setNotifySound)

        # Definindo o layout para opções de mensagem
        messageLayout = QGridLayout()
        messageLayout.addWidget(self.optionMessage, 0, 0, 1, 5)
        messageLayout.addWidget(labelMessage, 1, 0)
        messageLayout.addWidget(self.timeMessage, 1, 1)
        messageNotify.setLayout(messageLayout)

        # Definindo o layout para opções de som
        soundLayout = QGridLayout()
        soundLayout.addWidget(self.optionSound, 0, 0, 1, 4)
        soundLayout.addWidget(labelSound, 1, 0)
        soundLayout.addWidget(self.soundTheme, 1, 1)
        soundNotify.setLayout(soundLayout)

        # Criando o layout
        layout = QVBoxLayout()
        layout.addWidget(messageNotify)
        layout.addWidget(soundNotify)
        layout.addItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Espaço por precaução
        self.setLayout(layout)


########################################################################################################################


    # Alterando as opções de mensagens de notificação em 'settings.json'.
    def setNotifyMessage(self):
        if self.optionMessage.isChecked():
            write_json('NotifyMessage', True)
        else:
            write_json('NotifyMessage', False)


    # Alterando as opções de som de notificação em 'settings.json'.
    def setNotifySound(self):
        if self.optionSound.isChecked():
            write_json('NotifySound', True)
        else:
            write_json('NotifySound', False)


########################################################################################################################


# Classe para configuração de opções para conexão a internet.
class NetworkTab(QWidget):
    def __init__(self):
        super(NetworkTab, self).__init__()

        # Opção de autorreconexão
        connect = QGroupBox('Connection')
        update = QGroupBox('Update')
        self.autoReload = QCheckBox('Reload automatically in case of connection fail')
        self.autoReload.toggled.connect(self.setAutoReload)
        self.checkUpdate = QCheckBox('Check updates on startup')
        self.checkUpdate.toggled.connect(self.setCheckUpdate)

        # Definindo opções para o tempo de reconexão
        self.timeReload = QSpinBox()
        self.timeReload.setFixedWidth(60)
        self.timeReload.setMinimum(2)
        self.timeReload.setMaximum(15)
        self.timeReload.setValue(set_json('TimeReload') / 1000)
        self.timeReload.valueChanged.connect(lambda: write_json('TimeReload', self.timeReload.value() * 1000))
        labelReoad = QLabel('Time interval when reloading (s):')
        labelReoad.setAlignment(Qt.AlignRight)

        # Definindo layout para checagem de atualização
        self.layoutUpdate = QVBoxLayout()
        self.layoutUpdate.addWidget(self.checkUpdate)
        update.setLayout(self.layoutUpdate)

        # Verificando se a opção autoreload está ativa para setar o check box
        if set_json('AutoReload'):
            self.autoReload.setChecked(True)

        # Definindo o layout de reconexão
        startLayout = QGridLayout()
        startLayout.addWidget(self.autoReload, 0, 0, 1, 3)
        startLayout.addWidget(QLabel(''), 1, 0, 1, 2)
        startLayout.addWidget(labelReoad, 2, 0)
        startLayout.addWidget(self.timeReload, 2, 1)
        connect.setLayout(startLayout)

        # Criando o layout
        layout = QVBoxLayout()
        layout.addWidget(connect)
        layout.addWidget(update)
        layout.addItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Espaço por precaução
        self.setLayout(layout)


    # Definindo opção para autoreconexão em 'settings.json'.
    def setAutoReload(self):
        if self.autoReload.isChecked():
            write_json('AutoReload', True)
        else:
            write_json('AutoReload', False)


    # Definindo opção para checagem de atualização em 'settings.json'.
    def setCheckUpdate(self):
        if self.checkUpdate.isChecked():
            write_json('CheckUpdate', True)
        else:
            write_json('CheckUpdate', False)
