Worker: Claude (161cha, Claude Sonnet 5)
Date: 2026-09-25
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (이 스크립트 반영 전 base: 619998bb144c699f379a5c8f6c9a64843d108f28, 156차 이후 처음 코드 변경 -- 161차 candidate3 구현)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 021d1b8608c1c56cd6716bb06a2fe95a44b586a1, 160차 devnotes push 완료 상태)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 재확인 -- 신규 커밋 없음. 140~161차는 재점검 없음)

작업:
1. 세션 시작 4절 0단계로 지침 문서(v2, `021d1b8`) 조회, `git ls-remote`로 carrot-ryu-note HEAD `021d1b8`, carrot-ryu HEAD `619998bb` 확인(괴리 없음).
2. 160차 미완료 1번(후보 3번 좁은 필터 파라미터 확정, 사용자가 "추천값대로" 위임)을 이어서 진행 -- 파라미터 확정, 실제 코드 구현까지 완료.

완료:
1. 160차가 제안한 "곡률 값 자체 슬루 제한" 방식이 실측상 잡음을 오히려 늘린다는 걸 확인(seg8: jumps 13→16, seg31: 7→11)하고, "최종 스칼라 출력값(out_speed)에 직접 슬루 제한" 방식으로 재설계.
2. 재설계안으로 max_delta(1.0/2.0/5.0 km/h) 파라미터 스윕, curv_thresh=0.003 고정 -- seg1/8/11/15/17/23/31 7개 세그먼트에서 jump 감소·트리거 지연 없음 확인, max_delta=1.0 채택(상세는 WIP.md 161차 표 참고).
3. 신규 발견(FINDINGS.md 핵심 발견 59로 별도 등록): 경로 폴리라인이 300m 룩어헤드 안에서 2~3점으로 줄면 곡률이 사실상 0이 되어 route 후보 속도가 무제한(300×배율)으로 튀는 현상. `report()`의 des_jumps_route로 실차 영향(desiredSpeed에 실제로 반영되는지)을 세그먼트별로 확인 -- seg11/17/23은 영향 없음(route_src_cycles=0), seg8/15/31(160차 C-군집)은 실제 영향 있음(des_jumps_route=5/5/3), candidate3의 진짜 대상이 후자임을 재확인.
4. `carrot_man.py`에 candidate3 구현: `carrot_navi_route()` return 직전에 근접-직선(최대 곡률<0.003, 곡률 미산출 포함) 게이트 + 사이클당 ±1.0km/h 슬루 제한 삽입, `self.navi_route_speed_filt` 상태 변수를 `self.navi_points_start_index = 0` 리셋 지점 9곳(`__init__` 포함) 전부에서 함께 리셋. `py_compile` 통과, 동일 로직을 재생 데이터에 적용해 jump 감소 재확인.
5. PARAMS_REGISTRY.md에 candidate3 파라미터(curv_thresh=0.003, navi_route_speed_max_delta=1.0) 신규 등록.

미완료(다음 세션 우선순):
1. 최우선: 이번 세션 반영 스크립트(코드 1건 + devnotes) 사용자 실행 -> push 확인.
2. 경로 소진(폴리라인 부족) 현상(핵심 발견 59)의 수정안은 미착수 -- 이번 로그에서는 실차 영향 없어 우선순위 낮음, 필요시 route가 유일한 낮은 후보가 되는 상황을 더 찾아 재확인.
3. candidate3 실기기 검증 -- 반영 후 강수/야간 등 트리거 빈도가 다른 로그로 재검증 필요.
4. 156차 A안 실기기 검증(강제 종료/전원 차단 재현) -- 155~156차부터 이월.
5. 톨게이트(xTurn=6) 구간 실차 검증(114차부터 이월, 이번 로그도 xTurn=6 전이 0건).
6. (선택) zip 무결성/용량 확인, `build_zip()` 디스크 여유 확인 코드(155차 이월).
7. 148차 v1 `2>&1` 재발의 FINDINGS.md 정식 등록 여부, 147차 임시 스크립트 toolkit 미등록(이전 이월, 변동 없음).

검증:
- 161차 분석·구현은 open-loop 로그 재생(재구현 없이 ast 추출/exec 기반) 및 정적 코드 검증(py_compile)이며 실기기 테스트/실주행이 아니다.
- candidate3 파라미터 결정은 7개 세그먼트(seg1/8/11/15/17/23/31)의 재생 결과에 기반하며, 38세그먼트 전체나 다른 조건(강수/야간 등)에서 재검증되지 않았다.

주의사항:
- 161차는 156차 이후 처음으로 carrot-ryu 코드가 변경된다(candidate3, 1개 파일).
- 코드/devnotes 반영 스크립트는 각각 별도이며 사용자가 직접 실행해야 GitHub에 반영된다(9절/15절/18절).
- FINDINGS.md 핵심 발견 59는 정보 기록용이며, 수정안이 아니다 -- 후속 세션에서 필요성이 재확인되기 전까지 코드 변경 대상 아님.

다음 작업:
1. 사용자가 코드 반영 스크립트(`161cha_code_carrot_ryu-v1.ps1`)와 devnotes 반영 스크립트(`161cha_devnotes_carrot_ryu_note-v1.ps1`) 실행 -> 각각 push 확인.
2. push 확인 후 다음 세션에서 GitHub raw 조회로 실제 반영 내용 재확인(16절).
3. 실기기에서 강제 종료/전원 차단 재현(156차 A안) 또는 톨게이트 통과 로그 확보 시 그쪽도 병행 가능.
