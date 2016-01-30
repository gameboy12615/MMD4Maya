from MMD4Maya.Scripts.FBXConverter import *
from MMD4Maya.Scripts.FBXImporter import *
from MMD4Maya.Scripts.FBXModifier import *
from MMD4Maya.Scripts.UI.ExplorerWindow import *
from MMD4Maya.Scripts.Utils import *
from PySide import QtGui, QtCore

import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
import maya.utils
import shiboken
import shutil
import threading  
import os

class MainWindow(object):

    # Process thread
    class Processor(threading.Thread):
        def __init__(self, threadname, mainWindow = None):
            self.mainWindow = mainWindow
            threading.Thread.__init__(self, name = threadname)

        def run(self):
            self.mainWindow.AsyncProcess()

    def OnImportPmxButtonClicked(self, *args):
        self.ShowExplorer('pmd')

    def OnAddVmdButtonClicked(self, *args):
        self.ShowExplorer('vmd')

    def OnSelectVmdFile(self, *args):
        self.__selectedVmdFileIndex = cmds.textScrollList(self.vmdScrollList, query = True, selectIndexedItem = True)

    def OnDeleteKeyClicked(self, *args):
        if self.__selectedVmdFileIndex > 0:
            cmds.textScrollList(self.vmdScrollList, edit = True, removeIndexedItem = self.__selectedVmdFileIndex)

    def OnDeleteButtonClicked(self, *args):
        if self.__selectedVmdFileIndex > 0:
            cmds.textScrollList(self.vmdScrollList, edit = True, removeIndexedItem = self.__selectedVmdFileIndex)

    def OnCheckBoxOn(self, *args):
        self.__agreeTerms = True

    def OnCheckBoxOff(self, *args):
        self.__agreeTerms = False

    def OnProcessButtonClicked(self, *args):
        self.Process()

    def __init__(self):
        # private attribute
        self.__converter = FBXConverter(self)
        self.__modifier = FBXModifier(self)
        self.__importer = FBXImporter()
        self.__pmxFile = ''
        self.__vmdFileList = []
        self.__selectedVmdFileIndex = 0
        self.__agreeTerms = False
        self.__isProcessing = False

        # create window
        if cmds.window("MMD4Maya", exists = True):
            cmds.deleteUI("MMD4Maya")
        window = cmds.window(title="MMD4Maya", widthHeight=(600, 580), 
                             sizeable = False, minimizeButton = False, maximizeButton = False)
        # create layout
        cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 450), (2, 150)] )
        self.pmxText = cmds.textField()
        cmds.button(label = 'Import pmx/pmd file', command = self.OnImportPmxButtonClicked)
        self.vmdScrollList = cmds.textScrollList(height = 110, allowMultiSelection = False, 
                                                 selectCommand = self.OnSelectVmdFile, deleteKeyCommand = self.OnDeleteKeyClicked)
        cmds.button(label = 'Add vmd file', command = self.OnAddVmdButtonClicked)
        #cmds.button(label = 'Delete selected vmd file', command = self.OnDeleteButtonClicked)
        cmds.columnLayout(width = 600)
        cmds.separator(height = 10, style = 'none')
        cmds.text('Log viewer:', font = "boldLabelFont")
        cmds.separator(height = 10, style = 'none')
        self.logText = cmds.scrollField(width = 600, height = 300, editable = False)
        cmds.separator(height = 10, style = 'none')
        cmds.checkBox(label='You must agree to these terms of use before using the model/motion.', 
                      onCommand = self.OnCheckBoxOn, offCommand = self.OnCheckBoxOff)
        cmds.separator(height = 10, style = 'none')
        self.processButton = cmds.button(label = 'Process', width = 600, height = 62, command = self.OnProcessButtonClicked)
        # show window
        cmds.showWindow(window)

    def CheckReadmeFile(self, pmxFilePath):
        self.Log('================================= ReadMe ===================================')
        readmeFile = GetDirFormFilePath(pmxFilePath) + "readme.txt"
        def ShowDefaultReadme():
            self.Log("Please contact the model/motion author if you need them for commercial use!")
        if os.path.exists(readmeFile):
            inputFile = open(readmeFile)
            lines = inputFile.readlines()
            inputFile.close()
            try:
                for line in lines:
                    self.Log(line.decode('shift-jis'))
            except:
                ShowDefaultReadme()
        else:
            ShowDefaultReadme()
        self.Log('============================================================================')

    def SetPmxFile(self, fileName):
        self.__pmxFile = ConvertToUnixPath(fileName).encode('ascii','ignore')
        cmds.textField(self.pmxText, edit=True, text=self.__pmxFile)
        self.CheckReadmeFile(self.__pmxFile)

    def AddVmdFile(self, fileName):
        fileName = ConvertToUnixPath(fileName).encode('ascii','ignore')
        self.__vmdFileList.append(fileName)
        cmds.textScrollList(self.vmdScrollList, edit = True, append=[fileName])

    def Log(self, log):
        def WriteToLog(log):
            cmds.scrollField(self.logText, edit=True, insertText = log + '\n')
        # executeInMainThreadWithResult() can't call recursively, so Log() can't be called in executeInMainThreadWithResult()
        maya.utils.executeInMainThreadWithResult(WriteToLog, log)

    def MessageBox(self, msg = ''):
        cmds.confirmDialog(title='Confirm', message=msg)

    def ShowExplorer(self, type = 'pmd'):
        ptr = OpenMayaUI.MQtUtil.mainWindow()
        widget = shiboken.wrapInstance(long(ptr),QtGui.QWidget)
        explorerWin = ExplorerWindow(widget, type, self)
        explorerWin.show()

    def CleanTempFiles(self):
        # clean temp fbx directory
        shutil.rmtree(GetDirFormFilePath(self.fbxFilePath),True)
        # clean *.anim.bytes files
        for vmdFile in self.__vmdFileList:
            bytesFile = GetDirFormFilePath(vmdFile) + GetFileNameFromFilePath(vmdFile) + '.anim.bytes'
            if os.path.exists(bytesFile):
                os.remove(bytesFile)

    def AsyncProcess(self):
        self.__isProcessing = True
        self.Log('Start convert ' + self.__pmxFile)
        self.fbxFilePath = self.__converter.Process(self.__pmxFile, self.__vmdFileList)
        self.Log('Start modify ' + self.fbxFilePath)
        self.__modifier.Process(self.fbxFilePath)
        # run import process in GUI thread
        def ImportProcess():
            self.__importer.Process(self.fbxFilePath)
            self.CleanTempFiles()
            self.__isProcessing = False
        self.Log('Start import ' + self.fbxFilePath)
        maya.utils.executeInMainThreadWithResult(ImportProcess)
        self.Log('Import successed!')

    def Process(self):
        if not self.__agreeTerms:
            self.MessageBox('You must agree to these terms to continue!')
            return
        if self.__isProcessing:
            self.MessageBox('Processing now!')
            return
        preProcessor = self.Processor('MMD4MayaProcessor', self)
        preProcessor.daemon = True
        preProcessor.start()
