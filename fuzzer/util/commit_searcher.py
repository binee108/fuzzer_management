# -*- coding: utf-8 -*-
import sys
import subprocess
import re
import CrashInfo
import setting_parser
import os

base_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.normpath(os.path.join(base_path, ".."))


def chdir_v8():
    setting_info = get_setting_info()
    exec_directory = os.path.join(root_path, setting_info['exec_directory'])
    os.chdir(exec_directory)
    return os.getcwd()


def get_current_version():
    output = subprocess.Popen(['git', 'status', ], stdout=subprocess.PIPE).communicate()
    if "HEAD detached at origin/master" in output[0]:
        version = "origin/master"
    elif "HEAD detached at" in output[0]:
        version = re.findall(r'HEAD detached at (.*)\n', output[0])
    elif "On branch" in output[0]:
        version = re.findall(r'On branch (.*)\n', output[0])
    else:
        version = [None, ]
    return version[0]


def get_setting_info():
    setting_info = setting_parser.get_setting_config()
    return setting_info


def lkgr_list_get():
    # git branch -r | grep lkgr
    proc1 = subprocess.Popen(['git', 'branch', '-r', ], stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(['grep', 'lkgr', ], stdin=proc1.stdout, stdout=subprocess.PIPE)
    output = proc2.communicate()
    lkgr_version_list = re.findall(r'origin\/(.*)\n', output[0])
    return lkgr_version_list


def all_list_get():
    output = subprocess.Popen(['git', 'branch', '-r', ], stdout=subprocess.PIPE).communicate()
    all_version_list = re.findall(r'origin\/([0-9|.]+[-a-z]*)\n', output[0])
    return all_version_list


def lkgr_searching(v8_current_lkgr_version, lkgr_vlist, all_vlist, crash_input_file):
    start_index, end_index = 0, 0
    current_lkgr_index = lkgr_vlist.index(v8_current_lkgr_version)
    use_lkgr_vlist = lkgr_vlist[:current_lkgr_index]
    use_lkgr_vlist.reverse()
    pre_lkgr_version = lkgr_vlist[current_lkgr_index]
    for lkgr_version in use_lkgr_vlist:
        print "[*] - lkgr version search %s" % (lkgr_vlist[lkgr_version])
        check = crash_check(lkgr_version, crash_input_file)
        if check is False:
            start_index = all_vlist.index(lkgr_version)
            end_index = all_vlist.index(pre_lkgr_version)
            break
        elif check is True:
            pre_lkgr_version = lkgr_version
        else:
            return None, None
    return start_index, end_index


def binary_searching(start_index, end_index, all_vlist, crash_input_file):
    start = start_index
    end = end_index
    print "[*] - binary search start : %s - > %s" % (all_vlist[start], all_vlist[end])
    while start < end:
        print "[*] - %s <-> %s" % (all_vlist[start], all_vlist[end])
        mid = (start + end) / 2
        if crash_check(all_vlist[mid], crash_input_file):
            end = mid
        else:
            start = mid + 1
        if start == end:
            if start == start_index:
                return None
            else:
                return all_vlist[start]


def v8_change_branch(branch_version):
    result = subprocess.Popen(['git', 'checkout', branch_version], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if bool(re.search(r'Your branch is up-to-date with', result[0])):
        return True
    elif bool(re.search(r'Switched to a new branch ', result[1])):
        return True
    elif bool(re.search(r'Switched to branch ', result[1])):
        return True
    elif bool(re.search(r'HEAD is now at ', result[1])):
        return True
    else:
        print "[debug] - result[0] : " + result[0]
        print "[debug] - result[1] : " + result[1]
        return False


def v8_exec(crash_input_file):
    setting_info = get_setting_info()
    execute_target = os.path.join(root_path, setting_info['execute_target'])
    if common_tools.reliable_crash_chk(execute_target, crash_input_file, 1) == "Reliable":
        return True
    else:
        return False


def v8_build():
    print "[*] - build start"
    subprocess.call('gclient sync', shell=True, stdout=subprocess.PIPE)
    print "[*] - complete gclient sync"
    subprocess.call('tools/dev/v8gen.py x64.release', shell=True, stdout=subprocess.PIPE)
    print "[*] - complete tools/dev/v8gen.py x64.release"
    subprocess.call('ninja -C out.gn/x64.release', shell=True, stdout=subprocess.PIPE)
    print "[*] - complete ninja -C out.gn/x64.release"


def crash_check(version, crash_input_file):
    if v8_change_branch(version):
        v8_build()
        return v8_exec(crash_input_file)
    else:
        print "[*] - Change branch error!"
        return None


def search(crash_input_file, crash_lkgr_version=None):
    setting_info = setting_parser.get_setting_config()
    build_directory = os.path.join(root_path, setting_info['build_directory'])
    exec_directory = os.path.join(root_path, setting_info['exec_directory'])
    if os.path.exists(build_directory):
        subprocess.call("rm -rf %s" % (build_directory), shell=True)
    subprocess.call("cp -a %s %s" % (exec_directory, build_directory), shell=True)
    chdir_v8()
    lkgr_vlist = lkgr_list_get()
    all_vlist = all_list_get()
    if crash_lkgr_version is None:
        v8_origin_version = get_current_version()
        if v8_origin_version is None:
            print "[*] - Not found version."
            return None
        v8_crash_version = v8_origin_version
    else:
        v8_crash_version = crash_lkgr_version

    # searching
    start_index, end_index = lkgr_searching(v8_crash_version, lkgr_vlist, all_vlist, crash_input_file)
    if start_index is not None and end_index is not None:
        commit_crash_version = binary_searching(start_index, end_index, all_vlist, crash_input_file)
    if commit_crash_version is None:
        print "[*] - Not Found Version"
        return None
    else:
        print "[*] - Found regression version : %s" % commit_crash_version
        return commit_crash_version

if __name__ == "__main__":
    argv_len = len(sys.argv)
    if argv_len == 2:
        crash_input_file = sys.argv[1]
        crash_lkgr_version = None
    elif argv_len == 3:
        crash_input_file = sys.argv[1]
        crash_lkgr_version = sys.argv[2]
        if 'lkgr' not in crash_lkgr_version:
            print "[*] - Please enter only the lkgr version."
            exit(1)
    else:
        print "[*] - useage : python commit_searcher.py [crash_input_file] (crash_lkgr_version)"
        exit(1)
    setting_info = get_setting_info()
    execute_target = os.path.join(root_path, setting_info['exec_directory'], setting_info['execute_target'])
    if common_tools.reliable_crash_chk(execute_target, crash_input_file, 10) != "Reliable":
        search(crash_input_file, crash_lkgr_version)
    else:
        print "[*] - Unreliable Crash_Dump"
        exit(1)
