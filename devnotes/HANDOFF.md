# HANDOFF

Worker: Claude (67차 계속 -- 20절 이식 항목 11 push 확인 + stray 파일 발견/제거 완료)
Date: 2026-09-17
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `81754ea388b42fceb37200df2173eecd8b86bd4f`, 67차-fix -- 항목 11 push(`63addc2e`) 위에 stray 파일 제거까지 완료된 최종 상태)
Note Branch: carrot-ryu-note (base: `559963de54cd0cdf5f82b30c18b2ad709beb445a`, 67차 devnotes. 이 커밋으로 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스, 변경 없음).

작업:
직전 세션에서 작성한 `reapply_item11_67cha.ps1` 실행 로그를 이어받아, `git ls-remote` + 독립 `git clone`으로 항목 11(24차, 화면녹화 탭 사진 스트립, commit `a7a912c1`) 재적용이 carrot-ryu에 실제로 push됐음을 확인했다. 그 과정에서 저장소 루트를 전수 점검하다 반영 스크립트 준비 중 만들어진 파이썬 헬퍼 파일(`apply_item11_67cha.py`)이 같은 커밋(`63addc2e`)에 실수로 함께 커밋된 것을 발견해, 제거 스크립트를 작성/전달했고 사용자가 실행해 최종적으로 정리까지 완료했다.

완료:
1. `git clone --depth 1 --branch carrot-ryu`로 독립 재현: HEAD가 `63addc2e`(커밋 메시지 "67cha: reapply item 11 ...")임을 확인.
2. 항목 11 코드 실체 확인: `selfdrive/carrot/web/src/features/logs/screenshots.js`(신규), `runtime.js`, `style.css`, `server/config.py`, `server/features/screenrecord/{catalog.py,routes.py}` 전부 정상 존재. 생성 번들(`web/css/generated/logs.css`, `web/js/generated/logs.js`)도 재생성되어 포함됨(45차 핵심 발견 30 재발 방지 규칙 준수 확인).
3. 저장소 루트(`git ls-tree -r --name-only HEAD`, 슬래시 없는 최상위 파일만 필터링)를 전수 점검해 `apply_item11_67cha.py` 단 하나만 정상 저장소 파일이 아닌 stray 항목임을 확인. 나머지 루트 파일(AGENTS.md, Jenkinsfile 등)은 원래 openpilot 저장소의 정상 파일.
4. 제거 전용 스크립트 `cleanup_stray_67cha.ps1` 작성: 9절/18절 필수 규칙 준수(UTF-8 BOM, CRLF, `core.autocrlf=false` clone, stray 파일이 이미 없으면 아무 것도 바꾸지 않고 중단, `git rm`/`git commit`/`git push` 각 단계 실패 시 즉시 중단 + 임시폴더 삭제, `--force` 미사용). 사용자가 실행, push 로그(`63addc2e..81754ea3 carrot-ryu -> carrot-ryu`) 확인.
5. `git ls-remote` + 독립 `git clone --depth 1`으로 재검증: carrot-ryu HEAD가 `81754ea3`(커밋 메시지 "67cha-fix: remove stray apply_item11_67cha.py accidentally committed at repo root")로 확인, `apply_item11_67cha.py`는 저장소에서 완전히 사라졌고 항목 11 코드는 그대로 정상 존재함을 확인(16절, 완료로 단정하기 전 필수 재확인 절차 준수).
6. CURRENT_STATUS.md 항목 11/26 및 최상단 "carrot-ryu HEAD" 표기를 `81754ea3` 기준 "정리 완료"로 갱신.

미완료(다음 세션 최우선):
1. 항목 22(39차, commit `797fca2e` -- 체크박스/전체선택/업로드/다운로드 툴바로 screenshots.js/runtime.js/style.css 전면 재작성) 재적용 착수, 이어서 항목 23(39cha-fix, formatRelativeEpoch import) → 항목 26(formatLogBytes import, 44차) 순서로 진행.
2. carrot-ryu-v1 나머지 미이식 항목(1·2번 종방향/RES 안전장치, 5번 이후 Google Drive 파이프라인, 30~36번 스크린샷 DPI/캡처타이밍/render-texture/상하반전 등)도 순서 미정, 사용자 확인 필요(20절 5번).
3. 이식이 반 정도라도 끝나기 전까지 콤마 디바이스 git pull 금지 상태 유지(현재도 유지 중 -- 12·13·25·27·28·11번 반영, stray 파일까지 정리된 깨끗한 상태).
4. (낮은 우선순위, 이전부터 이월) WIP.md 본문 중간에 있는 중복 "# WIP" 헤더 정리 -- 이번 세션에서 devnotes 반영 스크립트 작성 중 재확인됨, 불변 원칙상 신중하게 처리 필요.

검증: 항목 11 코드 반영과 stray 파일 제거 모두 독립 `git clone` + `git ls-tree`로 직접 재확인했다(16절). 실차 검증: 미실시(12절) -- git pull 금지 상태.

주의사항:
- carrot-ryu는 이제 `81754ea3` 상태이며, 항목 11 코드는 정상이고 stray 파일도 완전히 제거됐다. 12·13·25·27·28·11번이 반영된 깨끗한 상태.
- WIP.md 본문 중간의 중복 "# WIP" 헤더는 devnotes 반영 스크립트에서 최상단(첫 번째) occurrence만 대상으로 삼아 우회했다. 파일 자체를 고치는 작업은 아직 하지 않았다(낮은 우선순위 이월 항목).

다음 작업 후보:
1. 항목 22(39차) 재적용 착수
2. Google Drive 업로드 파이프라인(5~14번) 재적용 착수
3. 종방향/RES 안전장치(1·2번) 재적용
4. WIP.md 중복 헤더 정리(낮은 우선순위)
5. 이식 진행률을 CURRENT_STATUS.md에 계속 갱신
