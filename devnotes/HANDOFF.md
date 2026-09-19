Worker: Claude (91차)
Date: 2026-09-19
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `260565f187a2d934f0e27464457eee63c8ec233a`, 90차 커밋(carrot-ms b4f751f4 재적용) -- 이번 세션은 코드 미변경)
Note Branch: carrot-ryu-note (base: `b7013c611444483a80094aa313b62d56121f4095`, 89차 devnotes 위. 이번 세션 WIP_SYNC.md/WIP.md/CURRENT_STATUS.md/HANDOFF.md 갱신, 반영 스크립트 실행/push 대기)
carrot-ms 마지막 검토/동기화 체크포인트(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스) 이후 **[91차]** carrot-ms(happymaj11r/openpilot) 현재 HEAD `e324f6735d3606800045ed6b28f41e79b17e5498`까지 16건 확인(89차 분석 15건 + 신규 1건). 15건 중 b4f751f4는 90차에 반영 완료, 11건은 제외 확정, 3건(4d1a3ded/ec95363a/557e6f6a)은 미반영, 신규 e324f67은 분류 이월. 상세는 WIP_SYNC.md 91차 체크포인트.

작업:
세션 시작 시 4절 0단계로 지침 문서(v2)와 HANDOFF.md/CURRENT_STATUS.md를 SHA 고정(`b7013c6`)으로 조회했다. HANDOFF.md(89차)의 코드 base(`0923f83`)와 달리 carrot-ryu HEAD가 `260565f`("90cha: reapply carrot-ms b4f751f4 ...", 2026-09-19 13:06 +0900)인 것을 발견했고(16절), devnotes 어디에도 90차 기록이 없음을 확인했다. 90차 세션이 코드 push까지만 마치고 devnotes 반영 전에 끊긴 것으로 보인다. 90차 세션 자체의 진행 경위(승인 대화, 당시 실행한 검증)는 확인하지 못했다.

사용자에게 상황을 보고하고 '진행' 승인을 받아, (1) 260565f를 carrot-ms b4f751f4 원본과 읽기 전용으로 대조 검증하고 (2) 그 결과를 devnotes에 사후 동기화하는 반영 스크립트(`91cha_devnotes_carrot_ryu_note.ps1`)를 작성했다. 승인 범위는 여기까지이며 남은 3건의 코드 반영은 착수하지 않았다.

완료:
1. 260565f 대 b4f751f4 패치 대조: 15개 파일(+307/-152) 660줄 동일, 차이는 carrot_man.py 헝크 헤더 시작 줄번호 1줄(1457 vs 1481)뿐.
2. 변경 .py 11개 py_compile 통과, 단위 테스트 47개 통과(camera_sync 5/path_geometry 8/curve_speed 22/precompiled_runner 12).
3. carrot-ms 신규 커밋 e324f67 발견 및 사전 조사(변경 파일 2개, carrot-ryu와 pre-image blob 동일 확인).
4. WIP_SYNC.md 널바이트 1개(116행) 발견.
5. devnotes 반영 스크립트 작성.

미완료(다음 세션 최우선):
1. 위 devnotes 반영 스크립트를 사용자가 실행해 WIP_SYNC.md/WIP.md/CURRENT_STATUS.md/HANDOFF.md를 push할 것.
2. 남은 3건(4d1a3ded -> ec95363a -> 557e6f6a, 커밋 발생 순서) 반영 여부를 사용자와 논의해 승인받은 뒤 9절 방식으로 착수. ec95363a는 augmented_road_view.py/road_markings.py 레인 대시 영역과 render_diagnostics.py 신규 파일을 착수 전 상세 대조해야 한다.
3. carrot-ms e324f67(radar_motion 정지 lead 인계 조건)의 필요 여부 판단: DH 2015(LEGACY)가 이 경로를 실제로 타는지 확인 후 사용자와 결정. 반영하기로 하면 pre-image blob이 carrot-ryu와 동일해 충돌 없이 적용 가능.
4. WIP_SYNC.md 116행 널바이트 정정 여부(사용자 결정, 정상 표기는 `02015190f58a4380a433ee0130e6374455dddc2e`).
5. 36개 항목(1~36) 및 b4f751f4 재적용분 전부의 실차 검증(이월, 여전히 미실시).
6. WIP.md 파일 맨 끝(1차 세션 기록)의 mojibake 처리 여부, "# WIP" 헤더 중복 정리 여부(기존부터 이월, 사용자 판단 필요).

검증: `git ls-remote`로 carrot-ryu(`260565f`)/carrot-ryu-note(`b7013c6`) 실제 HEAD 확인, `git clone --filter=blob:none`으로 carrot-ryu-note/carrot-ryu/carrot-ms(happymaj11r/openpilot) partial clone 후 `git show`/`git log`로 조회. 260565f와 b4f751f4의 패치를 diff, 변경 .py 11개를 py_compile, 단위 테스트 4개 파일 47개를 pytest로 실행(샌드박스 python3.12, sparse checkout에 openpilot/common 포함 필요). carrot-ms HEAD는 `git rev-list --count f19d404a..HEAD` = 1로 확인. 실차 검증: 미실시(이번 세션은 코드 변경 없이 GitHub 조회/샌드박스 검증만).

주의사항:
- 이 세션의 검증은 정적/샌드박스뿐이다. 260565f가 원본 패치와 일치한다는 것이지 콤마 디바이스에서 동작한다는 뜻이 아니다. 디바이스 git pull 금지 상태를 유지한다.
- 샌드박스 테스트 실행 방법: 반영 대상 브랜치를 sparse checkout(openpilot/selfdrive/modeld, carrot, ui, openpilot/common)한 뒤 `PYTHONPATH=<clone 루트> python3 -m pytest --noconftest -o addopts="" <test 파일>`. sparse checkout에 openpilot/common이 없으면 test_precompiled_runner가 ModuleNotFoundError로 실패하는데, 이는 carrot-ms 원본에서도 동일한 구성 문제다.
- api.github.com REST API rate limit(60회/시간)에 걸리면 `git clone --filter=blob:none --no-checkout` + `git show`로 우회한다(89차 실증, 이번 세션에서도 사용).
- 남은 3건과 e324f67은 저위험으로 보이더라도 정적 대조일 뿐 반영 승인이 아니다. 18절 원칙대로 사용자 명시적 승인 없이 다음 세션이 임의로 반영해서는 안 된다.

다음 작업 후보:
1. devnotes 반영 스크립트(`91cha_devnotes_carrot_ryu_note.ps1`) 실행/push 확인(push 후 `git ls-remote`로 carrot-ryu-note HEAD 재확인).
2. 남은 3건 및 e324f67 반영 여부 사용자 확인, 승인 시 ec95363a 상세 대조부터 진행.
3. WIP_SYNC.md 널바이트 정정 여부 확인.
4. 36개 항목 + b4f751f4 재적용분 실차 검증 착수.
