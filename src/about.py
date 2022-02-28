# -*- coding: utf-8 -*-

# Módulos do PyQt5
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

# Modulos integrados (src)
from utils import setIcon
from version import __version__, __appname__, __pagename__


########################################################################################################################


# Classe para o diálogo About.
class AboutDialog(QDialog):
    def __init__(self):
        super(AboutDialog, self).__init__()
        self.setWindowTitle(self.tr('About') + ' ' + __appname__)
        self.setFixedSize(0, 0)

        # Título e Logo
        title = QLabel(__pagename__)
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        logo = QLabel()
        pixmap = QPixmap(setIcon('original'))
        logo.setPixmap(pixmap.scaled(128, 128))

        # Layout com as informações
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(logo)
        layout.addWidget(QLabel(self.tr('Version') + ' ' + __version__ + '\n'))
        layout.addWidget(QLabel(self.tr('Maintainer') + ': Mauricio Ferrari'))
        layout.addWidget(QLabel(self.tr('Contact') + ': m10ferrari1200@gmail.com'))
        layout.addWidget(QLabel(self.tr('License') + ': GNU General Public License Version 3 (GLPv3)\n'))

        for i in range(0, layout.count()):  # Definindo os widgets no centro
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(QDialogButtonBox(QDialogButtonBox.Ok, clicked=self.accept))
        self.setLayout(layout)


    # Evitando que o diálogo About minimize.
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.showMaximized()
