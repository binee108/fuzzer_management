# -*- coding: utf-8 -*-
import os,sys
import urllib2
import threading
import time
import subprocess
import re
import requests

import ConfigParser

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

    return {'fuzz_name':fuzz_name, 'fuzz_target':fuzz_target, 'fuzz_version':fuzz_version, 'server_ip':server_ip,'server_port':server_port}

def crash_upload(config_info, crash_dump_file_path, crash_input_file_path):
    url = "http://%s:%s/management/crash_upload"%(config_info['server_ip'], config_info['server_port'])
    try :
        with open(crash_dump_file_path,'rb') as f:
            crash_dump_data = f.read()
    except :
        print "crash_dump_file_path open failed"
    try :
        with open(crash_input_file_path,'rb') as f:
            crash_input_data = f.read()
    except :
        print "crash_input_file_path open failed"

    data = {
    'fuzz_name':config_info['fuzz_name'],
    'crash_dump':crash_dump_data,
    'input_data':crash_input_data,
    }
    try : 
        r = requests.post(url = url, data = data)
        response = r.text
        print response
    except :
        print "crash_upload() request.post Error"
    print "url : %s"%url
    print "config_info['fuzz_name'] : %s"%config_info['fuzz_name']
    print "crash_dump size : %d"%len(data['crash_dump'])
    print "input_data size : %d"%len(data['input_data'])    
    

def start_main(crash_dump_file_path, crash_input_file_path):
    config_info = get_config_info()
    crash_upload(config_info, crash_dump_file_path, crash_input_file_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "[*] usage : python crash_uploader.py [crash_dump_file_path] [crash_input_file_path]"
    crash_dump_file_path = sys.argv[1]
    crash_input_file_path = sys.argv[2]
    start_main(crash_dump_file_path, crash_input_file_path)