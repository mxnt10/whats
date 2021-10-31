#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modules
from logging import warning, error
from subprocess import run
from os.path import expanduser


# Define application icon
def set_icon(entry_icon=None):
    icon = '/usr/share/pixmaps/whats.svg'
    l_icon = '../appdata/whats.svg'

    if entry_icon is not None:
        icon = '/usr/share/whats/icon_status/' + entry_icon + '.png'
        l_icon = '../icon_status/' + entry_icon + '.png'

    try:
        with open(icon):
            return icon
    except Exception as msg:
        warning('\033[33m %s.\033[32m Use a local icon...\033[m', msg)
        try:
            with open(l_icon):
                return l_icon
        except Exception as msg:
            # Exception for icon not found
            error('\033[31m %s \033[m', msg)
            return None


# Run map_link script
def run_map_link():
    ext_link = '/usr/share/whats/utils/map_link'
    l_ext_link = '../utils/map_link'

    try:
        with open(ext_link):
            run_map = ext_link + ' &'
    except Exception as msg:
        warning('\033[33m %s.\033[32m Use a local icon...\033[m', msg)
        run_map = l_ext_link + ' &'

    run(run_map, shell=True)


# Exit map_link script
def run_exit_map_link():
    ext_link = '/usr/share/whats/utils/exit_map_link'
    l_ext_link = '../utils/exit_map_link'

    try:
        with open(ext_link):
            run_map = ext_link + ' &'
    except Exception as msg:
        warning('\033[33m %s.\033[32m Use a local icon...\033[m', msg)
        run_map = l_ext_link + ' &'

    run(run_map, shell=True)


def name_map_ext():
    return expanduser('~/.config/whats/mapped_link')


def set_link():
    file = name_map_ext()
    # noinspection PyBroadException
    try:
        with open(file, 'r', encoding='utf8') as a:
            for line in a:
                return line
    except Exception:
        return None
