from MMD4Maya.Scripts.Utils import *
from xml.dom.minidom import parse
import maya.cmds as cmds

class FBXImporter:

    def ImportFBXFile(self, filePath):
        nPos = filePath.rfind('/')
        fileName = filePath[nPos+1:filePath.rfind('.')]
        importedFile = cmds.file(filePath, i=True, type='FBX', ignoreVersion=True, ra=True, rdn=True, mergeNamespacesOnClash=False, namespace=fileName)
        print importedFile + ' import completed!'

    def ImportTexture(self, filePath):
        dom = parse(filePath)

        texFileNames = dom.getElementsByTagName("fileName")
        textures = []
        for i, texFileName in enumerate(texFileNames) :
            textures.append(texFileName.childNodes[0].data.encode('shift-jis'))
            if cmds.objExists('file' + str(i+1)) :
                continue
            else:
                fileNode = cmds.shadingNode('file', asTexture=True)
                cmds.setAttr(fileNode + '.fileTextureName', textures[i], type="string")
        print textures

        materialNames = dom.getElementsByTagName("materialName")	
        materialID = []
        for i, materialName in enumerate(materialNames) :
            materialID.append(materialName.childNodes[0].data)
        print materialID

        textureIDs = dom.getElementsByTagName("textureID")
        materialTexID = []
        for i, textureID in enumerate(textureIDs) :
            materialTexID.append(textureID.childNodes[0].data)
        print materialTexID

        for i, iMatID in enumerate(materialID) :
            iTexID = int(materialTexID[int(i)])+1
            if(iTexID <= 0):
                continue
            try:
                cmds.connectAttr('file%s.outColor' %iTexID, '%s.color' %iMatID)
                print iMatID
            except:
                continue

    def Process(self, fbxFilePath):
        if os.path.exists(fbxFilePath):
            xmlFilePath = GetDirFormFilePath(fbxFilePath) + GetFileNameFromFilePath(fbxFilePath) + ".xml"
            self.ImportFBXFile(fbxFilePath)
            self.ImportTexture(xmlFilePath)
        return