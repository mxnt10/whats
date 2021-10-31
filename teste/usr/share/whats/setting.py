#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modules
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout


# Class for settings dialog
class SettingDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SettingDialog, self).__init__(*args, **kwargs)

        # Properties window
        self.setWindowTitle('Settings')
        self.setFixedSize(400, 500)

        # Define button OK
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)

        # Define layout
        layout = QVBoxLayout()

        # Create layout
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
