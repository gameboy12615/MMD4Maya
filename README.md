master branch: maya2015~maya2016<br>
maya2019 branch: maya2019<br>
## Updated for Maya 2019
1. Updated for maya 2019 (since I really needed it) and should work with all version from (2018, 2019, 2020, 2022)
since they all use pyside2.
I can't test this since I have only 2019 installed...fingers crossed tho :)

2. Also, I don't think this user is active on his github so if he doesn't approve the pull request I will host it on my account

# MMD4Maya
This is maya plug-in which use for importing pmx/pmd model to maya.<br>
It is based on pmx2fbx.exe which is written by http://stereoarts.jp/

## Install:
1. Copy `MMD4Maya.py` and `MMD4Maya` folder to your maya plug-ins folder. like: `Maya2019\bin\plug-ins`.
2. Enable MMD4Maya in maya Plug-in Manager.
3. In Maya-2019 you can find the MMD4Maya on your menu bar

## Steps to import:
1. Select a pmx/pmd file.
2. Select one or multiple vmd files.
3. Check the terms of use then click Process.
![](http://images2015.cnblogs.com/blog/675680/201601/675680-20160131230507896-565921880.jpg)

## Attention:
1. The file name of fbx file and texture files should not be japanese or chinese.
2. You can only import one model at a time, please save your model as the standard fbx file, then create a new scene to import another one.
