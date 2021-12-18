# -*- coding: utf-8 -*-

# Módulos do PyQt5
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

# Modulos integrados (src)
from utils import set_icon
from version import __version__


########################################################################################################################


# Classe para o About (Sobre).
class AboutDialog(QDialog):
    def __init__(self):
        super(AboutDialog, self).__init__()

        # Definindo as propriedades da janela
        self.setWindowTitle('About Whats')
        self.setFixedSize(0, 0)

        # Botão OK
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)

        # Layout e Título
        layout = QVBoxLayout()
        title = QLabel('Whats - WhatsApp Desktop')
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)

        # Definindo uma logo
        logo = QLabel()
        logo.setPixmap(QPixmap(set_icon('original')))
        layout.addWidget(logo)

        # Inserindo as mensagens de informação
        layout.addWidget(QLabel('Version ' + str(__version__) + '\n'))
        layout.addWidget(QLabel('Maintainer: Mauricio Ferrari'))
        layout.addWidget(QLabel('Contact: m10ferrari1200@gmail.com'))
        layout.addWidget(QLabel('License: GNU General Public License Version 3 (GLPv3)\n'))

        # Definindo tudo no centro
        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        # Adicionando o botão e criando o layout
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


    # Evitando que o diálogo About minimize.
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.showMaximized()
