from PySide import QtGui, QtCore
from MMD4Maya.Scripts.Utils import *

import pymel.util.path as pmp

class ExplorerWindow(QtGui.QMainWindow):
    def __init__(self, parent = None, type = 'pmd', mainWindow = None):
        super(ExplorerWindow,self).__init__(parent)
        self.mainWindow = mainWindow
        self.explorerType = type
        self.setWindowTitle('MMD4Maya Explorer')
        self.resize( 800, 800 )

        widget = QtGui.QWidget()
        self.setCentralWidget(widget)

        mainLayout = QtGui.QVBoxLayout()
        widget.setLayout(mainLayout)

        self.line = QtGui.QLineEdit(self)
        self.fileBrowserWidget = QtGui.QWidget(self)
        self.dirModel = QtGui.QFileSystemModel()
        self.dirModel.setRootPath("C:/")

        self.nameFilters = []
        if self.explorerType == 'pmd':
            self.nameFilters = ["*.pmd", "*.pmx"]
        elif self.explorerType == 'vmd':
            self.nameFilters = ["*.vmd"]

        self.dirModel.setNameFilters(self.nameFilters)
        self.dirModel.setNameFilterDisables(False)

        self.folderView = QtGui.QTreeView(parent = self)
        self.folderView.setModel(self.dirModel)
        self.folderView.clicked[QtCore.QModelIndex].connect(self.Clicked) 
        self.folderView.doubleClicked[QtCore.QModelIndex].connect(self.DoubleClicked) 

        self.folderView.setColumnWidth(0,250)

        mainLayout.addWidget(self.line,1,0)
        mainLayout.addWidget(self.folderView)

    def CheckFileExt(self, fileName):
        ext = GetExtFromFilePath(fileName)
        for filter in self.nameFilters:
            if ext.lower() == GetExtFromFilePath(filter):
                return True
        return False

    def Clicked(self,index):
        index = self.folderView.currentIndex()
        dirPath = pmp(self.dirModel.filePath(index)).normpath()
        self.line.setText(dirPath)

    def DoubleClicked(self,index):
        index = self.folderView.currentIndex()
        path = pmp(self.dirModel.filePath(index)).normpath()
        if self.CheckFileExt(path):
            if self.explorerType == 'pmd':
                self.mainWindow.SetPmxFile(path)
            elif self.explorerType == 'vmd':
                self.mainWindow.AddVmdFile(path)
            self.close()