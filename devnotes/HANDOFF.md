# HANDOFF

Worker: Claude (세션 4, 계속)
Date: 2026-09-12
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1, carrot-wip과 동일, 코드 변경 없음)
Note Branch: carrot-ryu-note (4차 계속 devnotes 반영)
carrot-wip 마지막 동기화 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (신규 커밋 없음 확인, 동기화 불필요)

작업:
완료:
- (이어서) DisableDM=2 의미 확인: 운전자 모니터링(졸음/주의분산 감지, 경고, 강제감속) 완전 OFF +
  Carrot Vision WebRTC 원격 스트리밍 활성화. carrot_settings.json 설명 문구 + process_config.py/
  selfdrived.py/controlsd.py 코드로 확정.
- LateralTorqueCustom=0 의미 확인: 저장된 LateralTorqueKf/Friction/AccelFactor/KiV/KpV/Kd 6개 값이
  전혀 적용되지 않음. 실제로는 opendbc torque_data/params.toml의 HYUNDAI_GENESIS 실측값
  (LAT_ACCEL_FACTOR≈2.7808, FRICTION≈0.0984)로 조향 토크 계산 중.
- FINDINGS.md / PARAMS_REGISTRY.md / WIP.md(4차 계속) / LAST_ANALYZED.md 갱신
- (직전 회차, 이미 push 완료됨) 종방향 PID 게인 고정 확인 — commit 2440764a

미완료:
- DisableDM=2가 사용자의 의도된 설정인지 실제로 확인 안 됨 (다음 세션에서 사용자에게 직접 질문 필요)
- LateralTorqueCustom을 켜서(1 이상) 커스텀 토크 테이블을 실제로 쓸지 여부는 사용자 결정 대기
- TFollowGap / 차간거리(t_follow.py), 곡선감속(curve_speed.py), 정지선(traffic_stop.py) 등
  carrot 전용 종방향 모듈은 아직 분석 안 함
- 종방향 MPC(longitudinal_mpc_lib) 코스트 함수 분석 안 함

검증: 실차 검증 미실시 (정적 코드/문서 분석 기준)

주의사항:
- DisableDM=2는 안전과 직결된 설정임. 다음 세션에서 이 대화나 devnotes를 이어받으면,
  사용자가 이 설정을 의도적으로 켠 것인지(예: DM 카메라 미장착 등 이유) 반드시 확인하고,
  Claude가 임의로 "안전하니 0으로 바꾸라"고 강권하지 말고 사실만 전달할 것.
- LateralTorqueCustom/LongTuningKpV류처럼 "저장은 되어있지만 실제 미적용"인 파라미터가
  이 프로젝트에 반복적으로 나타나는 패턴이 있음. 향후 다른 파라미터 분석 시에도
  "저장값 존재 = 실제 적용"으로 단정하지 말고 반드시 코드에서 읽는 조건을 확인할 것.
- carrot-ryu는 여전히 carrot-wip과 코드 동일 (분기 이후 실제 코드 수정 아직 없음)

다음 작업 후보:
- 사용자에게 DisableDM=2 의도 확인
- TFollowGap 등 차간거리 로직 분석
- 또는 사용자가 원하는 다른 항목
