#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modules
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

# Import source
from utils import set_icon


# Message for QtWebEngine not installed
class WarnDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(WarnDialog, self).__init__(*args, **kwargs)

        # Properties window
        self.setWindowTitle('Warning')
        self.setWindowIcon(QIcon(set_icon()))
        self.setFixedSize(340, 140)

        # Define message
        self.msg = QLabel('\nPyQtWebEngine is not installed. Please, install using:')
        self.comm = QLabel('pip3 install PyQtWebEngine\n')
        font = self.comm.font()
        font.setBold(True)
        self.comm.setFont(font)

        # Define button OK
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)

        # Define layout
        layout = QVBoxLayout()

        # Create layout
        layout.addWidget(self.msg)
        layout.addWidget(self.comm)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
