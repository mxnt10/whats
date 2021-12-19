#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Módulos importados
from bs4 import BeautifulSoup  # pip install beautifulsoup4
from logging import warning
from os.path import isfile, expanduser, realpath
from subprocess import run
from sys import argv

# Módulos do PyQt5
from PyQt5.QtCore import QUrl, QFileInfo, pyqtSlot, QMargins, Qt, QEvent, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineDownloadItem, QWebEngineSettings
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QSystemTrayIcon, QMenu, QAction

# Modulos integrados (src)
from about import AboutDialog
from agent import user_agent, prevent
from jsonTools import checkSettings, set_json, write_json
from setting import SettingDialog
from utils import set_icon, setSound
from version import __appname__, __pagename__, __url__, __desktop__, __err__

# Variáveis globais
cap_url = None
desk = expanduser('~/.config/autostart/' + __desktop__)
force_open_link = True


########################################################################################################################


# Classe para a interface principal.
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.start = self.notify_start = self.reload_start = False
        self.notify = self.changeTray = self.soma = 0

        # Pega o tamanho da fonte na primeira inicialização
        if set_json('SizeFont') is None:
            write_json('SizeFont', float(str(self.font().key()).split(',')[1]))

        # Definindo o som de notificação
        self.notify_sound = QMediaPlayer()
        self.notify_sound.setMedia(QMediaContent(QUrl.fromLocalFile(setSound(set_json('SoundTheme')))))

        # Loop para a verificação de novas mensagens
        self.notify_loop = QTimer()
        self.notify_loop.setInterval(set_json('VerifyNotify'))
        self.notify_loop.timeout.connect(lambda: self.view.page().toHtml(self.processHtml))

        # Loop para a autorreconexão
        self.reload = QTimer()
        self.reload.setInterval(set_json('TimeReload'))
        self.reload.timeout.connect(lambda: self.view.setUrl(QUrl(__url__)))

        # Propriedades gerais
        self.setWindowTitle(__pagename__)
        self.setWindowIcon(QIcon(set_icon()))
        self.setMinimumSize(800, 600)

        # Definições para a visualização da página do webapp
        self.view = Browser()
        self.view.statusbar_emit.connect(self.changeStatusBar)
        self.view.font_emit.connect(self.changeFont)
        self.view.opacity_emit.connect(self.changeOpacity)
        self.view.tray_emit.connect(self.changeTrayIcon)
        self.view.setPage(WhatsApp(self.view))
        self.view.page().linkHovered.connect(self.link_hovered)
        self.view.loadFinished.connect(self.loaded)
        self.view.load(QUrl(__url__))
        self.setCentralWidget(self.view)
        self.changeStatusBar()
        self.changeOpacity()
        self.changeFont()

        # Ativando tudo o que tiver de direito
        self.view.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.view.settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)
        self.view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

        # Criando o tray icon
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(set_icon('warning')))

        # Itens para o menu do tray icon
        self.trayHide = QAction('Hide', self)
        self.trayShow = QAction('Show', self)
        self.trayExit = QAction('Exit', self)

        # Funções para as opções do menu do tray icon
        self.trayHide.triggered.connect(self.on_hide)
        self.trayShow.triggered.connect(self.on_show)
        self.trayExit.triggered.connect(app.quit)

        # Menu para o tray icon
        self.trayMenu = QMenu()
        if set_json('StartUp') == 'Minimized':
            self.trayMenu.addAction(self.trayShow)
        else:
            self.trayMenu.addAction(self.trayHide)
        self.trayMenu.addAction(self.trayExit)
        self.tray.setContextMenu(self.trayMenu)
        self.changeTrayIcon()


########################################################################################################################


    # Definindo as opções do tray icon.
    def changeTrayIcon(self):
        if set_json('TrayIcon'):
            self.tray.show()
            if not self.notify_start:
                self.notify_loop.start()
        else:
            if self.tray.isVisible():
                self.tray.hide()


    # Definindo a opacidade da interface.
    def changeOpacity(self):
        if set_json('Opacity') == 100:
            self.setWindowOpacity(1)
        else:
            str_num = '0.' + str(set_json('Opacity'))
            self.setWindowOpacity(float(str_num))


    # Modificando o tamanho da fonte.
    def changeFont(self):
        self.view.settings().globalSettings().setFontSize(
            QWebEngineSettings.MinimumFontSize, int(set_json('SizeFont')))


    # Alterando visualização do statusbar.
    def changeStatusBar(self):
        if set_json('StatusBar'):
            self.statusBar().show()
        else:
            if not self.statusBar().isHidden():
                self.statusBar().hide()


    # Função que manipula o código-fonte do webapp para checar as mensagens não lidas, emitindo sons,
    # exibindo mensagens e alterando o ícone de notificação.
    def processHtml(self, html):
        self.soma = 0
        res = BeautifulSoup(html, 'html.parser')
        tags = res.findAll("div", {"class": "_1pJ9J"})

        for tag in tags:
            self.soma += int(tag.getText())
        if self.soma != self.notify and self.soma != 0:
            if self.isHidden() or int(self.windowState()) == 1 or int(self.windowState()) == 3:
                self.notify_sound.play()  # som de notificação
                self.notifyMessage()
            self.notify = self.soma  # Necessário para mapear alterações no número de mensagens
        try:
            if __err__ in res.title:  # Em caso de erro de conexão o título inicial não se altera
                if self.changeTray != 1:
                    self.tray.setIcon(QIcon(set_icon('error')))
                    self.changeTray = 1
            elif self.soma > 0:
                if self.changeTray != 2:
                    self.tray.setIcon(QIcon(set_icon('withmsg')))
                    self.changeTray = 2
            else:
                if self.changeTray != 3:
                    self.tray.setIcon(QIcon(set_icon('original')))
                    self.changeTray = 3
        except Exception as err:
            warning('\033[33m %s.\033[m', err)


    # Função para exibição de notificação.
    def notifyMessage(self):
        if self.soma > 1:
            ms = 'Unread messages.'
        else:
            ms = 'Unread message.'
        com = 'notify-send --app-name="' + __pagename__ + '" --expire-time=' + str(set_json('TimeMessage')) +\
              ' --icon="' + realpath(set_icon('notify')) + '" "' + str(self.soma) + ' ' + ms + '"'
        run(com, shell=True)


    # Mostra os links ao passar o mouse sobre eles no statusBar e captura o link numa variável.
    def link_hovered(self, link):
        if set_json('StatusBar'):
            self.statusBar().showMessage(link)
        global cap_url
        cap_url = link  # O link precisa ser salvo numa variável, pois o link é perdido ao tirar o mouse de cima


    # Ativar a reconexão WhatsApp Web pela alteração do título.
    def loaded(self):
        if self.view.page().title() == __err__:  # Se der erro de conexão o título inicial não muda
            if not self.reload_start and set_json('AutoReload'):  # Autorreconexão
                self.reload.start()
                self.notify = self.changeTray = 0
                self.reload_start = True
                if self.notify_start:  # Notificação pode ser desativada para economizar recursos de processamento
                    self.notify_loop.stop()
                    self.notify_start = False
        else:
            if self.reload_start:  # Ao voltar a conexão o loop deve parar
                self.reload.stop()
                self.reload_start = False
        if not self.notify_start and set_json('TrayIcon'):  # Ativa o som de notificação
            self.notify_loop.start()
            self.notify_start = True  # Não precisa ficar reativando o som cada vez que o webapp é recarregado


    # Minimizando para o system tray.
    def on_hide(self):
        self.hide()
        self.trayMenu.clear()  # Alterando as opções do menu do tray icon
        self.trayMenu.addAction(self.trayShow)
        self.trayMenu.addAction(self.trayExit)


    # Abrindo o webapp do system tray.
    def on_show(self):
        # Ao iniciar para o system tray, vai abrir pela primeira vez maximizado
        if not self.start and set_json('StartUp') == 'Minimized':
            self.showMaximized()
            self.start = True
        else:
            margin = QMargins(0, 0, 0, 1)  # Hack para ocultar a janela para depois, reaparecer na mesma posição
            self.setGeometry(self.geometry() + margin)
            self.show()
            self.setGeometry(self.geometry() - margin)

        self.trayMenu.clear()  # Alterando as opções do menu do tray icon
        self.trayMenu.addAction(self.trayHide)
        self.trayMenu.addAction(self.trayExit)

        # Evitando que o programa minimize ao invés de maximizar
        if self.isMinimized():
            for a in range(1, 10):
                self.show()


    # Evento ao fechar a janela.
    def closeEvent(self, event):
        event.ignore()  # Precisa

        # Se a opção trayicon está ativada, a janela vai ser minimizada para o system tray, senão será fechada
        if set_json('TrayIcon'):
            self.on_hide()
        else:
            app.quit()


########################################################################################################################


# Classe criada para o desenvolvimento menu de contexto personalizado.
class Browser(QWebEngineView):
    statusbar_emit = pyqtSignal()
    font_emit = pyqtSignal()
    opacity_emit = pyqtSignal()
    tray_emit = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.menu = QMenu()  # Para criar o menu de contexto
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
        self.menuReload.triggered.connect(lambda: self.setUrl(QUrl(__url__)))  # Método melhor
        self.menuConfig.triggered.connect(self.showSettings)
        self.menuAbout.triggered.connect(lambda: AboutDialog().exec_())


########################################################################################################################


    # Função para abrir as configurações da interface feita por conta das emissões de sinal.
    def showSettings(self):
        settings = SettingDialog()
        settings.statusbar_emit.connect(self.statusbar_emit)
        settings.font_emit.connect(self.font_emit)
        settings.opacity_emit.connect(self.opacity_emit)
        settings.tray_emit.connect(self.tray_emit)
        settings.exec_()


    # Função para abrir um link num navegador externo.
    def external_browser(self):
        global cap_url
        if not cap_url:  # Garantindo que a variável vai ter o link para abrir
            cap_url = self.save_url

        if cap_url is not None:
            QDesktopServices.openUrl(QUrl(cap_url))  # Abrindo no navegador externo
        cap_url = None


    # Criando o menu de contexto.
    def contextMenuEvent(self, event):
        self.menu.clear()
        if cap_url:  # Menu para o link posicionado pelo mouse
            self.menu.addAction(self.menuExternal)
            self.menu.addAction(self.menuLinkClip)
        else:
            self.menu.addAction(self.menuReload)
            self.menu.addSeparator()
            self.menu.addAction(self.menuConfig)
            self.menu.addAction(self.menuAbout)
        self.menu.popup(event.globalPos())


    # Executando ações conforme o clique do mouse.
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Vai ter clique direto, mas só vai funcionar essa opção com a captura de um link
            if cap_url and force_open_link:
                self.external_browser()
        if event.button() == Qt.RightButton:
            self.save_url = cap_url  # Vai precisar salvar a url nessa variável para o menu de contexto


    # Mapeando os eventos do Mouse.
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
        return False


########################################################################################################################


# Classe para a página do webapp.
class WhatsApp(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)
        self.profile().defaultProfile().setHttpUserAgent(user_agent)  # Não rola nada sem isso
        self.profile().downloadRequested.connect(self.download)
        self.featurePermissionRequested.connect(self.permission)


    # Função que possibilita o download de arquivos.
    @pyqtSlot(QWebEngineDownloadItem)
    def download(self, download):
        old_path = download.path()
        suffix = QFileInfo(old_path).suffix()
        path = QFileDialog.getSaveFileName(self.view(), "Save File", old_path, "*." + suffix)[0]
        if path:
            download.setPath(path)
            download.accept()


    # Permissões para o navegador.
    def permission(self, frame, feature):
        self.setFeaturePermission(frame, feature, QWebEnginePage.PermissionGrantedByUser)


########################################################################################################################


# Início do programa
if __name__ == '__main__':
    prevent()
    checkSettings()

    # Vai ser usado a mesma base para todos os webapps criados, portanto essa opção será incluída,
    # sendo ela usada ou não. Ainda assim, será possível a sua ativação manual em 'settings.json'.
    if set_json('DarkMode'):
        arg = argv + ["--blink-settings=forceDarkModeEnabled=true"]
    else:
        arg = []

    # Verificando alteração manual em autostart
    if isfile(desk) and not set_json('AutoStart'):
        write_json('AutoStart', True)
    elif not isfile(desk) and set_json('AutoStart'):
        write_json('AutoStart', False)

    # Inicialização do programa
    app = QApplication(argv + arg)
    app.setApplicationName(__appname__)
    clipboard = app.clipboard()
    main = MainWindow()

    # Definindo como o programa será aberto
    if set_json('StartUp') == 'Normal':
        main.showNormal()
    elif set_json('StartUp') == 'Maximized':
        main.showMaximized()
    elif set_json('StartUp') == 'Minimized':
        main.hide()

    # Iniciando a aplicação
    exit(app.exec_())
