import os
import os.path
import shlex
import subprocess


def escape_posix_path(posix_path):
    return shlex.quote(posix_path)


def escape_nt_path(nt_path):
    return subprocess.list2cmdline([nt_path])


def escape_path(path):
    # os.name
    # The name of the operating system dependent module imported.
    # The following names have currently been registered: 'posix', 'nt', 'java'.
    # Jython on POSIX:
    # >>> os.name
    # PyShadowString('java', 'posix') 
    # >>> os.name.getshadow()
    # 'posix'
    # Jython on NT:
    # >>> os.name
    # PyShadowString('java', 'nt') 
    # >>> os.name.getshadow()
    # 'nt'
    if os.name == 'posix' or os.name == 'java' and os.name.getshadow() == 'posix':
        return escape_posix_path(path)
    elif os.name == 'nt' or os.name == 'java' and os.name.getshadow() == 'nt':
        return escape_nt_path(path)
    else:
        raise OSError("Unsupported os.name: %s" % os.name)