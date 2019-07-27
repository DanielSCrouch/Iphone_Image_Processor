import os
import shutil

### shutil appears to drop some files in icloud when moving multiple
### save directories to local first

srcDir = '/Users/DC/Documents/Code/Photo Organiser/srcDirTest'
destDir = '/Users/DC/Documents/Code/Photo Organiser/destDirTest'

# Extract absolute filenames from directory tree
def extractFilePaths(dir, print_dir=False):
    """Return absolute path(s) of Files from dir tree"""
    absPaths = []
    for root, dirs, files in os.walk(dir):
        for name in files:
            absPaths.append(os.path.join(root, name))
        if print_dir:
            for name in dirs:
                print(os.path.join(root, name))
    print(f"[*] {(len(absPaths))} files identified")
    return absPaths

def copyFiles(filePaths, destDir):
    """Copy files from list of paths to direction. Maintain meta data"""
    count = 0
    for absPath in filePaths:
        shutil.copy2(absPath, destDir)
        count += 1
    print(f"[*] {count} files copies to {destDir}")

filePaths = extractFilePaths(srcDir)
copyFiles(filePaths, destDir)
