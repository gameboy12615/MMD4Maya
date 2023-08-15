from MMD4Maya.Scripts.FBXConverter import *
from MMD4Maya.Scripts.FBXImporter import *
from MMD4Maya.Scripts.FBXModifier import *
from MMD4Maya.Scripts.UI.ExplorerWindow import *
from MMD4Maya.Scripts.Utils import *
from PySide2 import QtCore, QtWidgets

import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
import maya.utils
import shiboken2
import shutil
import threading
import os
import glob

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
        self.__selectedVmdFileIndex = cmds.textScrollList(self.vmdScrollList, query = True, selectIndexedItem = True)[0]

    def OnDeleteKeyClicked(self, *args):
        self.DeleteSelectedVmdFile()

    def OnDeleteButtonClicked(self, *args):
        self.DeleteSelectedVmdFile()

    def OnTransparencyCheckBoxOn(self, *args):
        self.__importTransparency = True

    def OnTransparencyCheckBoxOff(self, *args):
        self.__importTransparency = False

    def OnTermsCheckBoxOn(self, *args):
        self.__agreeTerms = True

    def OnTermsCheckBoxOff(self, *args):
        self.__agreeTerms = False

    def OnProcessButtonClicked(self, *args):
        self.Process()

    def __init__(self):
        # private attribute
        self.__converter = FBXConverter(self)
        self.__modifier = FBXModifier(self)
        self.__importer = FBXImporter(self)
        self.__pmxFile = ''
        self.__vmdFileList = []
        self.__selectedVmdFileIndex = 0
        self.__agreeTerms = False
        self.__importTransparency = False
        self.__isProcessing = False
        self.__isHasTransparencyTexture = False

        # create window
        if cmds.window("MMD4Maya", exists = True):
            cmds.deleteUI("MMD4Maya")
        window = cmds.window(title="MMD4Maya", widthHeight=(603, 580), 
                             sizeable = False, minimizeButton = False, maximizeButton = False)
        # create layout
        mainLayout = cmds.columnLayout(width = 600)

        importLayout = cmds.rowColumnLayout(parent = mainLayout, numberOfColumns=2, columnWidth=[(1, 450), (2, 150)] )
        self.pmxText = cmds.textField(parent = importLayout)
        cmds.button(parent = importLayout, label = 'Import pmx/pmd file', command = self.OnImportPmxButtonClicked)
        self.vmdScrollList = cmds.textScrollList(parent = importLayout, height = 110, allowMultiSelection = False, 
                                                 selectCommand = self.OnSelectVmdFile, deleteKeyCommand = self.OnDeleteKeyClicked)
        importButtonLayout = cmds.columnLayout(parent = importLayout, width = 149, rowSpacing = 1)
        cmds.button(parent = importButtonLayout, label = 'Add vmd file', width = 149, height = 54, command = self.OnAddVmdButtonClicked)
        cmds.button(parent = importButtonLayout, label = 'Delete selected vmd file', width = 149, height = 54, command = self.OnDeleteButtonClicked)

        processLayout = cmds.columnLayout(parent = mainLayout, width = 600)
        cmds.separator(parent = processLayout, height = 8, style = 'none')

        settingLayout = cmds.rowColumnLayout(parent = processLayout, numberOfColumns=2, columnWidth=[(1, 450), (2, 150)] )
        cmds.text('Log viewer:', font = "boldLabelFont", align='left', parent = settingLayout)
        cmds.checkBox(parent = settingLayout, label='Import Transparency', 
                      onCommand = self.OnTransparencyCheckBoxOn, offCommand = self.OnTransparencyCheckBoxOff)

        cmds.separator(parent = processLayout, height = 8, style = 'none')
        self.logText = cmds.scrollField(parent = processLayout, width = 600, height = 297, editable = False)
        cmds.separator(parent = processLayout, height = 10, style = 'none')
        cmds.checkBox(parent = processLayout, label='You must agree to these terms of use before using the model/motion.', 
                      onCommand = self.OnTermsCheckBoxOn, offCommand = self.OnTermsCheckBoxOff)
        cmds.separator(parent = processLayout, height = 10, style = 'none')
        self.processButton = cmds.button(parent = processLayout, label = 'Process', width = 600, height = 60, 
                                         command = self.OnProcessButtonClicked)
        # show window
        cmds.showWindow(window)

    def CheckReadmeFile(self, pmxFilePath):
        def ShowDefaultReadme():
            self.Log('================================= ReadMe ===================================')
            self.Log("Please contact the model/motion author if you need them for commercial use!")
        self.ClearLog()
        txtFilenames = glob.glob(GetDirFormFilePath(pmxFilePath) + '*.txt')
        if txtFilenames:
            for readmeFile in txtFilenames:
                readmeFile = ConvertToUnixPath(readmeFile)
                if os.path.exists(readmeFile):
                    inputFile = open(readmeFile, encoding=CheckCharset(readmeFile), errors='ignore')
                    lines = inputFile.readlines()
                    inputFile.close()
                    try:
                        fileName = GetFileNameFromFilePath(readmeFile).decode('shift-jis') + '.txt'
                        self.Log('================================= ' + fileName + ' ===================================')
                        for line in lines:
                            self.Log(line.decode('shift-jis'))
                    except:
                        ShowDefaultReadme()
        else:
            ShowDefaultReadme()

    def SetPmxFile(self, fileName):
        if(IsContainEastAsianWord(fileName)):
            self.MessageBox('Only support English path!')
            return
        self.__pmxFile = ConvertToUnixPath(fileName).encode('ascii','ignore').decode()
        cmds.textField(self.pmxText, edit=True, text=self.__pmxFile)
        self.CheckReadmeFile(self.__pmxFile)

    def AddVmdFile(self, fileName):
        if(IsContainEastAsianWord(fileName)):
            self.MessageBox('Only support English path!')
            return
        fileName = ConvertToUnixPath(fileName).encode('ascii','ignore').decode()
        self.__vmdFileList.append(fileName)
        cmds.textScrollList(self.vmdScrollList, edit = True, append=[fileName])

    def SetHasTransparencyTexture(self, isHas):
        self.__isHasTransparencyTexture = isHas

    def IsImportTransparency(self):
        return self.__importTransparency

    def Log(self, log):
        def WriteToLog(log):
            cmds.scrollField(self.logText, edit = True, insertText = log + '\n')
        # executeInMainThreadWithResult() can't call recursively, so Log() can't be called in executeInMainThreadWithResult()
        maya.utils.executeInMainThreadWithResult(WriteToLog, log)

    def ClearLog(self):
        cmds.scrollField(self.logText, edit = True, clear = True)

    def MessageBox(self, msg = ''):
        cmds.confirmDialog(title='Confirm', message=msg)

    def ShowExplorer(self, type = 'pmd'):
        ptr = OpenMayaUI.MQtUtil.mainWindow()
        widget = shiboken2.wrapInstance(int(ptr),QtWidgets.QWidget)
        explorerWin = ExplorerWindow(widget, type, self)
        explorerWin.show()

    def DeleteSelectedVmdFile(self):
        index = int(self.__selectedVmdFileIndex) - 1
        lenth = len(self.__vmdFileList)
        if self.__selectedVmdFileIndex > 0 and index < lenth:
            cmds.textScrollList(self.vmdScrollList, edit = True, removeIndexedItem = self.__selectedVmdFileIndex)
            del self.__vmdFileList[index]

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
        self.__isHasTransparencyTexture = False
        try:
            self.Log('Start convert ' + self.__pmxFile)
            self.fbxFilePath = self.__converter.Process(self.__pmxFile, self.__vmdFileList)
            self.Log('Start modify ' + self.fbxFilePath)
            self.__modifier.Process(self.fbxFilePath)
            # run import process in GUI thread
            def ImportProcess():
                self.__importer.Process(self.fbxFilePath)
            self.Log('Start import ' + self.fbxFilePath)
            maya.utils.executeInMainThreadWithResult(ImportProcess)
            self.Log('Import successed!')
        finally:
            self.CleanTempFiles()
            self.__isProcessing = False
            if(self.__importTransparency and self.__isHasTransparencyTexture):
                cmds.setAttr('hardwareRenderingGlobals.transparencyAlgorithm', 3)
            else:
                cmds.setAttr('hardwareRenderingGlobals.transparencyAlgorithm', 1)

    def Process(self):
        if not self.__agreeTerms:
            self.MessageBox('You must agree to these terms to continue!')
            return
        if self.__isProcessing:
            self.MessageBox('Processing now!')
            return
        if self.__pmxFile is '':
            self.MessageBox('Please import a pmx/pmd file!')
            return
        self.ClearLog()
        preProcessor = self.Processor('MMD4MayaProcessor', self)
        preProcessor.daemon = True
        preProcessor.start()
