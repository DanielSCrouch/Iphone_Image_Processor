import os
import shutil
from PIL import Image


# /Users/DC/Documents/Photos/2017/02/10/20170210-193128/.IMG_0004.JPG.icloud
srcDir = '/Users/DC/Documents/Photos/2017/02'
destDir = '/Users/DC/Documents/Photos/2017Sorted'

# Extract absolute filenames from directory tree
def extractFilenames(dir, print_dir=False):
    """Return absolute path(s) of Files from dir tree"""
    absPaths = []
    for root, dirs, files in os.walk(dir):
        for name in files:
            absPaths.append(os.path.join(root, name))
        if print_dir:
            for name in dirs:
                print(os.path.join(root, name))
    return absPaths

def copyFiles(files, destDir):
    for absPath in files:
        shutil.copy(absPath, destDir)

files = extractFilenames(srcDir)
print(files)
copyFiles(files, destDir)

print(len(files), " Files moved.")


# def removeIcloudExt(files):
#     """Return list of files with .icloud ext removed"""
#     modifiedList = []
#     for filename in files:
#         modifiedList.append(filename.replace('.icloud', ''))
#     return modifiedList
# files = removeIcloudExt(files)
