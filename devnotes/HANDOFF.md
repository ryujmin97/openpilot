Worker: Claude (142cha, Claude Sonnet 5)
Date: 2026-09-23
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 139차 push 완료 상태 그대로 유지, `8e8b0d1a1569295a69a9817e378eef2ad861d79b` -- 142차도 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 141차 devnotes push 완료 상태, `9b1877fb256806e67720a973227bd1f50996fb0d`)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 세션 재확인 -- 신규 커밋 없음. 142차는 재점검 없음)

작업:
1. 사용자가 실주행 rlog 2세그먼트(00000443--c7549a52f2--5/--6, 2026-09-23) 제공, 110차 GATE_M 0.8/1.0과 114차 MAP_TURN_GUIDE_FACTOR=1.00의 실차 검증 요청.
2. rlog 안에서 git commit(`8e8b0d1a1...`)을 직접 확인해 로그가 139/141차 HEAD와 동일한 코드에서 기록됐음을 실증.
3. 그 커밋 기준으로 cereal/car.capnp 스키마를 sparse-checkout으로 새로 구성, devnotes/toolkit의 ego_extract.py/ego_episodes.py/route_extract.py로 로그 파싱·분석.
4. 자차 실제 급감속 에피소드 2건을 추출해 GATE_M 게이트 동작(margin_ratio/TTC 하이브리드)이 long_mpc.py 코드 공식과 부합하는지 대조.
5. carrotMan.xTurnInfo 전체를 확인해 114차 항목의 검증 가능 여부 판단.

완료:
1. 110차 GATE_M 0.8/1.0: 실차 로그 기반 최초 검증 완료(2개 급감속 에피소드 모두 설계 의도대로 동작, 과민 개방 사례 없음).
2. 114차 MAP_TURN_GUIDE_FACTOR=1.00: 이번 로그에는 분기/톨게이트 안내 이벤트(xTurn=3/4/6)가 전혀 없어 검증 불가임을 확정(다음 로그 필요).
3. WIP.md 142차 신설(최상단), HANDOFF.md(이 파일) 전체 갱신.
4. 이 devnotes 반영 스크립트를 사용자가 실제 Windows PowerShell 5.1에서 처음 실행(v1)했을 때, `git add -A` 파라미터 충돌 버그를 고치는 과정에서 139/140차 핵심 발견 53의 근본 수정(stderr 스트림 비병합)을 실수로 되돌려(`Invoke-Git` 안에 `2>&1`을 다시 넣음) `git clone` 단계에서 동일한 `NativeCommandError`로 즉시 중단되는 회귀가 실제로 재발했다. 사용자 실행 로그로 확인 후 즉시 `2>&1` 제거(v2)로 수정, 로컬 bare 저장소 dry-run(일반/Windows CRLF 두 모드)으로 재검증. 이 회귀는 리눅스 컨테이너의 pwsh 기반 dry-run으로는 애초에 재현되지 않는 종류(핵심 발견 53 자체가 이미 명시한 한계)이며, 실제 Windows PowerShell 5.1 실행에서만 드러났다.

미완료(다음 세션 최우선, 기존 이월 항목 포함):
1. 이번(142차) devnotes 반영 스크립트 실행/push 확인(16절).
2. 114차 MAP_TURN_GUIDE_FACTOR 검증용 로그 확보(분기/톨게이트 안내 구간 포함) -- 사용자가 해당 구간 통과 시 로그 제공 필요.
3. devnotes/toolkit/replace_block_template.ps1의 재사용 헬퍼에 Invoke-Git 패턴 반영 -- 140차부터 이월, 아직 미착수. 반영 시 아래 `-A` 충돌 버그의 수정판(파라미터 미선언 + 자동 `$args` 사용)을 그대로 채택할 것.
4. FINDINGS.md에 `Invoke-Git`의 `-A`(및 `-Args`와 접두어가 겹치는 다른 단일 옵션 전반) 충돌 버그를 핵심 발견으로 정식 등록 -- 이번 세션에서는 이 스크립트 자체의 수정으로만 반영했고, FINDINGS.md 별도 등록은 아직 하지 않음(신규 이월).
5. WIP_SYNC.md에 139차 세션의 carrot-ms 점검 결과(신규 커밋 없음)를 새 체크포인트로 기록하는 것은 여전히 이월 가능(선택 사항, 낮은 우선순위).

검증: 142차는 코드 변경 없음. GATE_M 항목은 실제 rlog 데이터 분석 + 코드(long_mpc.py) 직접 대조로 검증(11절, 12절 -- 정적 시뮬레이션이 아니라 실차 기록 로그 분석). devnotes 반영 스크립트는 9절 체크리스트 전항목 수행: `.ps1` 자체 BOM 포함 확인, WIP.md/CURRENT_STATUS.md anchor를 SHA 고정 원본에 사전 시뮬레이션(각 1회 매치) + 쓰기 후 재확인, HANDOFF.md 전체 재작성 후 BOM 없음 확인, pwsh 7.6.6 파서 구문 오류 0건, 로컬 bare 저장소 일반/Windows CRLF 재현 두 모드 모두 실행해 commit diff(2/0, 48대체, 10/0 -- 3 files, +35/-25)와 최종 파일 CRLF 잔존 0건까지 byte 단위로 일치 확인(코드 파일이 아니므로 py_compile 대상 없음). 이 dry-run 과정에서 `Invoke-Git -C $Tmp add -A` 호출이 실패하는 버그를 실제로 재현했고(아래 참고), 수정 후 두 모드 모두 재실행해 정상 완료까지 확인했다. 실차 검증: 있음(GATE_M 항목, 위 완료 1번 참고).

주의사항:
- 이번 세션 분석에 사용한 스키마/toolkit 실행 결과(피클/중간 산출물)는 Claude 샌드박스 임시 폴더에만 있으며 저장소에 커밋하지 않음(13절 -- 대용량 로그/산출물 미커밋 원칙). 업로드된 원본 rlog/qcamera 자체도 커밋 대상 아님.
- carrot-ryu(코드)는 이번 세션 변경 없음.
- **신규 버그 2건(142차 발견, FINDINGS.md 미등록)**:
  1. `Invoke-Git`(140차 도입) 헬퍼가 `param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)`로 파라미터명을 `Args`로 선언하고 있었는데, PowerShell의 이름 접두어 자동매칭 때문에 뒤이어 넘어오는 토큰이 정확히 `-A`(예: `git add -A`)일 경우 이를 `-Args`의 유일한 접두어 후보로 오인해 값 누락 오류(`Missing an argument for parameter 'Args'`)로 즉시 실패한다. 140/141차 devnotes 스크립트는 `git add -A`를 이 헬퍼로 호출한 적이 없어 지금까지 드러나지 않았고, 이번 142차가 처음으로 이 조합을 실행해 로컬 bare 저장소 dry-run(9절 체크리스트 9번)에서 실증됐다. 수정: `param()` 자체를 선언하지 않고 함수 안에서 PowerShell 자동 변수 `$args`만 참조하도록 변경 -- 파라미터를 선언하지 않으면 이름 매칭이 아예 일어나지 않아 어떤 단일 옵션(`-A`뿐 아니라 향후 `-a`/`-al` 등)과도 충돌하지 않는다.
  2. 위 1번을 고치는 과정에서 `$out = & git @args 2>&1`처럼 `2>&1`을 실수로 다시 넣었고, 이 v1이 사용자에게 전달돼 실제 Windows PowerShell 5.1에서 실행됐다. 139/140차 핵심 발견 53이 이미 확정한 바로 그 패턴(stderr 병합 -> `NativeCommandError` -> `$ErrorActionPreference="Stop"`으로 즉시 중단)이 그대로 재발해, `git clone`의 정상 진행 메시지("Cloning into ...")만으로 스크립트가 중단됐다(사용자 실행 로그로 확인). 리눅스 컨테이너의 pwsh 기반 로컬 dry-run 두 모드 모두 이 회귀를 잡아내지 못했다 -- 핵심 발견 53 자체가 이미 "컨테이너 환경(pwsh)과 Windows PowerShell 5.1 사이에 native stderr 처리 차이가 있어 컨테이너 dry-run만으로는 이 문제를 재현할 수 없다"고 명시해둔 한계 그대로다. 수정(v2): stderr를 전혀 병합하지 않고(`& git @args`, 리다이렉션 없음) `$LASTEXITCODE`만으로 판단하도록 되돌림.
  두 수정 모두 이 스크립트(v2)에 이미 반영돼 있다. `replace_block_template.ps1`에 `Invoke-Git`을 정식 등록할 때(9절 체크리스트 미완료 3번)와 FINDINGS.md 정식 등록 시(미완료 4번) 이 v2 버전(파라미터 미선언 + stderr 비병합)을 그대로 가져갈 것 -- 두 수정 중 하나만 반영하면 다른 쪽이 재발한다.

다음 작업 후보:
1. 142차 devnotes 반영 스크립트 실행/push 확인.
2. 114차 검증용 분기/톨게이트 로그 확보 시 동일 toolkit으로 재분석.
3. replace_block_template.ps1에 Invoke-Git 패턴(142차 `-A` 충돌 수정판) 반영.
4. FINDINGS.md에 Invoke-Git `-A` 충돌 버그를 핵심 발견으로 정식 등록.
5. WIP_SYNC.md 139차(carrot-ms 신규 커밋 없음) 체크포인트 기록(선택).