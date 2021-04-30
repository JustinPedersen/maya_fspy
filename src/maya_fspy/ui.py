"""
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

Usage:
    import maya_fspy.ui as mfspy_ui
    mfspy_ui.maya_fspy_ui()

Note that you will nee to set the correct axes inside of the standalone fspy application for the best results.
Vanishing point axes:
    1. -Z
    2. -X
Reference distance:
    Along the y-axis
"""
import os
import platform
from functools import partial

import maya.OpenMayaUI as omui
import pymel.core as pm
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

from .core import create_camera_and_plane

__author__ = 'Justin Pedersen'
__version__ = '1.2.0'

WINDOW_NAME = "Fspy Importer - v{}".format(__version__)

# Python 3 compatibility
if platform.python_version_tuple()[0] == '3':
    long = int


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def close_existing_windows():
    """
    Close any existing instances of the maya fspy window
    """
    for child_window in maya_main_window().children():
        if hasattr(child_window, 'windowTitle'):
            if child_window.windowTitle() == WINDOW_NAME:
                child_window.close()
                child_window.deleteLater()


class FSpyImporter(QtWidgets.QDialog):
    """
    Main UI Class for the importer
    """
    def __init__(self, parent=maya_main_window()):
        super(FSpyImporter, self).__init__(parent)

        self.setWindowTitle(WINDOW_NAME)
        self.setMinimumWidth(300)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.json_lineedit = QtWidgets.QLineEdit()
        self.json_btn = QtWidgets.QPushButton("JSON")
        self.image_lineedit = QtWidgets.QLineEdit()
        self.image_btn = QtWidgets.QPushButton("Image")
        self.import_btn = QtWidgets.QPushButton("Import")

        self.json_btn.setFixedHeight(20)
        self.json_lineedit.setFixedHeight(20)
        self.image_btn.setFixedHeight(20)
        self.image_lineedit.setFixedHeight(20)
        self.import_btn.setMinimumHeight(40)

    def create_layouts(self):
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self.json_btn, self.json_lineedit)
        form_layout.addRow(self.image_btn, self.image_lineedit)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.import_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.json_btn.clicked.connect(partial(self.set_line_edit, self.json_lineedit, 'Import Json'))
        self.image_btn.clicked.connect(partial(self.set_line_edit, self.image_lineedit, 'Import Image'))
        self.import_btn.clicked.connect(self.generate_camera)

    def set_line_edit(self, line_edit, caption):
        """
        Open a file dialog and set the result to the string inside a line edit.
        :param line_edit: The target line edit.
        :param str caption: The window caption.
        """
        # Setting up the dialog filters to only accept what is expected in that field to prevent user error.
        if line_edit == self.json_lineedit:
            file_filter = '*.json'
        else:
            all_image_formats = ['psd', 'als', 'avi', 'dds', 'gif', 'jpg', 'cin', 'iff', 'exr',
                                 'png', 'eps', 'yuv', 'hdr', 'tga', 'tif', 'tim', 'bmp', 'xpm']
            file_filter = 'All Image Files (*.{})'.format(' *.'.join([x for x in all_image_formats]))

        filename = pm.fileDialog2(fileMode=1, caption=caption, fileFilter=file_filter)
        if filename:
            line_edit.setText(filename[0])

    def generate_camera(self):
        """
        Main function to generate the camera and image plane from UI.
        """
        # Making sure no one put a .json file in the JSON field
        if os.path.splitext(self.json_lineedit.text())[-1].lower() != '.json':
            return pm.warning('The JSON field only accepts .json file formats')

        if self.json_lineedit and self.image_lineedit:
            create_camera_and_plane(self.json_lineedit.text(), self.image_lineedit.text())
        else:
            pm.warning('Please set a JSON and image path.')


def maya_fspy_ui():
    """
    Open the maya fspy ui.
    """
    close_existing_windows()
    fspy_importer_dialog = FSpyImporter()
    fspy_importer_dialog.show()
