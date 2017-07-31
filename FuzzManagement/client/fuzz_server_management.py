# -*- coding: utf-8 -*-
import os
import urllib2
import threading
import time
import subprocess
import ConfigParser
import re
import requests

base_path = os.path.dirname(os.path.realpath(__file__))

class ConnectPing:
    def __init__(self, config_info):
        self.config_info = config_info
    def get_ip_address(self):
        output = subprocess.Popen(['ifconfig',],stdout=subprocess.PIPE).communicate()
        result = re.findall(r'inet addr:(\S+)', output[0])
        if len(result) > 0 :
            for i in result:
                if not "127.0.0.1" in i :
                    return i
            print "Need to check network."
        else :
            print "Error ifconfig command failed."
        return None

    def connect_ping(self):
        local_ip = self.get_ip_address()
        self.url = "http://%s:%s/management/connect"%(self.config_info['server_ip'], self.config_info['server_port'])
        self.data = {
        'fuzz_name':self.config_info['fuzz_name'],
        'fuzz_ip': local_ip,
        'fuzz_target':self.config_info['fuzz_target'],
        'fuzz_version':self.config_info['fuzz_version'],
        }
        while(1):
            print "[*] - Send Ping"
            self.data['working_status'] = fuzz_working_check()
            try : 
                r = requests.post(url = self.url, data = self.data)
                response = r.text
            except:
                print "[*] - Check Web server running"
            time.sleep(60)
            

    def start(self):
        th = threading.Thread(target = self.connect_ping)
        th.start()
        return th

def get_config_info():
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'fuzz_config.conf')
    if os.path.exists(config_path) :
        config = ConfigParser.ConfigParser()
        config.read(config_path)
    ##### fuzz_config.conf #####
    # [FUZZER_INFO]
    # Fuzz_Name = whale_fuzz_1
    # Fuzz_Target = whale
    # Fuzz_Version = 5.9

    # [SERVER_INFO]
    # Server_IP=10.10.10.10
        fuzz_name = config.get('FUZZER_INFO','Fuzz_Name')
        fuzz_target = config.get('FUZZER_INFO','Fuzz_Target')
        fuzz_version = config.get('FUZZER_INFO','Fuzz_Version')
        server_ip = config.get('SERVER_INFO','Server_IP')
        server_port = config.get('SERVER_INFO','Server_PORT')
    else : 
        print "The fuzz_config.conf file does not exist."

    return {'fuzz_name':fuzz_name, 'fuzz_target':fuzz_target, 'fuzz_version':fuzz_version, 'server_ip':server_ip, 'server_port':server_port}

def command_listen():
    pass
    ####### long polling or socket방식으로 구현 #######

def fuzz_build():
    output = subprocess.Popen(['./setup.sh',],stdout=subprocess.PIPE)
def fuzz_start():
    if not fuzz_working_check():
        execute_file = os.path.join(base_path, "fuzz","fuzzer.py")
        print "[*] - fuzz start "
        os.system(execute_file)
    else : 
        print "[*] - already execute fuzzer!"

def fuzz_stop():
    output = subprocess.Popen(['pgrep','-f','fuzz/fuzzer.py'],stdout=subprocess.PIPE).communicate()
    if (len(output[0])!=0):
        os.system('kill -9 %s'%output[0])

def fuzz_reboot():
    output = subprocess.Popen(['pgrep','-f','fuzz/fuzzer.py'],stdout=subprocess.PIPE).communicate()
    if (len(output[0])!=0):
        os.system('kill -9 %s'%output[0])
    os.system('reboot')

def fuzz_working_check():
    execute_file = os.path.join(base_path, "fuzz","fuzzer.py")
    output = subprocess.Popen(['pgrep','-f',execute_file],stdout=subprocess.PIPE).communicate()
    if output[0] != '' :
        print "[*] - fuzz process working"
        return True
    else :
        print "[*] - fuzz process not working"
        return False

def start_main():
    config_info = get_config_info()
    th = ConnectPing(config_info).start()
    fuzz_start()
    time.sleep(1)
    th.join()

if __name__ == "__main__":
    start_main()