# -*- coding: utf-8 -*-

# Módulos importados
from json import dump, load
from os import makedirs, remove
from os.path import expanduser, isdir

# Módulos do PyQt5
from PyQt5.QtCore import qDebug

# Modulos integrados (src)
from version import __appname__

########################################################################################################################


j_folder = expanduser('~/.config/' + __appname__)
j_file = j_folder + '/settings.json'

default_js = {
  "AutoStart": False,
  "TrayIcon": True,
  "StartUp": "Normal",
  "StatusBar": False,
  "DarkMode": False,
  "NotifyMessage": False,
  "NotifySound": False,
  "VerifyNotify": 800,
  "TimeMessage": 5000,
  "SoundTheme": "message",
  "Opacity": 100,
  "SizeFont": None,
  "AutoReload": False,
  "CheckUpdate": False,
  "TimeReload": 2000
}


# Check if exist settings.json, else file as create
def checkSettings():
    try:
        with open(j_file):
            pass
    except Exception as msg:
        qDebug('\033[31m[DEBUG]\033[33m: ' + str(msg) + '. \033[32mCreate a settings.json...\033[m')
        if not isdir(j_folder):
            makedirs(j_folder)
        with open(j_file, 'w') as jfile:
            dump(default_js, jfile, indent=2)


# Set value of the json file
def set_json(op):
    with open(j_file) as jf:
        objJson = load(jf)
    return objJson[op]


# Write value of the json file
def write_json(op, val):
    with open(j_file, 'r') as jf:
        objJson = load(jf)
        objJson[op] = val

    # Replace original file
    remove(j_file)
    with open(j_file, 'w') as jf:
        dump(objJson, jf, indent=2)
