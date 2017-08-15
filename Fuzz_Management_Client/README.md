fuzzer_management 웹 서비스와 연결하여 호스트에서 관리하는 fuzz를 관리하고 관리 웹서비스에 정보를 전송하는 기능을 수행합니다.

## Setup

### (1) 설치 및 의존 모듈 설치
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-pip
sudo pip install --upgrade pip
sudo pip install requests
git clone ~~~~~~

cd Fuzz_Management
vi fuzz_config.conf
```

### (2) 설정
fuzz_config.conf 파일에서

```
[SERVER_INFO]
Server_ID=

[MANAGEWEB_INFO]
ManageWeb_IP=<관리 웹서버 IP>     (ex: ManageWeb_IP=10.211.55.7)
ManageWeb_PORT=<관리 웹서버 PORT> (ex: ManageWeb_PORT=8000) 
```
위와 같이 설정을 해줍니다.
Server_ID는 관리 웹서버에 연결하면 웹서버로부터 ID를 할당 받아서 자동으로 입력하므로 따로 설정 할 필요는 없습니다.

### (3) fuzzer 빌드
Fuzz_Management/fuzz 경로 안에 사용자가 커스텀한 fuzz를 넣어주면 됩니다.

fuzzer는 기본적으로 Fuzz_Management/fuzz/fuzzer.py 경로로 실행하도록 만들어줘야된다.
또한 퍼저에서 발생한 크래쉬는 
```
Fuzz_Management/crash_uploader.py <crashdump_path> <testcase_path>
```
위 경로 파일을 python으로 실행하여 인자를 전달하도록 만들어줘야한다.

regressions 탐색 기능은 
```
Fuzz_Management/fuzz/regressions_search.py <testcase_path>
```
위와 같은 경로에서 실행 될 수 있도록 만들고 regression 버전을 출력해야한다.
퍼저 내부에 실행하도록 설정하지 않았다.
이유는 exploitable한 정보라면 searching할 가치가 있지만 exploitable하지 않으면 
10시간을 서칭하는데 소비해야하는 문제가 발생한다.
따라서 crash list에서 crash덤프 정보를 확인하고 담당자가 searching을 요청 할 수 있게 구현했다.


## 연관 관계
management web server <-> fuzz_server_management <-> [Custom Fuzzer]

위와 같이 관리 웹서비스와 fuzzer의 중간 위치에서 중개하는 역할을 합니다.

# 코드 별 기능 설명
- crash_uploader.py는 fuzzer에서 발생한 crash 정보를 관리 웹 서비스에 전송하는 기능입니다.

- fuzz_server_management.py는 관리 웹서비스와 통신하면서 fuzzer를 build하거나 시작, 중지, 리부팅 등 관리 웹서비스로부터 명령을 받아서 기능을 수행하는 역할을 합니다.

- fuzz_config.conf는 통신하는 관리 웹서비스에 대한 정보 및 웹서비스로 부터 할당받은 ID값을 저장하는 설정파일입니다.


## 필요한 기능
(1) ASan로 빌드하여 corruption type과 exploitable을 확인해야한다.
(2) 중복 크래쉬를 묶어줘야한다.
(3) 테스트케이스 파일을 최적화 해야한다.

