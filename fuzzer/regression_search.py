# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import re


base_path = os.path.dirname(os.path.realpath(__file__))


def start_search(testcase_path):
    searcher_path = base_path + "/util/commitsearcher.py"
    testcase_path
    command_with_args = ['python', searcher_path, testcase_path]
    output = subprocess.Popen(command_with_args, stdout=subprocess.PIPE).communicate()[0]
    regression_version = re.findall(r'\[\*\] - Found regression version : (.+)\n', output)[0]
    print "regression_version : " + regression_version

if __name__ == "__main__":
    if len(sys.argv) > 1:
        testcase_path = sys.argv[1]
        start_search(testcase_path)
    else:
        pass
