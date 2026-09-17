Worker: Claude (82차 계속 -- 항목 21(37차 원본) 재적용 v4, push 대기)
Date: 2026-09-18
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `1bd10a7c790aea4a08c605502379a5da88f96aad`, 세션 시작 `git ls-remote`로 재확인 -- v3 실행이 py_compile 단계에서 중단되어 HEAD 변화 없음)
Note Branch: carrot-ryu-note (base: 이 커밋으로 갱신, 직전 base `d2502db0a39ef4ebe5132e7242947b870215a508`, 82차)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스, 변경 없음).

작업:
세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu(`1bd10a7c`)/carrot-ryu-note(`d2502db`)가
사용자가 전달한 82차 HANDOFF.md 기록과 정확히 일치함을 확인(16절, 괴리 없음) -- 즉 v3
스크립트는 실행됐으나 py_compile 검증 단계에서 안전하게 중단되어(15절/18절 안전장치 정상
동작) carrot-ryu에는 아무 변화가 없었다. 사용자가 전달한 v3 실행 로그를 분석해 원인을
확정하고 v4로 수정했다.

완료:
1. 사용자가 업로드한 실제 `82cha_item21_gdrive_folder_lock_v3.ps1` 파일 원문을 직접
   확인(요약/기억에 의존하지 않고 실제 파일 내용으로 diagnosis, 3절 원칙).
2. carrot-ryu(`1bd10a7c`) 현재 베이스의 `gdrive_upload.py`와 carrot-ryu-v1(`9ccf1206`)의
   동일 파일을 raw로 각각 조회해 diff 대조 -- 차이가 37차 수정(import asyncio 추가/
   `_folder_lock` 변수 추가/`_ensure_folder()` 본문을 락으로 감싸기) 하나임을 재확인.
3. v3 스크립트가 실제로 쓰는 anchor 3개 + 치환 로직을 리눅스 샌드박스에서 그대로
   재현: anchor 3개 전부 정확히 1회 매치, 치환 결과가 carrot-ryu-v1의 `gdrive_upload.py`와
   byte-exact 일치, `python3 -m py_compile` 정상 통과(exit 0) 확인 -- v3의 코드/치환
   로직 자체는 문제가 없음을 재확정(11절: 추측이 아니라 재현으로 확인).
4. v3 실행 로그(사용자 제공)를 분석: [1/6]~[4/6]까지 정상 통과([2/6] anchor 3개 전부
   1회 매치, [4/6] 파일 쓰기 성공)했고, [5/6] `python3 -m py_compile` 검증에서만
   아무 진단 출력 없이 `LASTEXITCODE -ne 0`으로 걸려 스크립트 자체의 throw 메시지만
   출력된 채 중단됨을 확인. v3의 `Get-PythonCmd`가 "python3"/"python" 두 이름의 존재
   여부만 `Get-Command`로 확인하고 실제 동작 여부는 검증하지 않는다는 점을 코드로 확인.
5. 원인을 핵심 발견 37(54차)과 동일한 패턴으로 특정: Windows 10/11이 "python3"/
   "python" 이름을 App Execution Alias(Microsoft Store 유도용 스텁)로 PATH에 기본
   등록해두는 경우가 흔해, `Get-Command`로는 "존재"로 잡히지만 실제 실행 시 콘솔
   출력 없이 조용히 비정상 종료(exit code만 비정상)할 수 있음 -- v3에서 관찰된 증상과
   정확히 일치. 54차에서 이미 확정된 해결 순서("py -3" -> "python3" -> "python")를
   v3가 반영하지 않고 있었음.
6. v4 작성: `Get-PythonCmd`를 "py -3" 최우선 순서로 바꾸고, 각 후보를 `Get-Command`
   존재 여부가 아니라 실제 `--version` 실행 결과("Python "으로 시작하는 정상 출력 +
   exit 0)로 검증하도록 강화. py_compile 실행 결과(stdout/stderr)를 성공/실패와
   무관하게 항상 콘솔에 출력하도록 추가(다음에 다른 원인으로 실패해도 바로 보이게).
   anchor 3개/CRLF->LF 정규화(Read-Utf8Lf)/LF 저장/BOM 포함 `.ps1`/`core.autocrlf=false`
   clone/임시폴더 자동삭제 등 나머지는 v3와 완전히 동일(10절 최소 변경 원칙, 이미
   검증된 부분은 건드리지 않음).
7. v4 파일 자체의 BOM 유무와 중괄호/괄호 균형을 바이트/텍스트 레벨로 재확인(9절
   필수 규칙 자가 점검).
8. WIP.md에 "82차 계속" 항목을 최상단(82차 원본 항목 바로 위)에 삽입, 이 파일
   (HANDOFF.md)과 CURRENT_STATUS.md(82차 불릿 + 코드 수정 현황 21번 줄)를 갱신.
9. carrot-ryu용 v4 스크립트와 carrot-ryu-note용 devnotes 스크립트를 present_files로
   전달.

미완료(다음 세션 최우선):
1. 사용자가 두 스크립트(v4 + devnotes)를 실행해 push한 뒤, 그 커밋 출력(특히 [5/6]
   "사용할 Python 후보 확정: ..." 로그와 py_compile OK 여부)을 전달해야 함. 다음
   세션은 `git ls-remote`로 carrot-ryu HEAD가 이 스크립트의 커밋으로 바뀌었는지부터
   먼저 확인할 것(16절).
2. 만약 v4도 동일하게 실패한다면(즉 "py -3"/"python3"/"python" 전부 정상 인터프리터로
   확인되지 않는다면), 사용자 PC에 Python이 실제로 설치돼 있는지, 설치돼 있다면 어떤
   이름/경로로 PATH에 등록돼 있는지 `where.exe python`/`where.exe py` 등으로 직접
   확인이 필요할 수 있음(원인이 App Execution Alias가 아닌 다른 것일 가능성 포함).
3. push 확인되면 Google Drive 파이프라인 이식(항목 5~10·12·17·18·20·21)이 전부
   완료되므로, 바로 이어서 항목 22(39차, `797fca2e`) 본편(화면녹화 탭 사진 업로드 UI
   체크박스/전체선택/다운로드/전송) 착수.
4. (항목 22 끝난 뒤) 항목 23(39cha-fix, screenshots.js formatRelativeEpoch import 누락
   수정), 항목 26(44차, screenshots.js formatLogBytes import 누락 수정) 순서로 재개.
5. (낮은 우선순위) WIP.md 파일 안의 "# WIP" 헤더 중복(다수 등장) 정리 -- 여전히
   미완료.
6. 실기기 검증: 항목 21(Drive 폴더 중복생성 레이스) 자체의 동작 확인 -- 코드가 push된
   다음 항목 5~21 전체 이식이 끝나면 배포/검증 대상(이번 세션 범위 밖).

검증: v4의 anchor/치환 로직(v3와 동일)을 리눅스 샌드버스 실제 재현으로 anchor 3개 전부
1회 매치, 결과가 carrot-ryu-v1의 `gdrive_upload.py`와 byte-exact 일치(diff 0줄),
`python3 -m py_compile` 정상 통과를 재확인. v4 파일 자체는 BOM 포함 여부와 중괄호/괄호
균형을 텍스트 레벨로 점검했으나, PowerShell 파서 자체로 실행 검증은 하지 못함(Windows
PowerShell 실행 환경이 이 세션에 없음) -- 사용자 실행 결과로 최종 확인 필요.
실차 검증: 미실시(항목 5~21 전체가 아직 실기기 미배포, git pull 금지 상태 유지 중).

주의사항:
- v3가 py_compile 단계에서 실패한 것은 15절/18절이 요구하는 안전장치(1회 매치 아니면
  중단, 검증 실패 시 commit/push 안 함)가 정상 동작한 결과이며, carrot-ryu에는 어떤
  영향도 없었다(git ls-remote로 HEAD 불변 재확인).
- 이번 원인(핵심 발견 37과 동일 패턴)은 스크립트마다 개별적으로 `Get-PythonCmd`를
  올바른 순서/검증 방식으로 구현해야 재발하지 않는다는 것을 다시 보여준 사례. 19절
  절차(사용자 승인)로 이 v4의 `Get-PythonCmd` 구현을 지침 문서 9절에 정식 반영할지는
  아직 제안만 된 상태(54차부터 이월, 채택 여부 미확정).

다음 작업 후보:
1. 두 스크립트(v4 + devnotes) 실행/push 확인부터 착수.
2. 완료/push 확인되면 항목 22(39차) 본편 착수.
