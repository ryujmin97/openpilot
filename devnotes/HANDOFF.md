Worker: Claude (93차 계속)
Date: 2026-09-19
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `25f21d406d23bfb79ad45a67890cc39e3ad9e67b`, 93차 557e6f6a 반영 커밋 -- push/blob 재검증 완료. 이번 세션 추가 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `bd69ab0139874c7e36d6f58552923a291fc98a92`, 93차 devnotes 위. 이번 세션 WIP.md/WIP_SYNC.md/CURRENT_STATUS.md/HANDOFF.md 갱신, 반영 스크립트 실행/push 대기)
carrot-ms 마지막 검토/동기화 체크포인트(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스) 이후 carrot-ms(happymaj11r/openpilot) 현재 HEAD `e324f6735d3606800045ed6b28f41e79b17e5498`(변경 없음, `git ls-remote` 확인)까지 16건 전부 분류 종결: b4f751f4(90차)/4d1a3ded(91차 계속2)/ec95363a(92차)/557e6f6a(93차) 반영 완료 4건, 나머지 11건 + e324f67(93차 계속, 사용자 승인) 제외 12건. 상세는 WIP_SYNC.md 93차 계속 체크포인트.

작업:
사용자가 코드/devnotes 두 스크립트 실행 완료를 알려왔고(로그 미전달), GitHub에서 직접 재확인했다. 이어 e324f67(radar_motion 정지 lead 인계 조건)의 필요 여부를 분석했고, 사용자가 "제외."로 확정했다.

완료:
1. 557e6f6a 반영 확인 -- carrot-ryu `25f21d4`(부모 `9eced40`), 변경 파일 1개 +3/-1, 결과 blob `d04b52ce89e54698215cce8cf84bab62d5e846f7`가 원본 post-image와 일치.
2. 93차 devnotes 반영 확인 -- carrot-ryu-note `bd69ab0`(부모 `1f98304`), 변경 4개 파일의 sha256이 스크립트 내장 사전 계산값과 일치, WIP_SYNC.md CRLF 유지.
3. e324f67 분석 -- radard(radard_dpath) -> DPathRadarController -> VisionRadarMatcher._stationary_closer_handoff_ready 호출 경로 확인. 새 분기는 서로 다른 레이더 점 2개가 필요. 사용자 제공 params_backup-1.json(HyundaiCameraSCC=1/EnableRadarTracks=0/EnableCornerRadar=0) 기준 radar_interface는 SCC 고정 ID 점 하나만 발행하므로 발동 불가. 제외 확정(코드 변경 없음).
4. 분석 중 정정: "EnableRadarTracks=0이면 radarUnavailable=True" 추론은 HyundaiCameraSCC=1(CAMERA_SCC 플래그로 radarUnavailable=False)이라 틀렸고, 결론은 radar_tracks=False로 유지됨.
5. carrot-ms 신규 16건 분류 종결(반영 4건 + 제외 12건).

미완료(다음 세션 최우선):
1. `93cha2_devnotes_e324f67_carrot_ryu_note.ps1` 실행/push 확인 -- push 후 `git ls-remote`와 SHA 고정 raw sha256 대조로 4개 파일 재검증(16절).
2. 세션 시작 시 carrot-ms에 `e324f67` 이후 신규 커밋이 있는지 확인(2절). 있으면 미검토 커밋만 분석, 없으면 다음 항목.
3. 36개 항목(1~36) 및 b4f751f4/4d1a3ded/ec95363a/557e6f6a 재적용분 전부의 실차 검증 준비(이월, 여전히 미실시). 실기기 배포(git pull) 여부는 20절 7항에 따라 사용자 판단이며, 현재는 git pull 금지 유지 중.
4. WIP.md 파일 맨 끝(1차 세션 기록)의 mojibake 처리 여부, "# WIP" 헤더 중복 정리 여부(기존부터 이월, 사용자 판단 필요).

검증: `git ls-remote`(carrot-ryu/carrot-ryu-note/carrot-ms), blobless clone으로 커밋/변경 파일/blob 대조, SHA 고정 raw + sha256 대조, `github.com/.../commit/<sha>.patch` 직접 조회, raw로 조회한 소스 정적 읽기(controller.py/primary.py/radar_interface.py/interface.py/values.py). pytest는 이번 세션에서 실행하지 않았다. 샌드박스에 PowerShell(pwsh)이 없어 devnotes 스크립트의 PowerShell 구문 실행은 검증하지 못했다(직전 두 스크립트는 사용자 PC에서 정상 완료). 실차 검증: 미실시.

주의사항:
- e324f67 제외 판단은 사용자가 올린 params_backup-1.json 값에 근거한다. 백업 시점과 현재 장치 값의 일치는 확인하지 못했다. EnableRadarTracks를 0보다 크게 바꾸거나 EnableCornerRadar를 켜면 재검토해야 한다.
- 스크립트는 실행 시점에 4개 파일의 sha256이 예상(bd69ab0 상태)과 다르면 아무것도 수정하지 않고 중단한다. 중단되면 로그를 그대로 전달할 것(16절, `--force` 금지).
- WIP_SYNC.md는 CRLF 파일이라 스크립트가 삽입 텍스트만 CRLF로 변환한다(나머지 3개는 LF 유지). 바이트 단위로 처리하므로 기존 내용(WIP.md 끝의 mojibake 포함)은 그대로 보존된다.

다음 작업 후보:
1. devnotes 스크립트 실행 결과 확인 및 재검증.
2. carrot-ms 신규 커밋 확인(2절).
3. 36개 항목 + 재적용분 실차 검증 준비.
