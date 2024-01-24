import Metashape
import sys
import os
import math
import tkinter
import tempfile
from tkinter import filedialog
from zipfile import ZipFile
from PySide2 import QtGui, QtCore, QtWidgets
from pathlib import Path


class ImportProjectDlg(QtWidgets.QDialog):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle("Import Project")

        self.btnQuit = QtWidgets.QPushButton("&Close")
        self.btnP1 = QtWidgets.QPushButton("&Import...")

        # creating layout
        layout = QtWidgets.QGridLayout()
        layout.setSpacing(10)

        layout.addWidget(self.btnP1, 2, 0)
        layout.addWidget(self.btnQuit, 2, 1)
        self.setLayout(layout)

        QtCore.QObject.connect(self.btnP1, QtCore.SIGNAL("clicked()"), self.import_prj)
        QtCore.QObject.connect(
            self.btnQuit, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("reject()")
        )

        self.exec()

    def import_prj(self):
        app = QtWidgets.QApplication.instance()
        filename = Metashape.app.getOpenFileName("Specify the import file:")
        if not filename:
            print("Script aborted: invalid input file.")
            return 0

        print("Script started...")

        # importPrj(filename)
        importPrjByScript(filename)
        print("Script finished. Project imported!")
        self.close()
        return 1


def import_project():
    app = QtWidgets.QApplication.instance()
    parent = app.activeWindow()
    dlg = ImportProjectDlg(parent)


def importPrjByScript(fname, chunkName="Untitled_Chunk"):
    doc = Metashape.app.document
    runscript = Metashape.Tasks.RunScript()
    runscript.path = (
        "C:\Program Files\Agisoft\Metashape Pro\scripts\ImportProjectCore.py"
    )
    runscript.args = '"{0}"'.format(fname) + " " + chunkName
    runscript.apply(doc)


# def importPrjByScript(fname):
#    doc = Metashape.app.document
#    runscript = Metashape.Tasks.RunScript()
#    runscript.path = "C:\Program Files\Agisoft\Metashape Pro\scripts\ImportProjectCore.py"
#    runscript.args = "\"{0}\"".format(fname)
#    runscript.apply(doc)


label = "Plugins/Import/Import Project..."
Metashape.app.addMenuItem(label, import_project)
print("To execute this script press {}".format(label))
