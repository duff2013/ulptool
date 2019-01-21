#! python3.7
# -*- coding: utf-8 -*-

import wget # Download

## OS interactions
import os
import sys
import glob
import shutil
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

## System parameters
directory = os.getcwd()

temp_dir = "temp_" + str(time.time())
win_dir = "C:\\Users\\<USERNAME>\\AppData\\Local\\Arduino15\\packages\\esp32"
lin_dir = "~/Library/Arduino15/packages/esp32"
mac_dir = "~/Library/Arduino15/packages/esp32"

wdir = "" # Working directory
# core_version = "1.0.0" # 1.0.0 by default, will be determinated after the OS
supported_core_version = ['1.0.0', '1.0.1'] # We can imagine to update this variable from the directory

"""
In the 'arduino_ulp' release you downloaded and unpacked, copy the folder 'ulp' to .../esp32/hardware/esp32/1.0.0/tools/sdk/include/ replacing the existing folder named 'ulp', "1.0.0" is the version number of the core you installed, change version number accordingly.

In the 'arduino_ulp' repository folder you downloaded and unpacked, copy the file 'platform.txt' to .../esp32/hardware/esp32/1.0.0/ replacing the one you have. If you want, just remain the old "platform.txt" so you can revert back. Remeber "1.0.0" has to match your version.

In the 'arduino_ulp' release you downloaded, copy the 'ulp_example' folder to where Arduino saves your sketches.

Create a new folder named exactly 'binutils' in directory .../esp32/tools/

Unpack and copy the folder of the pre-compiled binutils-esp32ulp toolchain you downloaded to .../esp32/tools/binutils/
"""

def main(argv):
    print("Try to create a temp folder (" + os.path.abspath(temp_dir) + ")")
    createFolder(os.path.abspath(temp_dir))
    print("Move to the temp directory and begin download")
    os.chdir(os.path.abspath(temp_dir))
    wget.download(url)

    # See https://docs.python.org/3/library/sys.html#sys.platform
    if sys.platform.startswith('win32'):
        wget.download(binutils_win_url)
        wdir = win_dir.replace("<USERNAME>", getpass.getuser())
	
    elif sys.platform.startswith('linux'):
        wget.download(binutils_linux_url)
        wdir = lin_dir
	
    elif sys.platform.startswith('darwin'):
        wget.download(binutils_mac_url)
        wdir = mac_dir
	
    else:
        print("Unsupported operating system: " + sys.platform)
        exit(1)

    ## Extract all the files
    print("\nExtract the files in temp")
    unzip()

    ## Find and print the core version(s) and check compatibility
    list_core_version = [en for en in os.listdir(os.path.join(wdir,'hardware','esp32')) if os.path.isdir(os.path.join(wdir,'hardware','esp32', en)) and en in supported_core_version]
    list_len = len(list_core_version)
    if list_len > 1:
        print("ULP will be installed for these core versions of the esp32: V" + " - V".join(list_core_version))
    elif list_len == 1:
        print("ULP will be installed for this core version of the esp32: V" + " - V".join(list_core_version))
    else:
        print("No supported version detected. Install ESP32 Arduino core or check the check the Github page of the project for your issue.")
    

    if list_len:
        i = 1
        for core_version in list_core_version:
            ## Print core version
            print("\nFor core version: " + core_version)
            ## Copy the 'ulp' folder
            print("(" + str(i) + "/" + str(list_len*2+1) + ") Copy the 'ulp' folder")
            i += 1
            os.chdir(os.path.join(directory, temp_dir ,'arduino_ulp-master'))
            ulp_dir = os.path.join(wdir,'hardware','esp32', core_version, 'tools', 'sdk', 'include', 'ulp')
            try:
                shutil.rmtree(ulp_dir)
            except:
                print("No 'ulp' directory, 'ulp' will be created")
            shutil.copytree(os.path.abspath('ulp'), ulp_dir)
                
            ## Copy the 'platform.txt' file
            print("(" + str(i) + "/" + str(list_len*2+1) + ") Copy the 'platform.txt' file")
            i += 1
            plt_dir = os.path.join(wdir,'hardware','esp32', core_version)
            shutil.copyfile('platform.txt', os.path.join(plt_dir, 'platform.txt'))

        ## Copy the 'binutils'
        print("\n(" + str(i) + "/" + str(list_len*2+1) + ") Copy 'binutils' folder\n")
        os.chdir(directory), os.chdir(temp_dir)
        bin_dir = os.path.join(wdir,'tools', 'binutils', 'esp32ulp-elf-binutils')
        try:
            shutil.copytree(os.path.abspath('esp32ulp-elf-binutils'), bin_dir)
        except:
            print("Overwrite 'esp32ulp-elf-binutils'")
            shutil.rmtree(bin_dir)
            shutil.copytree(os.path.abspath('esp32ulp-elf-binutils'), bin_dir)
    else:
        print("Installation failed")

    ## Remove the 'temp' directory
    print("Go back in the 'setup' directory and remove the 'temp' directory (" + temp_dir + ")")
    os.chdir(directory)
    shutil.rmtree(os.path.abspath(temp_dir))
    print("Execution time: " + str(time.time()-start_time) + " seconds")
    pause()
    exit(0)

##  Function to create a directory
##  (https://gist.github.com/keithweaver/562d3caa8650eefe7f84fa074e9ca949)
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)


def pause():
    if sys.version_info[0]>2:
        input("Press any key to quit.")
    else:
        raw_input("Press any key to quit.")
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
	
