jsfunfuzz를 커스텀마이징한 fuzz입니다.

## v8 빌드
Fuzz_Management_Client/fuzz 경로 안에 fuzzer폴더 내부에 있는 파일을 넣어줍니다.
fuzz경로에 v8을 빌드합니다.
```
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH=`pwd`/depot_tools:"$PATH"
fetch v8
cd v8
git checkout 5.9-lkgr
gclient sync
tools/dev/v8gen.py x64.release
ninja -C out.gn/x64.release
cd ../
cp -a v8 v8_exec

```

## 퍼저만 실행하는 방법

```
python fuzzer.py
```

## Fuzz_Management_Client를 통하여 실행하는 방법
```
cd [Fuzz_Management_Client폴더경로]
python fuzz_server_management.py
```

## 코드 별 기능 설명
- fuzzer.py는 fuzzer를 시작하는 코드입니다.

- util/CrashInfo.py는 fuzzer에서 crash가 발생하면 crash dump text를 생성하고 crash의 reliable을 체크합니다.

- util/fileManipulation.py fuzzer를 실행한 testcase를 생성하는 기능을 수행합니다. fuzzer 수행시 jsfunfuzz.js를 실행하여 생성된 stdout으로 출력된 내용에서 실제로 javascript로 실행된 코드를 복구합니다.

- util/gdb-quick.txt는 CrashInfo.py에서 crash dump를 할 때 사용되는 gdb 명령어 스크립트입니다.

- util/setting_parser.py는 setting.conf파일의 옵션을 값을 가져오는 기능을 합니다.

- util/commit_searcher.py는 regression한 버전을 찾는 기능을 합니다.
crash가 발생한 crash_lkgr버전을 입력하면 해당 버전으로부터 crash가 발생하는 버전을 찾아줍니다.


## regression search 실행 방법
```
python commit_searcher.py <testcase_path> <crash_lkgr_version>
```

