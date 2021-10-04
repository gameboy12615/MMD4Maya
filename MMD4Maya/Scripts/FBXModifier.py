from MMD4Maya.Scripts.Utils import *

class FBXModifier:

    def __init__(self, mainWindow = None):
        self.mainWindow = mainWindow

    def FormatMaterialName(self, name):
        newName = ''
        if '.' in name:
            nPos = name.find('.')
            newName = 'mat_' + name[0:nPos]
        else:
            newName = 'mat_' + name
        return newName

    def FormatBoneName(self, name):
        newName = 'No_' + name
        newName = newName.replace('!', 'i_')
        newName = newName.replace('.', '_')
        newName = newName.replace('+', '_Plus')
        return newName

    def ModifyMaterialName(self, fbxFilePath):
        inputFbxFile = open(fbxFilePath, 'r', encoding='UTF-8')
        inputFbxLines = inputFbxFile.readlines()
        inputFbxFile.close()
        outputFbxFile = open(fbxFilePath, 'w', encoding='UTF-8')
        tag1 = 'Material::'
        tag2 = ';Material::'
        for line in inputFbxLines:
            if not line:
                break
            if tag2 in line:
                nPos1 = line.find(tag2)
                temp1 = line[0:nPos1]
                temp2 = line[nPos1+len(tag2):len(line)]
                nPos2 = temp2.find(', Model::')
                temp3 = temp2[nPos2:len(temp2)]
                materialName = self.FormatMaterialName(temp2[0:nPos2])
                temp = temp1 + tag2 + materialName + temp3
                outputFbxFile.write(temp)
            elif tag1 in line:
                nPos1 = line.find(tag1)
                temp1 = line[0:nPos1]
                temp2 = line[nPos1+len(tag1):len(line)]
                nPos2 = temp2.find('"')
                temp3 = temp2[nPos2:len(temp2)]
                materialName = self.FormatMaterialName(temp2[0:nPos2])
                temp = temp1 + tag1 + materialName + temp3
                outputFbxFile.write(temp)
            else:
                outputFbxFile.write(line)
        outputFbxFile.close()

    def ModifyBoneName(self, fbxFilePath):
        inputFbxFile = open(fbxFilePath, 'r', encoding='UTF-8')
        inputFbxLines = inputFbxFile.readlines()
        inputFbxFile.close()
        tagBone = '"NodeAttribute::'
        boneNames = []
        # save bone names to array
        for line in inputFbxLines:
            if not line:
                break
            if tagBone in line:
                nPos1 = line.find(tagBone)
                temp = line[nPos1+len(tagBone):len(line)]
                nPos2 = temp.find('",')
                boneName = temp[0:nPos2]
                boneNames.append(boneName)
        # modify bone names in memory
        newBoneNames = []
        for i, boneName in enumerate(boneNames):
            newBoneNames.append(self.FormatBoneName(boneName))
        filterTags = ['NodeAttribute::', 'Model::', 'SubDeformer::']
        inputFbxLinesLenth = len(inputFbxLines)
        for i, line in enumerate(inputFbxLines):
            if not line:
                break
            else:
                for tag in filterTags:
                    if tag in line:
                        self.mainWindow.Log('modify line ' + str(i) + ' of ' + str(inputFbxLinesLenth))
                        for j, boneName in enumerate(boneNames):
                            inputFbxLines[i] = inputFbxLines[i].replace(boneNames[j], newBoneNames[j])
                        break
        # save modified bone names to file
        outputFile = open(fbxFilePath, 'w', encoding='UTF-8')
        for line in inputFbxLines:
            if not line:
                break
            else:
                outputFile.write(line)
        outputFile.close()

    def ModifyXmlFile(self, xmlFilePath):
        extraTextureDir = GetExtraTextureDir()
        textureDir = GetDirFormFilePath(xmlFilePath) + "../"
        ReplaceAllStringInFile(xmlFilePath, '<materialName>', '<materialName>mat_')
        ReplaceAllStringInFile(xmlFilePath, '<fileName>', '<fileName>' + textureDir)
        ReplaceAllStringInFile(xmlFilePath, '<fileName>' + textureDir + 'toon', '<fileName>' + extraTextureDir + 'toon')

    def Process(self, fbxFilePath):
        xmlFilePath = GetDirFormFilePath(fbxFilePath) + GetFileNameFromFilePath(fbxFilePath) + ".xml"
        self.ModifyMaterialName(fbxFilePath)
        self.ModifyBoneName(fbxFilePath)
        self.ModifyXmlFile(xmlFilePath)
        print('modify process completed!')
