# HANDOFF

Worker: Claude (64차 -- 20절 이식 항목 4 재적용: 온로드 시계 좌측 화면 경계 잘림 수정(13차, 2adced8 원본)을 새 베이스(706efb47 + 63차 429f105e) 위에 재적용)
Date: 2026-09-17
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `429f105e16853b5230d7eb7a082de2b817a3d8e9`, 63차 HEAD 위에 13차 원본 재적용 커밋 추가 -> `4e3b44a81f2fc79c3b6f23ebaee40a1bc73d370b`)
Note Branch: carrot-ryu-note (base: `ccc89e50938ec549725702ceee158b132b1c3c9f`, 63차 devnotes. 이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스, 변경 없음).

작업:
63차에서 확정된 다음 이식 후보(20절 이식 항목 4번: 온로드 시계 좌측 화면 경계 잘림 수정, 13차 2adced8 기준)를 착수. 원본 커밋이 hud_renderer.py 한 곳(_draw_date_time)만 건드리는 작은 diff였고, 그 함수가 12차 재적용(63차) 이후에도 원본 base(`0e9c84a51e`)와 정확히 동일하게 남아있음을 확인해, Replace-Block 방식으로 그대로 재적용했다.

완료:
1. GitHub API/commit diff 조회로 13차 원본 커밋(2adced8)의 diff를 확인 -- hud_renderer.py `_draw_date_time`에서 `if show_datetime in (1, 2):` 블록에 텍스트 실측 폭 기준 x좌표 보정 로직(`measure_text_cached` 호출 + `min_x` 계산) 7줄 추가가 전부임을 확인.
2. 새 베이스(carrot-ryu HEAD `429f105e`)의 hud_renderer.py를 직접 조회해, diff의 원본 기준 blob(`0e9c84a51e`)과 해당 함수 내용이 정확히 일치함을 확인(12차 재적용 이후 이 함수는 변경된 적 없음). `measure_text_cached`/`draw_text_ui_style`/`UI_CONFIG.border_size` 모두 이미 import/정의되어 있어 추가 의존성 없이 적용 가능함을 확인.
3. Replace-Block(9절, CRLF->LF 정규화 병행)으로 sandbox에서 원본 커밋과 동일한 삽입 블록을 구성, 치환 결과가 정확히 1회 매치 + `py_compile` 통과함을 확인. 특히 치환 결과 파일의 blob 내용이 원본 13차 커밋의 결과 blob(`d7e8d7b6a5`)과 완전히 일치함을 diff로 재확인(바이트 단위 재현).
4. 사용자가 `reapply_13cha_64.ps1` 실행, commit `4e3b44a81f2fc79c3b6f23ebaee40a1bc73d370b`로 carrot-ryu에 push 완료.
5. `git ls-remote`(carrot-ryu=`4e3b44a8`)와 commit diff 직접 조회로 반영 내용이 원본 13차 커밋과 정확히 일치함(결과 blob `d7e8d7b6a5` 동일)을 재확인.
6. carrot-ryu-v1 "코드 수정 현황" 항목 4(온로드 시계 좌측 경계 잘림 수정)를 "재반영 완료(commit `4e3b44a8`)"로 CURRENT_STATUS.md에 개별 갱신.

미완료: 없음(이번 항목은 이식/검증/devnotes 갱신까지 한 세션에 완결).

미완료(다음 세션 최우선):
1. carrot-ryu-v1 "코드 수정 현황" 나머지 항목 재적용 계속: 1·2번(종방향/RES 안전장치), 5번 이후(Google Drive 파이프라인 등), 스크린샷 관련 후속 수정(25·26~28·30~36번).
2. [63차부터 이월, 사용자 확인 필요] 스크린샷 후속 수정(DPI 반전/캡처 타이밍/render-texture 재설계/상하반전 등, carrot-ryu-v1에는 이미 실차검증까지 끝난 상태로 존재)을 다음에 이어서 할지, Google Drive 파이프라인 등 다른 서브시스템을 먼저 할지 순서를 정해야 함(20절 5번).
3. 이식이 반 정도라도 진행되기 전까지 콤마 디바이스 git pull 금지 상태 유지(현재도 여전히 유지 중 -- 12·13차만 반영된 상태).

검증: 코드 변경은 `git ls-remote` + commit diff로 직접 재확인, 원본 커밋과 결과 blob까지 일치 확인(위 완료 5번). 실차 검증: 미실시(12절) -- git pull 금지 상태이므로 디바이스에 배포된 적 없음.

주의사항:
- carrot-ryu는 여전히 커스텀 코드 대부분이 없는 상태(12·13차 두 항목만 추가됨). git pull 금지 유지 중이므로 실차 영향 없음.
- carrot-ryu-v1은 이식 체크리스트이자 임시 참조용이므로 1절 원칙대로 수정하지 않는다.

다음 작업 후보:
1. 스크린샷 후속 수정(25·26~28·30~36번) 몰아서 재적용 -- 또는 사용자가 다른 순서 지정
2. Google Drive 업로드 파이프라인(5~14번) 재적용 착수
3. 종방향/RES 안전장치(1·2번) 재적용
4. 이식 진행률을 CURRENT_STATUS.md에 계속 갱신