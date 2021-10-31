#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import Modules
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

# Import Sources
from utils import set_icon
from version import __version__

# Class for about dialog
class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        # Properties window
        self.setWindowTitle('Sobre o Whats')
        self.setFixedSize(400, 270)

        # Define button OK
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        # noinspection PyUnresolvedReferences
        self.buttonBox.accepted.connect(self.accept)

        # Define layout and text title
        layout = QVBoxLayout()
        title = QLabel('Whats - WhatsApp Desktop')
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)

        # Define logo for about
        logo = QLabel()
        logo.setPixmap(QPixmap(set_icon()))
        layout.addWidget(logo)

        # Text items
        layout.addWidget(QLabel('Version ' + str(__version__) + '\n'))
        layout.addWidget(QLabel('Maintainer: Mauricio Ferrari'))
        layout.addWidget(QLabel('Contact: m10ferrari1200@gmail.com\n'))

        # Define items in center
        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        # Create layout
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    # Capture event on minimize
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            # noinspection PyTypeChecker
            if self.windowState() & Qt.WindowMinimized:
                self.showMaximized()
