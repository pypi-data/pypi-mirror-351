import getpass
import os
import platform
import subprocess
import sys

from dataclasses import dataclass


# -------------------
## holds OS specific info and runs OS specific commands
# there are four recognized OS:
#    OS      os_name
#  -------   ----------
#  Ubuntu  : ubuntu
#  Mac     : macos
#  Windows : win
#  RPI     : rpi
@dataclass(frozen=True)
class _OsSpecificInvocation:
    ## holds the OS name
    os_name: str
    ## holds the OS version info
    os_version: str
    ## holds the python version
    python_version: str
    ## projects directory
    proj_dir: str
    ## root directory of projects directory
    root_dir: str
    ## current userid
    userid: str
    ## hostname of the pc
    hostname: str

    # -------------------
    ## initialize
    #
    # selects the current platform and sets impl to it
    # @return None
    @classmethod
    def set_all_data(cls):
        ## holds the implementation class
        if os.path.isfile('/sys/firmware/devicetree/base/model'):
            os_name = 'rpi'
            # TODO confirm this is correct
            os_version = f'RPI {platform.system()} {platform.release()}'
            root_dir = '~'
            proj_dir = os.path.expanduser(os.path.join(root_dir, 'projects'))
        elif sys.platform == 'win32':
            os_name = 'win'
            os_version = f'win32 {platform.system()} {platform.release()}'
            root_dir = '/c'
            # translates to c:\projects
            proj_dir = os.path.expanduser(os.path.join(os.sep, 'projects'))
        elif sys.platform == 'darwin':
            os_name = 'macos'
            os_version = f'macOS {platform.mac_ver()[0]}'
            root_dir = '~'
            proj_dir = os.path.expanduser(os.path.join(root_dir, 'projects'))
        elif sys.platform == 'linux':
            os_name = 'ubuntu'
            os_version = cls._ubuntu_os_version()
            root_dir = '~'
            proj_dir = os.path.expanduser(os.path.join(root_dir, 'projects'))
        else:
            print(f'BUG  unrecognized OS: "{sys.platform}"')
            sys.exit(1)

        ## holds python version e.g. "Python 3.10"
        python_version = f'Python {sys.version_info.major}.{sys.version_info.minor}'

        return cls(os_name=os_name,
                   os_version=os_version,
                   python_version=python_version,
                   root_dir=root_dir,
                   proj_dir=proj_dir,
                   userid=getpass.getuser(),
                   hostname=platform.uname().node
                   )

    # -------------------
    ## run a command
    #
    # @param cmd          the command to run
    # @param working_dir  the working directory; default is '.'
    # @param print_cb     callback function to print the current output line; default is None
    # @return rc return code, lines the full set of output lines
    def run_cmd(self, cmd, working_dir='.', print_cb=None):
        shell = True
        ## see os_name property above
        if self.os_name == 'win':
            cmd = ['c:/msys64/usr/bin/bash', '-c', cmd]

        proc = subprocess.Popen(cmd,  # pylint: disable=consider-using-with
                                cwd=working_dir,
                                shell=shell,
                                bufsize=0,
                                universal_newlines=True,
                                stdin=None,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

        last_line = ''
        lineno = 0
        lines = []
        while True:
            if last_line:
                last_line = last_line.rstrip()
                lines.append(last_line)
                if print_cb:
                    print_cb(lineno, last_line)
                    sys.stdout.flush()
            ret_code = proc.poll()
            if ret_code is not None and last_line == '':
                break
            last_line = proc.stdout.readline()
            lineno += 1

        # proc.wait()
        sys.stdout.flush()
        rc = proc.returncode

        return rc, lines

    # -------------------
    ## holds OS information for Ubuntu
    #
    # @return string indicating OS info
    @classmethod
    def _ubuntu_os_version(cls):
        proc = subprocess.Popen(["lsb_release", "-a"],  # pylint: disable=consider-using-with
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT
                                )
        (out, _) = proc.communicate()
        out = out.decode('utf-8')

        version = 'notset'
        codename = 'notset'
        for line in out.split('\n'):
            # print(f'line: "{line}"')
            args = line.split('\t')
            if args[0] == 'Release:':
                version = args[1]
            elif args[0] == 'Codename:':
                codename = args[1]
        return f'Ubuntu {version} {codename}'


OsSpecific = _OsSpecificInvocation.set_all_data()
