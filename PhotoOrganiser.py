#!/usr/bin/env python

# Standard Python libraries.
import argparse
import os
import time
import shutil
import reverse_geocode
import geocoder
import subprocess
import pathlib
import re

# Third party Python libraries.
# Custom Python libraries.

# ICloud seems to cause latency issues - use on local only

global FILETYPES
FILETYPES = ('.jpg', '.JPG', '.MOV', '.HEIC')

class PhotoOrganiser:
    """Photo Organiser class object"""

    def __init__(self, srcDir, destDir):
        """Iniitialize Organiser class object."""
        self.srcDir = srcDir
        self.destDir = destDir

        # If destination directory not specified then create
        if not destDir:
            basename = f"{os.path.basename(srcDir)} sorted {get_timestamp()}"
            os.mkdir(basename)
            self.destDir = os.path.join(os.getcwd(), basename)

    def go(self):
        """Copy, sort and rename image files to destination directory"""
        print('running')
        if self.checkFileTypes():
            self.copyFiles()
            self.metaNaming()

    def checkFileTypes(self):
        absPaths = self.getPaths()
        for absPath in absPaths:
            baseName, ext = os.path.splitext(os.path.basename(absPath))
            if ext not in FILETYPES:
                response = input(f"{ext} found in source directory, continue? [Y,n]")
                if response == 'n' or 'N':
                    return False
                else:
                    return True
        return True

    def copyFiles(self):
        """Copy files from srcPaths to destDir. Maintain meta data"""
        count = 0
        for absPath in self.getPaths():
            shutil.copy2(absPath, self.destDir)
            count += 1
        print(f"[*] {count} files copied to {self.destDir}")

    def getPaths(self, print_dirTree=False):
        """Return srcPaths list of absolute file paths from dir tree"""
        srcPaths = []
        for root, dirs, files in os.walk(self.srcDir):
            for name in files:
                if name != '.DS_Store':
                    srcPaths.append(os.path.join(root, name))
            if print_dirTree:
                for name in dirs:
                    print(os.path.join(root, name))
        print(f"[*] {(len(srcPaths))} files identified")
        return srcPaths

    def metaNaming(self):
        """Use terminal commands to extract location from EXIF data
            and update destDir file names accordingly"""
        count = 0
        pic_file = pathlib.Path(self.destDir).glob('*.*')
        for file in pic_file:
            baseName, ext = os.path.splitext(file)
            if ext in FILETYPES:
                print(file)
                command = ['mdls',
                           '-name', 'kMDItemLatitude',
                           '-name', 'kMDItemLongitude',
                           str(file)]
                output = subprocess.check_output(command, encoding='utf-8')

                print(output)
                # Parse the output
                lines = output.splitlines()
                values = [line.split()[-1] for line in lines]

                # Convert to float, check value coordinates
                geoLocate = False
                try:
                    lat, lon = [float(value) for value in values]
                    geoLocate = True
                except:
                    lat, lon = values

                # Get geolocation
                location = ''
                if geoLocate:
                    result = reverse_geocode.search([(lat, lon)])
                    location = '_' + result[0]['city'] + result[0]['country_code']

                # Get creation date and time
                command = ['mdls',
                           '-name', 'kMDItemFSCreationDate',
                           str(file)]
                output = subprocess.check_output(command, encoding='utf-8')

                # Parse the output
                date = re.search('\d{4}-\d{2}-\d{2}', output).group(0)
                time = re.search('\d{2}:\d{2}:\d{2}', output).group(0).replace(':', '-')

                # Rename file
                newBaseName = f"{date}_{time}{location}"
                absPath = os.path.join(self.destDir, file)
                self.renameFile(absPath, newBaseName)

                count += 1
            else:
                print('file type not included: ', file)
        print(f"[*] {count} files renamed")

    def renameFile(self, absPath, newBaseName):
        """Rename file in path with new base name, keep extension"""
        dir = os.path.dirname(absPath)
        baseName, ext = os.path.splitext(os.path.basename(absPath))
        newName = os.path.join(dir, newBaseName + ext)
        os.rename(absPath, newName)

def get_timestamp():
    """Retrieve a pre-formated datetimestamp."""
    now = time.localtime()
    timestamp = time.strftime("%Y%m%d_%H%M%S", now)
    return timestamp

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="PhotoOrganiser - copy, sort and rename photos")
    parser.add_argument(
        "-sd",
        dest="srcDir",
        action="store",
        required=True,
        help="Directory to copy images from."
    )
    parser.add_argument(
        "-dd",
        dest="destDir",
        action="store",
        default=False,
        help="Directory to copy to."
    )

    args = parser.parse_args()

    if not os.path.exists(args.srcDir):
        print("[!] Specify a valid file containing images with -sd")
        sys.exit(0)

    print(f"[*] Initiation timestamp: {get_timestamp()}")
    po = PhotoOrganiser(**vars(args))
    po.go()
    print(f"[*] Completion timestamp: {get_timestamp()}")

    print("[+] Done!")
