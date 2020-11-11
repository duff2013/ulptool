import os
import sys
import glob
import shlex
import argparse
import subprocess

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store')   # Compiler path
    parser.add_argument('-b', action='store')   # Build path
    # parser.add_argument('-f', action='store')   # Compiler flag
    # parser.add_argument('-xf', action='store')  # Extra ompiler flag
    # parser.add_argument('-sf', action='store')  # Compiler sufixes
    args, options = parser.parse_known_args()
    """
    print('b', args.b)
    print('c', args.c)
    print('f', args.f)
    print('sf', args.sf)
    print('xf', args.xf)
    """
    bpath = args.b

    os.chdir(os.path.join(bpath, 'sketch'))
    ulp_files = glob.glob('*.s')

    # cmd = args.c.replace('\\','/')

    """
    cmd += ' ' + args.f.replace('\\','/')
    
    if not ulp_files:
        sys.stdout.write('No ULP extra flags\r')
    else:
        sys.stdout.write('Adding ULP extra flags\r')
        cmd += ' ' + args.xf.replace('"','').replace('\\','/')
    cmd += ' ' + args.sf.replace('"','').replace('\\','/')

    cmd_args = shlex.split(cmd)

    temp = ''
    cmd_formated = []
    previous = ''
    for arg in cmd_args:
        if arg == '-L':
            temp = '"-L'
        elif arg.startswith('-'):
            cmd_formated.append(arg)
        else:
            if temp == '"-L':
                temp += arg + '"'
                cmd_formated.append(temp)
            else:
                if previous != '-T' and previous != '-u':
                    cmd_formated.append('"' + arg + '"')
                else:
                    cmd_formated.append(arg)
        previous = arg
    """
    
    # print(cmd_formated)
    # last_val = cmd_formated[len(cmd_formated)-1]

    """
    all_args = []
    for arg in argv:
        all_args.append(arg.replace('\\','/'))

    print(all_args)
    """        
        
    # print(argv)
    # print(last_val)
    # print(type(argv))
    # print(all_args.index(last_val))
    # print(argv[:])
    # print(cmd_formated[len(cmd_formated)-1])
    # print(' '.join(cmd_formated))

    index_c = argv.index('-c')
    index_f = argv.index('-f')
    index_xf = argv.index('-xf')
    index_sf = argv.index('-sf')

    # print(index_c, index_f, index_xf, index_sf)
    c_p = argv[index_c+1:index_f]       # Compiler's path
    c_f = argv[index_f+1:index_xf]      # Compiler's flags
    c_xf = argv[index_xf+1:index_sf]    # Compiler's extra flags
    c_sf = argv[index_sf+1:]            # Compiler's sufix flags

    cmd = []
    if not ulp_files:
        sys.stdout.write('No ULP extra flags\r')
        cmd = c_p + c_f + c_sf
    else:
        sys.stdout.write('Adding ULP extra flags\r')
        cmd = c_p + c_f + c_xf + c_sf
    #print(' '.join(cmd))

    '''
    cmd_formated = []
    previous = ''
    for arg in cmd:
        if arg.startswith('-') and not (('/' in arg) or ('\\' in arg)):
            cmd_formated.append(arg)
        else:
            if ('/' in arg) or ('\\' in arg):
                cmd_formated.append('"' + arg + '"')
            else:
                if previous != '-T' and previous != '-u':
                    cmd_formated.append('"' + arg + '"')
                else:
                    cmd_formated.append(arg)
        previous = arg

    # print(' '.join(cmd_formated))
    '''
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    (out, err) = proc.communicate()
    if err:
        error_string = ' '.join(cmd) + '\r' + err.decode('utf-8')
        sys.exit(error_string)
    else:
        sys.stdout.write(' '.join(cmd))
        
    sys.exit(0)
    
if __name__ == '__main__':
    main(sys.argv[1:])

# compiler.c.elf.extra_flags="-L {build.path}/sketch/" -T ulp_main.ld "{build.path}/sketch/ulp_main.bin.bin.o"
