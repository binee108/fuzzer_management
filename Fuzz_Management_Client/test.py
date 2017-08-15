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

url = "http://10.106.138.179:8000/manage/crash_upload"
data = {
	"server_id": "7",
}
multiple_files = [
	('crash_dump', ('crash_dump.txt', open('crash_uploader.py', 'rb'), 'text/plain')),
	('test_case', ('test_case.txt', open('crash_uploader.py', 'rb'), 'text/plain')),
]
r = requests.post(url=url, data=data, files=multiple_files)
response = r.text
print response
