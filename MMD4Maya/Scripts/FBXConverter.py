import subprocess
from MMD4Maya.Scripts.Utils import *

class FBXConverter:

    exeFile = "PMX2FBX/pmx2fbx.exe"

    def __init__(self, mainWindow = None):
        self.mainWindow = mainWindow

    def ExecutePMX2FBX(self, command, cmdConsole = True):
        if cmdConsole:
            subprocess.call(command)
        else:
            # readline will block when convert animation(if has vmd file), fix later.
            subProcess = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            # print pmx2fbx log
            while subProcess.poll() == None:
                log = subProcess.stdout.readline()
                self.mainWindow.Log(line.decode('shift-jis'))

    def Process(self, pmxFile, vmdFileList = []):
        currentDir = GetScriptsRootDir()
        pmxFile = ConvertToUnixPath(pmxFile)
        pmxFileName = GetFileNameFromFilePath(pmxFile)
        pmxDir = GetDirFormFilePath(pmxFile)

        # create temp dir
        newDir = CreateDirInParentDir(pmxDir, '.temp_' + pmxFileName)
        outputFile = newDir + pmxFileName + ".fbx"

        arguments = ""
        arguments += "\""
        arguments += pmxFile
        arguments += "\" "
        for vmdFile in vmdFileList:
            arguments += "\""
            arguments += ConvertToUnixPath(vmdFile)
            arguments += "\" "

        command = currentDir + self.exeFile + " -o \"" + outputFile + "\" " + arguments
        self.mainWindow.Log(command)
        self.ExecutePMX2FBX(command)
        self.mainWindow.Log("convert process finished!")
        return outputFile
