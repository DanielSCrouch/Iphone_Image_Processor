from subprocess import Popen
from subprocess import PIPE
import os

imagePath = "IMG_1096.HEIC"

cmdLat = "mdls " + imagePath + "| grep Latitude | awk '{print $3}'"
cmdLon = "mdls " + imagePath + "| grep Longitude | awk '{print $3}'"

def terminalReturn(cmd):
    """Returns command from terminal. SECURITY RISK if missued, see docs"""
    return Popen(cmd, shell=True, stdout=PIPE).communicate()[0]

lat = terminalReturn(cmdLat)
lon = terminalReturn(cmdLon)

print('IMG_1096.HEIC (', lat, ', ', lon, ')')
