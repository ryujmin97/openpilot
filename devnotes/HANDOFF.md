Worker: Claude (144cha, Claude Sonnet 5)
Date: 2026-09-23
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 139차 push 완료 상태 그대로 유지, `8e8b0d1a1569295a69a9817e378eef2ad861d79b` -- 144차도 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 143차 devnotes push 완료 상태, `ffc30f67598dd02487088b0dd72101fcd9de74f7`)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 세션 재확인 -- 신규 커밋 없음. 140~144차는 재점검 없음)

작업:
1. 사용자가 제공한 실주행 rlog 1세그먼트(`00000446--6455a5f5c4--20`, 60.1s)로 114차 HANDOFF.md 미완료 2번(MAP_TURN_GUIDE_FACTOR 검증용 분기/톨게이트 안내 구간 로그 확보)에 착수.
2. `git ls-remote`로 carrot-ryu(`8e8b0d1a`)/carrot-ryu-note(`ffc30f6`) 현재 HEAD를 확인, 지침 문서(v2)/HANDOFF.md/CURRENT_STATUS.md를 SHA 고정 raw로 재조회해 4절 0~1단계 수행.
3. rlog 안 `initData.gitCommit`/`gitBranch`를 pycapnp로 직접 디코딩해 로그가 현재 carrot-ryu HEAD와 같은 코드로 기록됐음을 확인(3절/16절).
4. 그 커밋 기준 `openpilot/cereal/*.capnp` + `opendbc_repo/opendbc/car/car.capnp`를 GitHub에서 새로 sparse-checkout해 스키마 디렉터리 구성, `devnotes/toolkit/route_decel/route_extract.py`(113차 등록 도구 재사용, 신규 toolkit 없음)로 rlog를 20Hz 표로 병합·분석.
5. 분석 결과를 WIP.md 144차 신설(최상단)/CURRENT_STATUS.md 144차 요약 한 줄 삽입(`## 코드 수정 현황` 헤더 직전)/HANDOFF.md(이 파일) 전체 갱신으로 기록.
6. devnotes 반영 스크립트(코드 변경 없어 devnotes 1개만)를 작성해 전달.

완료:
1. 114차 MAP_TURN_GUIDE_FACTOR=1.00의 최초 실차 검증(xTurn=4, 우 분기/차로변경 안내 구간). xDist 486m(진입)부터 -14m(통과)까지 전체 구간에서 vEgo가 87.0->57.9km/h까지 aEgo -0.15~-1.2 m/s² 범위에서만 연속·완만히 감속, 112~114차가 문제삼던 급감속(예: 108차 로그 -4.0 m/s²) 재현 없음을 확인.
2. `longitudinalPlanSource`가 550개 표본 중 529개 `cruise`(리드 게이팅 아님), `radarState.leadOne.dRel` 50~93m(근접 상황 아님)로 이번 감속이 순수 route 커브/분기 로직에 의한 것임을 코드(`carrot_serv.map_turn_speed_factor()`)+로그 대조로 확정(11절).
3. t≈23.1~25.5s 구간이 `selfdriveState.state=overriding`+`gasP=True`(운전자 가속페달 개입)임을 확인해, 이 구간을 시스템 급감속으로 오판하지 않도록 기록(113차계속과 동일 계열 패턴).
4. WIP.md 144차 신설(최상단, LF 유지)/CURRENT_STATUS.md 144차 요약 한 줄 삽입(LF 유지, `## 코드 수정 현황` 헤더 직전)/HANDOFF.md(이 파일) 전체 갱신을 반영 스크립트로 작성.
5. 9절 체크리스트 중 이번 세션에서 실제로 수행한 항목: (1번) `.ps1` 비ASCII 포함 -> UTF-8 BOM 포함 확인. (2번) `git clone`에 `--config core.autocrlf=false` 포함, `devnotes/toolkit/replace_block_template.ps1`의 `Invoke-ReplaceBlock`(CRLF 정규화 내장)/`Invoke-Git`(143차 기준 최신판, `2>&1` 미사용+파라미터 미선언) 그대로 재사용(14절). (3번) `finally` 블록에 임시 폴더 삭제 포함. (5번) HANDOFF.md 전체교체는 `[System.IO.File]::WriteAllText(...,UTF8Encoding($false))`만 사용. (6/7번) WIP.md/CURRENT_STATUS.md 앵커(`"# WIP\n\n## 143차"`, `"코드 변경 없음. 상세: WIP.md 143차 참고.\n\n## 코드 수정 현황"`)를 SHA 고정(`ffc30f67...`) 원본에 Python으로 사전 시뮬레이션해 각각 정확히 1회 매치 + 치환 결과(파일 앞부분 재확인)까지 확인, 그 결과를 스크립트의 `$Old`/`$New` 문자열로 그대로 사용.

미완료(다음 세션 최우선, 기존 이월 항목 포함):
1. 이번(144차) devnotes 반영 스크립트 실행/push 확인(16절).
2. **9절 체크리스트 8/9번(pwsh 파서 구문 검증, 로컬 bare 저장소 일반/Windows CRLF 재현 두 모드 clone-to-push dry-run)은 이번 세션에서 수행하지 못했다** -- 이 세션의 샌드박스에 pwsh가 설치돼 있지 않았고, 143차처럼 GitHub 릴리스 tarball을 받아 설치하는 절차까지는 진행하지 않았다(11절: 수행하지 않은 것을 했다고 보고하지 않음). 대신 (a) 143차가 이미 확정한 "carrot-ryu-note에는 `.gitattributes`가 없어 CRLF 체크아웃 위험이 구조적으로 해당하지 않음"을 근거로 CRLF 모드 dry-run의 필요성 자체가 낮고, (b) `Invoke-ReplaceBlock`/`Invoke-Git`은 133/140~143차에서 이미 여러 번 실제 실행/검증된 재사용 함수이며 이번 스크립트가 새로 작성한 부분은 앵커 문자열 3개뿐이고 그 앵커는 위 완료 5번대로 Python으로 사전 시뮬레이션했다는 점으로 위험을 낮췄으나, 이것이 9절이 요구하는 pwsh 파서/dry-run 자체를 대체하지는 못한다. 다음 세션(또는 이 세션 이어서 pwsh 설치 시도)에서 가능하면 보완.
3. 114차 이월 항목: xTurn=6(톨게이트) 케이스 로그 미확보(이번 로그는 xTurn=4만 포함). 디바이스 `MapTurnSpeedFactor`(base) 실측값 미확인(params_keys.h 기본값 90(=0.90)과 113차가 언급한 실측값 135(=1.35)가 상충) -- 확인되면 `route_extract.py replay`로 이전 배율(1.05)과의 직접 counterfactual 비교 가능.
4. 110차 GATE_M 관련 추가 실차 사례(이번 로그는 근접 리드 상황 자체가 없었음, 142차의 2건에서 추가할 표본 없음).
5. devnotes/toolkit/replace_block_template.ps1의 재사용 헬퍼에 Invoke-Git 패턴 반영 -- 140차부터 이월, 아직 미착수(144차도 착수 안 함, 코드 반영 스크립트가 없는 세션이라 해당 없음).
6. WIP_SYNC.md에 139차 세션의 carrot-ms 점검 결과(신규 커밋 없음)를 새 체크포인트로 기록하는 것은 여전히 이월 가능(선택 사항, 낮은 우선순위).

검증: 144차는 코드 변경 없음. 114차 MAP_TURN_GUIDE_FACTOR=1.00에 대한 실차 검증은 이번 세션에서 처음으로 수행됐다(rlog 안 initData.gitCommit 직접 디코딩 + route_extract.py 표 분석, 12절: 실차 검증 있음으로 표기하되 표본 1건·xTurn=4 한정임을 명시). devnotes 반영 스크립트 자체는 완료 5번에 정리된 항목만 통과했고, 미완료 2번에 명시한 9절 8/9번은 통과하지 못함(수행 자체를 하지 않음).

주의사항:
- carrot-ryu(코드)는 이번 세션 변경 없음.
- 이번 세션에서 만든 로컬 스키마/toolkit 산출물(schema/, out_r.pkl 등)은 Claude 샌드박스 임시 폴더에만 있으며 저장소에 커밋하지 않음(13절). 대용량 rlog.zst/qcamera.ts 자체도 커밋 대상이 아님.
- 이번 devnotes 반영 스크립트는 9절 8/9번을 수행하지 않은 상태로 전달됨 -- 위 미완료 2번 참고. `Invoke-ReplaceBlock`/`Invoke-Git` 재사용 함수 자체는 과거 세션에서 반복 검증됐지만, 이 스크립트 파일 전체를 pwsh 파서로 구문 검증하거나 로컬 bare 저장소에서 실제로 실행해 본 것은 아니다.

다음 작업 후보:
1. 144차 devnotes 반영 스크립트 실행/push 확인.
2. xTurn=6(톨게이트) 안내 구간을 포함하는 로그 확보 시 동일 toolkit(`route_extract.py`)으로 재분석.
3. 디바이스 `MapTurnSpeedFactor` 실제 값 확인 후 `route_extract.py replay`로 1.05 대 1.00 counterfactual 비교.
4. replace_block_template.ps1에 남은 코드 반영 스크립트 이월 항목(위 미완료 5번) 처리.
5. WIP_SYNC.md 139차 체크포인트 기록(선택).
