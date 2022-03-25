# -*- coding: utf-8 -*-

# Módulos importados
from os.path import expanduser, isdir
from os import chmod, makedirs
from shutil import rmtree

# Módulos do PyQt5
from PyQt5.QtCore import qDebug

# Modulos integrados (src)
from version import __appname__


########################################################################################################################


# Link para pegar o userAgent: http://httpbin.org/user-agent
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36'


# A ideia dessa função é prevenir a mensagem de novegador desatualizado mesmo que o agent user seja utilizado.
def prevent():
    log_folder = expanduser('~/.local/share/' + __appname__ + '/QtWebEngine/Default/Service Worker/')

    try:
        if isdir(log_folder):
            rmtree(log_folder)

        makedirs(log_folder)
        chmod(log_folder, 0o444)  # Impedir alteração
    except Exception as msg:
        qDebug('\033[31m[DEBUG]\033[33m: ' + str(msg) + '...\033[m')
