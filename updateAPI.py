#script to install latest version from API repository from GitHub

import os
import time
os.system
#deletes old programs

os.system("rm TGPub.py")
os.system("rm VOCGpub.py")

#os.system("rm updateAPI.py")
#os.system("rm README.md")
#clones repository
os.system("git clone https://github.com/Chriisbrown/API.git")
time.sleep(10)
#moves files out of API file to where update.py stored
os.system("mv /Users/george/Desktop/Anaphite/API/TGpub.py /Users/george/Desktop/Anaphite/TGpub.py")
os.system("mv /Users/george/Desktop/Anaphite/API/VOCGpub.py /Users/george/Desktop/Anaphite/VOCGpub.py")
#os.system("mv /Users/george/Desktop/Anaphite/API/VOCGpub.py /Users/george/Desktop/Anaphite/VOCpub.py")

#removes the API directory now relavent contents have been removed
os.system("rm -r -f /Users/george/Desktop/Anaphite/API")
