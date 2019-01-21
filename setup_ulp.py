# -*- coding: utf-8 -*-
#! python3.7
import wget # Download

## OS interactions
import os
import sys
import glob
import shutil
import platform # https://stackoverflow.com/questions/110362/how-can-i-find-the-current-os-in-python
import getpass # https://www.saltycrane.com/blog/2011/11/how-get-username-home-directory-and-hostname-python/

import zipfile # Extract zip files
import tarfile

import time

start_time = time.time()

url = "https://github.com/duff2013/arduino_ulp/archive/master.zip"
## Need to be manualy updated
binutils_win_url = "https://github.com/espressif/binutils-esp32ulp/releases/download/v2.28.51-esp32ulp-20180809/binutils-esp32ulp-win32-2.28.51-esp32ulp-20180809.zip"
binutils_linux_url = "https://github.com/espressif/binutils-esp32ulp/releases/download/v2.28.51-esp32ulp-20180809/binutils-esp32ulp-linux64-2.28.51-esp32ulp-20180809.tar.gz"
binutils_mac_url = "https://github.com/espressif/binutils-esp32ulp/releases/download/v2.28.51-esp32ulp-20180809/binutils-esp32ulp-macos-2.28.51-esp32ulp-20180809.tar.gz"

directory = os.getcwd()
system = platform.system()
temp_dir = "./temp_" + str(time.time())
win_dir = "C:\\Users\\<USERNAME>\\AppData\\Local\\Arduino15\\packages\\esp32"
lin_dir = "~/Library/Arduino15/packages/esp32"
mac_dir = "~/Library/Arduino15/packages/esp32"
wdir = "" # Working directory
core_version = "1.0.0" # 1.0.0 by default

"""
In the 'arduino_ulp' release you downloaded and unpacked, copy the folder 'ulp' to .../esp32/hardware/esp32/1.0.0/tools/sdk/include/ replacing the existing folder named 'ulp', "1.0.0" is the version number of the core you installed, change version number accordingly.

In the 'arduino_ulp' repository folder you downloaded and unpacked, copy the file 'platform.txt' to .../esp32/hardware/esp32/1.0.0/ replacing the one you have. If you want, just remain the old "platform.txt" so you can revert back. Remeber "1.0.0" has to match your version.

In the 'arduino_ulp' release you downloaded, copy the 'ulp_example' folder to where Arduino saves your sketches.

Create a new folder named exactly 'binutils' in directory .../esp32/tools/

Unpack and copy the folder of the pre-compiled binutils-esp32ulp toolchain you downloaded to .../esp32/tools/binutils/
"""

def main(argv):
    print("Try to create a temp folder")
    createFolder(temp_dir)
    print("Move to the temp directory and begin download")
    os.chdir(temp_dir)
    wget.download(url)
    
    # system = "Linux" # To test tar decrompression
    if system=="Windows":
        wget.download(binutils_win_url)
        wdir = win_dir.replace("<USERNAME>", getpass.getuser())        
        #print(system)
	
    elif system=="Linux":
        wget.download(binutils_linux_url)
        wdir = lin_dir
	
    elif system=="Mac":
        wget.download(binutils_mac_url)
        wdir = mac_dir
	
    else:
        print("Unsupported operating system: " + system)
        exit(0)
        
    print("\nUncompress the files in temp")
    unzip()
    core_version = os.listdir(wdir + '\\hardware\\esp32')[0]
    print("ESP32 core version: " + core_version)
    print("\n(1/3) Copy the /ulp folder")
    os.chdir('./arduino_ulp-master')
    ulp_dir = wdir + "/hardware/esp32/" + core_version + "/tools/sdk/include/ulp"
    shutil.rmtree(ulp_dir)
    shutil.copytree('./ulp', ulp_dir)
    print("(2/3) Copy the plateform.txt file")
    plt_dir = wdir + "/hardware/esp32/" + core_version + "/"
    shutil.copyfile('platform.txt', plt_dir + 'platform.txt')
    print("(3/3) Copy /binutils folder\n")
    
    os.chdir(directory), os.chdir(temp_dir)
    bin_dir = wdir + "/tools/binutils/esp32ulp-elf-binutils"
    try:
        shutil.copytree('./esp32ulp-elf-binutils', bin_dir)
    except:
        shutil.rmtree(bin_dir)
        shutil.copytree('./esp32ulp-elf-binutils', bin_dir)
        
    print("Go back in the setup directory and remove the temp folder")
    #input()
    os.chdir(directory)
    shutil.rmtree(temp_dir)

    #wget.download(url)
    print("Execution time: " + str(time.time()-start_time) + " seconds")
    input("Press any key to quit.")

##  Function to create a directory
##  (https://gist.github.com/keithweaver/562d3caa8650eefe7f84fa074e9ca949)
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

def unzip():
    zip_list = glob.glob('*.zip')
    tar_gz_list = glob.glob('*.tar.gz')
    tar_list = glob.glob('*.tar')
    
    for file in zip_list:
        with zipfile.ZipFile(file, 'r') as zf:
            zf.extractall()
            zf.close()
            
    for file in tar_gz_list:
        with tarfile.open(file, "r:gz") as tar:
            tar.extractall()
            tar.close()
            
    for file in tar_list:
        with tarfile.open(file, "r:") as tar:
            tar.extractall()
            tar.close()

if __name__ == '__main__':
    main(sys.argv[1:])
