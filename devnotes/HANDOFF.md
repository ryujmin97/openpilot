Worker: Claude (163cha, Claude Sonnet 5)
Date: 2026-09-25
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: 1e3bbb5ed019731865dc1ffea35ac13569065625, 162cha candidate3-경로소진수정 반영 확인됨 -- 이번 세션 수정은 아직 미반영, 반영 스크립트 실행/push 대기)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: a920133efa03f373e89df6b71b97a352b224f6b2, 162차 devnotes push 완료 상태)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 재확인 -- 신규 커밋 없음. 140~163차는 재점검 없음)

작업:
1. 세션 시작 중 `git ls-remote`로 carrot-ryu HEAD가 `1e3bbb5e`(162cha)로 이미 push 완료돼 있음을 확인.
2. 사용자가 업로드한 실주행 rlog 10세그먼트(`0000044d--e8bd778f2d--16~25`, 2026-09-25)로 "안내지점 라우트가 여전히 이상하다 -- 안내지점 정보 의존 없이 일반 곡선과 동일하게 적용해달라"는 요청을 조사. 로그의 `initData.gitCommit`이 `1e3bbb5e`(현재 HEAD)와 일치함을 확인.
3. cereal/car.capnp 스키마를 로그 기록 커밋 기준으로 sparse-checkout, carrotMan 필드(desiredSpeed/desiredSource/xTurnInfo/xDistToTurn/szPosRoadName)를 20Hz 12,000표본 추출/분석.
4. 근본 원인 확정: `turnSpeedControlMode==2`의 route 게이트(`0<=xDistToTurn<=300m`)가 안내 지점이 300m보다 먼 구간(전체의 28.1%)에서 route 후보 자체를 배제, 그중 76.0%는 desiredSpeed가 route보다 최대 140km/h 높은 다른 소스로 결정됨을 확인.
5. `carrot_serv.py` 수정: `map_turn_speed_factor()`/관련 상수 4개 삭제, route 배율은 항상 `mapTurnSpeedFactor` 고정값 사용, `turnSpeedControlMode==2`의 거리 게이트 삭제(2/3/4 모드 전부 항상 route 후보 포함으로 통합). 대상 함수가 사라져 `test_map_turn_guide_factor.py` 삭제.
6. 로그 재생으로 수정 효과 검증(46.4% 표본에서 desiredSpeed 하향 조정, 근접구간 변화 478건은 전부 gas-override로 무관함 확인) + `py_compile` + 로컬 bare 저장소(carrot-ryu HEAD `1e3bbb5e` 미러링) 대상 일반/Windows CRLF 재현 두 모드 dry-run(동일 diff +14/-105, 동일 post-image blob hash `641afb20e4`) 통과.
7. dry-run 중 `Get-PythonCmd` 반환값 스칼라 자동축약 버그(153차 핵심 발견과 동일 계열) 신규 발견/수정(`@(Get-PythonCmd)` 래핑).

완료:
1. 핵심 발견 62 신규 등록(원인/실증/수정/검증, FINDINGS.md).
2. WIP.md 163차 항목 작성.
3. 코드 반영 스크립트(`163cha_code_carrot_ryu.ps1`) 작성 및 9절 자가검증 체크리스트(BOM 없음/`core.autocrlf=false`/임시폴더 자동삭제/`Get-PythonCmd`+EOF공급(+스칼라축약 버그 수정)/전체재작성 WriteAllBytes 무BOM/pre-post blob hash guard/pwsh 파서 구문 오류 0건/로컬 bare 저장소 일반+Windows CRLF 재현 두 모드 byte-exact 일치) 통과 완료.

미완료(다음 세션 우선순):
1. 최우선: 사용자가 `163cha_code_carrot_ryu.ps1` 실행 -> push 확인(carrot-ryu HEAD가 `1e3bbb5e`에서 갱신되는지 GitHub API로 재확인).
2. 이 devnotes 반영 스크립트(`163cha_devnotes_carrot_ryu_note.ps1`) 자체도 실행 -> push 확인.
3. 이번 수정으로 route 후보가 실제로 desiredSpeed를 낮추는 빈도/크기가 "일반 곡선 감속으로서" 체감상 적절한지(`MapTurnSpeedFactor`=90 자체의 절댓값 튜닝 필요 여부) 실주행 로그로 재검증.
4. 안내지점(xTurnInfo/xDistToTurn) 통과 직후(xDist<0) 구간의 route 동작도 이번 수정 범위에서 함께 확인(회귀 여부).
5. (161차 원안 이월) candidate3 + 162차 경로 소진 수정 실기기 검증.
6. 156차 A안 실기기 검증(잔존 zip 정리 로직), 톨게이트(xTurn=6) 구간 실차 검증 -- 이월 그대로.
7. (선택) zip 무결성/용량 확인, `build_zip()` 디스크 여유 확인 코드(155차 이월).
8. 148차 v1 `2>&1` 재발의 FINDINGS.md 정식 등록 여부, 147차 임시 스크립트 toolkit 미등록(이전 이월, 변동 없음).

검증:
- 실주행 rlog 10세그먼트(로그 기록 커밋이 현재 HEAD와 일치, 12,000 carrotMan 표본)로 근본 원인(모드 2 route 게이트가 안내 지점 300m 밖 구간에서 route 후보를 통째로 배제)을 정량 실증했다(28.1%가 이 상태, 그중 76.0%는 route가 desiredSpeed보다 낮은데도 배제, 최대 격차 140km/h).
- 수정 후 재생: 전체 표본의 46.4%(5,565건)에서 desiredSpeed가 낮아짐(수정 전 과속 방치였던 구간), 근접구간(0~300m, 기존에도 route 포함)에서의 변화 478건은 전부 `desiredSource=gas`(운전자 가속페달 개입) 등 이 수정과 무관한 원인임을 확인해 회귀 없음을 확인.
- `py_compile` 통과, 삭제 대상 이름(`MAP_TURN_GUIDE_*`/`map_turn_speed_factor`) 잔여 참조 0건(주석 1곳만 서술적 언급).
- 로컬 bare 저장소(carrot-ryu 실제 HEAD `1e3bbb5e` 트리 미러링) 대상 clone->pre-hash guard->전체교체(base64)->py_compile->post-hash guard->commit->push 전 과정을 두 모드(정상 LF / Windows CRLF 체크아웃 시뮬레이션)로 dry-run, 두 모드 모두 동일한 diff(2 files changed, +14/-105, 테스트 파일 삭제 포함)와 동일한 post-image blob hash(`641afb20e45f6c565f431c613fefb3ff263964f0`)를 만들었다.
- 다만 이는 리눅스 컨테이너의 시뮬레이션이며 실제 사용자 Windows PowerShell 5.1 실행 자체를 대체하지 않는다(핵심 발견 52/55가 이미 지적한 한계와 동일).

주의사항:
- carrot-ryu는 `1e3bbb5e`(162차 경로 소진 수정 완료) -- 이번 세션 수정은 아직 그 위에 반영되지 않은 상태다.
- 이번 코드 반영 스크립트는 `carrot_serv.py`를 base64로 전체교체하고 `test_map_turn_guide_factor.py`를 삭제하는 방식이라, 대상 파일들에 이 스크립트 작성 이후 다른 변경이 먼저 push되면(예: 사용자가 다른 세션/AI로 같은 파일을 건드리면) pre-image blob hash guard가 걸려 안전 중단된다 -- 정상 동작이므로 강제로 우회하지 말 것.
- `MapTurnSpeedFactor`(Params, 기본값 90) 자체의 절댓값은 이번 세션에서 건드리지 않았다. 이번 수정은 "안내 지점 정보에 대한 의존을 제거"하는 것이었지 배율 값 조정이 아니다.

다음 작업:
1. 사용자가 코드 반영 스크립트(`163cha_code_carrot_ryu.ps1`)와 devnotes 반영 스크립트(`163cha_devnotes_carrot_ryu_note.ps1`) 실행 -> 각각 push 확인.
2. push 확인 후 다음 세션에서 GitHub raw 조회로 실제 반영 내용 재확인(16절), 이어서 미완료 3·4번(route 감속 체감/통과 직후 구간) 착수.
