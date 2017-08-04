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

url = "http://127.0.0.1:8000/test_upload"
data = {
	"test_name": "hello test name",
	"fuzz_name": "fuzz1"
}
multiple_files = [
	('test_file_1', ('foo.txt', open('crash_uploader.py', 'rb'), 'text/plain'))
]
r = requests.post(url=url, data=data, files=multiple_files)
response = r.text
print response
