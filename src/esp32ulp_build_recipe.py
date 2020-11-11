# Copyright (c) 2018 Colin Duffy (https://github.com/duff2013)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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

EXTRA_FLAGS =\
    {'doitESP32devkitV1': os.path.join(
     'variants', 'doitESP32devkitV1'),
     'esp32': os.path.join('cores', 'esp32'),
     'E': '-E',
     'P': '-P',
     'XC': '-xc',
     'O': '-o',
     'O+': '-O',
     'I': '-I',
     'C': '-C',
     'A': '-A',
     'T': '-T',
     'G': '-g',
     'F': '-f',
     'S': '-s',
     'BINARY': 'binary',
     'D__ASSEMBLER__': '-D__ASSEMBLER__',
     'DESP_PLATFORM': '-DESP_PLATFORM',
     'DMBEDTLS_CONFIG_FILE': os.path.join(
         '-DMBEDTLS_CONFIG_FILE=mbedtls', 'esp_config.h'),
     'DHAVE_CONFIG_H': '-DHAVE_CONFIG_H',
     'MT': '-MT',
     'MMD': '-MMD',
     'MP': '-MP',
     'DWITH_POSIX': '-DWITH_POSIX',
     'INPUT_TARGET': '--input-target',
     'OUTPUT_TARGET': '--output-target',
     'ELF32_XTENSA_LE': 'elf32-xtensa-le',
     'BINARY_ARCH': '--binary-architecture',
     'XTENSA': 'xtensa',
     'RENAME_SECTION': '--rename-section',
     'EMBEDDED': '.data=.rodata.embedded',
     'CRU': 'cru',
     'ELF32': 'elf32-esp32ulp',
     'POSIX': 'posix'}


def main(argv):
    # Parse arguments (i.e.: -b in python script.py -b)
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', action='store')
    parser.add_argument('-p', action='store')
    parser.add_argument('-u', action='store')
    parser.add_argument('-x', action='store')
    parser.add_argument('-t', action='store')
    parser.add_argument('-I', action='append')
    args, options = parser.parse_known_args()

    ## Begin to append the preprocessor flags in a list
    for item in args.I:
        CPREPROCESSOR_FLAGS.append('-I')
        CPREPROCESSOR_FLAGS.append(item)

    ## Append the board options in a list
    board_options = []
    for item in options:
        if item.startswith('--'):
            board_options.append(item[1:])

    PATHS =\
        {'build': args.b,
         'core': args.p,
         'ulptool': args.t,
         'ucompiler': args.u,
         'xcompiler': args.x}

    os.chdir(os.path.join(PATHS['build'], 'sketch'))

    gen_assembly(PATHS)

    ulp_files = glob.glob('*.s')

    update_compilation_method(ppath)
    
    if not ulp_files:
        sys.stdout.write('No ULP Assembly File(s) Detected...\r\n')
        # try:
        #     with open('ulp_main.ld',"w"): pass
        #     # Comment extra flag
        #     # update_platform_local(ppath, enable_extra_flag = False)
        # except Exception as error:
        #     sys.stdout.write(error)

        # <-- Not used
        # with open('tmp.s', "w") as ulp:
        #     pass
        open('tmp.s', "w")

        ulp_files.append('tmp.s')
        build_ulp(PATHS, ulp_files, board_options, False)
        os.remove('tmp.s')
    else:
        build_ulp(PATHS, ulp_files, board_options, True)
    sys.exit(0)


def build_ulp(PATHS, ulp_sfiles, board_options, has_s_file):
    console_string = ''
    if has_s_file:
        console_string = 'ULP Assembly File(s) Detected: ' + \
            ', '.join(ulp_sfiles) + '\r\n'

    # <-- Not used
    # cmds = gen_cmds(os.path.join(PATHS['core'], 'tools'))

    flash_msg = ''
    ram_msg = ''

    for _file in ulp_sfiles:
        # <-- Not used
        # file = file.split('.')
        # file_names = gen_file_names(_file[0])

        # Run each assembly file (foo.S) through C preprocessor
        cmd = gen_xtensa_preprocessor_cmd(PATHS, _file, board_options)
        proc = subprocess.Popen(
            cmd[1],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False)

        (out, err) = proc.communicate()
        if err:
            error_string = cmd[0] + '\r\n' + err
            sys.exit(error_string)
            # error_string = cmd[0] + '\r' + err.decode('utf-8')
            # sys.exit(error_string)
        else:
            console_string += cmd[0] + '\r\n'
            # sys.stdout.write(cmd[0])

        # Run preprocessed assembly sources through assembler
        cmd = gen_binutils_as_cmd(PATHS, _file)
        proc = subprocess.Popen(
            cmd[1],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False)

        (out, err) = proc.communicate()
        if err:
            error_string = cmd[0] + '\r\n' + err
            sys.exit(error_string)
            # error_string = cmd[0] + '\r' + err.decode('utf-8')
            # sys.exit(error_string)
        else:
            console_string += cmd[0] + '\r\n'
            # sys.stdout.write(cmd[0])

    # Run linker script template through C preprocessor
    cmd = gen_xtensa_ld_cmd(PATHS, ulp_sfiles, board_options)
    proc = subprocess.Popen(
        cmd[1],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False)

    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r\n' + err
        # error_string = cmd[0] + '\r\n' + err.decode('utf-8')
        sys.exit(error_string)

    else:
        console_string += cmd[0] + '\r\n'
        # sys.stdout.write(cmd[0])

    # Link object files into an output ELF file
    cmd = gen_binutils_ld_cmd(PATHS, ulp_sfiles)
    proc = subprocess.Popen(
        cmd[1],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False)

    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r\n' + err
        # error_string = cmd[0] + '\r\n' + err.decode('utf-8')
        sys.exit(error_string)

    else:
        console_string += cmd[0] + '\r\n'
        # sys.stdout.write(cmd[0])

    # Get section memory sizes
    cmd = gen_binutils_size_cmd(PATHS)
    proc = subprocess.Popen(
        cmd[1],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False)

    (out, err) = proc.communicate()

    if err:
        error_string = cmd[0] + '\r\n' + err
        # error_string = cmd[0] + '\r\n' + err.decode('utf-8')
        sys.exit(error_string)

    else:
        # file_names_constant = gen_file_names_constant()
        # with open(file_names_constant['sym'],"w") as fsym:
        #     fsym.write(out.decode('utf-8'))
        # sys.stdout.write(cmd[0])
        try:
            file_path = os.path.join(
                PATHS['core'],
                'tools',
                'sdk',
                'include',
                'config',
                'sdkconfig.h')

            with open(file_path, "r") as file:
                text = file.read()

            mem = re.findall(
                r'#define CONFIG_ULP_COPROC_RESERVE_MEM (.*?)\n', text)[0]

            SECTIONS = dict(re.findall(
                r'^(\.+[0-9a-zA-Z_]+)\s+([0-9]+)',
                out,
                re.MULTILINE))

            maximum = 0.0
            text = 0.0
            data = 0.0
            bss = 0.0
            header = 0.0
            total = 0.0

            flash_precent = 0.0
            ram_precent = 0.0

            try:
                maximum = float(mem)

            except Exception:
                pass

            try:
                text = float(SECTIONS['.text'])

            except Exception:
                pass

            try:
                data = float(SECTIONS['.data'])

            except Exception:
                pass

            try:
                bss = float(SECTIONS['.bss'])

            except Exception:
                pass

            try:
                header = float(SECTIONS['.header'])

            except Exception:
                pass

            try:
                flash_precent =\
                    text/(maximum - data - bss - header) * 100

            except Exception:
                flash_precent =\
                    text/((maximum + 1) - data - bss - header) * 100

            try:
                ram_precent =\
                    (data + bss)/(maximum - text - header) * 100

            except Exception:
                ram_precent =\
                    (data + bss)/((maximum + 1) - text - header) * 100

            total = text + data + bss + header
            ram_left = maximum - total

            flash_msg =\
                "ULP uses %s bytes (%s%%) of program storage space. Maximum is %s bytes.\r\n" % (int(text), int(flash_precent), int(maximum - header))
            ram_msg = "Global variables use %s bytes (%s%%) of dynamic memory, leaving %s bytes for local variables. Maximum is %s bytes.\r\n" % (int(data + bss), int(ram_precent), int(ram_left), int(maximum - header))

        except Exception:
            pass

        console_string += cmd[0] + '\r\n'

    # Generate list of global symbols
    cmd = gen_binutils_nm_cmd(PATHS)
    proc = subprocess.Popen(
        cmd[1],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False)

    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r\n' + err
        sys.exit(error_string)
    else:
        file_names_constant = gen_file_names_constant()
        with open(file_names_constant['sym'], "w") as fsym:
            fsym.write(out)
        console_string += cmd[0] + '\r\n'

    # Create LD export script and header file
    cmd = gen_mapgen_cmd(PATHS)
    proc = subprocess.Popen(
        cmd[1],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False)

    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r\n' + err
        # error_string = cmd[0] + '\r\n' + err.decode('utf-8')
        sys.exit(error_string)

    else:
        console_string += cmd[0] + '\r\n'
        # sys.stdout.write(cmd[0])

    # Add the generated binary to the list of binary files
    cmd = gen_binutils_objcopy_cmd(PATHS)
    proc = subprocess.Popen(
        cmd[1],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False)

    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r\n' + err
        # error_string = cmd[0] + '\r\n' + err.decode('utf-8')
        sys.exit(error_string)

    else:
        console_string += cmd[0] + '\r\n'
        # sys.stdout.write(cmd[0])

    # Add the generated binary to the list of binary files
    cmd = gen_xtensa_objcopy_cmd(PATHS)
    proc = subprocess.Popen(
        cmd[1],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False)

    (out, err) = proc.communicate()
    if err:
        error_string = cmd[0] + '\r\n' + err
        # error_string = cmd[0] + '\r\n' + err.decode('utf-8')
        sys.exit(error_string)

    else:
        console_string += cmd[0] + '\r\n'
        # sys.stdout.write(cmd[0])

    # Check if sdkconfig.h md5 hash has changed indicating the file has changed
    sdk_hash = md5(os.path.join(
        PATHS['core'],
        'tools',
        'sdk',
        'include',
        'config',
        'sdkconfig.h'))

    dict_hash = dict()
    with open(os.path.join(PATHS['ulptool'], 'hash.json'), 'r') as file:
        dict_hash = json.load(file)

    if sdk_hash != dict_hash['sdkconfig.h']['hash']:
        with open(os.path.join(PATHS['ulptool'], 'hash.json'), 'w') as file:
            dict_hash['sdkconfig.h']['hash'] = sdk_hash
            file.write(json.dumps(dict_hash))

        # Run esp32.ld thru the c preprocessor generating esp32_out.ld
        cmd = gen_xtensa_ld_preprocessor_cmd(PATHS)
        proc = subprocess.Popen(
            cmd[1],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False)

        (out, err) = proc.communicate()
        if err:
            error_string = cmd[0] + '\r\n' + err
            sys.exit(error_string)

        else:
            console_string += cmd[0] + '\r\n'

    # print outputs or errors to the console
    candy = 81 * '*' + '\r\n'
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
                if top.startswith("#ifdef _ULPCC_"):
                    if bottom.startswith("#endif"):
                        ulpcc_files.append(file)

    except Exception as e:
        print(e)

    for file in ulpcc_files:
        cmd = gen_lcc_cmd(PATHS, file)
        proc = subprocess.Popen(
            cmd[1],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False)

        (out, err) = proc.communicate()
        if err:
            error_string = cmd[0] + '\r\n' + err
            sys.exit(error_string)
        else:
            if out == "":
                print(cmd[0])
            else:
                sys.exit(str(out))


def gen_lcc_cmd(PATHS, file):
    soc_path = os.path.join(
        PATHS['core'], 'tools', 'sdk', 'include', 'soc', 'soc')
    include_path = os.path.join(
        PATHS['core'], 'tools', 'sdk', 'include', 'soc')
    header_path = os.path.join(PATHS['ulptool'], 'ulpcc', 'include')
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
    XTENSA_GCC_PREPROCESSOR.append(os.path.join(
        PATHS['core'], 'tools', 'sdk', 'ld', 'esp32_out.ld'))
    XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['I'])
    XTENSA_GCC_PREPROCESSOR.append(os.path.join(
        PATHS['core'], 'tools', 'sdk', 'include', 'config'))
    XTENSA_GCC_PREPROCESSOR.append(os.path.join(
        PATHS['core'], 'tools', 'sdk', 'ld', 'esp32.ld'))
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
    # XTENSA_GCC_PREPROCESSOR.append(EXTRA_FLAGS['C'])
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
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['OUTPUT_TARGET'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['ELF32_XTENSA_LE'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['BINARY_ARCH'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['XTENSA'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['RENAME_SECTION'])
    XTENSA_OBJCOPY.append(EXTRA_FLAGS['EMBEDDED'])
    XTENSA_OBJCOPY.append(file_names_constant['bin'])
    XTENSA_OBJCOPY.append(file_names_constant['bin_o'])
    STR_CMD = ' '.join(XTENSA_OBJCOPY)
    return STR_CMD, XTENSA_OBJCOPY


def gen_file_names(sfile):
    file_names =\
        {'o': sfile + '.ulp.o',
         'ps': sfile + '.ulp.pS',
         'lst': sfile + '.ulp.lst'}
    return file_names


def gen_file_names_constant():
    file_names =\
        {'ld': 'ulp_main.common.ld',
         'elf': 'ulp_main.elf',
         'map': 'ulp_main.map',
         'sym': 'ulp_main.sym',
         'bin': 'ulp_main.bin',
         'bin_o': 'ulp_main.bin.bin.o'}
    return file_names


def gen_cmds(path):
    cmds =\
        {'ULP_MAPGEN': os.path.join(path, 'esp32ulp_mapgen.py')}
    return cmds


def gen_xtensa_cmds(path):
    cmds =\
        {'XTENSA_GCC': os.path.join(path, 'xtensa-esp32-elf-gcc'),
         'XTENSA_OBJCPY': os.path.join(path, 'xtensa-esp32-elf-objcopy'),
         'XTENSA_AR': os.path.join(path, 'xtensa-esp32-elf-ar')}
    return cmds


def gen_binutils_cmds(path):
    cmds =\
        {'ULP_AS': os.path.join(path, 'esp32ulp-elf-as'),
         'ULP_LD': os.path.join(path, 'esp32ulp-elf-ld'),
         'ULP_NM': os.path.join(path, 'esp32ulp-elf-nm'),
         'ULP_SIZE': os.path.join(path, 'esp32ulp-elf-size'),
         'ULP_OBJCPY': os.path.join(path, 'esp32ulp-elf-objcopy')}
    return cmds


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


## Uncomment/Comment extra flag for compilation
def update_platform_local(ppath, enable_extra_flag = True):
    temp = []
    ## Read and evalute the next action (overwrite or return)
    with open(os.path.join(ppath, 'platform.local.txt'), "r") as pltf:
        for line in pltf:
            temp.append(line)

    temp_write = temp

    if 'compiler.c.elf.extra_flags' in ' '.join(temp):
        for index_line in range(len(temp)):      
            if 'compiler.c.elf.extra_flags' in temp[index_line]:
                if (enable_extra_flag and not ('#' in temp[index_line])) or (not enable_extra_flag and ('#' in temp[index_line])):
                    sys.stdout.write('ULP compilation is already activated.\n' if enable_extra_flag else 'ULP compilation is already desactivated.\n')
                    return
                
                elif enable_extra_flag and ('#' in temp[index_line]):       # Update to active ulp compilation
                    error = 'Active ULP compilation, you have to recompile the code.'
                    extra_flag = temp[index_line][temp[index_line].find('compiler.c.elf.extra_flags'):]
                    temp_write.remove(temp[index_line])
                    temp_write.insert(index_line, extra_flag)
                    
                elif not enable_extra_flag and not ('#' in temp[index_line]):   # Update to desactivate the ulp compilation
                    error = 'Desactive ULP compilation, you have to recompile the code.'
                    extra_flag = '## ' + temp[index_line][temp[index_line].find('compiler.c.elf.extra_flags'):]
                    temp_write.remove(temp[index_line])
                    temp_write.insert(index_line, extra_flag)
                
    else:
        return "Unable to uptdate 'platform.local.txt'"

    # Overwrite the file
    with open(os.path.join(ppath, 'platform.local.txt'), "w") as pltf:
        for line in temp_write:
            pltf.write(line)
    sys.exit(error)
    return

def update_compilation_method(ppath):
    ## Search variable in 'platform.txt'
    temp_plt = []
    with open(os.path.join(ppath, 'platform.txt'), "r") as pltf:
        for line in pltf:
            temp_plt.append(line)

    for line in temp_plt:
        if 'recipe.c.combine.pattern' in line:
            recipe_c_combine_pattern = line

    """
    From:
    ## Combine gc-sections, archives, and objects
    recipe.c.combine.pattern="{compiler.path}{compiler.c.elf.cmd}" {compiler.c.elf.flags} {compiler.c.elf.extra_flags} -Wl,--start-group {object_files} "{archive_file_path}" {compiler.c.elf.libs} -Wl,--end-group -Wl,-EL -o "{build.path}/{build.project_name}.elf"

    To:
    ## Combine gc-sections, archives, and objects
    recipe.c.combine.pattern=python "{tools.ulptool.path}recipe_c_combine_pattern.py" -b "{build.path}" -c "{compiler.path}{compiler.c.elf.cmd}" -f {compiler.c.elf.flags} -xf {compiler.c.elf.extra_flags} -sf -Wl,--start-group {object_files} "{archive_file_path}" {compiler.c.elf.libs} -Wl,--end-group -Wl,-EL -o "{build.path}/{build.project_name}.elf"
    """
    
    ## Build variable
    var = 'recipe.c.combine.pattern'
    script = '=python "{tools.ulptool.path}recipe_c_combine_pattern.py" -b "{build.path}" -c '
    compiler_path = recipe_c_combine_pattern[recipe_c_combine_pattern.find('=')+1:]
    compiler_path = compiler_path[:compiler_path.find('" ')+1] + ' -f '  
    compiler_flags = '{compiler.c.elf.flags}' if '{compiler.c.elf.flags}' in recipe_c_combine_pattern else ''
    compiler_extra_flags = '{compiler.c.elf.extra_flags}' if '{compiler.c.elf.extra_flags}' in recipe_c_combine_pattern else ''
    compiler_sufix_flags = recipe_c_combine_pattern[recipe_c_combine_pattern.find('{compiler.c.elf.extra_flags}')+len('{compiler.c.elf.extra_flags}')+1:] if recipe_c_combine_pattern.find('{compiler.c.elf.extra_flags}') != -1 else ''
    cmd = var + script + compiler_path + compiler_flags + ' -xf ' + compiler_extra_flags + ' -sf ' + compiler_sufix_flags

    ## Check 'platform.local.txt' file for update
    temp_plt_lc = []
    with open(os.path.join(ppath, 'platform.local.txt'), "r") as pltf:
        for line in pltf:
            temp_plt_lc.append(line)
    
    update_needed = []
    up_to_date_flag = False
    for line in temp_plt_lc:
        if cmd in line:
            sys.stdout.write("'platform.local.txt' is up to date.\n")
            up_to_date_flag = True
        elif var in line:
            sys.stdout.write("'platform.local.txt' need to be updated (from old version).\n")
            update_needed.append(line)
    
    for i in update_needed:
        temp_plt_lc.remove(i)

    ## Update if needed
    if up_to_date_flag:
        if len(update_needed):
            sys.stdout.write("'platform.local.txt' need to be cleaned.\nStarts cleaning.\n")
            with open(os.path.join(ppath, 'platform.local.txt'), "w") as pltf:
                for line in temp_plt_lc:
                    pltf.write(line)
            sys.exit('\nYou need to recompile your script (this should happend only once).\n')
        return
        
    sys.stdout.write("'platform.local.txt' need to be updated.\nStarts update.\n")
    temp_plt_lc.append('\n## Combine gc-sections, archives, and objects with python\n')
    temp_plt_lc.append(cmd)

    with open(os.path.join(ppath, 'platform.local.txt'), "w") as pltf:
        for line in temp_plt_lc:
            pltf.write(line)
    
    sys.exit('\nYou need to recompile your script (this should happend only once).\n')
    
if __name__ == '__main__':
    main(sys.argv[1:])
