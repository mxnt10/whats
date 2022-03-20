#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Módulos importados
from bs4 import BeautifulSoup  # pip install beautifulsoup4
from locale import getdefaultlocale
from logging import warning
from os.path import isfile, expanduser
from sys import argv
from threading import Thread

# Módulos do PyQt5
from PyQt5.QtCore import QUrl, QFileInfo, pyqtSlot, QMargins, Qt, QEvent, QTimer, pyqtSignal, QTranslator
from PyQt5.QtGui import QIcon, QDesktopServices, QKeySequence
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWebEngineWidgets import (QWebEngineView, QWebEnginePage, QWebEngineDownloadItem, QWebEngineSettings,
                                      QWebEngineProfile)
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QSystemTrayIcon, QMenu, QAction, QShortcut

# Modulos integrados (src)
from about import AboutDialog
from agent import user_agent, prevent
from jsonTools import checkSettings, set_json, write_json
from notify import verifyNotify
from setting import SettingDialog
from utils import setIcon, checkUpdate, setTranslate
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
        self.textUpdate1 = self.textUpdate2 = self.textUpdate3 = self.message1 = self.message2 = None
        self.start = self.notify_start = self.reload_start = self.ckUpdate = self.sysLogin = False
        self.notify = self.changeTray = self.soma = 0

        # Passagem de parâmetros para o webapp
        for ag in argv:
            if ag == '--system-login':  # Parâmetro para a inicialização durante o login do sistema.
                self.sysLogin = True

        # Pega o tamanho da fonte na primeira inicialização
        if set_json('SizeFont') is None:
            write_json('SizeFont', float(str(self.font().key()).split(',')[1]))

        # Para o som de notificação
        self.notify_sound = QMediaPlayer()

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
        self.setWindowIcon(QIcon(setIcon()))
        self.setMinimumSize(800, 600)

        # Definições para a visualização da página do webapp
        self.view = Browser()
        self.view.statusbar_emit.connect(self.changeStatusBar)
        self.view.font_emit.connect(self.changeFont)
        self.view.opacity_emit.connect(self.changeOpacity)
        self.view.tray_emit.connect(self.changeTrayIcon)
        self.view.setPage(WebPage(self.view))
        self.view.page().linkHovered.connect(self.link_hovered)
        self.view.loadFinished.connect(self.loaded)
        self.view.load(QUrl(__url__))
        self.setCentralWidget(self.view)
        self.changeStatusBar()
        self.changeOpacity()
        self.changeFont()

        # Teclas de atalho
        self.shortcut1 = QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_R), self)
        self.shortcut1.activated.connect(lambda: self.view.load(QUrl(__url__)))
        self.shortcut2 = QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Q), self)
        self.shortcut2.activated.connect(app.quit)
        self.shortcut3 = QShortcut(QKeySequence(Qt.AltModifier + Qt.Key_S), self)
        self.shortcut3.activated.connect(self.view.showSettings)
        self.shortcut4 = QShortcut(QKeySequence(Qt.Key_Backspace), self)
        self.shortcut4.activated.connect(self.view.back)

        # Criando o tray icon
        self.tray = QSystemTrayIcon()
        self.tray.activated.connect(self.onTrayIconActivated)
        self.tray.setIcon(QIcon(setIcon('warning')))

        # Itens para o menu do tray icon
        self.trayHide = QAction(self.tr('Hide'), self)
        self.trayShow = QAction(self.tr('Show'), self)
        self.trayExit = QAction(self.tr('Exit'), self)

        # Ícones para o menu do tray icon
        self.trayHide.setIcon(QIcon.fromTheme('go-down'))
        self.trayShow.setIcon(QIcon.fromTheme('go-up'))
        self.trayExit.setIcon(QIcon.fromTheme('application-exit'))
        self.trayExit.setShortcut('Ctrl+Q')

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


    # Função que possui o objetivo de ser executada como um thead independentepara resolver problemas
    # de lentidão durante o uso do webapp.
    def bs(self, htm, parser):
        res = BeautifulSoup(htm, parser)
        try:
            if not __err__ in res.title and res.findAll('div', {'class': '_26lC3'}):
                verifyNotify(self, res)
            if __err__ in res.title:  # Em caso de erro de conexão o título inicial não se altera
                if self.changeTray != 1:
                    self.tray.setIcon(QIcon(setIcon('error')))
                    self.changeTray = 1
            elif self.soma > 0:
                if self.changeTray != 2:
                    self.tray.setIcon(QIcon(setIcon('withmsg')))
                    self.changeTray = 2
            else:
                if self.changeTray != 3:
                    self.tray.setIcon(QIcon(setIcon('original')))
                    self.changeTray = 3
        except Exception as err:
            warning('\033[33m %s.\033[m', err)


    # Função que manipula o código-fonte do webapp para a checagem das mensagens não lidas, emitindo sons,
    # exibindo mensagens e alterando o ícone de notificação.
    def processHtml(self, htm):
        self.message1 = self.tr('Unread messages.')  # Textos definidos aqui por conta da tradução
        self.message2 = self.tr('Unread message.')
        t = Thread(name='scratch', target=self.bs, args=(htm, 'html.parser'))
        t.start()


    # Mostra os links ao passar o mouse sobre eles no statusBar e captura o link numa variável.
    def link_hovered(self, link):
        if set_json('StatusBar'):
            self.statusBar().showMessage(link)
        global cap_url
        cap_url = link  # O link precisa ser salvo numa variável, pois o link é perdido ao tirar o mouse de cima


    # Ações após finalizar o carregamento do webapp.
    def loaded(self):
        if self.view.page().title() == __err__:  # Se der erro de conexão o título inicial não muda
            if not self.reload_start and set_json('AutoReload'):  # Autorreconexão
                self.reload.start()
                self.notify = self.changeTray = 0
                self.reload_start = True
            if self.notify_start:  # Notificação pode ser desativada para economizar recursos de processamento
                self.notify_loop.stop()
                self.tray.setIcon(QIcon(setIcon('error')))
        else:
            if self.reload_start:  # Ao voltar a conexão o loop deve parar
                self.reload.stop()
                self.reload_start = False
                self.notify_start = False
        if not self.notify_start and set_json('TrayIcon'):  # Ativa o som de notificação
            self.notify_loop.start()
            self.notify_start = True  # Não precisa ficar reativando o som cada vez que o webapp é recarregado
        if set_json('CheckUpdate') and not self.ckUpdate:
            self.textUpdate1 = self.tr('Update available')  # Textos definidos aqui por conta da tradução
            self.textUpdate2 = self.tr('A new version is available')
            self.textUpdate3 = self.tr('New version')
            t = Thread(name='update', target=checkUpdate, args=(self, 1))
            t.start()
            self.ckUpdate = True


    # Gambiarra legítima para garantir que a janela vai abrir no topo.
    def top(self):
        self.hide()
        self.show()


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

        QTimer.singleShot(100, self.top)
        self.trayMenu.clear()  # Alterando as opções do menu do tray icon
        self.trayMenu.addAction(self.trayHide)
        self.trayMenu.addAction(self.trayExit)


    # Evento para mostrar e ocultar a janela com apenas um clique no tray icon.
    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isHidden():
                self.on_show()
            else:
                self.on_hide()


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

        # Ativando tudo o que tiver de direito
        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

        # Necessário para maear os eventos de mouse
        QApplication.instance().installEventFilter(self)
        self.setMouseTracking(True)

        # Definindo itens para a criação do menu
        self.menuExternal = QAction(self.tr('Open link in the browser'))
        self.menuLinkClip = QAction(self.tr('Copy link to clipboard'))
        self.menuReload = QAction(self.tr('Reload'))
        self.menuConfig = QAction(self.tr('Preferencies'))
        self.menuAbout = QAction(self.tr('About'))

        # Ícones para o menu
        self.menuExternal.setIcon(QIcon.fromTheme('globe'))
        self.menuLinkClip.setIcon(QIcon.fromTheme('edit-copy'))
        self.menuReload.setIcon(QIcon.fromTheme('view-refresh'))
        self.menuConfig.setIcon(QIcon.fromTheme('configure'))
        self.menuAbout.setIcon(QIcon.fromTheme('help-about'))

        # Teclas de atalho
        self.menuReload.setShortcut('Ctrl+R')
        self.menuConfig.setShortcut('Alt+S')

        # Adicionar funções para as opções de menu
        self.menuExternal.triggered.connect(self.externalBrowser)
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
    def externalBrowser(self):
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
                self.externalBrowser()
        if event.button() == Qt.RightButton:
            self.save_url = cap_url  # Vai precisar salvar a url nessa variável para o menu de contexto


    # Mapeando os eventos do Mouse.
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
        return False


########################################################################################################################


# Classe para a página do webapp.
class WebPage(QWebEnginePage):
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
        path = QFileDialog.getSaveFileName(self.view(), self.tr("Save File"), old_path, "*." + suffix)[0]
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
    lang = getdefaultlocale()[0]
    QWebEngineProfile.defaultProfile().setHttpAcceptLanguage(lang.split('_')[0])
    clipboard = app.clipboard()
    translate = QTranslator()
    translate.load(setTranslate() + '/whats_' + lang.split('_')[0] + '.qm')
    app.installTranslator(translate)
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
