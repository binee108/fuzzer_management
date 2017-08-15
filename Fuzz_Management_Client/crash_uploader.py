# -*- coding: utf-8 -*-
import os
import sys
import requests

import ConfigParser


def get_config_info():
    """
    fuzz_config.conf 파일의 설정값을 가져오는 함수입니다.
    ** fuzz_server_management.py와 중복되므로 별도의 util함수로 빼야함! **
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

    return {
        'server_id': server_id,
        'manageweb_ip': manageweb_ip,
        'manageweb_port': manageweb_port}


def crash_upload(config_info, crash_dump_file_path, crash_input_file_path, crash_hash, reliable):
    """
    fuzzer로부터 받은 crash파일과 testcase파일을 관리 웹서버로 전송하는 함수입니다.
    requests 모듈을 사용하여 파일을 업로드한다.
    """
    if not os.path.exists(crash_dump_file_path):
        print "crash_dump_file_path error"
    if not os.path.exists(crash_input_file_path):
        print "crash_input_file_path error"
    url = "http://%s:%s/manage/crash_upload" % (config_info['manageweb_ip'], config_info['manageweb_port'])

    data = {
        'server_id': config_info['server_id'],
        'crash_hash': crash_hash,
        'reliable': reliable
    }
    multiple_files = [
        ('crash_dump', ('crash_dump.txt', open(crash_dump_file_path, 'rb'), 'text/plain')),
        ('test_case', ('test_case.txt', open(crash_input_file_path, 'rb'), 'text/plain'))
    ]
    try:
        r = requests.post(url=url, data=data, files=multiple_files)
        response = r.text
        print response
    except:
        print "url : " + url
        print "crash_dump_file_path : " + crash_dump_file_path
        print "crash_input_file_path : " + crash_input_file_path
        print "config_info['server_id']: " + config_info['server_id']
        print "crash_upload() request.post Error"


def start_main(crash_dump_file_path, crash_input_file_path):
    config_info = get_config_info()
    crash_upload(config_info, crash_dump_file_path, crash_input_file_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "[*] usage: python crash_uploader.py [crash_dump_file_path] [crash_input_file_path]"
    crash_dump_file_path = sys.argv[1]
    crash_input_file_path = sys.argv[2]
    print "crash_dump_file_path : " + crash_dump_file_path
    print "crash_input_file_path : " + crash_input_file_path
    start_main(crash_dump_file_path, crash_input_file_path)
