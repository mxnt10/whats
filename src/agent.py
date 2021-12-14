#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modules
from os.path import expanduser, isdir
from os import chmod, makedirs
from shutil import rmtree

# Link for userAgent:
# http://httpbin.org/user-agent


# Function for prevent outdated browser message
def prevent():
    # Outdated browser
    log_folder = expanduser('~/.local/share/Whats/QtWebEngine/Default/Service Worker/')

    try:
        if isdir(log_folder):
            rmtree(log_folder)

        makedirs(log_folder)
        chmod(log_folder, 0o444)
    except Exception as msg:
        print(msg)


# Define userAgent
def user_agent():
    """ Returns a User Agent that will be seen by the website. """
    return 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
