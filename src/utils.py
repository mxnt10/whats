# -*- coding: utf-8 -*-

# Módulos importados
from logging import warning, error
from os import remove, walk
from os.path import expanduser, isfile, realpath, isdir
from subprocess import run
from requests import get
from soupsieve.util import lower
from shutil import copy

# Módulos do Qt5
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaContent

# Modulos integrados (src)
from jsonTools import set_json, write_json
from version import __dir__, __desktop__, __icon__, __version__, __appname__


########################################################################################################################


# Define o ícone das aplicações.
def setIcon(entry_icon=None):

    # Definição da localização dos ícones e de forma opcional, os ícones a serem usados
    if entry_icon is not None:
        icon = __dir__ + '/icon_status/' + entry_icon + '.png'
        l_icon = '../icon_status/' + entry_icon + '.png'
    else:
        icon = '/usr/share/pixmaps/' + __icon__
        l_icon = '../appdata/' + __icon__

    try:
        with open(icon):
            return icon
    except Exception as msg:
        warning('\033[33m %s.\033[32m Use a local icon...\033[m', msg)
        try:
            with open(l_icon):
                return l_icon
        except Exception as msg:
            # Caso nenhum ícone seja encontrado, vai sem ícone mesmo
            error('\033[31m %s \033[m', msg)
            return None


# Verifica a existência do arquivo whats.desktop no diretório autostart.
def setDesktop():
    orig = '/usr/share/applications/' + __desktop__
    dest = expanduser('~/.config/autostart')
    desk = dest + '/' + __desktop__

    try:
        if not isfile(desk) and set_json('AutoStart'):
            with open(orig):  # Antes da cópia, é preciso verificar a sua existência
                copy(orig, dest)
        elif isfile(desk) and not set_json('AutoStart'):
            remove(desk)
        return True

    except Exception as msg:  # Se o arquivo não existe, não tem porque ativar a opção autostart
        error('\033[31m %s \033[m', msg)
        write_json('AutoStart', False)
        return False


# Busca por arquivos de áudio que servirão como tema das mensagens de notificação.
def setSound(sound):
    dirSound = __dir__ + '/sound/' + sound + '.mp3'
    l_dirSound = realpath('../sound/' + sound + '.mp3')  # O realpath é necessário para funcionar no QMediaPlayer

    try:
        with open(dirSound):
            return dirSound  # Esse aqui não precisa realpath, pois é caminho absoluto
    except Exception as msg:
        warning('\033[33m %s.\033[32m Use a local sound folder...\033[m', msg)
        return l_dirSound


# Cria uma lista com as opções de temas de som.
def listSound():
    res = []
    dirSound = __dir__ + '/sound/'
    if not isdir(dirSound):
        dirSound = '../sound'

    for directory, subdir, files in walk(dirSound):
        for file in files:
            res.append(file.split('.')[0])
        return res


# Verificar localização dos arquivos de tradução.
def setTranslate():
    dirTranslate = '../translate'
    if not isdir(dirTranslate):
        dirTranslate = __dir__ + '/translate/'
    else:
        warning('\033[32m Using a local translate folder...\033[m')
    return dirTranslate


# Função que verifica se há atualizações disponíveis.
def checkUpdate(self, num):
    """
    :param self: parâmetro self.
    :type num: só está aí por conta do multiprocessamento.
    """
    try:
        res = get('https://raw.githubusercontent.com/mxnt10/' + lower(__appname__) + '/master/RELEASE')
        if res.status_code != 200:
            raise ValueError('Connection fail, ' + str(res.status_code))

        new_ver = res.text.split("\n")
        if new_ver[0] != str(__version__):
            com = 'notify-send --app-name="' + __appname__ + ' - ' + self.textUpdate1 + '" --expire-time=' +\
                  str(set_json('TimeMessage')) + ' "' + self.textUpdate2 + '.\n' + self.textUpdate3 +\
                  ': ' + new_ver[0] + '"'
            run(com, shell=True)
            self.notify_sound.setMedia(QMediaContent(QUrl.fromLocalFile(setSound(set_json('SoundTheme')))))
            self.notify_sound.play()

    except ValueError as msg:
        error("\033[33m Update check failed.\033[31m %s \033[m", msg)
