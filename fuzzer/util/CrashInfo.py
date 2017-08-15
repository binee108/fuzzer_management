# -*- coding: utf-8 -*-
# Reference MozillaSecurity/lithium
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import signal
import hashlib
import common_tools

isLinux = (platform.system() == 'Linux')


def crash_dump_hash(crash_dump_path):
    with open(crash_dump_path) as f:
        dump_data = f.read()
    output = re.search(r'backtrace\s+(#[0-9]+\s\s0x[\w]+\sin\s.+\n)+', dump_data).group(0)
    find_list = re.findall(r'#[0-9]+\s+(0x[0-9a-z]+)\sin\s(.+)\n', output)
    sum_addr_value = ''
    sum_func_name = ''
    for i in find_list:
        sum_addr_value += i[0][-3:]
        sum_func_name += i[1]

    sum_data = sum_addr_value + sum_func_name
    m = hashlib.md5()
    m.update(sum_data.encode('utf-8'))
    crash_hash = m.hexdigest()
    return crash_hash


def is_crash(killed, result_code):
    ASAN_EXIT_CODE = 77
    crash_chk = False
    if killed and (result_code == -signal.SIGKILL):
        msg = 'TIMED OUT'
    elif result_code == 0:
        msg = 'NORMAL'
    elif result_code == ASAN_EXIT_CODE:
        msg = 'CRASHED (Address Sanitizer fault)'
        crash_chk = True
    elif result_code > 0:
        msg = 'ABNORMAL exit code ' + str(result_code)
    else:
        signum = -result_code
        msg = 'CRASHED signal %d (%s)' % (signum, get_signal_name(signum, "Unknown signal"))
        crash_chk = True
    print(msg)
    return crash_chk


def reliable_crash_chk(execute_file, input_file, repeat=10, timeout=300):
    command_with_args = [execute_file, input_file]
    count = 0
    for i in xrange(repeat):
        return_data = common_tools.run_timeout(command_with_args, time_out_limit=timeout)
        crash_chk = is_crash(return_data['killed'], return_data['result_code'])

        if crash_chk:
            count += 1
        print "[*] - Crash %d  result_code : %d" % (count, return_data['result_code'])

    if count == repeat:
        return "Reliable"
    elif count > 0:
        return "Unreliable"
    else:
        return "None"


def get_signal_name(num, default=None):
    for p in dir(signal):
        if p.startswith("SIG") and not p.startswith("SIG_"):
            if getattr(signal, p) == num:
                return p
    return default


def shellify(cmd):
    """Try to convert an arguments array to an equivalent string that can be pasted into a shell."""
    okUnquotedRE = re.compile(r"""^[a-zA-Z0-9\-\_\.\,\/\=\~@\+]*$""")
    okQuotedRE = re.compile(r"""^[a-zA-Z0-9\-\_\.\,\/\=\~@\{\}\|\(\)\+ ]*$""")
    ssc = []
    for i in xrange(len(cmd)):
        item = cmd[i]
        if okUnquotedRE.match(item):
            ssc.append(item)
        elif okQuotedRE.match(item):
            ssc.append('"' + item + '"')
    return ' '.join(ssc)


def disable_corefile():
    """When called as a preexec_fn, sets appropriate resource limits for the JS shell. Must only be called on POSIX."""
    import resource  # module only available on POSIX
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def get_abspath_for_file(filename):
    """Get the absolute path of a particular file, given its base directory and filename."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def norm_expuser_path(p):
    return os.path.normpath(os.path.expanduser(p))


def timeout_kill(p):
    try:
        p.kill()
    except WindowsError:
        if p.poll() == 0:
            try:
                print("Failed to kill process due to timeout")
                p.kill()
            except WindowsError:
                if p.poll() == 0:
                    print("Last attempt to kill processes due to time-out")
                    p.kill()


def construct_gdbcommand(progfullname, crashedPID):
    """Construct a command that uses the POSIX debugger (gdb) to turn a minidump file into a stack trace."""
    # On Mac and Linux, look for a core file.
    coreFilename = None
    if isLinux:
        isPidUsed = False
        if os.path.exists('/proc/sys/kernel/core_uses_pid'):
            with open('/proc/sys/kernel/core_uses_pid') as f:
                isPidUsed = bool(int(f.read()[0]))  # Setting [0] turns the input to a str.
        coreFilename = 'core.' + str(crashedPID) if isPidUsed else 'core'  # relative path
        print "current directory : " + os.getcwd()
        print "coreFilename : " + coreFilename
        if not os.path.isfile(coreFilename):
            coreFilename = norm_expuser_path(os.path.join('~', coreFilename))  # try the home dir

    if coreFilename and os.path.exists(coreFilename):
        debuggerCmdPath = get_abspath_for_file('gdb-quick.txt')
        assert os.path.exists(debuggerCmdPath)

        # Run gdb and move the core file. Tip: gdb gives more info for:
        # (debug with intact build dir > debug > opt with frame pointers > opt)
        return ["gdb", "-n", "-batch", "-x", debuggerCmdPath, progfullname, coreFilename]
    else:
        return None


def grab_crashlog(progfullname, crashedPID, log_path, wantStack):
    """Return the crash log if found."""
    # progname = os.path.basename(progfullname)

    useLogFiles = isinstance(log_path, str)
    if useLogFiles:
        if os.path.exists(log_path + "-crash.txt"):
            os.remove(log_path + "-crash.txt")
        if os.path.exists(log_path + "-core"):
            os.remove(log_path + "-core")

    # if not wantStack or progname == "valgrind":
    #     return

    if os.name == 'posix':
        debuggerCmd = construct_gdbcommand(progfullname, crashedPID)
    else:
        debuggerCmd = None

    if debuggerCmd:
        coreFile = debuggerCmd[-1]
        assert os.path.isfile(coreFile)
        debuggerExitCode = subprocess.call(
            debuggerCmd,
            stdin=None,
            stderr=subprocess.STDOUT,
            stdout=open(log_path + "-crash.txt", 'w') if useLogFiles else None,
            # It would be nice to use this everywhere, but it seems to be broken on Windows
            # (http://docs.python.org/library/subprocess.html)
            close_fds=(os.name == "posix"),
            preexec_fn=(disable_corefile if isLinux else None)  # Do not generate a corefile if gdb crashes in Linux
        )
        if debuggerExitCode != 0:
            print 'Debugger exited with code %d : %s' % (debuggerExitCode, shellify(debuggerCmd))
        if useLogFiles:
            if os.path.isfile(coreFile):
                shutil.move(coreFile, log_path + "-core")
                subprocess.call(["gzip", '-f', log_path + "-core"])
                # chmod here, else the uploaded -core.gz files do not have sufficient permissions.
                subprocess.check_call(['chmod', 'og+r', log_path + "-core.gz"])
            return log_path + "-crash.txt"
        else:
            print "I don't know what to do with a core file when log_path is null"
    elif isLinux:
        print "Warning: grab_crashlog() did not find a core file for PID %d." % crashedPID
        # print "Note: Your soft limit for core file sizes is currently %d. You can increase it with 'ulimit -c' in bash." % getCoreLimit()[0]
