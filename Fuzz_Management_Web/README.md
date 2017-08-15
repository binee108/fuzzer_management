# Fuzz_Management_Web
Fuzz_Management_Web은 Fuzz를 수행하는 여러 분산 서버를 통합하여 관리하는 web서비스입니다.


## django 설치 방법
```
sudo apt-get upate
sudo apt-get install python-pip
sudo pip install --upgrade pip
sudo pip install django==1.11
```

## Web 서버 초기 실행 방법
```
python Fuzz_Management_Web/FuzzManagement/manage.py migrate
python Fuzz_Management_Web/FuzzManagement/manage.py makemigrate management
python Fuzz_Management_Web/FuzzManagement/manage.py migrate
```
처음 서버를 실행 시킬 시 DB파일 생성해야합니다.
```
python Fuzz_Management_Web/FuzzManagement/manage.py runserver 0.0.0.0:8000
```

## 시나리오
Web 서버를 실행한다.
Fuzz_Management_Client에서
fuzz_server_management.py를 실행하여 서버와 연결한다.
첫 서버와 연결 시 Client는 server ID를 할당 받는다.

fuzzer/add에서 fuzzer 엔진을 추가한다.(build_script가 핵심이고 그 외 타겟 정보)
아직 fuzzer를 자동으로 빌드하는 스크립트를 만들지 않았으므로, 빌드 파일은 아무거 파일을 올린다. 또한 빌드를 직접해 줘야한다.
Fuzz_Management_Client/fuzz 경로에 직접 빌드를 한다.
fuzzer/README.md의 v8빌드 과정 참고!

빌드가 완료된 서버를 start버튼으로 fuzzing을 시작한다.
fuzzer에서 발생한 crash 정보는 crash/list에서 확인 할 수 있다.

server/list에서 연결된 서버를 확인하고 수정 기능을 통해서 fuzz엔진과 서버명을 설정한다.
server/list에서 build를하고(미구현이므로 직접 빌드) start 버튼을 클릭하여 fuzzing을 시작한다.
crash는 crash/list에서 확인할 수 있다.
stop 버튼을 클릭하면 fuzzing이 멈춘다.

## 페이지 url구성
manage/ - Client와 통신할 때 사용 되는 URL입니다.(일반 웹 사용자는 사용안함.)
manage/register - Client와 첫 통신 시 server ID를 할당하는 페이지
manage/connect - Client의 연결 상태를 전달하는 페이지
manage/crash_upload - Crash 정보를 업로드하는 페이지
manage/command_polling - fuzz server에 요청하는 명령어를 폴링으로 전달하는 페이지

fuzzer/ - fuzzer 엔진과 관련된 정보를 다루는 URL입니다.
fuzzer/list - fuzzer의 엔진 리스트
fuzzer/view/num - fuzzer의 엔진 view 화면
fuzzer/add - fuzzer 엔진 추가
fuzzer/modify/num - fuzzer 엔진 수정

server/ - fuzzer server와 관련된 정보를 다루는 URL입니다.
server/list - 서버 리스트
server/modify/num - 서버 정보를 변경한다.
manage/request_command - 서버에 명려어를 요청하는 페이지(처리 페이지 떄문에 사용자 view가 없음.)

crash/ - Crash와 관련된 저보를 다루는 URL입니다.
crash/list - crash 리스트



## 앞으로 추가 될 기능
regresssion기능 추가(crash_list 에서 요청 가능하도록 버튼 추가)
crash/list 에서 Common Issue로 forward하는 기능

Common Issue 페이지 - 내부 이슈와 외부 이슈를 통합 관리하는 페이지입니다.
내부 이슈는 crash list에서 forward하거나 직접 작성 할 수 있고,
외뷰 이슈 또한 직접 작성하여 관리 할 수 있게 만들 예정입니다.
이슈에 등록된 PoC파일로 regression 버전 찾기 버튼도 추가할 예정입니다.

server_fuzzer 서버 로그 관리 기능.
fuzz 서버에서 발생하는 로그를 확인 할 수 있는 페이지.(다량의 로그로 용량 이슈가 발생 할 수 있음. 보류)

dash board 페이지 - dash 보드를 통해서 통계자료 확인 할 수 있음.
 
mail 알림기능 - crash가 발생하였을 때 관리자 메일로 알림을 보내는 기능.

