#!/usr/bin/env python
# compile ulp files in Arduino enviroment

import os
import sys
import glob
import shlex
import optparse
import subprocess

CPREPROCESSOR_FLAGS = dict()
CPREPROCESSOR_FLAGS['app_trace']            = "/sdk/include/app_trace "
CPREPROCESSOR_FLAGS['app_update']           = "/sdk/include/app_update "
CPREPROCESSOR_FLAGS['bluedroid']            = "/sdk/include/bluedroid "
CPREPROCESSOR_FLAGS['bootloader_support']   = "/sdk/include/bootloader_support "
CPREPROCESSOR_FLAGS['bt']                   = "/sdk/include/bt "
CPREPROCESSOR_FLAGS['coap']                 = "/sdk/include/coap "
CPREPROCESSOR_FLAGS['config']               = "/sdk/include/config "
CPREPROCESSOR_FLAGS['console']              = "/sdk/include/console "
CPREPROCESSOR_FLAGS['driver']               = "/sdk/include/driver "
CPREPROCESSOR_FLAGS['esp32']                = "/sdk/include/esp32 "
CPREPROCESSOR_FLAGS['esp_adc_cal']          = "/sdk/include/esp_adc_cal "
CPREPROCESSOR_FLAGS['ethernet']             = "/sdk/include/ethernet "
CPREPROCESSOR_FLAGS['expat']                = "/sdk/include/expat "
CPREPROCESSOR_FLAGS['fatfs']                = "/sdk/include/fatfs "
CPREPROCESSOR_FLAGS['freertos']             = "/sdk/include/freertos "
CPREPROCESSOR_FLAGS['heap']                 = "/sdk/include/heap "
CPREPROCESSOR_FLAGS['jsmn']                 = "/sdk/include/jsmn "
CPREPROCESSOR_FLAGS['json']                 = "/sdk/include/json "
CPREPROCESSOR_FLAGS['log']                  = "/sdk/include/log "
CPREPROCESSOR_FLAGS['lwip']                 = "/sdk/include/lwip "
CPREPROCESSOR_FLAGS['mbedtls']              = "/sdk/include/mbedtls "
CPREPROCESSOR_FLAGS['mbedtls_port']         = "/sdk/include/mbedtls_port "
CPREPROCESSOR_FLAGS['mdns']                 = "/sdk/include/mdns "
CPREPROCESSOR_FLAGS['newlib']               = "/sdk/include/newlib "
CPREPROCESSOR_FLAGS['nghttp']               = "/sdk/include/nghttp "
CPREPROCESSOR_FLAGS['nvs_flash']            = "/sdk/include/nvs_flash "
CPREPROCESSOR_FLAGS['openssl']              = "/sdk/include/openssl "
CPREPROCESSOR_FLAGS['sdmmc']                = "/sdk/include/sdmmc "
CPREPROCESSOR_FLAGS['soc']                  = "/sdk/include/soc "
CPREPROCESSOR_FLAGS['spi_flash']            = "/sdk/include/spi_flash "
CPREPROCESSOR_FLAGS['spiffs']               = "/sdk/include/spiffs "
CPREPROCESSOR_FLAGS['tcpip_adapter']        = "/sdk/include/tcpip_adapter "
CPREPROCESSOR_FLAGS['ulp']                  = "/sdk/include/ulp "
CPREPROCESSOR_FLAGS['vfs']                  = "/sdk/include/vfs "
CPREPROCESSOR_FLAGS['wear_levelling']       = "/sdk/include/wear_levelling "
CPREPROCESSOR_FLAGS['wpa_supplicant']       = "/sdk/include/wpa_supplicant "
CPREPROCESSOR_FLAGS['xtensa-debug-module']  = "/sdk/include/xtensa-debug-module "

EXTRA_FLAGS = dict()
EXTRA_FLAGS['doitESP32devkitV1']    = '/variants/doitESP32devkitV1'
EXTRA_FLAGS['esp32']                = '/cores/esp32'
EXTRA_FLAGS['E']                    = '-E'
EXTRA_FLAGS['P']                    = '-P'
EXTRA_FLAGS['XC']                   = '-xc'
EXTRA_FLAGS['O']                    = '-o'
EXTRA_FLAGS['O+']                   = '-O'
EXTRA_FLAGS['I']                    = '-I'
EXTRA_FLAGS['A']                    = '-A'
EXTRA_FLAGS['T']                    = '-T'
EXTRA_FLAGS['BINARY']               = 'binary'
EXTRA_FLAGS['D__ASSEMBLER__']       = '-D__ASSEMBLER__'
EXTRA_FLAGS['DESP_PLATFORM']        = '-DESP_PLATFORM'
EXTRA_FLAGS['DMBEDTLS_CONFIG_FILE'] = '-DMBEDTLS_CONFIG_FILE=mbedtls/esp_config.h'
EXTRA_FLAGS['DHAVE_CONFIG_H']       = '-DHAVE_CONFIG_H'
EXTRA_FLAGS['MT']                   = '-MT'
EXTRA_FLAGS['MMD']                  = '-MMD'
EXTRA_FLAGS['MP']                   = '-MP'
EXTRA_FLAGS['DWITH_POSIX']          = '-DWITH_POSIX'
EXTRA_FLAGS['INPUT_TARGET']         = '--input-target'
EXTRA_FLAGS['OUTPUT_TARGET']        = '--output-target'
EXTRA_FLAGS['ELF32_XTENSA_LE']      = 'elf32-xtensa-le'
EXTRA_FLAGS['BINARY_ARCH']          = '--binary-architecture'
EXTRA_FLAGS['XTENSA']               = 'xtensa'
EXTRA_FLAGS['RENAME_SECTION']       = '--rename-section'
EXTRA_FLAGS['EMBEDDED']             = '.data=.rodata.embedded'
EXTRA_FLAGS['CRU']                  = 'cru'
EXTRA_FLAGS['ELF32']                = 'elf32-esp32ulp'

#########################################################################################################
def main(argv):
    parser = optparse.OptionParser()
    parser.add_option('-b', '--buildpath', dest='bpath', help='Sketch Build Path')
    parser.add_option('-e', '--compiler.c.elf.flags', dest='elfflags', help='Compiler c elf flags')
    parser.add_option('-p', '--platformpath', dest='ppath', help='ESP-IDF Platform Path')
    parser.add_option('--DF_CPU', dest='df_cpu', help='CPU Speed')
    parser.add_option('--DARDUINO', dest='darduino', help='Run Time IDE Version')
    parser.add_option('--DARDUINO_', dest='darduino_dev', help='Board Development Type')
    parser.add_option('--DARDUINO_ARCH_', dest='darduino_arch', help='Arch Type')
    parser.add_option('--DARDUINO_BOARD', dest='darduino_board', help='Board Type')
    parser.add_option('--DARDUINO_VARIANT', dest='darduino_variant', help='Board Variant')
    
    (options, args) = parser.parse_args()
    
    if options.elfflags:
        print "COMPILER ELF"
        return 0
    if options.bpath is None:
        print "build path error_string"
        sys.exit(2)
    if options.ppath is None:
        print "platform path error_string"
        sys.exit(2)
    
    board_options = []
    board_options.append("-DF_CPU=" + options.df_cpu)
    board_options.append("-DARDUINO=" + options.darduino)
    board_options.append("-DARDUINO_" + options.darduino_dev)
    board_options.append("-DARDUINO_ARCH_" + options.darduino_arch)
    board_options.append("-DARDUINO_BOARD=" + options.darduino_board)
    board_options.append("-DARDUINO_VARIANT=" + options.darduino_variant)

    os.chdir(options.bpath + "/sketch/")

    ulp_files = glob.glob('*.s')
    if not ulp_files:
        print "No ULP Assembly File(s) Detected..."
        f= open("ulp_main.ld","w+")
    else:
        build_ulp(options.bpath, options.ppath, ulp_files, board_options)

    sys.exit(0)

#########################################################################################################
def build_ulp(build_path, platform_path, ulp_sfiles, board_options):
    print "ULP Assembly File(s) Detected: " + str(ulp_sfiles)
    #sys.stdout.write(msg)
    #sys.stdout.flush()
    #print "ULP ASSEMBLY FILE(s) DETECTED: ", ulp_sfiles
    console_string = ""
    cmds = gen_cmds(platform_path + "/tools")
    for file in ulp_sfiles:
        file = file.split(".")
        file_names = gen_file_names(file[0])
        
        ## Run each assembly file (foo.S) through C preprocessor
        cmd = gen_xtensa_preprocessor_cmd(build_path, platform_path, file, board_options)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (out, err) = proc.communicate()
        if out != '':
            error_string = cmd[0] + '\n' + out
            sys.exit(error_string)
        else:
            console_string = cmd[0] + '\n'

        ## Run preprocessed assembly sources through assembler
        cmd = gen_binutils_as_cmd(build_path, platform_path, file, board_options)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (out, err) = proc.communicate()
        if out != '':
            error_string = cmd[0] + '\n' + out
            sys.exit(error_string)
        else:
            console_string += cmd[0] + '\n'

        ## Run linker script template through C preprocessor
        cmd = gen_xtensa_ld_cmd(build_path, platform_path, file, board_options)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (out, err) = proc.communicate()
        if out != '':
            error_string = cmd[0] + '\n' + out
            sys.exit(error_string)
        else:
            console_string += cmd[0] + '\n'

        ## Link object files into an output ELF file
        cmd = gen_binutils_ld_cmd(build_path, platform_path, file, board_options)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (out, err) = proc.communicate()
        if out != '':
            error_string = cmd[0] + '\n' + out
            sys.exit(error_string)
        else:
            console_string += cmd[0] + '\n'

        ## Generate list of global symbols
        cmd = cmds['ulp_nm'] + " -g -f posix " + file_names['elf'] + " > " + file_names['sym']
        proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
        (out, err) = proc.communicate()
        if out != '':
            error_string = cmd[0] + '\n' + out
            sys.exit(error_string)
        else:
            console_string += cmd + '\n'

        ## Create LD export script and header file
        cmd = gen_mapgen_cmd(build_path, platform_path, file, board_options)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (out, err) = proc.communicate()
        if out != '':
            error_string = cmd[0] + '\n' + out
            sys.exit(error_string)
        else:
            console_string += cmd[0] + '\n'

        ## Add the generated binary to the list of binary files
        cmd = gen_binutils_objcopy_cmd(build_path, platform_path, file, board_options)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (out, err) = proc.communicate()
        if out != '':
            error_string = cmd[0] + '\n' + out
            sys.exit(error_string)
        else:
            console_string += cmd[0] + '\n'

        ## Add the generated binary to the list of binary files
        cmd = gen_xtensa_objcopy_cmd(build_path, platform_path, file, board_options)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (out, err) = proc.communicate()
        if out != '':
            error_string = cmd[0] + '\n' + out
            sys.exit(error_string)
        else:
            console_string += cmd[0] + '\n'
        
        ## embed into arduino.ar
        cmd = gen_xtensa_ar_cmd(build_path, platform_path, file, board_options)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (out, err) = proc.communicate()
        if out != '':
            error_string = cmd[0] + '\n' + out
            sys.exit(error_string)
        else:
            console_string += cmd[0]
                
        print console_string
    
    return 0

#########################################################################################################
def gen_xtensa_preprocessor_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(platform_path + "/tools")
    file_names = gen_file_names(file[0])
    LIBRARIES = []
    for flag in CPREPROCESSOR_FLAGS:
        path = platform_path + "/tools" + CPREPROCESSOR_FLAGS[flag]
        LIBRARIES.append("-I")
        LIBRARIES.append(path.strip())
    XTENSA_GCC_PREPROCESSOR = []
    XTENSA_GCC_PREPROCESSOR.append(cmds['xtensa_gcc'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['DESP_PLATFORM'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['MMD'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['MP'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['DWITH_POSIX'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['DMBEDTLS_CONFIG_FILE'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['DHAVE_CONFIG_H'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['MT'])
    XTENSA_GCC_PREPROCESSOR.append(file_names['o'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['E'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['P'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['XC'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['O'])
    XTENSA_GCC_PREPROCESSOR.append(file_names['ps'])
    XTENSA_GCC_PREPROCESSOR.extend(LIBRARIES)
    XTENSA_GCC_PREPROCESSOR.extend(board_options)
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['I'])
    XTENSA_GCC_PREPROCESSOR.append(build_path + "/sketch")
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['D__ASSEMBLER__'])
    XTENSA_GCC_PREPROCESSOR.append(file[0] + ".s")
    STR_CMD = ' '.join(XTENSA_GCC_PREPROCESSOR)
    return STR_CMD, XTENSA_GCC_PREPROCESSOR

#########################################################################################################
def gen_binutils_as_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(platform_path + "/tools")
    file_names = gen_file_names(file[0])
    ULP_AS = []
    ULP_AS.append(cmds['ulp_as'])
    ULP_AS.append("-al=" + file_names['lst'])
    ULP_AS.append(EXTRA_FLAGS['O'])
    ULP_AS.append(file_names['o'])
    ULP_AS.append(file_names['ps'])
    STR_CMD = ' '.join(ULP_AS)
    return STR_CMD, ULP_AS

#########################################################################################################
def gen_xtensa_ld_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(platform_path + "/tools")
    file_names = gen_file_names(file[0])
    LIBRARIES = []
    for flag in CPREPROCESSOR_FLAGS:
        path = platform_path + "/tools" + CPREPROCESSOR_FLAGS[flag]
        LIBRARIES.append("-I")
        LIBRARIES.append(path.strip())
    XTENSA_GCC_LD = []
    XTENSA_GCC_LD.append(cmds['xtensa_gcc'])
    XTENSA_GCC_LD.append(EXTRA_FLAGS['DESP_PLATFORM'])
    XTENSA_GCC_LD.append(EXTRA_FLAGS['MMD'])
    XTENSA_GCC_LD.append(EXTRA_FLAGS['MP'])
    XTENSA_GCC_LD.append(EXTRA_FLAGS['DWITH_POSIX'])
    XTENSA_GCC_LD.append(EXTRA_FLAGS['DMBEDTLS_CONFIG_FILE'])
    XTENSA_GCC_LD.append(EXTRA_FLAGS['DHAVE_CONFIG_H'])
    XTENSA_GCC_LD.append(EXTRA_FLAGS['MT'])
    XTENSA_GCC_LD.append(file_names['ld'])
    XTENSA_GCC_LD.append(EXTRA_FLAGS['E'])
    XTENSA_GCC_LD.append(EXTRA_FLAGS['P'])
    XTENSA_GCC_LD.append(EXTRA_FLAGS['XC'])
    XTENSA_GCC_LD.append(EXTRA_FLAGS['O'])
    XTENSA_GCC_LD.append(file_names['ld'])
    XTENSA_GCC_LD.extend(LIBRARIES)
    XTENSA_GCC_LD.extend(board_options)
    XTENSA_GCC_LD.append(EXTRA_FLAGS['I'])
    XTENSA_GCC_LD.append(build_path + "/sketch")
    XTENSA_GCC_LD.append(EXTRA_FLAGS['D__ASSEMBLER__'])
    XTENSA_GCC_LD.append(platform_path + "/tools/sdk/include/ulp/ld/esp32.ulp.ld")
    STR_CMD = ' '.join(XTENSA_GCC_LD)
    return STR_CMD, XTENSA_GCC_LD

#########################################################################################################
def gen_binutils_ld_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(platform_path + "/tools")
    file_names = gen_file_names(file[0])
    ULP_LD = []
    ULP_LD.append(cmds['ulp_ld'])
    ULP_LD.append("-o")
    ULP_LD.append(file_names['elf'])
    ULP_LD.append(EXTRA_FLAGS['A'])
    ULP_LD.append(EXTRA_FLAGS['ELF32'])
    ULP_LD.append("-Map=" + file_names['map'])
    ULP_LD.append(EXTRA_FLAGS['T'])
    ULP_LD.append(file_names['ld'])
    ULP_LD.append(file_names['o'])
    STR_CMD = ' '.join(ULP_LD)
    return STR_CMD, ULP_LD

#########################################################################################################
def gen_mapgen_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(platform_path + "/tools")
    file_names = gen_file_names(file[0])
    ULP_MAPGEN = []
    ULP_MAPGEN.append(cmds['ulp_mapgen'])
    ULP_MAPGEN.append("-s")
    ULP_MAPGEN.append(file_names['sym'])
    ULP_MAPGEN.append("-o")
    ULP_MAPGEN.append("ulp_main")
    STR_CMD = ' '.join(ULP_MAPGEN)
    return STR_CMD, ULP_MAPGEN

#########################################################################################################
def gen_binutils_objcopy_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(platform_path + "/tools")
    file_names = gen_file_names(file[0])
    ULP_OBJCOPY = []
    ULP_OBJCOPY.append(cmds['ulp_objcpy'])
    ULP_OBJCOPY.append(EXTRA_FLAGS['O+'])
    ULP_OBJCOPY.append(EXTRA_FLAGS['BINARY'])
    ULP_OBJCOPY.append(file_names['elf'])
    ULP_OBJCOPY.append(file_names['bin'])
    STR_CMD = ' '.join(ULP_OBJCOPY)
    return STR_CMD, ULP_OBJCOPY

#########################################################################################################
def gen_xtensa_objcopy_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(platform_path + "/tools")
    file_names = gen_file_names(file[0])
    XTENSA_OBJCOPY = []
    XTENSA_OBJCOPY.append(cmds['xtensa_objcpy'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['INPUT_TARGET'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['BINARY'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['OUTPUT_TARGET'] )
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['ELF32_XTENSA_LE'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['BINARY_ARCH'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['XTENSA'] )
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['RENAME_SECTION'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['EMBEDDED'])
    XTENSA_OBJCOPY.append(file_names['bin'])
    XTENSA_OBJCOPY.append(file_names['bin_o'])
    STR_CMD = ' '.join(XTENSA_OBJCOPY)
    return STR_CMD, XTENSA_OBJCOPY

#########################################################################################################
def gen_xtensa_ar_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(platform_path + "/tools")
    file_names = gen_file_names(file[0])
    XTENSA_AR = []
    XTENSA_AR.append(cmds['xtensa_ar'])
    XTENSA_AR.append(EXTRA_FLAGS['CRU'])
    XTENSA_AR.append(build_path + "/arduino.ar")
    XTENSA_AR.append(file_names['bin_o'])
    STR_CMD = ' '.join(XTENSA_AR)
    return STR_CMD, XTENSA_AR

#########################################################################################################
def gen_file_names(sfile):
    file_names = dict();
    file_names['o']     = sfile + ".ulp.o"
    file_names['ps']    = sfile + ".ulp.pS"
    file_names['lst']   = sfile + ".ulp.lst"
    file_names['ld']    = "ulp_main.common.ld"
    file_names['elf']   = "ulp_main.elf"
    file_names['map']   = "ulp_main.map"
    file_names['sym']   = "ulp_main.sym"
    file_names['bin']   = "ulp_main.bin"
    file_names['bin_o'] = "ulp_main.bin.bin.o"
    return file_names

#########################################################################################################
def gen_cmds(path):
    cmds = dict();
    cmds['xtensa_gcc']    = path + "/xtensa-esp32-elf/bin/xtensa-esp32-elf-gcc"
    cmds['xtensa_objcpy'] = path + "/xtensa-esp32-elf/bin/xtensa-esp32-elf-objcopy"
    cmds['xtensa_ar']     = path + "/xtensa-esp32-elf/bin/xtensa-esp32-elf-ar"
    cmds['ulp_as']        = path + "/esp32ulp-elf-binutils/bin/esp32ulp-elf-as"
    cmds['ulp_ld']        = path + "/esp32ulp-elf-binutils/bin/esp32ulp-elf-ld"
    cmds['ulp_nm']        = path + "/esp32ulp-elf-binutils/bin/esp32ulp-elf-nm"
    cmds['ulp_objcpy']    = path + "/esp32ulp-elf-binutils/bin/esp32ulp-elf-objcopy"
    cmds['ulp_mapgen']    = path + "/sdk/include/ulp/esp32ulp_mapgen.py"
    return cmds

#########################################################################################################
if __name__ == "__main__":
    main(sys.argv[1:])
