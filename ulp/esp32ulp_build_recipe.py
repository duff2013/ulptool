#   Copyright (c) 2018 Colin Duffy (https://github.com/duff2013)
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy of this
#   software and associated documentation files (the "Software"), to deal in the Software
#   without restriction, including without limitation the rights to use, copy, modify, merge,
#   publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
#   to whom the Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all copies or
#   substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#   INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#   PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
#   FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#   OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.


import os
import sys
import glob
import optparse
import subprocess

CPREPROCESSOR_FLAGS = dict()
CPREPROCESSOR_FLAGS['app_trace']            = os.path.join('tools','sdk','include','app_trace')
CPREPROCESSOR_FLAGS['app_update']           = os.path.join('tools','sdk','include','app_update')
CPREPROCESSOR_FLAGS['bluedroid']            = os.path.join('tools','sdk','include','bluedroid')
CPREPROCESSOR_FLAGS['bootloader_support']   = os.path.join('tools','sdk','include','bootloader_support')
CPREPROCESSOR_FLAGS['bt']                   = os.path.join('tools','sdk','include','bt')
CPREPROCESSOR_FLAGS['coap']                 = os.path.join('tools','sdk','include','coap')
CPREPROCESSOR_FLAGS['config']               = os.path.join('tools','sdk','include','config')
CPREPROCESSOR_FLAGS['console']              = os.path.join('tools','sdk','include','console')
CPREPROCESSOR_FLAGS['driver']               = os.path.join('tools','sdk','include','driver')
CPREPROCESSOR_FLAGS['esp32']                = os.path.join('tools','sdk','include','esp32')
CPREPROCESSOR_FLAGS['esp_adc_cal']          = os.path.join('tools','sdk','include','esp_adc_cal')
CPREPROCESSOR_FLAGS['ethernet']             = os.path.join('tools','sdk','include','ethernet')
CPREPROCESSOR_FLAGS['expat']                = os.path.join('tools','sdk','include','expat')
CPREPROCESSOR_FLAGS['fatfs']                = os.path.join('tools','sdk','include','fatfs')
CPREPROCESSOR_FLAGS['freertos']             = os.path.join('tools','sdk','include','freertos')
CPREPROCESSOR_FLAGS['heap']                 = os.path.join('tools','sdk','include','heap')
CPREPROCESSOR_FLAGS['jsmn']                 = os.path.join('tools','sdk','include','jsmn')
CPREPROCESSOR_FLAGS['json']                 = os.path.join('tools','sdk','include','json')
CPREPROCESSOR_FLAGS['log']                  = os.path.join('tools','sdk','include','log')
CPREPROCESSOR_FLAGS['lwip']                 = os.path.join('tools','sdk','include','lwip')
CPREPROCESSOR_FLAGS['mbedtls']              = os.path.join('tools','sdk','include','mbedtls')
CPREPROCESSOR_FLAGS['mbedtls_port']         = os.path.join('tools','sdk','include','mbedtls_port')
CPREPROCESSOR_FLAGS['mdns']                 = os.path.join('tools','sdk','include','mdns')
CPREPROCESSOR_FLAGS['newlib']               = os.path.join('tools','sdk','include','newlib')
CPREPROCESSOR_FLAGS['nghttp']               = os.path.join('tools','sdk','include','nghttp')
CPREPROCESSOR_FLAGS['nvs_flash']            = os.path.join('tools','sdk','include','nvs_flash')
CPREPROCESSOR_FLAGS['openssl']              = os.path.join('tools','sdk','include','openssl')
CPREPROCESSOR_FLAGS['sdmmc']                = os.path.join('tools','sdk','include','sdmmc')
CPREPROCESSOR_FLAGS['soc']                  = os.path.join('tools','sdk','include','soc')
CPREPROCESSOR_FLAGS['spi_flash']            = os.path.join('tools','sdk','include','spi_flash')
CPREPROCESSOR_FLAGS['spiffs']               = os.path.join('tools','sdk','include','spiffs')
CPREPROCESSOR_FLAGS['tcpip_adapter']        = os.path.join('tools','sdk','include','tcpip_adapter')
CPREPROCESSOR_FLAGS['ulp']                  = os.path.join('tools','sdk','include','ulp')
CPREPROCESSOR_FLAGS['vfs']                  = os.path.join('tools','sdk','include','vfs')
CPREPROCESSOR_FLAGS['wear_levelling']       = os.path.join('tools','sdk','include','wear_levelling')
CPREPROCESSOR_FLAGS['wpa_supplicant']       = os.path.join('tools','sdk','include','wpa_supplicant')
CPREPROCESSOR_FLAGS['xtensa-debug-module']  = os.path.join('tools','sdk','include','xtensa-debug-module')

EXTRA_FLAGS = dict()
EXTRA_FLAGS['doitESP32devkitV1']    = os.path.join('variants','doitESP32devkitV1')
EXTRA_FLAGS['esp32']                = os.path.join('cores','esp32')
EXTRA_FLAGS['E']                    = '-E'
EXTRA_FLAGS['P']                    = '-P'
EXTRA_FLAGS['XC']                   = '-xc'
EXTRA_FLAGS['O']                    = '-o'
EXTRA_FLAGS['O+']                   = '-O'
EXTRA_FLAGS['I']                    = '-I'
EXTRA_FLAGS['A']                    = '-A'
EXTRA_FLAGS['T']                    = '-T'
EXTRA_FLAGS['G']                    = '-g'
EXTRA_FLAGS['F']                    = '-f'
EXTRA_FLAGS['S']                    = '-s'
EXTRA_FLAGS['BINARY']               = 'binary'
EXTRA_FLAGS['D__ASSEMBLER__']       = '-D__ASSEMBLER__'
EXTRA_FLAGS['DESP_PLATFORM']        = '-DESP_PLATFORM'
EXTRA_FLAGS['DMBEDTLS_CONFIG_FILE'] = os.path.join('-DMBEDTLS_CONFIG_FILE=mbedtls','esp_config.h')
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
EXTRA_FLAGS['POSIX']                = 'posix'

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
    board_options.append('-DF_CPU=' + options.df_cpu)
    board_options.append('-DARDUINO=' + options.darduino)
    board_options.append('-DARDUINO_' + options.darduino_dev)
    board_options.append('-DARDUINO_ARCH_' + options.darduino_arch)
    board_options.append('-DARDUINO_BOARD=' + options.darduino_board)
    board_options.append('-DARDUINO_VARIANT=' + options.darduino_variant)

    os.chdir(os.path.join(options.bpath, 'sketch'))
    
    ulp_files = glob.glob("*.s")
    if not ulp_files:
        print "No ULP Assembly File(s) Detected..."
        with open('ulp_main.ld',"w") as fld:
            fld.close()
    else:
        build_ulp(options.bpath, options.ppath, ulp_files, board_options)

    sys.exit(0)

def build_ulp(build_path, platform_path, ulp_sfiles, board_options):
    print "ULP Assembly File(s) Detected: " + str(ulp_sfiles)
    console_string = ""
    cmds = gen_cmds(os.path.join(platform_path, 'tools'))
    for file in ulp_sfiles:
        file = file.split('.')
        file_names = gen_file_names(file[0])
        
        ## Run each assembly file (foo.S) through C preprocessor
        cmd = gen_xtensa_preprocessor_cmd(build_path, platform_path, file, board_options)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (out, err) = proc.communicate()
        if err:
            error_string = cmd[0] + '\n' + out
            sys.exit(error_string)
        else:
            console_string += cmd[0] + '\n'
        
        ## Run preprocessed assembly sources through assembler
        cmd = gen_binutils_as_cmd(build_path, platform_path, file, board_options)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
        (out, err) = proc.communicate()
        if err:
            error_string = cmd[0] + '\n' + err
            sys.exit(error_string)
        else:
            console_string += cmd[0] + '\n'

    ## Run linker script template through C preprocessor
    cmd = gen_xtensa_ld_cmd(build_path, platform_path, ulp_sfiles, board_options)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\n' + out
        sys.exit(error_string)
    else:
        console_string += cmd[0] + '\n'
    
    ## Link object files into an output ELF file
    cmd = gen_binutils_ld_cmd(build_path, platform_path, ulp_sfiles, board_options)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\n' + out
        sys.exit(error_string)
    else:
        console_string += cmd[0] + '\n'

    ## Generate list of global symbols
    cmd = gen_binutils_nm_cmd(build_path, platform_path, ulp_sfiles, board_options)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\n' + out
        sys.exit(error_string)
    else:
        file_names_constant = gen_file_names_constant()
        with open(file_names_constant['sym'],"w") as fsym:
            fsym.write(out)
        console_string += cmd[0] + '\n'


    ## Create LD export script and header file
    cmd = gen_mapgen_cmd(build_path, platform_path, ulp_sfiles, board_options)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\n' + out
        sys.exit(error_string)
    else:
        console_string += cmd[0] + '\n'
    
    ## Add the generated binary to the list of binary files
    cmd = gen_binutils_objcopy_cmd(build_path, platform_path, ulp_sfiles, board_options)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\n' + out
        sys.exit(error_string)
    else:
        console_string += cmd[0] + '\n'

    ## Add the generated binary to the list of binary files
    cmd = gen_xtensa_objcopy_cmd(build_path, platform_path, ulp_sfiles, board_options)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\n' + out
        sys.exit(error_string)
    else:
        console_string += cmd[0] + '\n'
    
    ## embed into arduino.ar
    cmd = gen_XTENSA_AR_cmd(build_path, platform_path, ulp_sfiles, board_options)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\n' + out
        sys.exit(error_string)
    else:
        console_string += cmd[0]

    print console_string
    
    return 0

def gen_xtensa_preprocessor_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(os.path.join(platform_path, 'tools'))
    file_names = gen_file_names(file[0])
    LIBRARIES = []
    for flag in CPREPROCESSOR_FLAGS:
        path = os.path.join(platform_path, CPREPROCESSOR_FLAGS[flag])
        LIBRARIES.append('-I')
        LIBRARIES.append(path)
    XTENSA_GCC_PREPROCESSOR = []
    XTENSA_GCC_PREPROCESSOR.append(cmds['XTENSA_GCC'])
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
    XTENSA_GCC_PREPROCESSOR.append(os.path.join(build_path, 'sketch'))
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['D__ASSEMBLER__'])
    XTENSA_GCC_PREPROCESSOR.append(file[0] + '.s')
    STR_CMD = ' '.join(XTENSA_GCC_PREPROCESSOR)
    return STR_CMD, XTENSA_GCC_PREPROCESSOR

def gen_binutils_as_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(os.path.join(platform_path, 'tools'))
    file_names = gen_file_names(file[0])
    ULP_AS = []
    ULP_AS.append(cmds['ULP_AS'])
    ULP_AS.append('-al=' + file_names['lst'])
    ULP_AS.append(EXTRA_FLAGS['O'])
    ULP_AS.append(file_names['o'])
    ULP_AS.append(file_names['ps'])
    STR_CMD = ' '.join(ULP_AS)
    return STR_CMD, ULP_AS

def gen_xtensa_ld_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(os.path.join(platform_path, 'tools'))
    file_names = gen_file_names_constant()
    LIBRARIES = []
    for flag in CPREPROCESSOR_FLAGS:
        path = os.path.join(platform_path, CPREPROCESSOR_FLAGS[flag])
        LIBRARIES.append('-I')
        LIBRARIES.append(path.strip())
    XTENSA_GCC_LD = []
    XTENSA_GCC_LD.append(cmds['XTENSA_GCC'])
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
    XTENSA_GCC_LD.append(os.path.join(build_path, 'sketch'))
    XTENSA_GCC_LD.append(EXTRA_FLAGS['D__ASSEMBLER__'])
    XTENSA_GCC_LD.append(os.path.join(platform_path, 'tools', 'sdk', 'include', 'ulp', 'ld', 'esp32.ulp.ld'))
    STR_CMD = ' '.join(XTENSA_GCC_LD)
    return STR_CMD, XTENSA_GCC_LD

def gen_binutils_ld_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(os.path.join(platform_path, 'tools'))
    file_names_constant = gen_file_names_constant()
    ULP_LD = []
    ULP_LD.append(cmds['ULP_LD'])
    ULP_LD.append(EXTRA_FLAGS['O'])
    ULP_LD.append(file_names_constant['elf'])
    ULP_LD.append(EXTRA_FLAGS['A'])
    ULP_LD.append(EXTRA_FLAGS['ELF32'])
    ULP_LD.append('-Map=' + file_names_constant['map'])
    ULP_LD.append(EXTRA_FLAGS['T'])
    ULP_LD.append(file_names_constant['ld'])
    for f in file:
        f = f.split('.')
        file_names = gen_file_names(f[0])
        ULP_LD.append(file_names['o'])
    STR_CMD = ' '.join(ULP_LD)
    return STR_CMD, ULP_LD

def gen_binutils_nm_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(os.path.join(platform_path, 'tools'))
    file_names_constant = gen_file_names_constant()
    ULP_NM = []
    ULP_NM.append(cmds['ULP_NM'])
    ULP_NM.append(EXTRA_FLAGS['G'])
    ULP_NM.append(EXTRA_FLAGS['F'])
    ULP_NM.append(EXTRA_FLAGS['POSIX'])
    ULP_NM.append(file_names_constant['elf'])
    STR_CMD = ' '.join(ULP_NM)
    return STR_CMD, ULP_NM

def gen_mapgen_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(os.path.join(platform_path, 'tools'))
    file_names_constant = gen_file_names_constant()
    ULP_MAPGEN = []
    ULP_MAPGEN.append(cmds['ULP_MAPGEN'])
    ULP_MAPGEN.append(EXTRA_FLAGS['S'])
    ULP_MAPGEN.append(file_names_constant['sym'])
    ULP_MAPGEN.append(EXTRA_FLAGS['O'])
    ULP_MAPGEN.append('ulp_main')
    STR_CMD = ' '.join(ULP_MAPGEN)
    return STR_CMD, ULP_MAPGEN

def gen_binutils_objcopy_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(os.path.join(platform_path, 'tools'))
    file_names_constant = gen_file_names_constant()
    ULP_OBJCOPY = []
    ULP_OBJCOPY.append(cmds['ULP_OBJCPY'])
    ULP_OBJCOPY.append(EXTRA_FLAGS['O+'])
    ULP_OBJCOPY.append(EXTRA_FLAGS['BINARY'])
    ULP_OBJCOPY.append(file_names_constant['elf'])
    ULP_OBJCOPY.append(file_names_constant['bin'])
    STR_CMD = ' '.join(ULP_OBJCOPY)
    return STR_CMD, ULP_OBJCOPY

def gen_xtensa_objcopy_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(os.path.join(platform_path, 'tools'))
    file_names_constant = gen_file_names_constant()
    XTENSA_OBJCOPY = []
    XTENSA_OBJCOPY.append(cmds['XTENSA_OBJCPY'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['INPUT_TARGET'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['BINARY'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['OUTPUT_TARGET'] )
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['ELF32_XTENSA_LE'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['BINARY_ARCH'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['XTENSA'] )
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['RENAME_SECTION'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['EMBEDDED'])
    XTENSA_OBJCOPY.append(file_names_constant['bin'])
    XTENSA_OBJCOPY.append(file_names_constant['bin_o'])
    STR_CMD = ' '.join(XTENSA_OBJCOPY)
    return STR_CMD, XTENSA_OBJCOPY

def gen_XTENSA_AR_cmd(build_path, platform_path, file, board_options):
    cmds = gen_cmds(os.path.join(platform_path, 'tools'))
    file_names_constant = gen_file_names_constant()
    XTENSA_AR = []
    XTENSA_AR.append(cmds['XTENSA_AR'])
    XTENSA_AR.append(EXTRA_FLAGS['CRU'])
    XTENSA_AR.append(os.path.join(build_path, 'arduino.ar'))
    XTENSA_AR.append(file_names_constant['bin_o'])
    STR_CMD = ' '.join(XTENSA_AR)
    return STR_CMD, XTENSA_AR

def gen_file_names(sfile):
    file_names = dict();
    file_names['o']     = sfile + '.ulp.o'
    file_names['ps']    = sfile + '.ulp.pS'
    file_names['lst']   = sfile + '.ulp.lst'
    return file_names

def gen_file_names_constant():
    file_names = dict();
    file_names['ld']    = 'ulp_main.common.ld'
    file_names['elf']   = 'ulp_main.elf'
    file_names['map']   = 'ulp_main.map'
    file_names['sym']   = 'ulp_main.sym'
    file_names['bin']   = 'ulp_main.bin'
    file_names['bin_o'] = 'ulp_main.bin.bin.o'
    return file_names

def gen_cmds(path):
    cmds = dict();
    cmds['XTENSA_GCC']    = os.path.join(path, 'xtensa-esp32-elf','bin','xtensa-esp32-elf-gcc')
    cmds['XTENSA_OBJCPY'] = os.path.join(path, 'xtensa-esp32-elf','bin','xtensa-esp32-elf-objcopy')
    cmds['XTENSA_AR']     = os.path.join(path, 'xtensa-esp32-elf','bin','xtensa-esp32-elf-ar')
    cmds['ULP_AS']        = os.path.join(path, 'esp32ulp-elf-binutils','bin','esp32ulp-elf-as')
    cmds['ULP_LD']        = os.path.join(path, 'esp32ulp-elf-binutils','bin','esp32ulp-elf-ld')
    cmds['ULP_NM']        = os.path.join(path, 'esp32ulp-elf-binutils','bin','esp32ulp-elf-nm')
    cmds['ULP_OBJCPY']    = os.path.join(path, 'esp32ulp-elf-binutils','bin','esp32ulp-elf-objcopy')
    cmds['ULP_MAPGEN']    = os.path.join(path, 'sdk','include','ulp','esp32ulp_mapgen.py')
    return cmds

if __name__ == '__main__':
    main(sys.argv[1:])
