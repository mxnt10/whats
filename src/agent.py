# -*- coding: utf-8 -*-

# Módulos importados
from os.path import expanduser, isdir
from os import chmod, makedirs
from shutil import rmtree


########################################################################################################################


# Link para pegar o userAgent: http://httpbin.org/user-agent
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'


# A ideia dessa função é prevenir a mensagem de novegador desatualizado mesmo que o agent user seja utilizado.
def prevent():
    log_folder = expanduser('~/.local/share/Whats/QtWebEngine/Default/Service Worker/')

    try:
        if isdir(log_folder):
            rmtree(log_folder)

        makedirs(log_folder)
        chmod(log_folder, 0o444)  # Impedir alteração
    except Exception as msg:
        print(msg)
