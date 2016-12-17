from PySide2 import QtCore, QtWidgets
from MMD4Maya.Scripts.Utils import *

import pymel.util.path as pmp

class ExplorerWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None, type = 'pmd', mainWindow = None):
        super(ExplorerWindow,self).__init__(parent)
        self.mainWindow = mainWindow
        self.explorerType = type
        self.setWindowTitle('MMD4Maya Explorer')
        self.resize( 800, 800 )

        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)

        mainLayout = QtWidgets.QVBoxLayout()
        widget.setLayout(mainLayout)

        self.fileBrowserWidget = QtWidgets.QWidget(self)
        self.dirModel = QtWidgets.QFileSystemModel()
        self.dirModel.setRootPath("C:/")

        importLayout = QtWidgets.QHBoxLayout()
        importLayout.setSpacing(10)
        self.pathViewer = QtWidgets.QLineEdit(self)
        importButton = QtWidgets.QPushButton('Import')
        importButton.clicked.connect(self.OnImportButtonClicked)
        cancelButton = QtWidgets.QPushButton('Cancel')
        cancelButton.clicked.connect(self.OnCancelButtonClicked)
        fileNameLabel = QtWidgets.QLabel('File name:')

        self.nameFilters = []
        if self.explorerType == 'pmd':
            self.nameFilters = ["*.pmd", "*.pmx"]
        elif self.explorerType == 'vmd':
            self.nameFilters = ["*.vmd"]

        self.dirModel.setNameFilters(self.nameFilters)
        self.dirModel.setNameFilterDisables(False)

        self.folderView = QtWidgets.QTreeView(parent = self)
        self.folderView.setModel(self.dirModel)
        self.folderView.clicked[QtCore.QModelIndex].connect(self.Clicked) 
        self.folderView.doubleClicked[QtCore.QModelIndex].connect(self.DoubleClicked) 
        self.folderView.setColumnWidth(0,250)

        mainLayout.addWidget(self.folderView)
        mainLayout.addLayout(importLayout)
        importLayout.addWidget(fileNameLabel)
        importLayout.addWidget(self.pathViewer)
        importLayout.addWidget(importButton)
        importLayout.addWidget(cancelButton)

    def CheckFileExt(self, fileName):
        ext = GetExtFromFilePath(fileName)
        for filter in self.nameFilters:
            if ext.lower() == GetExtFromFilePath(filter):
                return True
        return False

    def UpdatePathViewer(self):
        index = self.folderView.currentIndex()
        path = pmp(self.dirModel.filePath(index)).normpath()
        self.pathViewer.setText(path)

    def ImportFile(self):
        index = self.folderView.currentIndex()
        path = pmp(self.dirModel.filePath(index)).normpath()
        if self.CheckFileExt(path):
            if self.explorerType == 'pmd':
                self.mainWindow.SetPmxFile(path)
            elif self.explorerType == 'vmd':
                self.mainWindow.AddVmdFile(path)
            self.close()

    def Clicked(self,index):
        self.UpdatePathViewer()

    def DoubleClicked(self,index):
        self.ImportFile()

    def OnImportButtonClicked(self):
        self.ImportFile()

    def OnCancelButtonClicked(self):
        self.close()