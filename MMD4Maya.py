import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI

from MMD4Maya.Scripts.UI.MainWindow import *

def ShowMainWindow(*args):
    MainWindow()

def ShowHelp(*args):
	cmds.confirmDialog(title = "Help", message = "\
Steps to import:\n\
1. Select a pmx/pmd file.\n\
2. Select one or multiple vmd files.\n\
3. Check the terms of use then click Process.\n\
\n\
Attention:\n\
1. The file name of fbx file and texture files should not be japanese or chinese.\n\
2. You can only import one model at a time, please save your model as the standard fbx file, then create a new scene to import another one.\n\
\n\
Enjoy! >_< \n\
\n\
Author: Takamachi Marisa\n\
Contact: http://weibo.com/u/2832212042",\
	icon = "information")

def CustomMayaMenu():
	gMainWindow = mel.eval('$temp1=$gMainWindow')
	menus = cmds.window(gMainWindow, q = True, menuArray = True)
	found = False
	
	for menu in menus:
		label = cmds.menu(menu, q = True, label = True)
		if label == "MMD4Maya":
			found = True
	
	if found == False:
		customMenu = cmds.menu(parent=gMainWindow, label = 'MMD4Maya')
		cmds.menuItem(parent = customMenu, label = "Open MMD4Maya", c = ShowMainWindow)
		cmds.menuItem(parent = customMenu, label = "Help", c = ShowHelp)

# Initialize the plug-in
def initializePlugin(plugin):
	CustomMayaMenu()

# Uninitialize the plug-in
def uninitializePlugin(plugin):
	pass