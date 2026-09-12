# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 상태: 코드 변경 없음, 분석/기록 진행 중 (4차 완료)
- carrot-ryu 최신 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (carrot-wip과 동일)
- carrot-wip 마지막 동기화 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (분기 시점 기준, 신규 커밋 없음 확인)
- 최근 핵심 발견: 현대·기아·제네시스는 종방향 PID 게인(Kp/Ki/Kf)이 코드에 고정되어
  LongTuningKpV/KiV/Kf 설정값이 실제로는 무시됨. 조절 가능한 종방향 노브는
  LongActuatorDelay / VEgoStopping / StoppingAccel 뿐 (FINDINGS.md 2026-09-12 참고)
- 보류 항목: DisableDM=2, LateralTorqueCustom 의미 분석 (사용자 요청 시 재개)
