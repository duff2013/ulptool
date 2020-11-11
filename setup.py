#! python3.7
# -*- coding: utf-8 -*-

"""
Todo :

[x] Add offline mode from the ulp folder (launch the script from the extracted archive from github)
[x] Add offline mode for binutils (copy unpackted folder or .tar/.tar.gz/.zip file in the same directory as this script)
[x] Install ULP examples in the skecth directory (need to read preference file)
[ ] Add supported core version check from file

What this script does (hybrid online or offline installation are possible):

[x] Move the ulptool folder you downloaded and unpacked to the tools folder here -> .../esp32/tools/.

[x] Copy the 'platform.local.txt' file to .../esp32/hardware/esp32/1.0.0/. Remember 1.0.0 has to match your esp32 core version.

[x] In the ulptool release you downloaded, move or copy the .../esp32/tools/ulptool/src/ulp_examples folder to where Arduino saves your sketches.

[x] Move esp32ulp-elf-binutils folder you downloaded and unpacked to -> .../esp32/tools/ulptool/src/.

Tested on:

Windows 10, Python 3 and 2
"""

## 'wget' isn't a base Python lib
try:
    import wget # Download
except:
    from six.moves import urllib
    print("Missing wget module, urllib will be used instead")

## https://stackoverflow.com/questions/12965203/how-to-get-json-from-webpage-into-python-script
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import json

## OS interactions
import os
import sys
import glob
import shutil

import zipfile # Extract zip files
import tarfile

import time
start_time = time.time()

## url to get the JSON from the 'binutils' and 'ulptool' Github
url_binutils = "https://api.github.com/repos/espressif/binutils-esp32ulp/releases"
url_ulptool = "https://api.github.com/repos/duff2013/ulptool/releases"

## System parameters
directory = os.getcwd()

temp_dir = "temp_" + str(time.time())
win_dir = "~\\AppData\\Local\\Arduino15\\packages\\esp32"
win_dir_old = "~\\AppData\\Roaming\\Arduino15\\packages\\esp32"
lin_dir = "~/.arduino15/packages/esp32"
mac_dir = "~/Library/Arduino15/packages/esp32"

wdir = "" # Working directory
# core_version = "1.0.0" # 1.0.0 by default, will be determinated after the OS
supported_core_version = ['1.0.0', '1.0.1'] # We can imagine to update this variable from the directory

def main(argv):
    flag_linux32 = 0
    
    ## Create a temp directory in thr current working directory
    print("Create a temp folder (" + os.path.abspath(temp_dir) + ").")
    createFolder(os.path.abspath(temp_dir))
    print("Move to the temp directory.")
    os.chdir(os.path.abspath(temp_dir))
    
    ## Select online or offline mode for ulp install (automatic)
    ulp_offline = 0
    binutils_offline = 1
    clean_binutils = 0

    ## Check if we are in the 'ulptool-master' folder
    if (os.path.basename(directory).startswith("ulptool") or os.path.basename(directory).startswith("duff2013-ulptool")) and os.path.exists(os.path.join(directory, 'src')) and os.path.exists(os.path.join(directory, 'platform.local.txt')):
        ulp_offline = 1
        ulp_dirname = os.path.basename(directory)         
        print("ULP tools install, offline mode")

    else:
        print("Download 'ULP tools' files")
        url = get_ulptool_lr()[1]
        dl(url)
        
    # See https://docs.python.org/3/library/sys.html#sys.platform
    if sys.platform.startswith('win32'):
        _, archive = filedirstartswith("binutils-esp32ulp-win32-", directory)
        direct, _ = filedirstartswith("esp32ulp-elf-binutils", directory)
        if direct:
            os.chdir(directory)
            direct = direct[len(direct)-1]
        elif archive:
            os.chdir(directory)
            unzip(archive[len(archive)-1])
            direct = "esp32ulp-elf-binutils"
            clean_binutils = 1
        else:
            # Online installation for binutils
            binutils_offline = 0
            try:
                _, _, binutils_win_url = get_binutils_urls(get_json(url_binutils))
            except:
                binutils_win_url = "https://github.com/espressif/binutils-esp32ulp/releases/download/v2.28.51-esp32ulp-20180809/binutils-esp32ulp-win32-2.28.51-esp32ulp-20180809.zip"
            dl(binutils_win_url)

        if binutils_offline:
            print("'binutils' offline installation mode for Windows")
        wdir = os.path.expanduser(win_dir)

        if os.path.exists(wdir):
            print("'Arduino15' directory found on your Windows machine.")
        else:
            wdir = os.path.expanduser(win_dir_old)
            if os.path.exists(wdir):
                print("'Arduino15' directory found on your Windows machine, but you are using an old version of Arduino. Please consider to first update the Arduino IDE and to run this script again after.")
            else:
                print("Install the Arduino IDE before running this script.")
                supported_core_version.clear() # Disable installation
            
    elif sys.platform.startswith('linux'):
        if sys.maxsize > 2**32:
            flag_linux32 = 0
            _, archive = filedirstartswith("binutils-esp32ulp-linux64-", directory)
            direct, _ = filedirstartswith("esp32ulp-elf-binutils", directory)
            if direct:
                os.chdir(directory)
                direct = direct[len(direct)-1]
            elif archive:
                os.chdir(directory)
                unzip(archive[len(archive)-1])
                direct = "esp32ulp-elf-binutils"
                clean_binutils = 1
            else:
                # Online installation
                binutils_offline = 0
                try:
                    binutils_linux_url, _, _ = get_binutils_urls(get_json(url_binutils))
                except:
                    binutils_linux_url = "https://github.com/espressif/binutils-esp32ulp/releases/download/v2.28.51-esp32ulp-20180809/binutils-esp32ulp-linux64-2.28.51-esp32ulp-20180809.tar.gz"
                dl(binutils_linux_url)

            if binutils_offline:
                print("'binutils' offline installation mode for Linux")
        else:
            print('There isn\'t a compatible version of binutils for 32bit linux operating systems, go to \'https://github.com/espressif/binutils-esp32ulp/issues/1\' to build the utilities')
            flag_linux32 = 1
        wdir = os.path.expanduser(lin_dir)
        if os.path.exists(wdir):
            print("'Arduino15' directory found on your Linux machine.")
        else:
            print("Install the Arduino IDE before running this script.")
            supported_core_version.clear()
	
    elif sys.platform.startswith('darwin'):
        _, archive = filedirstartswith("binutils-esp32ulp-macos-", directory)
        direct, _ = filedirstartswith("esp32ulp-elf-binutils", directory)
        if direct:
            os.chdir(directory)
            direct = direct[len(direct)-1]
        elif archive:
            os.chdir(directory)
            unzip(archive[len(archive)-1])
            direct = "esp32ulp-elf-binutils"
            clean_binutils = 1
        else:
            # Online install
            binutils_offline = 0
            try:
                _, binutils_mac_url, _ = get_binutils_urls(get_json(url_binutils))
            except:
                binutils_mac_url = "https://github.com/espressif/binutils-esp32ulp/releases/download/v2.28.51-esp32ulp-20180809/binutils-esp32ulp-macos-2.28.51-esp32ulp-20180809.tar.gz"
            dl(binutils_mac_url)

        if binutils_offline:
            print("'binutils' offline installation mode for Mac OS")
        wdir = os.path.expanduser(mac_dir)

        if os.path.exists(wdir):
            print("'Arduino15' directory found on your Mac OS machine.")
        else:
            print("Install the Arduino IDE before running this script.")
            supported_core_version.clear()
	
    else:
        print("Unsupported operating system: " + sys.platform)
        exit(1)

    ## Extract all the files if any online installation
    if not (binutils_offline and ulp_offline): 
        print("\nExtract the files in temp")
        os.chdir(os.path.join(directory, temp_dir))
        unzip()
        
        if not ulp_offline:
            ulp_dirname,_ = filedirstartswith("duff2013-ulptool")   ## Find the folder name, since this one is unknown before download, we have to find it...
            ulp_dirname = ulp_dirname[0]

    ## Find and print the core version(s) and check compatibility
    try:    
        list_core_version = [en for en in os.listdir(os.path.join(wdir,'hardware','esp32')) if os.path.isdir(os.path.join(wdir,'hardware','esp32', en)) and en in supported_core_version]
        list_len = len(list_core_version)
        if list_len > 1:
            print("ULP will be installed for these core versions of the esp32: \nV" + "\nV".join(list_core_version))
        elif list_len == 1:
            print("ULP will be installed for this core version of the esp32: \nV" + "\nV".join(list_core_version))
        else:
            print("No supported version detected. Install ESP32 Arduino core or look on the Github page of the project for your issue.")
            print("ESP32 supported Arduino core version are: \nV" + '\nV'.join(supported_core_version))
            
    except:
        list_len = 0
        print("No supported version detected. Install ESP32 Arduino core or look on the Github page of the project for your issue.")
        print("ESP32 supported Arduino core version are: \nV" + '\nV'.join(supported_core_version))

    ## Start the installation
    if list_len:
        nbr_step = str(list_len+3)
        i = 1
        for core_version in list_core_version:
            ## Print core version
            print("\nFor core version: " + core_version)
            
            ## Copy the 'platform.local.txt' file
            if ulp_offline:
                os.chdir(directory)
            else:
                os.chdir(os.path.join(directory, temp_dir , ulp_dirname))

            print("(" + str(i) + "/" + nbr_step + ") Copy the 'platform.local.txt' file.")
            i += 1
            plt_dir = os.path.join(wdir,'hardware','esp32', core_version)
            shutil.copyfile('platform.local.txt', os.path.join(plt_dir, 'platform.local.txt'))

        ## Create the tool directory and tree       
        ulptool_dir = os.path.join(wdir,'tools','ulptool')
        if os.path.exists(ulptool_dir):
            shutil.rmtree(ulptool_dir)
            print('Remove previous install.')
        createFolder(ulptool_dir)
        createFolder(os.path.join(ulptool_dir, 'src'))

        ## Copy the 'binutils' to '.../ulptool/src/'
        if not flag_linux32:
            print("\n(" + str(i) + "/" + nbr_step + ") Copy 'binutils' folder.")
            if binutils_offline:
                os.chdir(directory)
            else:
                os.chdir(os.path.join(directory, temp_dir))

            #bin_dir = directory if ulp_offline else os.path.join(directory, temp_dir, 'ulptool-master')
            bin_dir = os.path.join(ulptool_dir, 'src', 'esp32ulp-elf-binutils')

            try:
                shutil.copytree(os.path.abspath('esp32ulp-elf-binutils'), bin_dir)
            except:
                print("Overwrite 'esp32ulp-elf-binutils'.\n")
                shutil.rmtree(bin_dir)
                shutil.copytree(os.path.abspath('esp32ulp-elf-binutils'), bin_dir)
            if clean_binutils:
                shutil.rmtree(os.path.join(directory, direct))
            
        else:
            print("\n(" + str(i) + "/" + nbr_step + ") Installation failed, you have to compile the binutils tool yourself (there isn't a support for Linux 32 bit).\n")
        i += 1

        ## Copy the 'ulptool' folder file by file (to make a clean install)
        print("(" + str(i) + "/" + nbr_step + ") Copy the 'ulptool' folder.")
        i += 1

        ulp_wdir = directory if ulp_offline else os.path.join(directory, temp_dir, ulp_dirname)
        shutil.copytree(os.path.join(ulp_wdir , 'src', 'esp32'), os.path.join(ulptool_dir, 'src', 'esp32'))
        shutil.copytree(os.path.join(ulp_wdir , 'src', 'ld'), os.path.join(ulptool_dir, 'src', 'ld'))
        shutil.copyfile(os.path.join(ulp_wdir , 'README.md'), os.path.join(ulptool_dir, 'README.md'))
        shutil.copyfile(os.path.join(ulp_wdir , 'platform.local.txt'), os.path.join(ulptool_dir, 'platform.local.txt'))
        shutil.copyfile(os.path.join(ulp_wdir , 'revisions.md'), os.path.join(ulptool_dir, 'revisions.md'))
        shutil.copyfile(os.path.join(ulp_wdir , 'src', 'esp32ulp_build_recipe.py'), os.path.join(ulptool_dir, 'src', 'esp32ulp_build_recipe.py'))
        shutil.copyfile(os.path.join(ulp_wdir , 'src', 'esp32ulp_mapgen.py'), os.path.join(ulptool_dir, 'src', 'esp32ulp_mapgen.py'))
	try:
		shutil.copyfile(os.path.join(ulp_wdir , 'src', 'recipe_c_combine_pattern.py'), os.path.join(ulptool_dir, 'src', 'recipe_c_combine_pattern.py'))
	except:
		pass
        ## Copy the ULP example to the sketch directory
        sk_dir = get_sketchpath()
        print("(" + str(i) + "/" + nbr_step + ") Copy the 'ulp_examples' folder to your sketch directory (" + sk_dir + ").")
        try:
            shutil.copytree(os.path.join(ulp_wdir , 'src', 'ulp_examples'), os.path.join(sk_dir, 'ulp_examples'))
        except:
            print("Overwrite 'ulp_examples'.\n")
            shutil.rmtree(os.path.join(sk_dir, 'ulp_examples'))
            shutil.copytree(os.path.join(ulp_wdir , 'src', 'ulp_examples'), os.path.join(sk_dir, 'ulp_examples'))

    ## Remove the 'temp' directory
    print("Go back in the 'setup' directory and remove the 'temp' directory (" + temp_dir + ").")
    os.chdir(directory)
    shutil.rmtree(os.path.abspath(temp_dir))
    print("Execution time: " + str(time.time()-start_time) + " seconds.")
    pause()
    exit(0)

        ######################################
        ##                                  ##
        ##      Functions' definitions      ##
        ##                                  ##
        ######################################
    
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

def unzip(filename = None): # Extract all the files in current directory
    if filename == None:
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
    else:
        if filename.endswith('.zip'):
            with zipfile.ZipFile(filename, 'r') as zf:
                zf.extractall()
                zf.close()
                
        elif filename.endswith('.tar'):
            with tarfile.open(filename, "r:") as tar:
                tar.extractall()
                tar.close()
                
        elif filename.endswith('.tar.gz'):
            with tarfile.open(filename, "r:gz") as tar:
                tar.extractall()
                tar.close()
                
        else:
            print('Unknow archive type  (or unsupported) for \' ' + filename + '\', extension must be \'.zip\', \'.tar\' or \'.tar.gz\'')

def dl(url):    # Download in working directory
    try:
        wget.download(url)
    except:
        try:
            urllib.request.urlretrieve(url, url[url.rfind('/')+1:])
        except:
            print("Connection error")
            pause()
            exit(2)

def filedirstartswith(name, path = None):
    list_filedir = [fd for fd in os.listdir(path) if fd.startswith(name)]
    files_list = [file for file in list_filedir if not os.path.isdir(os.path.join(file) if path == None else os.path.join(path, file))]
    dir_list = [file for file in list_filedir if os.path.isdir(os.path.join(file) if path == None else os.path.join(path, file))]
    return dir_list, [archive for archive in files_list if archive.endswith('.zip') or archive.endswith('.tar') or archive.endswith('.tar.gz')]

def get_json(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

def get_binutils_urls(json):
    lin_url = ""
    mac_url = ""
    win_url = ""
    for index in range(len(json[0]['assets'])):
        temp = json[0]['assets'][index]['browser_download_url']
        if "linux64" in temp:
            lin_url = temp
        elif "macos" in temp:
            mac_url = temp
        elif "win32" in temp:
            win_url = temp
        else:
            print("Error: Unknown value from the Github JSON API.")
    return lin_url, mac_url, win_url

def get_sketchpath():
    dar_dir = '~/Library/Arduino15/'
    lin_dir = '~/.arduino15/'
    win_dir = '~\\AppData\\Local\\Arduino15\\'
    old_win_dir = '~\\AppData\\Roaming\\Arduino15\\'

    if sys.platform.startswith('darwin'):
        fdir = os.path.expanduser(dar_dir)

    elif sys.platform.startswith('linux'):
        fdir = os.path.expanduser(lin_dir)

    elif sys.platform.startswith('win32'):
        fdir = os.path.expanduser(win_dir)
        if not os.path.exists(fdir):
            fdir = os.path.expanduser(old_win_dir)

    else:
        print('Error, unknow OS type.')


    if not os.path.exists(fdir):
        print('Error: Path to \'preferences.txt\' does not exists.')
    else:
        with open(os.path.join(fdir, 'preferences.txt'),"rb") as f:
            for l in f:
                l = l.decode('utf-8').replace(' ','').replace('\n','').replace('\r','')
                if l.startswith('sketchbook.path'):
                    dir = l[l.rfind('=')+1:]
                    if os.path.exists(dir):
                        return dir
                    else:
                        return None
                    
def get_ulptool_lr(url_ulptool = None):
    if url_ulptool == None:
        url_ulptool = "https://api.github.com/repos/duff2013/ulptool/releases"
    data = get_json(url_ulptool)
    release = "0.0.0", 0
    
    for i in range(len(data)):
        if data[i]["prerelease"] == False:
            release = (data[i]["tag_name"], i) if data[i]["tag_name"]>release[0] else release

    return data[release[1]]["tarball_url"], data[release[1]]["zipball_url"] 

if __name__ == '__main__':
    main(sys.argv[1:])
