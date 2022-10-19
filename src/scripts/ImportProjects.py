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

class ImportProjectsDlg(QtWidgets.QDialog):

    def __init__ (self, parent):
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
        QtCore.QObject.connect(self.btnQuit, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("reject()"))    

        self.exec()

    def import_prj(self):

        app = QtWidgets.QApplication.instance()
        filenames = Metashape.app.getOpenFileNames("Specify the import file:")
        if not filenames:
            print("Script aborted: invalid input file.")    
            return 0

        print("Script started...")

        i = 1;

        for fname in filenames:
            importPrjByScript(fname, Path(fname).stem)
            i = i + 1
        #importPrj(filename)
        
        print("Script finished. Project imported!")
        self.close()
        return 1 

def import_projects():
    app = QtWidgets.QApplication.instance()
    parent = app.activeWindow()
    dlg = ImportProjectsDlg(parent)

#def importPrjByScript(fname, chunkName="Untitled Chunk"):
#    doc = Metashape.app.document
#    runscript = Metashape.Tasks.RunScript()
#    runscript.path = "C:\Program Files\Agisoft\Metashape Pro\scripts\ImportProjectCore.py"
#    runscript.args = "\"{0}\"".format(fname) + " " + chunkName
#    runscript.apply(doc)


label = "Plugins/Import/Import Projects..."
Metashape.app.addMenuItem(label, import_projects)
print("To execute this script press {}".format(label))