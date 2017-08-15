# -*- coding: utf-8 -*-
import ConfigParser
import base64
import json
import os
import re
import socket
import subprocess
import threading
import time

import requests

base_path = os.path.dirname(os.path.realpath(__file__))


class ConnectPing:
    """
    관리 웹서버와 통신상태를 전달하는 클래스이다.

    매 60초마다 서버와 통신하여 연결상태를 갱신하고,
    fuzzer가 작동하고 있는 여부도 전달한다.
    fuzz_server_management.py가 실행 된 이후 서버가 종료 될 때까지
    지속적인 연결을 해야하므로, 쓰레드로 while문을 돌려서 실행한다.
    """
    def __init__(self, config_info):
        self.config_info = config_info

    def connect_ping(self):
        config_info = get_config_info()
        local_ip = get_ip_address()
        self.url = "http://%s:%s/manage/connect" % (self.config_info['manageweb_ip'], self.config_info['manageweb_port'])
        self.data = {
            'server_id': config_info['server_id'],
            'server_ip': local_ip
        }
        while(1):
            print "[*] - Send Ping"
            if fuzz_working_check():
                self.data['working_status'] = "On"
            else:
                self.data['working_status'] = "Off"
            try:
                r = requests.post(url=self.url, data=self.data)
                response = r.text
                if 'Success' not in response:
                    print "Connection Failed."
            except:
                print "[*] - Check Web server running"

            time.sleep(60)

    def start(self):
        th = threading.Thread(target=self.connect_ping)
        th.start()
        return th


class CommandListen:
    """
    관리 웹서버로부터 명령어를 전달 받는 클래스이다.

    매 5초마다 관리서버로 Server_ID를 전달하여 해당 Server_ID로 등록된
    명령어를 polling방식으로 가져온다.
    가져온 명령어는 command_process함수를 통해서 각각의 명령어를 수행한다.
    fuzz_server_management.py가 실행 된 이후 서버가 종료 될 때까지
    지속적인 연결을 해야하므로, 쓰레드로 while문을 돌려서 실행한다.
    """
    def __init__(self, config_info):
        self.config_info = config_info

    def command_process(self, command):
        if not command['en_data'] is None:
            plain_data = base64.decodestring(command['en_data'])
        if command['command'] in 'build':
            fuzz_build(plain_data)
        elif command['command'] in 'start':
            fuzz_start()
        elif command['command'] in 'stop':
            fuzz_stop()
        elif command['command'] in 'reboot':
            fuzz_reboot()
        elif command['command'] in 'regression':
            plain_data = base64.decodestring(command['en_data'])
            regression_version = regressions_search(plain_data)
            if 'issue_id' in command:
                update_regression_version(regression_version, issue_id=command['issue_id'])
            elif 'crash_id' in command:
                update_regression_version(regression_version, crash_id=command['crash_id'])
            else:
                print "[*] - Error issue_id, crash_id empty"
                return None

    def polling_request(self):
        command_list = ['build', 'start', 'stop', 'reboot', 'regression']
        self.url = "http://%s:%s/manage/command_polling" % (self.config_info['manageweb_ip'], self.config_info['manageweb_port'])
        self.data = {
            'server_id': self.config_info['server_id'],
        }
        while(1):
            try:
                r = requests.post(url=self.url, data=self.data)
                response = r.text
            except:
                print "[*] - Check Web server running"
                time.sleep(5)
                continue
            if "EMPTY" not in response:
                command_data = json.loads(response)
                if command_data['command'] in command_list:
                    print "command : " + command_data['command']  # debug code
                    self.command_process(command_data)
                    continue
                else:
                    print "[*] - Invalid Command"
            else:
                pass
                # print "[*] - Empty command"
            time.sleep(5)

    def start(self):
        th = threading.Thread(target=self.polling_request)
        th.start()
        return th


def get_ip_address():
    """
    로컬 IP를 가져오는 함수이다.
    관리 웹 서버상에 내부IP로 표시하여, 여러 서버를 구별 할 수 있게 도와줍니다.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("google.com", 80))
    r = s.getsockname()[0]
    s.close()
    return r


def set_config_info(section, option, value):
    """
    fuzz_config.conf 파일의 옵션을 설정하는 함수입니다.
    """
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fuzz_config.conf')
    if os.path.exists(config_path):
        config = ConfigParser.ConfigParser()
        config.read(config_path)
        config.set(section, option, value)
        with open(config_path, 'wb') as configfile:
            config.write(configfile)


def get_config_info():
    """
    fuzz_config.conf 파일의 옵션을 가져오는 함수입니다.
    """
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fuzz_config.conf')
    if os.path.exists(config_path):
        config = ConfigParser.ConfigParser()
        config.read(config_path)
        # [SERVER_INFO]
        # Server_ID=

        # [MANAGEWEB_INFO]
        # ManageWeb_IP=10.211.55.7
        # ManageWeb_PORT=8000
        server_id = config.get('SERVER_INFO', 'Server_ID')
        manageweb_ip = config.get('MANAGEWEB_INFO', 'ManageWeb_IP')
        manageweb_port = config.get('MANAGEWEB_INFO', 'ManageWeb_PORT')
    else:
        print "The fuzz_config.conf file does not exist."

    return {'server_id': server_id,
            'manageweb_ip': manageweb_ip,
            'manageweb_port': manageweb_port}


def fuzz_build(data):
    with open('setup.sh', 'wb') as f:
        f.write(data)
    output = subprocess.Popen(['./setup.sh', ], stdout=subprocess.PIPE).communicate()[0]
    return output


def fuzz_start():
    print "start"
    if not fuzz_working_check():
        execute_file = os.path.join(base_path, "fuzz", "fuzzer.py")
        print "[*] - fuzz start "
        subprocess.Popen(execute_file.split(' '))
        return 0
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
    """
    Crash가 발생한 Regression버전을 찾는 기능을 실행하는 함수입니다.
    """
    testcase_name = "testcase_data.txt"
    if os.path.exists(testcase_name):
        os.remove(testcase_name)
    try:
        with open(testcase_name, "wb") as f:
            f.write(testcase_data)
    except:
        pass
    if fuzz_working_check():
        fuzz_stop()
    commit_version = subprocess.Popen(['python', 'fuzz/regression_search.py', testcase_name], stdout=subprocess.PIPE).communicate()[0]
    return commit_version


def update_regression_version(regression_version, crash_id=None, issue_id=None):
    config_info = get_config_info()
    url = "http://%s:%s/manage/regression_version_update" % (config_info['manageweb_ip'], config_info['manageweb_port'])
    data = {
        'regression_version': regression_version,
        'crash_id': crash_id,
        'issue_id': issue_id
    }
    try:
        r = requests.post(url=url, data=data)
        response = r.text
    except:
        print "[*] - regression_version search fail.(request error)"
        return False
    if 'Success' in response:
        print "[*] - regression_version search complete."
        return True
    else:
        print "[*] - regression_version search fail.(server error)"
        return False


def fuzz_working_check():
    """
    fuzzer가 동작하고 있는지 확인하는 함수입니다.
    """
    execute_file = os.path.join(base_path, "fuzz", "fuzzer.py")
    output = subprocess.Popen(['pgrep', '-f', execute_file], stdout=subprocess.PIPE).communicate()
    if output[0] != '':
        print "[*] - fuzz process working"
        return True
    else:
        print "[*] - fuzz process not working"
        return False


def register_server(config_info):
    """
    Fuzz_Server_Management_Client 가 관리 웹 서버와 첫 연결을 할 때 등록하는 과정입니다.
    첫 연결한 경우 관리 웹 서버로부터 ID를 할당 받습니다.
    할당받은 ID는 fuzz_config.conf파일에 저장합니다.
    """
    url = "http://%s:%s/manage/register" % (config_info['manageweb_ip'], config_info['manageweb_port'])
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
        server_id = re.findall(r'server_id : (.+)', response)[0]
        set_config_info('SERVER_INFO', 'Server_ID', server_id)
        return True
    else:
        return False


def start_main():
    th = []
    config_info = get_config_info()
    while not config_info['server_id']:
        if register_server(config_info):
            break
        time.sleep(1)
    config_info = get_config_info()  # reload server_id
    time.sleep(1)
    th.append(ConnectPing(config_info).start())
    th.append(CommandListen(config_info).start())
    # fuzz_start()
    for thread in th:
        thread.join()

if __name__ == "__main__":
    start_main()
