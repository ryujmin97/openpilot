# HANDOFF

Worker: Claude (세션 5)
Date: 2026-09-12
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1, carrot-wip과 동일, 코드 변경 없음)
Note Branch: carrot-ryu-note (5차 devnotes 반영)
carrot-wip 마지막 동기화 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (신규 커밋 없음 확인, 동기화 불필요)

작업:
완료:
- 사용자 방향 확정: 종방향 코드 분석 우선 완료 → 실차주행 → 로그분석 순서로 진행
- route(경로) 기반 커브 감속 체인 전체 추적 완료: carrot_man.py(GPS 폴리라인→곡률→속도) →
  carrot_serv.py(speed_n_sources) → carrot_functions.py(v_cruise_kph 갱신) →
  longitudinal_planner.py → MPC v_cruise 상한까지 실제 감속 명령으로 이어짐을 확인
- 이 차량 실제 설정 TurnSpeedControlMode=2(route 감속 활성화 상태) 확인 (기본값 1이 아님)
- T_FOLLOW/TFollowGap(차간거리) 체인 전체 추적 완료: t_follow.py(헬퍼) →
  carrot_functions.py(get_T_FOLLOW, personality/속도보정/감속시 boost&hold/클립/램프) →
  long_mpc.py(MPC 리드차 장애물 제약)까지 실제 반영됨을 확인
- 이 차량은 EnableSpeedTF=0, LeadAccelResponse=0으로 단순 personality 고정값 모드 운용 확인
- FINDINGS.md / PARAMS_REGISTRY.md / WIP.md(5차) / LAST_ANALYZED.md / CURRENT_STATUS.md 갱신

미완료:
- traffic_stop.py(정지선 감속) 분석 안 함
- curve_speed.py(비전 커브 감속) 분석 안 함
- longitudinal MPC 코스트 함수(long_mpc.py 나머지, jerk_factor/aChangeCostStarting 등) 분석 안 함
- TurnSpeedControlMode=2(route 감속 켜짐)가 사용자 의도인지, 폰 내비 앱(APN) 연동이 실제로
  붙어있는지 확인 안 됨 (DisableDM=2와 동일한 "설정은 있는데 의도 미확인" 패턴)
- EnableSpeedTF=0 / LeadAccelResponse=0이 의도적 설정인지 확인 안 됨
- 실차주행 전혀 안 함 (콤마 디바이스 실장착/실주행 로그 없음)

검증: 실차 검증 미실시 (정적 코드/설정값 분석 기준)

주의사항:
- TurnSpeedControlMode=2 / DisableDM=2 둘 다 "저장값은 있지만 사용자 의도 확인 안 된 안전
  관련 설정"임. 다음 세션에서 사용자에게 직접 확인 필요 (Claude가 임의로 끄라고 권하지 말 것).
- carrot-ryu는 여전히 carrot-wip과 코드 동일 (분기 이후 실제 코드 수정 아직 없음)
- 종방향 분석이 어느 정도 마무리되면(traffic_stop.py, curve_speed.py, MPC 코스트 함수까지),
  실차주행 단계로 넘어가기로 사용자와 합의됨. 실차주행 시 route 로그는 13절 원칙에 따라
  Git에 직접 커밋하지 말고 Google Drive 등에 보관, devnotes에는 참조 정보만 남길 것.

다음 작업 후보:
- traffic_stop.py(정지선), curve_speed.py(비전 커브), longitudinal MPC 코스트 함수 순으로 종방향 분석 마무리
- 종방향 분석 마무리 후: 사용자에게 TurnSpeedControlMode/EnableSpeedTF 등 의도 확인
- 그 다음: 콤마 디바이스 실차주행 → route 로그 수집 → 로그분석 단계로 전환
