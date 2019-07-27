#!/usr/bin/env python

# Standard Python libraries.
import argparse
import os
import time
import shutil
import reverse_geocode
import geocoder
from subprocess import Popen
from subprocess import PIPE

# Third party Python libraries.
# Custom Python libraries.

# ICloud causes latency issues - use on local only

class PhotoOrganiser:
    """Photo Organiser class object"""

    def __init__(self, srcDir, destDir):
        """Iniitialize Organiser class object."""
        self.srcDir = srcDir
        self.destDir = destDir
        if not destDir:
            basename = f"{os.path.basename(srcDir)} sorted {get_timestamp()}"
            os.mkdir(basename)
            self.destDir = os.path.join(os.getcwd(), basename)
        self.srcPaths = []

    def go(self):
        """Copy, sort and rename image files to destination directory"""
        self.updatePaths()
        self.copyFiles()
        self.renameFiles()

    def updatePaths(self, print_dirTree=False):
        """Update srcPaths list of absolute file paths from dir tree"""
        for root, dirs, files in os.walk(self.srcDir):
            for name in files:
                if name != '.DS_Store':
                    self.srcPaths.append(os.path.join(root, name))
            if print_dirTree:
                for name in dirs:
                    print(os.path.join(root, name))
        print(f"[*] {(len(self.srcPaths))} files identified")

    def copyFiles(self):
        """Copy files from srcPaths list to destDir. Maintain meta data"""
        count = 0
        for absPath in self.srcPaths:
            shutil.copy2(absPath, self.destDir)
            count += 1
        print(f"[*] {count} files copied to {self.destDir}")

    def renameFiles(self):
        count = 0
        for root, dirs, files in os.walk(self.destDir):
            for file in files:
                absPath = os.path.join(root, file)
                newName = self.getMetaName(absPath)
                os.rename(absPath, newName)
                count += 1
        print(f"[*] {count} files have been renamed")

    def getMetaName(self, imagePath):
        """Use terminal commands to extract location from EXIF data
            and return name based on meta data"""

        print('.......========.......')
        try:
            cmdLat = "mdls \"" + imagePath + "\" | grep Latitude | awk '{print $3}'"
            subprocess = Popen(cmdLat, shell=True, stdout=PIPE)
            Popen.wait(subprocess)
            lat = subprocess.communicate()[0]
            latFloat = float(lat.decode())
        except Exception as e:
            print("Failed finding lattitude, exception:", e)
            print("lat value: ", lat)

        try:
            cmdLon = "mdls \"" + imagePath + "\" | grep Longitude | awk '{print $3}'"
            lon = (Popen(cmdLon, shell=True, stdout=PIPE).communicate()[0])
            lonFloat = float(lon.decode())
        except Exception as e:
            print("Failed finding longitude, exception:", e)
            print("lon value: ", lat)

        coordinates = (latFloat, lonFloat),
        result = reverse_geocode.search(coordinates)
        location = result[0]['city'] + result[0]['country_code']
        cmdDate = "mdls " + imagePath + "| grep -w kMDItemFSCreationDate | awk '{print $3}'"
        date = (Popen(cmdDate, shell=True, stdout=PIPE).communicate()[0]).decode()
        dateFormat = date.replace('-','-').strip()
        cmdTime = "mdls \"" + imagePath + "\" | grep -w kMDItemFSCreationDate | awk '{print $4}'"
        time = (Popen(cmdTime, shell=True, stdout=PIPE).communicate()[0]).decode()
        timeFormat = time.replace(':','-').strip()
        print(os.path.basename(imagePath), 'has been successful')
        print(f"{dateFormat}_{timeFormat}_{location}")
        return(f"{dateFormat}_{timeFormat}_{location}")

# lat=$(mdls IMG_0149.JPG | grep Latitude | awk '{print $3}')
# lat=$(mdls "/Users/DC/Documents/Code/Photo Organiser/srcDirTest sorted 20190727_140755/IMG_0164.JPG" | grep Latitude | awk '{print $3}')

    # def getMetaName(self, imagePath):
    #     """Use terminal commands to extract location from EXIF data
    #         and return name based on meta data"""
    #     cmdLat = "mdls \"" + imagePath + "\" | grep Latitude | awk '{print $3}'"
    #     cmdLon = "mdls \"" + imagePath + "\" | grep Longitude | awk '{print $3}'"
    #     print('.......========.......')
    #     lat = (Popen(cmdLat, shell=True, stdout=PIPE).communicate()[0])
    #     # lat=$(mdls IMG_0149.JPG | grep Latitude | awk '{print $3}')
    #     # lat=$(mdls "/Users/DC/Documents/Code/Photo Organiser/srcDirTest sorted 20190727_140755/IMG_0164.JPG" | grep Latitude | awk '{print $3}')
    #     lon = (Popen(cmdLon, shell=True, stdout=PIPE).communicate()[0])
    #     try:
    #         latFloat = float(lat.decode())
    #     except Exception as e:
    #         print('problem lat: ',lat.decode(), 'with image: ', imagePath)
    #         print('exception: ', e)
    #     try:
    #         lonFloat = float(lon.decode())
    #     except:
    #         print('problem lon: ',lat.decode(), 'with image: ', imagePath)
    #     coordinates = (latFloat, lonFloat),
    #     result = reverse_geocode.search(coordinates)
    #     location = result[0]['city'] + result[0]['country_code']
    #     cmdDate = "mdls " + imagePath + "| grep -w kMDItemFSCreationDate | awk '{print $3}'"
    #     date = (Popen(cmdDate, shell=True, stdout=PIPE).communicate()[0]).decode()
    #     dateFormat = date.replace('-','-').strip()
    #     cmdTime = "mdls \"" + imagePath + "\" | grep -w kMDItemFSCreationDate | awk '{print $4}'"
    #     time = (Popen(cmdTime, shell=True, stdout=PIPE).communicate()[0]).decode()
    #     timeFormat = time.replace(':','-').strip()
    #     return(f"{dateFormat}_{timeFormat}_{location}")


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
