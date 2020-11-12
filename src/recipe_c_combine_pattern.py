import os
import sys
import glob
import shlex
import argparse
import subprocess


def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', action='store', help="compiler path")
    parser.add_argument('-b', action='store', help="build path")

    args, _ = parser.parse_known_args()

    bpath = args.b

    os.chdir(os.path.join(bpath, 'sketch'))
    ulp_files = glob.glob('*.s')
    index_c = argv.index('-c')
    index_f = argv.index('-f')
    index_xf = argv.index('-xf')
    index_sf = argv.index('-sf')

    c_p = argv[index_c+1:index_f]       # Compiler's path
    c_f = argv[index_f+1:index_xf]      # Compiler's flags
    c_xf = argv[index_xf+1:index_sf]    # Compiler's extra flags
    c_sf = argv[index_sf+1:]            # Compiler's sufix flags

    cmd = []
    if not ulp_files:
        sys.stdout.write('No ULP extra flags\r\n')
        cmd = c_p + c_f + c_sf

    else:
        sys.stdout.write('Adding ULP extra flags\r\n')
        cmd = c_p + c_f + c_xf + c_sf

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False)

    (_, err) = proc.communicate()

    if err:
        error_string = ' '.join(cmd) + '\r\n' + err.decode('utf-8')
        sys.exit(error_string)

    else:
        sys.stdout.write(' '.join(cmd))

    sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])

# compiler.c.elf.extra_flags="-L {build.path}/sketch/"
# -T ulp_main.ld "{build.path}/sketch/ulp_main.bin.bin.o"
