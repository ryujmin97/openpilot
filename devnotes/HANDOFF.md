Worker: Claude (91차 계속)
Date: 2026-09-19
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `260565f187a2d934f0e27464457eee63c8ec233a`. 4d1a3ded 반영 스크립트 `91cha2_4d1a3ded_carrot_ryu.ps1` 실행/push 대기 -- 다음 세션은 `git ls-remote`로 실제 HEAD를 먼저 확인할 것)
Note Branch: carrot-ryu-note (base: `b55388c6b700885b0c3f5bde66e9e6f3618adf8c`, 91차 devnotes 위. 이번 세션 WIP_SYNC.md/WIP.md/CURRENT_STATUS.md/HANDOFF.md 갱신, 반영 스크립트 `91cha2_devnotes_carrot_ryu_note.ps1` 실행/push 대기)
carrot-ms 마지막 검토/동기화 체크포인트(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스) 이후 carrot-ms(happymaj11r/openpilot) 현재 HEAD `e324f6735d3606800045ed6b28f41e79b17e5498`까지 16건 확인. b4f751f4 반영 완료(90차), 4d1a3ded 반영 스크립트 준비(실행/push 대기), ec95363a/557e6f6a 미반영, e324f67 분류 이월, 나머지 11건 제외 확정. 상세는 WIP_SYNC.md 91차 계속 체크포인트.

작업:
사용자가 91차 devnotes 반영 스크립트 실행 완료를 알려와 GitHub(`git ls-remote`, SHA 고정 raw)에서 재확인했다(carrot-ryu-note `b55388c`, 4개 파일, carrot-ryu는 `260565f` 그대로). 이어서 사용자가 새 원칙을 지시했다: 코드 변경 시 devnotes 기록도 같은 세션에서 동시에 진행한다. 남은 3건의 처리 순서는 사용자가 Claude 판단에 위임해, 90차 반영의 직접 후속인 carrot-ms 4d1a3ded를 먼저 골랐다(check_contracts.py `modeld-mirror` 계약이 carrot-ryu 260565f에서 FAIL이고 4d1a3ded 시점에서 PASS인 것을 샌드박스에서 확인). 4d1a3ded의 코드 반영 스크립트(carrot-ryu)와 이 devnotes 스크립트(carrot-ryu-note)를 같은 응답에서 함께 전달했다. WIP_SYNC.md의 널바이트 1개도 정정했다.

완료:
1. 91차 devnotes push(`b55388c`) GitHub 재확인.
2. 4d1a3ded 분석: 변경 파일 2개(carrot/model_selector/carrot_modeld.py, upstream_baseline/modeld.py.baseline, +11/-80), 두 파일의 pre-image blob이 carrot-ryu와 동일, Replace-Block 7개(3+4)를 pre-image에 순차 적용한 결과가 4d1a3ded의 blob과 byte 일치.
3. 반영 스크립트 2개 작성 및 사전 실행 검증(PowerShell 7.4로 로컬 저장소에 대해 실행).
4. WIP_SYNC.md 널바이트 정정, devnotes 4개 파일 갱신.

미완료(다음 세션 최우선):
1. 코드 반영 스크립트(`91cha2_4d1a3ded_carrot_ryu.ps1`)와 devnotes 스크립트(`91cha2_devnotes_carrot_ryu_note.ps1`)를 사용자가 실행/push했는지 `git ls-remote`로 확인. 코드 push 후 carrot-ryu의 새 HEAD와 부모(260565f), 변경 파일 2개를 확인하고 WIP_SYNC.md/CURRENT_STATUS.md의 4d1a3ded 항목을 "반영 완료"로 갱신.
2. ec95363a(레인 대시 배치/UI CPU 분리, 8개 파일 +185/-39, augmented_road_view.py/road_markings.py/render_diagnostics.py 신규 상세 대조 필요) -> 557e6f6a(precompiled_worker.py 진단 로그 1파일) 순으로 반영 여부 진행. 사용자가 순서를 위임했으므로 별도 승인 요청 없이 준비하되, 코드 반영 스크립트와 devnotes 스크립트는 항상 같은 응답에서 함께 전달할 것.
3. carrot-ms e324f67(radar_motion 정지 lead 인계 조건)의 필요 여부 판단: DH 2015(LEGACY)가 이 경로를 실제로 타는지 확인 후 사용자와 결정. 대상 두 파일의 pre-image blob이 carrot-ryu와 동일해 충돌 없이 적용 가능.
4. 4d1a3ded 반영 후 carrot-ryu에서 check_contracts.py `modeld-mirror`가 PASS인지 샌드박스에서 재확인(다른 FAIL 4건은 tinygrad_repo 부재로 인한 샌드박스 한계).
5. 36개 항목(1~36) 및 b4f751f4/4d1a3ded 재적용분 전부의 실차 검증(이월, 여전히 미실시).
6. WIP.md 파일 맨 끝(1차 세션 기록)의 mojibake 처리 여부, "# WIP" 헤더 중복 정리 여부(기존부터 이월, 사용자 판단 필요).

검증: `git ls-remote`로 carrot-ryu(`260565f`)/carrot-ryu-note(`b55388c`) 실제 HEAD 확인, SHA 고정 raw 조회로 91차 devnotes 반영 확인. 4d1a3ded 패치는 `git clone --filter=blob:none`(happymaj11r/openpilot)의 `git show`/`git rev-parse`로 조회했고, 반영 스크립트의 블록을 pre-image에 순차 적용한 결과 blob이 4d1a3ded와 일치함을 확인. check_contracts.py를 carrot-ryu 260565f/carrot-ms b4f751f4/carrot-ms 4d1a3ded 세 상태에서 실행해 비교. 반영 스크립트 2개는 PowerShell 7.4(Linux)로 로컬 bare 저장소에 대해 실행 검증했으나 Windows PowerShell 5.1에서는 실행하지 못했다. 실차 검증: 미실시(이번 세션은 코드 push 전이며 GitHub 조회와 샌드박스 검증뿐).

주의사항:
- 4d1a3ded는 carrot-ms 반영 작업이고 미러(carrot_legacy) 경로에만 영향이 있다. DH 2015에서 이 경로가 쓰이는지는 미확인이다. 디바이스 git pull 금지 상태를 유지한다.
- 스크립트는 사용자가 실행하기 전에는 반영된 것이 아니다. 두 스크립트 중 한쪽만 실행됐을 수 있으므로(90차 사례) 다음 세션은 carrot-ryu와 carrot-ryu-note의 실제 HEAD를 각각 확인해 서로 맞는지 볼 것.
- 샌드박스 계약 점검 방법: `python3 carrot/model_selector/check_contracts.py`(표준 라이브러리만 사용). `tinygrad_repo`가 없으면 script-paths/tinygrad-pickle-compat/compile-env-guards/wiring이 FAIL이지만 이는 반영 전후와 무관한 한계다. 판단 기준은 `modeld-mirror` 한 줄이다.
- 샌드박스 테스트 실행 방법: 반영 대상 브랜치를 sparse checkout(openpilot/selfdrive/modeld, carrot, ui, openpilot/common)한 뒤 `PYTHONPATH=<clone 루트> python3 -m pytest --noconftest -o addopts="" <test 파일>`.
- 남은 항목과 e324f67의 정적 대조 결과는 반영 승인이 아니라 준비 자료다. 반영 스크립트는 항상 사용자가 실행해야 반영된다(9절, 15절).

다음 작업 후보:
1. 두 스크립트 실행 결과(로그) 확인, `git ls-remote`로 carrot-ryu/carrot-ryu-note HEAD 재확인.
2. ec95363a 상세 대조(변경 8개 파일) 후 반영 스크립트+devnotes 스크립트 동시 준비.
3. 557e6f6a 반영, e324f67 필요 여부 판단.
4. 36개 항목 + b4f751f4/4d1a3ded 재적용분 실차 검증 착수.
