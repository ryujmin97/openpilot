Worker: Claude (93차)
Date: 2026-09-19
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `9eced40e12dba9ecaa71fe4bd25a812d39d956ce`, 92차 ec95363a 반영 커밋 -- 93차 시작 시 push/blob 재검증 완료. 이번 세션은 557e6f6a 반영 스크립트 작성까지, 코드 push는 실행 대기)
Note Branch: carrot-ryu-note (base: `1f983041cd7d662f6aaae789d77c0030a1ca2190`, 92차 devnotes 위. 이번 세션 WIP.md/WIP_SYNC.md/CURRENT_STATUS.md/HANDOFF.md 갱신, 반영 스크립트 실행/push 대기)
carrot-ms 마지막 검토/동기화 체크포인트(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스) 이후 carrot-ms(happymaj11r/openpilot) 현재 HEAD `e324f6735d3606800045ed6b28f41e79b17e5498`(93차 `git ls-remote`로 변경 없음 확인)까지 16건 확인. b4f751f4(90차)/4d1a3ded(91차 계속2)/ec95363a(92차 작성, 93차 push 확인) 반영 완료, 11건 제외 확정, 557e6f6a는 이번 세션에서 상세 대조 완료(반영 스크립트 실행/push 대기), e324f67 분류 이월. 상세는 WIP_SYNC.md 93차 체크포인트.

작업:
사용자가 세션 시작 지침(지침 문서 조회)에 이어 "557e6f6a 착수"를 지시했다. 지침 문서(v2, carrot-ryu-note `1f98304`)를 브랜치 URL과 SHA 고정 URL 양쪽으로 조회해 내용이 동일함을 확인한 뒤, HANDOFF.md(92차)의 base와 실제 HEAD가 다른 점(carrot-ryu `f1e920d` -> `9eced40`)을 16절 절차로 먼저 재검증했다. 그 후 557e6f6a("Identify model artifact and input size in worker diagnostics", precompiled_worker.py 1파일 +3/-1) 상세 대조와 반영 스크립트 작성까지 진행했다.

완료:
1. ec95363a push 확인 -- carrot-ryu `9eced40`(부모 `f1e920d`, 92cha 커밋 메시지 그대로), 변경 파일 8개 +185/-39, 8개 결과 blob이 원본 patch post-image 인덱스와 전부 일치(blobless clone + `git rev-parse <commit>:<path>` 대조). ec95363a 반영 완료 확정.
2. carrot-ms HEAD `e324f67` 변경 없음, ryujmin97/openpilot 브랜치 구성(carrot-ryu/carrot-ryu-note/carrot-ryu-v1) 문서와 일치 확인.
3. 557e6f6a 원본 patch(26줄) 조회 -- `diagnostics.record` context에 format/camera_width/camera_height/input_bytes/model_sha256 추가만(타이밍 메타데이터 전용).
4. carrot-ryu `9eced40`의 precompiled_worker.py blob `1c2e2a3b5e6dbdfc4545b1595094bf5d81872ada`가 원본 pre-image와 byte-exact 일치(충돌 없음).
5. 신규 참조 값 존재 확인: width/height(main 29행 argv), input_bytes(66행, record 호출 99행보다 앞), manifest['pickle']['sha256'](worker 32행이 이미 사용), manifest['format'](installed.json이 `validate_catalog` 통과 catalog dict 전체를 그대로 저장하므로 항상 존재).
6. `tests/test_precompiled_runner.py`의 worker 직접 실행 테스트는 checksum 검증 단계에서 실패하는 경로라 record 지점에 도달하지 않아 영향 없음(코드 읽기 확인, 미실행).
7. 별도 sparse clone에서 `git apply --check` 통과 -> 적용 -> 변경 파일 1개 +3/-1, `py_compile` 통과, 결과 blob `d04b52ce89e54698215cce8cf84bab62d5e846f7`가 원본 post-image와 일치, CR 0/BOM 없음.
8. 반영 스크립트 `93cha_item_557e6f6a_carrot_ryu.ps1`(base64 전체교체 + pre-image blob 가드 + post blob/py_compile/변경 파일 1개/numstat +3/-1 검증 + push 후 원격 HEAD 대조) 작성, 9절 체크리스트 전 항목 명령 출력으로 통과, payload 역디코드 byte-exact 재확인.
9. devnotes 스크립트 `93cha_devnotes_557e6f6a_carrot_ryu_note.ps1`(WIP.md/WIP_SYNC.md/CURRENT_STATUS.md/HANDOFF.md 4개 파일, 바이트 단위 splice + 사전 계산한 pre/post sha256 대조) 같은 응답에서 함께 전달(91차 계속의 새 원칙).

미완료(다음 세션 최우선):
1. `93cha_item_557e6f6a_carrot_ryu.ps1` 실행/push 확인 -- push 후 `git ls-remote` + blobless clone으로 변경 파일 1개(+3/-1), 결과 blob `d04b52ce89e54698215cce8cf84bab62d5e846f7` 재검증(16절). 코드 push 이후 devnotes(CURRENT_STATUS.md 5행 등)의 carrot-ryu HEAD 표기도 새 커밋으로 정정.
2. `93cha_devnotes_557e6f6a_carrot_ryu_note.ps1` 실행/push 확인.
3. carrot-ms `e324f67`(radar_motion 정지 lead 인계 조건)의 필요 여부 판단: DH 2015(LEGACY)가 이 경로를 실제로 타는지 확인 후 사용자와 결정.
4. 36개 항목(1~36) 및 b4f751f4/4d1a3ded/ec95363a/557e6f6a 재적용분 전부의 실차 검증(이월, 여전히 미실시).
5. WIP.md 파일 맨 끝(1차 세션 기록)의 mojibake 처리 여부, "# WIP" 헤더 중복 정리 여부(기존부터 이월, 사용자 판단 필요).

검증: `git ls-remote`(carrot-ryu/carrot-ryu-note/carrot-ms/브랜치 목록), 지침 문서 브랜치 URL vs SHA 고정 URL sha256 대조, `git clone --filter=blob:none`로 커밋/변경 파일/blob 대조, `github.com/.../commit/<sha>.patch` 직접 조회, `raw.githubusercontent.com`(SHA 고정) + `git hash-object`, sparse clone에서 `git apply --check`/적용/`py_compile`. pytest는 이번 세션에서 실행하지 않았다. 샌드박스에 PowerShell(pwsh)이 없어 두 스크립트의 PowerShell 구문 실행은 검증하지 못했다(9절 체크리스트의 정적 검사와 payload 역디코드만 수행). 실차 검증: 미실시.

주의사항:
- 두 스크립트 모두 실행 시점에 대상 파일의 사전 상태(코드: pre-image blob, devnotes: 파일별 sha256)가 예상과 다르면 아무것도 수정하지 않고 중단하도록 만들어져 있다. 중단되면 로그를 그대로 전달할 것(16절, `--force` 금지).
- WIP_SYNC.md는 CRLF 파일이라 devnotes 스크립트가 그 파일에 한해 삽입 텍스트를 CRLF로 변환한다(WIP.md/CURRENT_STATUS.md/HANDOFF.md는 LF 유지). 바이트 단위로 처리하므로 기존 내용(WIP.md 끝의 mojibake 포함)은 그대로 보존된다.
- 557e6f6a는 usbgpu precompiled worker 진단 로그 메타데이터만 바꾸며 주행 동작 변경이 아니지만, DH 2015 실주행에서 이 경로 사용 여부는 미확인이다.

다음 작업 후보:
1. 코드/devnotes 스크립트 실행 결과 로그 확인 및 재검증.
2. e324f67 필요 여부 판단.
3. 36개 항목 + 재적용분 실차 검증 착수.
