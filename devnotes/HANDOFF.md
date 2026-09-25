Worker: Claude (164cha, Claude Sonnet 5)
Date: 2026-09-25
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: 8775ea0d300a240c48bad34488aeccb9490ed711, 163차 route 게이트 제거 push 확인됨 -- GitHub raw 조회로 carrot_serv.py 실제 내용(MAP_TURN_GUIDE_* 삭제/test 파일 삭제)까지 재확인함, 16절)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 566d10bf8d7c06b73e1ea71585e643ed6b123867, 163차 devnotes push 확인됨)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 재확인 -- 신규 커밋 없음. 140~164차는 재점검 없음)

작업:
1. 세션 시작 시 `git ls-remote`로 carrot-ryu HEAD가 `8775ea0d`(163차 코드), carrot-ryu-note HEAD가 `566d10b`(163차 devnotes)로 이미 push 완료돼 있음을 확인. `carrot_serv.py` raw 조회로 실제 코드 반영 내용까지 재확인(16절).
2. 사용자가 163차와 동일한 실주행 rlog 10세그먼트(`0000044d--e8bd778f2d--16~25`)를 재업로드, "1·2번(route 감속 체감/통과직후 회귀) 지금 있는 로그로 바로 분석" 요청.
3. rlog 안 `initData.gitCommit`이 `1e3bbb5e`(163차 수정 이전 HEAD)와 일치함을 확인(163차와 동일한 기존 로그).
4. `devnotes/toolkit/route_decel/route_extract.py`(113차, 재사용) + 로그 기록 커밋 스키마로 12,000표본(20Hz) 재추출, 게이트 기준(근접/원거리/통과직후/기타)으로 분류·분석.

완료:
1. 핵심 발견 63 신규 등록(FINDINGS.md).
2. WIP.md 164차 항목 작성.
3. 163차 한계 이월 2건 모두 결론: (1) MapTurnSpeedFactor 절댓값 조정 근거 없음(이번 로그 기준), (2) 통과직후(xDist<0) 구간도 163차 수정 범위 안에서 이미 해결, 회귀 없음.

미완료(다음 세션 우선순):
1. (161차 원안 이월) candidate3 + 162차 경로 소진 수정 실기기 검증.
2. 156차 A안 실기기 검증(잔존 zip 정리 로직), 톨게이트(xTurn=6) 구간 실차 검증 -- 이월 그대로.
3. (선택) zip 무결성/용량 확인, `build_zip()` 디스크 여유 확인 코드(155차 이월).
4. 148차 v1 `2>&1` 재발의 FINDINGS.md 정식 등록 여부, 147차 임시 스크립트 toolkit 미등록(이전 이월, 변동 없음).
5. (신규 이월, 164차 한계) MapTurnSpeedFactor 적정성 결론은 1개 로그 기준 -- 다른 도로/조건 로그로 일반화 검증 필요. `road` 후보의 실제 `limit_speed` 계산과 `nRoadLimitSpeed` 필드 관계를 코드로 직접 확인(로그 관찰상 무제한 placeholder 추정, 미확정).
6. 163차 코드 변경(route 게이트 제거) 자체의 실차(디바이스) 검증 -- 미실시.

검증:
- `route_extract.py extract`로 10세그먼트 12,000표본 재추출(각 세그먼트 rows=1199~1201, duration 약 60s, 163차와 동일 총량 확인).
- `MapTurnSpeedFactor=90`(base=0.90)일 때 `map_turn_speed_factor()`의 `guide=min(base,1.00)`이 base<=1.0이면 항상 `base`와 같아짐을 수식으로 확인 -- 로그 `route=` 값을 그대로 163차 수정 후 로직의 route 후보값으로 재사용 가능함의 근거로 명시.
- xTurnInfo==-1 표본의 xDistToTurn이 전부 음수임을 groupby로 확인, 게이트 배제 6,376건 중 5,092건(79.9%)에서 route가 새로 binding됨을 정량화, seg23 예시 구간(t=24~33s)을 20Hz로 직접 출력해 route 값의 안정성(120.0 고정)과 vturn/road의 스파이크를 대조 확인.

주의사항:
- 이번 세션은 코드 변경 없음(분석 전용). 163차 코드(`carrot_serv.py`)는 GitHub push는 확인됐으나 디바이스 배포/실차 검증은 아직.
- MapTurnSpeedFactor 관련 결론은 1개 로그(10세그먼트, 12,000표본) 기준 잠정 결론이며, 다른 도로/조건 로그로 일반화 검증이 이월되어 있다.

다음 작업:
1. 위 미완료 항목 중 우선순위를 다음 세션에서 사용자가 지정 -- 특히 163차 코드의 실차(디바이스 반영 후 실주행) 검증이 우선 후보.
2. 이 devnotes 반영 스크립트(`164cha_devnotes_carrot_ryu_note.ps1`) 실행 -> push 확인.
