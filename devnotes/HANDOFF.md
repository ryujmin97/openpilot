# HANDOFF

Worker: Claude (세션 3)
Date: 2026-09-12
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1, carrot-wip과 동일, 아직 코드 변경 없음)
Note Branch: carrot-ryu-note (3차 devnotes 반영)
carrot-wip 마지막 동기화 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (분기 시점, 아직 추가 동기화 없음)

작업:
완료:
- 사용자 디바이스 params_backup-4.json 수령 및 devnotes에 스냅샷 보관
- 현재 적용 중인 주요 튜닝 파라미터 PARAMS_REGISTRY.md에 정리
- DisableMinSteerSpeed=1 실제 적용 확인 (기존 FINDINGS와 일치)

미완료:
- DisableDM=2 의미/근거 미확인
- LateralTorqueCustom=0인데 LateralTorque* 값들이 커스텀된 이유 미확인
- carrot-wip 다른 영역(종방향 제어 세부 로직 등) 분석 미착수

검증: 실차 검증 미실시 (사용자 제공 백업 파일 기반 기록)

주의사항:
- carrot-ryu는 아직 carrot-wip과 코드 차이 없음
- 이번 파라미터들은 "현재 적용 중"인 값이므로, 향후 값을 바꿀 때는
  이 스냅샷과 비교해서 변경 이력을 PARAMS_REGISTRY.md에 남길 것

다음 작업 후보:
- DisableDM=2, LateralTorqueCustom 관련 코드 분석
- 또는 사용자가 원하는 다른 튜닝 항목 우선 분석
