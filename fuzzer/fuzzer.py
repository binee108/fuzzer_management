#!/usr/bin/env python
# coding=utf-8
# pylint: disable=fixme,import-error,invalid-name,line-too-long,missing-docstring,no-member,too-many-branches,too-many-locals,too-many-statements,unused-argument,wrong-import-position

from __future__ import absolute_import
import resource
import os
import subprocess
import time
import signal
import util.CrashInfo as CrashInfo
import util.fileManipulation
import util.setting_parser
import util.commit_searcher
import util.common_tools as common_tools

ASAN_EXIT_CODE = 77
(CRASHED, TIMED_OUT, NORMAL, ABNORMAL, NONE) = range(5)
file_path = os.path.dirname(os.path.realpath(__file__))


def get_signal_name(num, default=None):
    for p in dir(signal):
        if p.startswith("SIG") and not p.startswith("SIG_"):
            if getattr(signal, p) == num:
                return p
    return default


def crash_result(child, LogPrefix, progfullname, testcase):
    util.CrashInfo.grab_crashlog(progfullname, child.pid, LogPrefix, True)
    [before, after] = util.fileManipulation.fuzzSplice(testcase)
    try:
        with open(LogPrefix + '-out.txt', 'rb') as f:
            newfileLines = before + [l.replace('/*FRC-', '/*') for l in util.fileManipulation.linesStartingWith(f, "/*FRC-")] + after
        util.fileManipulation.writeLinesToFile(newfileLines, LogPrefix + "-orig.js")
    except:
        os.rename(LogPrefix + '-out.txt', LogPrefix + '-out.txt_MemoryError')
        os.rename(LogPrefix + "-err.txt", LogPrefix + '-err.txt_MemoryError')
        print "[*] - crash_result() Error"
        return None, None
    crash_dump = LogPrefix + "-crash.txt"
    ori_testcase = LogPrefix + "-orig.js"
    return crash_dump, ori_testcase


def reliable_check(excute_file, testcase):
    crash_reliable = util.common_tools.reliable_crash_chk(excute_file, testcase, 10)
    print "[*] Crash " + crash_reliable
    return crash_reliable


def crash_upload(LogPrefix, crash_dump, testcase, crash_hash, reliable):
    command_with_args = []
    crash_uploader_path = os.path.normpath(os.path.join(file_path, "../crash_uploader.py"))
    command_with_args.append('python')
    command_with_args.append(crash_uploader_path)
    command_with_args.append(crash_dump)
    command_with_args.append(testcase)
    command_with_args.append(crash_hash)
    command_with_args.append(reliable)
    output = subprocess.Popen(['python', crash_uploader_path, crash_dump, testcase, crash_hash, reliable], stdout=subprocess.PIPE).communicate()
    if "Seccuss" in output[0]:
        os.remove(LogPrefix + "-crash.txt")
        os.remove(LogPrefix + "-out.txt")
        os.remove(LogPrefix + "-err.txt")
        os.remove(LogPrefix + "-orig.js")
    else:
        print output[0]
        print "[*] - upload Fail"


def start_fuzz(command_with_args, log_path, time_out_limit=300):
    iteration = 0
    while 1:
        iteration += 1
        # Open log file
        useLogFiles = isinstance(log_path, str)
        if useLogFiles:
            LogPrefix = os.path.join(log_path, "w" + str(iteration))
            childStdOut = open(LogPrefix + "-out.txt", "w")
            childStdErr = open(LogPrefix + "-err.txt", "w")

        if not os.path.exists(command_with_args[1]):
            print "No such file %s" % command_with_args[1]

        # execute js file
        return_data = common_tools.run_timeout(command_with_args, useLogFiles, childStdOut, childStdErr, time_out_limit)
        print "Round %d " % iteration,
        print " %5.1fs " % return_data['running_time'],

        is_crash = CrashInfo.is_crash(return_data['killed'], return_data['result_code'])

        if is_crash is True:
            progfullname = os.path.normpath(os.path.expanduser(command_with_args[0]))
            testcase = os.path.abspath(command_with_args[1])
            crash_dump, ori_testcase = crash_result(return_data['child'], LogPrefix, progfullname, testcase)
            if crash_dump is None or ori_testcase is None:
                continue
            reliable = reliable_check(command_with_args[0], ori_testcase)
            if reliable == "Reliable":
                pass
                # print "Reliable start commit search!"
                # commit_version = util.commit_searcher.search(ori_testcase)
                # if not commit_version is None:
                #     print "Found commit version!"
            crash_hash = CrashInfo.crash_dump_hash(crash_dump)
            crash_upload(LogPrefix, crash_dump, ori_testcase, crash_hash, reliable)
        else:
            os.remove(LogPrefix + "-out.txt")
            os.remove(LogPrefix + "-err.txt")


def main():
    # Command arguments setting.
    setting_info = util.setting_parser.get_setting_config()
    exec_directory = os.path.join(file_path, setting_info['exec_directory'])
    excute_file = os.path.join(exec_directory, setting_info['execute_target'])
    testcase = os.path.join(file_path, setting_info['testcase'])
    command_with_args = [excute_file, testcase]

    # v8 setting settig.
    if not os.path.exists(exec_directory):
        print "Please target build or Invalid exec_directory in setting.conf"
        exit(0)

    # Create a temporary task folder
    i = 1
    while True:
        tmpdir_with_num = 'wtmp' + str(i)
        tmpdir = os.path.join(file_path, tmpdir_with_num)
        if os.path.isdir(tmpdir):
            i += 1
            pass
        else:
            os.mkdir(tmpdir)
            break

    # Start Fuzzing!
    start_fuzz(command_with_args, tmpdir)

if __name__ == "__main__":
    main()
