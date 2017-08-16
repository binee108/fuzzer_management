# -*- coding: utf-8 -*-
import ConfigParser
import os


def get_setting_config():
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../setting.conf')
    if os.path.exists(config_path):
        config = ConfigParser.ConfigParser()
        config.read(config_path)
    # file : fuzz_config.conf
    # [FUZZER_INFO]
    # Fuzz_Name = whale_fuzz_1
    # Fuzz_Target = whale
    # Fuzz_Version = 5.9

    # [SERVER_INFO]
    # Server_IP=10.10.10.10
        build_directory = config.get('PATH', 'build_directory')
        exec_directory = config.get('PATH', 'exec_directory')
        execute_target = config.get('PATH', 'execute_target')
        testcase = config.get('PATH', 'testcase')
    else:
        print "setting.conf file does not exist."

    return {'build_directory': build_directory,
            'exec_directory': exec_directory,
            'execute_target': execute_target,
            'testcase': testcase}
