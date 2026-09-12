# HANDOFF

Worker: Claude (세션 5, 계속)
Date: 2026-09-12
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1, carrot-wip과 동일, 코드 변경 없음)
Note Branch: carrot-ryu-note (5차 계속 devnotes 반영)
carrot-wip 마지막 동기화 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (신규 커밋 없음 확인, 동기화 불필요)

작업:
완료:
- 종방향(가감속) 코드 분석 1단계 전체 마무리:
  1) LongControl PID 게인 고정 확인 (4차)
  2) DisableDM / LateralTorqueCustom 의미 확인 (4차 계속)
  3) route(경로) 감속 체인 + T_FOLLOW/TFollowGap 체인 (5차)
  4) traffic_stop.py(E2E 정지신호), curve_speed.py(비전 커브), longitudinal MPC 코스트 함수 (5차 계속)
- 종방향 전체 체계를 다이어그램으로 종합 정리 (FINDINGS.md 5차 계속 마지막 항목)
- 이 차량의 실제 설정값 다수 확인: TurnSpeedControlMode=2, AutoCurveSpeedFactor=80,
  TrafficLightDetectMode=2, StopDistanceCarrot=700, TrafficStopDistanceAdjust=0,
  EnableSpeedTF=0, LeadAccelResponse=0, DynamicTFollowLC=100, TFollowDecelBoost=10
- FINDINGS.md / PARAMS_REGISTRY.md / WIP.md(5차 계속) / LAST_ANALYZED.md / CURRENT_STATUS.md 갱신

미완료 / 확인 필요 (다음 세션 우선순위):
- TurnSpeedControlMode=2(route 감속 켜짐)가 사용자 의도인지, 폰 내비 앱(APN) 연동이 실제로
  붙어있는지 확인 안 됨 (DisableDM=2와 동일한 "설정은 있는데 의도 미확인" 패턴)
- EnableSpeedTF=0 / LeadAccelResponse=0이 의도적 설정인지 확인 안 됨
- DisableDM=2 의도 여부, LateralTorqueCustom=0인 이유 여전히 미확인 (오래된 보류 항목)
- 실차주행 전혀 안 함 (콤마 디바이스 실장착/실주행 로그 없음)

검증: 실차 검증 미실시 (모든 결론은 정적 코드/설정값 분석 기준)

주의사항:
- TurnSpeedControlMode=2 / DisableDM=2 둘 다 "저장값은 있지만 사용자 의도 확인 안 된 안전
  관련 설정"임. 다음 세션에서 사용자에게 직접 확인 필요 (Claude가 임의로 끄라고 권하지 말 것).
- carrot-ryu는 여전히 carrot-wip과 코드 동일 (분기 이후 실제 코드 수정 아직 없음)
- 종방향 코드 분석은 이번 회차로 1단계를 마무리하기로 사용자와 합의. 다음은 실차주행 단계.
  route 로그는 13절 원칙에 따라 Git에 직접 커밋하지 말고 Google Drive 등에 보관, devnotes에는
  참조 정보만 남길 것.
- 실차주행 전, 위 "확인 필요" 항목(특히 안전 관련 DisableDM=2, TurnSpeedControlMode=2)을
  먼저 사용자와 확인하는 것을 권장 (실차 검증 전 마지막 점검 기회).

다음 작업 후보 (우선순위 순):
1. 사용자에게 TurnSpeedControlMode/EnableSpeedTF/DisableDM 등 의도 확인
2. 콤마 디바이스 실차주행 → route 로그 수집
3. 로그분석 툴킷 준비/재사용 (devnotes/toolkit/README.md 먼저 확인) → 로그분석으로 코드
   분석과 실제 거동 일치 여부 검증
