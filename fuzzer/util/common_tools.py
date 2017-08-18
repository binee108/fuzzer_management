# -*- coding: utf-8 -*-
import re
import hashlib
import resource
import subprocess
import sys
import time
import CrashInfo


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


# ulimit Set
def ulimit_set():
    # module only available on POSIX
    # Limit address space to 2GB (or 1GB on ARM boards such as ODROID).
    gb = 2**30
    resource.setrlimit(resource.RLIMIT_AS, (2 * gb, 2 * gb))

    # Limit corefiles to 0.5 GB.
    half_gb = int(gb / 2)
    resource.setrlimit(resource.RLIMIT_CORE, (half_gb, half_gb))


def run_timeout(command_with_args, uselog_files=False, child_stdout=None, child_stderr=None, time_out_limit=300):
    # runtime measurement
    start_time = time.time()
    try:
        child = subprocess.Popen(
            command_with_args,
            stdin=(None),
            stdout=(child_stdout if uselog_files else subprocess.PIPE),
            stderr=(child_stderr if uselog_files else subprocess.PIPE),
            preexec_fn=ulimit_set
        )
        if not uselog_files:
            child.communicate()
    except OSError as e:
        print("Tried to run : %r" % command_with_args)
        print("error : %s" % e)
        sys.exit(2)

    # Initialize variables
    killed = False
    # Check program exit status
    while 1:
        result_code = child.poll()
        running_time = time.time() - start_time
        if result_code is None:
            if running_time > time_out_limit and not killed:
                timeout_kill(child)
                killed = True
            else:
                time.sleep(0.010)
        else:
            break

    # Log file close
    if uselog_files:
        child_stdout.close()
        child_stderr.close()

    return_data = {
        'killed': killed,
        'running_time': running_time,
        'result_code': result_code,
        'child': child
    }
    return return_data


def reliable_crash_chk(execute_file, testcase, repeat=10, timeout=300):
    command_with_args = [execute_file, testcase]
    count = 0
    for i in xrange(repeat):
        return_data = run_timeout(command_with_args, time_out_limit=timeout)
        crash_chk = CrashInfo.is_crash(return_data['killed'], return_data['result_code'])

        if crash_chk:
            count += 1
        print "[*] - Crash %d  result_code : %d" % (count, return_data['result_code'])

    if count == repeat:
        return "Reliable"
    elif count > 0:
        return "Unreliable"
    else:
        return "None"

