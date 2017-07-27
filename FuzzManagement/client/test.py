import requests


# test connect_ping script
# url = "http://127.0.0.1:8000/management/upload"
# data = {
# 'fuzz_name':"test1",
# 'fuzz_ip':"20.20.20.20",
# 'fuzz_target':"test_target",
# 'fuzz_version':"1.0ver"
# # 'working_status':
# # 'build_state':
# }
# data['working_status'] = True
# r = requests.post(url = url, data = data)
# response = r.text
# print response


    # fuzz_server = models.ForeignKey(Fuzz_server)
    # crash_hash = models.CharField(max_length=128)
    # crash_dump = models.CharField(max_length=128)
    # input_data = models.CharField(max_length=128)
    # report_time = models.DateTimeField(auto_now_add=True)

url = "http://127.0.0.1:8000/management/crash_upload"
data = {
'fuzz_name':"test1",
'crash_hash':"test value",
'crash_dump':"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
'input_data':"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
}
r = requests.post(url = url, data = data)
response = r.text
print response