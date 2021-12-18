# -*- coding: utf-8 -*-

# Módulos importados
from logging import warning, error
from os import remove
from os.path import expanduser, isfile, realpath
from shutil import copy

# Modulos integrados (src)
from jsonTools import set_json, write_json


########################################################################################################################


# Define o ícone das aplicações.
def set_icon(entry_icon=None):

    # Definição da localização dos ícones e de forma opcional, os ícones a serem usados
    if entry_icon is not None:
        icon = '/usr/share/whats/icon_status/' + entry_icon + '.png'
        l_icon = '../icon_status/' + entry_icon + '.png'
    else:
        icon = '/usr/share/pixmaps/whats.svg'
        l_icon = '../appdata/whats.svg'

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
def set_desktop():
    orig = '/usr/share/applications/whats.desktop'
    dest = expanduser('~/.config/autostart')
    desk = dest + '/whats.desktop'

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
    dirSound = '/usr/share/whats/sound/' + sound + '.mp3'
    l_dirSound = realpath('../sound/' + sound + '.mp3')  # O realpath é nessesário para funcionar no QMediaPlayer

    try:
        with open(dirSound):
            return dirSound  # Esse aqui não precisa realpath, pois é caminho absoluto
    except Exception as msg:
        warning('\033[33m %s.\033[32m Use a local sound folder...\033[m', msg)
        return l_dirSound
