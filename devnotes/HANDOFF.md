# HANDOFF

Worker: Claude (세션 2)
Date: 2026-09-12
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1, carrot-wip과 동일)
Note Branch: carrot-ryu-note (2차 devnotes 반영)
carrot-wip 마지막 동기화 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (분기 시점, 아직 추가 동기화 없음)

작업:
완료:
- 브랜치 3종 세팅 완료 (carrot-wip / carrot-ryu / carrot-ryu-note)
- minSteerSpeed 60km/h 제한 관련 분석 완료
- DisableMinSteerSpeed 설정 토글 존재 확인 (코드 수정 불필요, 설정으로 해결)

미완료:
- 콤마 디바이스에서 DisableMinSteerSpeed=1 적용 후 실차 검증
- carrot-wip 다른 영역(종방향 제어, DM 등) 분석 미착수

검증: 실차 검증 미실시 (정적 분석만 수행)

주의사항:
- carrot-ryu는 아직 carrot-wip과 코드 차이 없음 (분기만 한 상태)
- DisableMinSteerSpeed=1 설정 후에도 저속에서 실제 조향 개입 강도/안정성은
  SMDPS 개조 품질에 좌우되므로 초기 테스트는 안전한 공간에서 진행 권장

다음 작업:
- (사용자 결정 필요) 콤마 디바이스 설정 반영 후 실주행 테스트 진행 여부
- 또는 다음 분석 대상 선정 (예: longitudinal 튜닝, MDPS 토크 파라미터 등)
