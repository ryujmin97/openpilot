Worker: Claude (192cha, Claude Sonnet 5)
Date: 2026-09-28
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit 6ed56f0d64df0612e3993e247d03fc199903569e, 변동 없음 -- 192cha는 코드 변경 없음.)
Note Branch: carrot-ryu-note (base commit c30d469614bfcb56e1ea4fce607f8a7ab04c8a7c, 191cha push 완료 확인. 192cha devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 3441183 -> 735a9a4 (192cha에서 신규 74건 전수 판정 완료, 전부 제외)

작업:
1. carrot-ms 정기 동기화 점검(2절): 체크포인트 3441183 이후 신규 74건
   (3441183..735a9a4)을 개별 판정.
2. 판정 결과를 WIP_SYNC.md 192차 체크포인트와 WIP.md 192cha 회차에 기록.
3. 이 HANDOFF.md 갱신.

완료:
1. 74건 전부 제외 확정:
   - Jetson/Jetlink/설치기 계열 70건: 이 차량 구성에 없는 외장 추론 호스트 전용.
   - eefd372: CAN FD HUD 전용(DH2015는 일반 CAN).
   - 72a33fb + 5e10742: VEgoStopping 최소값 1->10 상향 및 저장값 자동 상향.
     사용자 결정으로 제외(선택지 c). 실적용값 5 유지.
   - 14e2cfa: radar_track_state==1 필터. DH2015는 trackState가 항상 0이라 no-op.
2. WIP_SYNC.md / WIP.md 기록.

미완료:
1. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보,
   pytest CI 환경(conftest.py 포함 실제 cereal 실행), 102ms wide-camera BOOT_TS gap.
2. (이월) 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 검증.

검증:
- 정적 확인만 수행(커밋 목록, 변경 파일, 핵심 diff, radar_interface.py 코드 경로).
  Jetson 계열 70건은 라인 단위로 읽지 않음.
- 실차 검증: 미실시(12절, 192cha는 코드 변경 없음).

주의사항:
- carrot-ryu에는 openpilot/common/stopping_params.py가 없다(VEgoStopping은
  get_float * 0.01 직접 사용, 최소값 1). carrot-ms 후속 커밋이 get_stopping_speed에
  의존하면 이 차이를 먼저 확인할 것.
- 다음 코드 변경 세션은 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes)을 따른다.

다음 작업:
1. 이월 항목(실차 검증들) 중 우선순위 있는 것부터 진행.
2. 다음 carrot-ms 점검은 체크포인트 735a9a4 이후 신규 커밋부터.