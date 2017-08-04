# -*- coding: utf-8 -*-
import os
import threading
import time
import subprocess
import re
import requests
import base64
import json

import ConfigParser

base_path = os.path.dirname(os.path.realpath(__file__))


class ConnectPing:
    def __init__(self, config_info):
        self.config_info = config_info

    def connect_ping(self):
        local_ip = get_ip_address()
        self.url = "http://%s:%s/management/connect" % (self.config_info['manageweb_ip'], self.config_info['manageweb_port'])
        self.data = {
            'server_name': self.config_info['server_name'],
            'server_ip': local_ip,
            'fuzz_target': self.config_info['fuzz_target'],
            'fuzz_version': self.config_info['fuzz_version'],
        }
        while(1):
            print "[*] - Send Ping"
            self.data['working_status'] = fuzz_working_check()
            try:
                r = requests.post(url=self.url, data=self.data)
                response = r.text
            except:
                print "[*] - Check Web server running"
            time.sleep(60)

    def start(self):
        th = threading.Thread(target=self.connect_ping)
        th.start()
        return th


class CommandListen:
    def __init__(self, config_info):
        self.config_info = config_info

    def command_process(self, command):
        if command['command'] is 'build':
            fuzz_build()
        elif command['command'] is 'start':
            fuzz_start()
        elif command['command'] is 'stop':
            fuzz_stop()
        elif command['command'] is 'reboot':
            fuzz_reboot()
        elif command['command'] is 'regression_search':
            if not command['testcase_en'] is None:
                test_case_data = base64.decodestring(command['input_data_en'])
                regressions_search(test_case_data)
            else:
                print "args empty!"

    def polling_request(self):
        command_list = ['build', 'start', 'stop', 'reboot', 'regressions_search']
        self.url = "http://%s:%s/management/command_polling" % (self.config_info['manageweb_ip'], self.config_info['manageweb_port'])
        self.data = {
            'fuzz_name': self.config_info['fuzz_name'],
        }

        while(1):
            try:
                r = requests.post(url=self.url, data=self.data)
                response = r.text
            except:
                print "[*] - Check Web server running"
                time.sleep(5)
                continue
            command_data = json.loads(response)
            if command_data['command'] in command_list:
                print "command : " + command_data['command']  # debug code
                self.command_process(command_data)
            else:
                if "EMPTY" is not response:
                    print "Response Error"
                time.sleep(5)

    def start(self):
        th = threading.Thread(target=self.polling_request)
        th.start()
        return th


def get_ip_address():
    output = subprocess.Popen(['ifconfig', ], stdout=subprocess.PIPE).communicate()
    result = re.findall(r'inet addr:(\S+)', output[0])
    if len(result) > 0:
        for i in result:
            if "127.0.0.1" not in i:
                return i
        print "Need to check network."
    else:
        print "Error ifconfig command failed."
    return None


def set_config_info(section, option, value):
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fuzz_config.conf')
    if os.path.exists(config_path):
        config = ConfigParser.ConfigParser()
        config.read(config_path)
        config.set(section, option, value)
        with open(config_path, 'wb') as configfile:
            config.write(configfile)


def get_config_info():
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fuzz_config.conf')
    if os.path.exists(config_path):
        config = ConfigParser.ConfigParser()
        config.read(config_path)
    # file : fuzz_config.conf
    # [SERVER_INFO]
    # Server_ID=
    # Server_Name=
    # Fuzz_Target=
    # Fuzz_Version=

    # [MANAGEWEB_INFO]
    # ManageWeb_IP=10.211.55.5
    # ManageWeb_PORT=8000
        server_id = config.get('SERVER_INFO', 'Server_ID')
        server_name = config.get('SERVER_INFO', 'Server_Name')
        fuzz_target = config.get('SERVER_INFO', 'Fuzz_Target')
        fuzz_version = config.get('SERVER_INFO', 'Fuzz_Version')
        manageweb_ip = config.get('MANAGEWEB_INFO', 'ManageWeb_IP')
        manageweb_port = config.get('MANAGEWEB_INFO', 'ManageWeb_PORT')
    else:
        print "The fuzz_config.conf file does not exist."

    return {'server_id': server_id,
            'server_name': server_name,
            'fuzz_target': fuzz_target,
            'fuzz_version': fuzz_version,
            'manageweb_ip': manageweb_ip,
            'manageweb_port': manageweb_port}


def fuzz_build():
    output = subprocess.Popen(['./setup.sh', ], stdout=subprocess.PIPE)
    pass


def fuzz_start():
    if not fuzz_working_check():
        execute_file = os.path.join(base_path, "fuzz", "fuzzer.py")
        print "[*] - fuzz start "
        os.system(execute_file)
    else:
        print "[*] - already execute fuzzer!"


def fuzz_stop():
    output = subprocess.Popen(['pgrep', '-f', 'fuzz/fuzzer.py'], stdout=subprocess.PIPE).communicate()
    if (len(output[0]) != 0):
        os.system('kill -9 %s' % output[0])


def fuzz_reboot():
    output = subprocess.Popen(['pgrep', '-f', 'fuzz/fuzzer.py'], stdout=subprocess.PIPE).communicate()
    if (len(output[0]) != 0):
        os.system('kill -9 %s' % output[0])
    os.system('reboot')


def regressions_search(testcase_data):
    pass
    testcase_name = "testcase_data.txt"
    if os.path.exists(testcase_name):
        os.remove(testcase_name)
    try:
        with open(testcase_name, "wb") as f:
            f.write(testcase_data)
    except:
        pass
    if not fuzz_working_check():
        fuzz_stop()
    commit_version = subprocess.Popen(['python', 'fuzz/regressions_search.py', testcase_name], stdout=subprocess.PIPE).communicate()
    return commit_version


def fuzz_working_check():
    execute_file = os.path.join(base_path, "fuzz", "fuzzer.py")
    output = subprocess.Popen(['pgrep', '-f', execute_file], stdout=subprocess.PIPE).communicate()
    if output[0] != '':
        print "[*] - fuzz process working"
        return True
    else:
        print "[*] - fuzz process not working"
        return False


def register_server(config_info):
    url = "http://%s:%s/register" % (config_info['manageweb_ip'], config_info['manageweb_port'])
    data = {
        'server_id': "null",
        'server_ip': get_ip_address()
    }
    while True:
        try:
            r = requests.post(url=url, data=data)
            break
        except:
            time.sleep(5)
            continue
    response = r.text
    if "server_id : " in response:
        print response
        server_id = re.findall(r'server_id : (.+)', response)[0]
        print server_id
    set_config_info('SERVER_INFO', 'Server_ID', server_id)


def start_main():
    th = []
    config_info = get_config_info()
    if not config_info['server_id']:
        register_server(config_info)
        time.sleep(1)
    th.append(ConnectPing(config_info).start())
    # th.append(CommandListen(config_info).start())
    # # fuzz_start()
    # time.sleep(1)
    # for thread in th:
    #     thread.join()

if __name__ == "__main__":
    start_main()
