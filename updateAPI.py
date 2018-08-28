#script to install latest version from API repository from GitHub
#script to install latest version from API repository from GitHub

import os
import time
os.system
#deletes old programs

os.system("rm TGpub.py")
os.system("rm VOCGpub.py")
os.system("rm updateAPI.py")
#os.system("rm updateAPI.py")
#os.system("rm README.md")
#clones repository
os.system("git clone https://github.com/Chriisbrown/API.git")
time.sleep(20)
#moves files out of API file to where update.py stored
os.system("mv /home/pi/Temperature/API/TGpub.py /home/pi/Temperature/TGpub.py")
os.system("mv /home/pi/Temperature/API/VOCGpub.py /home/pi/Temperature/VOCGpub.py")
os.system("mv /home/pi/Temperature/API/VOCGpub.py /home/pi/Temperature/updateAPI.py")


#removes the API directory now relavent contents have been removed
os.system("rm -r -f /home/pi/Temperature/API")
