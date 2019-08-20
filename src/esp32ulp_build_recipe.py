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

# version 2.4.1
import os
import re
import sys
import glob
import json
import hashlib
import platform
import argparse
import subprocess

CPREPROCESSOR_FLAGS = []

EXTRA_FLAGS = dict()
EXTRA_FLAGS['doitESP32devkitV1']    = os.path.join('variants','doitESP32devkitV1')
EXTRA_FLAGS['esp32']                = os.path.join('cores','esp32')
EXTRA_FLAGS['E']                    = '-E'
EXTRA_FLAGS['P']                    = '-P'
EXTRA_FLAGS['XC']                   = '-xc'
EXTRA_FLAGS['O']                    = '-o'
EXTRA_FLAGS['O+']                   = '-O'
EXTRA_FLAGS['I']                    = '-I'
EXTRA_FLAGS['C']                    = '-C'
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
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', action='store')
    parser.add_argument('-p', action='store')
    parser.add_argument('-u', action='store')
    parser.add_argument('-x', action='store')
    parser.add_argument('-t', action='store')
    parser.add_argument('-I', action='append')
    args, options = parser.parse_known_args()

    for item in args.I:
        CPREPROCESSOR_FLAGS.append('-I')
        CPREPROCESSOR_FLAGS.append(item)

    board_options = []
    for item in options:
        if item.startswith('--'):
            board_options.append(item[1:])

    PATHS = dict()
    PATHS['build']     = args.b
    PATHS['core']      = args.p
    PATHS['ulptool']   = args.t
    PATHS['ucompiler'] = args.u
    PATHS['xcompiler'] = args.x

    os.chdir(os.path.join(PATHS['build'], 'sketch'))

    gen_assembly(PATHS)

    ulp_files = glob.glob('*.s')

    if not ulp_files:
        sys.stdout.write('No ULP Assembly File(s) Detected...\r')
        with open('tmp.s',"w") as ulp: pass
        ulp_files.append('tmp.s')
        build_ulp(PATHS, ulp_files, board_options, False)
        os.remove('tmp.s')
    else:
        build_ulp(PATHS, ulp_files, board_options, True)
    sys.exit(0)


def build_ulp(PATHS, ulp_sfiles, board_options, has_s_file):
    console_string = ''
    if has_s_file:
        console_string = 'ULP Assembly File(s) Detected: ' + ', '.join(ulp_sfiles) + '\r'

    cmds = gen_cmds(os.path.join(PATHS['core'], 'tools'))

    flash_msg = ''
    ram_msg   = ''


    for file in ulp_sfiles:
        file = file.split('.')
        file_names = gen_file_names(file[0])

        ## Run each assembly file (foo.S) through C preprocessor
        cmd = gen_xtensa_preprocessor_cmd(PATHS, file, board_options)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (out, err) = proc.communicate()
        if err:
            error_string = cmd[0] + '\r' + err
            sys.exit(error_string)
        else:
            console_string += cmd[0] + '\r'

        ## Run preprocessed assembly sources through assembler
        cmd = gen_binutils_as_cmd(PATHS, file)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
        (out, err) = proc.communicate()
        if err:
            error_string = cmd[0] + '\r' + err
            sys.exit(error_string)
        else:
            console_string += cmd[0] + '\r'

    ## Run linker script template through C preprocessor
    cmd = gen_xtensa_ld_cmd(PATHS, ulp_sfiles, board_options)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r' + err
        sys.exit(error_string)
    else:
        console_string += cmd[0] + '\r'

    ## Link object files into an output ELF file
    cmd = gen_binutils_ld_cmd(PATHS, ulp_sfiles)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r' + err
        sys.exit(error_string)
    else:
        console_string += cmd[0] + '\r'

    ## Get section memory sizes
    cmd = gen_binutils_size_cmd(PATHS)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r' + err
        sys.exit(error_string)
    else:
        try:
            file_path = os.path.join(PATHS['core'], 'tools', 'sdk', 'include', 'config', 'sdkconfig.h' )
            with open(file_path, "r") as file: text = file.read()

            mem = re.findall(r'#define CONFIG_ULP_COPROC_RESERVE_MEM (.*?)\n', text)[0]
            SECTIONS = dict(re.findall('^(\.+[0-9a-zA-Z_]+)\s+([0-9]+)', out, re.MULTILINE))
            max    = 0.0
            text   = 0.0
            data   = 0.0
            bss    = 0.0
            header = 0.0
            total  = 0.0

            flash_precent = 0.0
            ram_precent   = 0.0

            try: max = float(mem)
            except Exception: pass

            try: text = float(SECTIONS['.text'])
            except Exception: pass

            try: data = float(SECTIONS['.data'])
            except Exception: pass

            try: bss = float(SECTIONS['.bss'])
            except Exception: pass

            try: header = float(SECTIONS['.header'])
            except Exception: pass

            try:
                flash_precent = text/(max - data - bss - header) * 100
            except Exception:
                flash_precent = text/((max + 1) - data - bss - header) * 100

            try:
                ram_precent = (data + bss)/(max - text - header) * 100
            except Exception:
                ram_precent = (data + bss)/((max + 1) - text - header) * 100

            total = text + data + bss + header
            ram_left = max - total

            flash_msg = "ulp uses %s bytes (%s%%) of program storage space. Maximum is %s bytes.\r" % (int(text), int(flash_precent), int(max - header))
            ram_msg = 'Global variables use %s bytes (%s%%) of dynamic memory, leaving %s bytes for local variables. Maximum is %s bytes.\r' % (int(data+bss), int(ram_precent), int(ram_left), int(max - header))
        except Exception as e:
            pass

        console_string += cmd[0] + '\r'

    ## Generate list of global symbols
    cmd = gen_binutils_nm_cmd(PATHS)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r' + err
        sys.exit(error_string)
    else:
        file_names_constant = gen_file_names_constant()
        with open(file_names_constant['sym'],"w") as fsym:
            fsym.write(out)
        console_string += cmd[0] + '\r'

    ## Create LD export script and header file
    cmd = gen_mapgen_cmd(PATHS)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r' + err
        sys.exit(error_string)
    else:
        console_string += cmd[0] + '\r'

    ## Add the generated binary to the list of binary files
    cmd = gen_binutils_objcopy_cmd(PATHS)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r' + err
        sys.exit(error_string)
    else:
        console_string += cmd[0] + '\r'

    ## Add the generated binary to the list of binary files
    cmd = gen_xtensa_objcopy_cmd(PATHS)
    proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r' + err
        sys.exit(error_string)
    else:
        console_string += cmd[0] + '\r'

    ## Check if sdkconfig.h md5 hash has changed indicating the file has changed
    sdk_hash = md5(os.path.join(PATHS['core'] , 'tools', 'sdk', 'include', 'config', 'sdkconfig.h'))
    dict_hash = dict()
    with open(os.path.join(PATHS['ulptool'], 'hash.json'), 'r') as file:
        dict_hash = json.load(file)
    if sdk_hash != dict_hash['sdkconfig.h']['hash']:
        with open(os.path.join(PATHS['ulptool'], 'hash.json'), 'w') as file:
            dict_hash['sdkconfig.h']['hash'] = sdk_hash
            file.write(json.dumps(dict_hash))
        ## Run esp32.ld thru the c preprocessor generating esp32_out.ld
        cmd = gen_xtensa_ld_preprocessor_cmd(PATHS)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (out, err) = proc.communicate()
        if err:
            error_string = cmd[0] + '\r' + err
            sys.exit(error_string)
        else:
            console_string += cmd[0] + '\r'

    ## print outputs or errors to the console
    candy = '*********************************************************************************\r'
    if has_s_file:
        print(console_string + candy + flash_msg + ram_msg + candy)
    return 0

def gen_assembly(PATHS):
    c_files = glob.glob('*.c')
    ulpcc_files = []
    try:
        for file in c_files:
            with open(file, "rb") as f:
                top = f.readline().strip()
                bottom = f.readlines()[-1].strip()
                if top == "#ifdef _ULPCC_":
                    if bottom == "#endif":
                        ulpcc_files.append(file)

    except Exception as e:
        print e

    for file in ulpcc_files:
        cmd = gen_lcc_cmd(PATHS, file)
        proc = subprocess.Popen(cmd[1],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=False)
        (out, err) = proc.communicate()
        if err:
            error_string = cmd[0] + '\r' + err
            sys.exit(error_string)
        else:
            if out == "":
                print cmd[0]
            else:
                sys.exit(str(out))


def gen_lcc_cmd(PATHS, file):
    soc_path     = os.path.join(PATHS['core'], 'tools', 'sdk', 'include', 'soc', 'soc')
    include_path = os.path.join(PATHS['core'], 'tools', 'sdk', 'include', 'soc')
    header_path  = os.path.join(PATHS['ulptool'], 'ulpcc', 'include')
    if platform.system() == 'Darwin':
        lcc_path = os.path.join(PATHS['ulptool'], 'ulpcc', 'bin', 'darwin')
    elif platform.system() == 'Linux':
        lcc_path = os.path.join(PATHS['ulptool'], 'ulpcc', 'bin', 'linux')
    elif platform.system() == 'Windows':
        sys.exit("ulpcc is not supported on Windows")
    LCC = []
    LCC.append(lcc_path + '/lcc')
    LCC.append('-I' + soc_path)
    LCC.append('-I' + include_path)
    LCC.append('-I' + header_path)
    LCC.append('-D_ULPCC_')
    LCC.append('-lccdir=' + lcc_path)
    LCC.append('-Wf-target=ulp')
    LCC.append('-S')
    LCC.append(file)
    LCC.append("-o")
    LCC.append(file[:-1] + 's')
    STR_CMD = ' '.join(LCC)
    return STR_CMD, LCC

def gen_xtensa_ld_preprocessor_cmd(PATHS):
    cmds = gen_xtensa_cmds(PATHS['xcompiler'])
    XTENSA_GCC_PREPROCESSOR = []
    XTENSA_GCC_PREPROCESSOR.append(cmds['XTENSA_GCC'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['E'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['P'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['C'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['XC'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['O'])
    XTENSA_GCC_PREPROCESSOR.append(os.path.join(PATHS['core'] , 'tools', 'sdk', 'ld', 'esp32_out.ld'))
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['I'])
    XTENSA_GCC_PREPROCESSOR.append(os.path.join(PATHS['core'] , 'tools', 'sdk', 'include', 'config'))
    XTENSA_GCC_PREPROCESSOR.append(os.path.join(PATHS['core'] , 'tools', 'sdk', 'ld', 'esp32.ld'))
    STR_CMD = ' '.join(XTENSA_GCC_PREPROCESSOR)
    return STR_CMD, XTENSA_GCC_PREPROCESSOR

def gen_xtensa_preprocessor_cmd(PATHS, file, board_options):
    cmds = gen_xtensa_cmds(PATHS['xcompiler'])
    file_names = gen_file_names(file[0])
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
    #XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['C'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['E'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['P'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['XC'])
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['O'])
    XTENSA_GCC_PREPROCESSOR.append(file_names['ps'])
    XTENSA_GCC_PREPROCESSOR.extend(CPREPROCESSOR_FLAGS)
    XTENSA_GCC_PREPROCESSOR.extend(board_options)
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['I'])
    XTENSA_GCC_PREPROCESSOR.append(os.path.join(PATHS['build'], 'sketch'))
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['D__ASSEMBLER__'])
    XTENSA_GCC_PREPROCESSOR.append(file[0] + '.s')
    STR_CMD = ' '.join(XTENSA_GCC_PREPROCESSOR)
    return STR_CMD, XTENSA_GCC_PREPROCESSOR

def gen_binutils_as_cmd(PATHS, file):
    cmds = gen_binutils_cmds(PATHS['ucompiler'])
    file_names = gen_file_names(file[0])
    ULP_AS = []
    ULP_AS.append(cmds['ULP_AS'])
    ULP_AS.append('-al=' + file_names['lst'])
    ULP_AS.append('-W')
    ULP_AS.append(EXTRA_FLAGS['O'])
    ULP_AS.append(file_names['o'])
    ULP_AS.append(file_names['ps'])
    STR_CMD = ' '.join(ULP_AS)
    return STR_CMD, ULP_AS

def gen_xtensa_ld_cmd(PATHS, file, board_options):
    cmds = gen_xtensa_cmds(PATHS['xcompiler'])
    file_names = gen_file_names_constant()
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
    XTENSA_GCC_LD.extend(CPREPROCESSOR_FLAGS)
    XTENSA_GCC_LD.extend(board_options)
    XTENSA_GCC_LD.append(EXTRA_FLAGS['I'])
    XTENSA_GCC_LD.append(os.path.join(PATHS['build'], 'sketch'))
    XTENSA_GCC_LD.append(EXTRA_FLAGS['D__ASSEMBLER__'])
    XTENSA_GCC_LD.append(os.path.join(PATHS['ulptool'], 'ld', 'esp32.ulp.ld'))
    STR_CMD = ' '.join(XTENSA_GCC_LD)
    return STR_CMD, XTENSA_GCC_LD

def gen_binutils_ld_cmd(PATHS, file):
    cmds = gen_binutils_cmds(PATHS['ucompiler'])
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

def gen_binutils_size_cmd(PATHS):
    cmds = gen_binutils_cmds(PATHS['ucompiler'])
    file_names_constant = gen_file_names_constant()
    ULP_LD = []
    ULP_LD.append(cmds['ULP_SIZE'])
    ULP_LD.append(EXTRA_FLAGS['A'])
    ULP_LD.append(file_names_constant['elf'])
    STR_CMD = ' '.join(ULP_LD)
    return STR_CMD, ULP_LD

def gen_binutils_nm_cmd(PATHS):
    cmds = gen_binutils_cmds(PATHS['ucompiler'])
    file_names_constant = gen_file_names_constant()
    ULP_NM = []
    ULP_NM.append(cmds['ULP_NM'])
    ULP_NM.append(EXTRA_FLAGS['G'])
    ULP_NM.append(EXTRA_FLAGS['F'])
    ULP_NM.append(EXTRA_FLAGS['POSIX'])
    ULP_NM.append(file_names_constant['elf'])
    STR_CMD = ' '.join(ULP_NM)
    return STR_CMD, ULP_NM

def gen_mapgen_cmd(PATHS):
    cmds = gen_cmds(PATHS['ulptool'])
    file_names_constant = gen_file_names_constant()
    ULP_MAPGEN = []
    ULP_MAPGEN.append('python')
    ULP_MAPGEN.append(cmds['ULP_MAPGEN'])
    ULP_MAPGEN.append(EXTRA_FLAGS['S'])
    ULP_MAPGEN.append(file_names_constant['sym'])
    ULP_MAPGEN.append(EXTRA_FLAGS['O'])
    ULP_MAPGEN.append('ulp_main')
    STR_CMD = ' '.join(ULP_MAPGEN)
    return STR_CMD, ULP_MAPGEN

def gen_binutils_objcopy_cmd(PATHS):
    cmds = gen_binutils_cmds(PATHS['ucompiler'])
    file_names_constant = gen_file_names_constant()
    ULP_OBJCOPY = []
    ULP_OBJCOPY.append(cmds['ULP_OBJCPY'])
    ULP_OBJCOPY.append(EXTRA_FLAGS['O+'])
    ULP_OBJCOPY.append(EXTRA_FLAGS['BINARY'])
    ULP_OBJCOPY.append(file_names_constant['elf'])
    ULP_OBJCOPY.append(file_names_constant['bin'])
    STR_CMD = ' '.join(ULP_OBJCOPY)
    return STR_CMD, ULP_OBJCOPY

def gen_xtensa_objcopy_cmd(PATHS):
    cmds = gen_xtensa_cmds(PATHS['xcompiler'])
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

def gen_file_names(sfile):
    file_names = dict()
    file_names['o']     = sfile + '.ulp.o'
    file_names['ps']    = sfile + '.ulp.pS'
    file_names['lst']   = sfile + '.ulp.lst'
    return file_names

def gen_file_names_constant():
    file_names = dict()
    file_names['ld']    = 'ulp_main.common.ld'
    file_names['elf']   = 'ulp_main.elf'
    file_names['map']   = 'ulp_main.map'
    file_names['sym']   = 'ulp_main.sym'
    file_names['bin']   = 'ulp_main.bin'
    file_names['bin_o'] = 'ulp_main.bin.bin.o'
    return file_names

def gen_cmds(path):
    cmds = dict()
    cmds['ULP_MAPGEN']    = os.path.join(path, 'esp32ulp_mapgen.py')
    return cmds

def gen_xtensa_cmds(path):
    cmds = dict()
    cmds['XTENSA_GCC']    = os.path.join(path, 'xtensa-esp32-elf-gcc')
    cmds['XTENSA_OBJCPY'] = os.path.join(path, 'xtensa-esp32-elf-objcopy')
    cmds['XTENSA_AR']     = os.path.join(path, 'xtensa-esp32-elf-ar')
    return cmds

def gen_binutils_cmds(path):
    cmds = dict()
    cmds['ULP_AS']        = os.path.join(path, 'esp32ulp-elf-as')
    cmds['ULP_LD']        = os.path.join(path, 'esp32ulp-elf-ld')
    cmds['ULP_NM']        = os.path.join(path, 'esp32ulp-elf-nm')
    cmds['ULP_SIZE']      = os.path.join(path, 'esp32ulp-elf-size')
    cmds['ULP_OBJCPY']    = os.path.join(path, 'esp32ulp-elf-objcopy')
    return cmds

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

if __name__ == '__main__':
    main(sys.argv[1:])
