# HANDOFF

Worker: Claude (50차 -- 49차 진단 로그 실차 반영 확인 + 로그 분석으로 export_image 원인 좁힘 + PNG 롤백 반영)
Date: 2026-09-16
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `dfdbfff9a7df48aac869b1417ea6398dd6768f32`, 49차 진단 로그+버튼위치 반영이 실기기에 이미 push/git pull/reboot까지 완료된 상태에서 시작. 이번 세션 변경: screenshot_capture.py 저장 확장자 `.jpg` -> `.png` 롤백 -- 아래 반영 스크립트 실행 대기)
Note Branch: carrot-ryu-note (base: `21c04355e2c1ba7b7f3c3585adc3df06e5a566e4`, 49차. 이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 체크포인트 이후 신규 23건 확인, WIP_SYNC.md 40차 체크포인트 반영 스크립트 실행 여부 미확인(계속 이월)

작업:
사용자가 (1) 온로드 HUD 실기기 촬영 사진 1장(스크린샷 버튼이 좌측으로 이동된 모습, 버튼 위치는 의도대로 됐다고 확인), (2) carrotweb 위젯 실행 로그 캡처 1장(`git pull` 41fd34a74..dfdbfff9a Fast-forward + `reboot` 로그, 49차 커밋 메시지 "49cha: add diagnostic logging..." 확인), (3) 실기기 터미널에서 뽑은 `grep -ai screenshot /data/log/swaglog.*` 결과(약 20줄, git pull 전/후 구간 혼재)를 제공. 지침 문서 4절 0단계(git ls-remote SHA 고정)부터 시작, HANDOFF.md/CURRENT_STATUS.md 확인 후 진행.

완료:
1. `git ls-remote`로 carrot-ryu HEAD가 `dfdbfff9a7df48aac869b1417ea6398dd6768f32`임을 확인 -- 사용자가 이미 49차 반영 스크립트를 실행해 push까지 완료했음을 실증(49차 미완료 1번 해소).
2. 사용자가 준 swaglog grep 결과를 두 구간(git pull 이전 commit `41fd34a7`=47차 / 이후 commit `dfdbfff9`=49차)으로 나눠 분석. git pull 이후 구간에서 raylib의 `Failed to export image` 경고 직후 매번 `screenshot_button.py:28 _on_click`에서 `capture_onroad_screenshot: export_image failed for ...` 경고가 함께 찍히는 것을 확인.
3. 이 경고 문자열이 코드상 `capture_onroad_screenshot()`의 `rl.export_image()`가 `False`를 반환했을 때만 나온다는 점(screenshot_capture.py 직접 재확인)으로부터, (a) 클릭이 `_on_click()`까지 정상 전달되고 (b) `load_image_from_screen()`도 성공했음을 로그 근거로 실증 -- 49차 미완료 2번 중 "클릭 전달 문제" 가설을 배제(11절, 추측 아닌 로그 근거).
4. 실패 지점이 오직 `rl.export_image()` 호출 자체임을 좁힘. 이 실패가 git pull 이전(47차, 진단 로그 추가 전) 구간에도 이미 있었다는 점과, 46차까지(PNG 저장 시절)는 방향은 뒤집혀도 저장 자체는 성공했다는 기존 devnotes 기록을 근거로 "JPG export가 이 기기의 raylib 빌드(comma-deps-raylib==6.0.0.1.post101)에서 지원되지 않는다"를 유력 가설로 제시. 단, DPI 수정(`load_image_from_screen()` 전환)과 확장자 변경(PNG->JPG)이 47차에 같은 커밋으로 함께 들어가 변수가 분리되지 않은 상태임을 명시(11절, 확정 아님).
5. 사용자가 화면 촬영 사진으로 스크린샷 버튼 위치가 의도한 대로 이동됐음을 직접 확인(49차 미완료 3번 해소).
6. 변수 분리를 위해 `screenshot_capture.py`의 저장 확장자만 `.jpg` -> `.png`로 되돌리는 최소 변경을 반영(`load_image_from_screen()` DPI 수정은 그대로 유지). Replace-Block 앵커(도크스트링 문단 + `filename = time.strftime(...)` 줄)가 파일 전체에서 정확히 1회 매치함을 확인(9절).
7. carrot-ryu 반영 스크립트(코드 1개 파일, Replace-Block) + carrot-ryu-note 반영 스크립트(WIP.md/FINDINGS.md 이어붙이기, HANDOFF.md/CURRENT_STATUS.md 교체) 작성.

미완료 (다음 세션 이월):
1. [최우선, 신규] 이번 세션에서 전달한 스크립트 2개(carrot-ryu 코드, carrot-ryu-note devnotes)의 실행 결과 확인.
2. [최우선, 신규] PNG 롤백 반영 후 실제로 스크린샷 버튼을 눌러 사진이 저장되는지 확인 -- 성공하면 JPG export 미지원이 원인으로 확정(다음 세션에서 JPG 대안 검토), 실패하면(같은 raylib 경고 재현) 확장자와 무관한 다른 원인으로 조사 방향 전환 필요.
3. [이월, 47차] 저장 성공 시 사진 방향/용량(가로 2160x1080, 파일 크기)도 함께 재확인 -- 47차 DPI 수정 자체의 실차 검증이 이번 건과 함께 처리 가능.
4. [이월, 37차] 락 수정의 실제 동시성 재현 검증(의도적으로 거의 동시에 두 업로드 시도).
5. [이월, 34차] 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
6. [이월] 28~30차 레이아웃 정밀 재검증.
7. [이월] "선택 다운로드" 버튼 실제 동작(다운로드 성공 여부) 여전히 미확인.
8. [이월] 실기기 터미널로 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부 확인(핵심 발견 16).
9. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 삭제/갱신.
10. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
11. [이월] carrot-ms 모델 셀렉터 코드 분석 착수. WIP_SYNC.md 40차 체크포인트 반영 확인 필요.
12. [사용자 승인 필요, 이월] 핵심 발견 31의 재발 방지 제안(스크립트 파일명 버전 표시 규칙화) 채택 여부 결정.
13. [낮은 우선순위, 이월] WIP.md 파일 안 "# WIP" 헤더 중복(1번째 줄과 그 아래 실제로 존재함) 근본 정리 미실시 -- 이번 세션 devnotes 반영 스크립트도 이 중복을 인지해 "# WIP" 문자열을 앵커로 찾지 않고 파일의 실제 첫 줄 다음에 위치 기반으로 새 내용을 삽입하는 방식을 사용함(9절 "정확히 1회 매치" 요구를 우회하기 위함, 핵심 발견 26 참고).

검증: screenshot_capture.py Replace-Block 매치 카운트 1 확인(Python으로 직접 검증), py_compile 통과 예정(스크립트 자체에 포함). **실차 검증: 미실시** -- PNG 롤백 후 실제 저장 성공 여부가 다음 세션 최우선 확인 대상.

주의사항:
- 코드(carrot-ryu)와 devnotes(carrot-ryu-note) 반영 스크립트를 분리해서 전달함 -- 섞어서 실행하지 말 것.
- 이번 변경은 "JPG export가 원인이다"를 확정한 것이 아니라 가설을 검증하기 위한 변수 분리 테스트다(11절). 다음 세션은 결과를 먼저 확인한 뒤 판단할 것 -- PNG도 실패하면 JPG 미지원 가설은 기각되고 완전히 새로운 조사가 필요하다.
- screenshot_capture.py 도크스트링의 "Saved as .jpg (was .png)" 설명 문단은 47차 당시의 결정 배경을 남기기 위해 삭제하지 않고, 그 아래에 50차 롤백 사유를 추가하는 방식으로 처리함(과거 기록 보존).

다음 작업 후보:
1. PNG 롤백 실차 테스트로 JPG export 미지원 가설 확정/기각(최우선)
2. 저장 성공 시 47차 DPI 수정(가로/JPG->PNG 용량) 실차 검증도 함께 처리(이월)
3. 37차 락 동시성 재현 검증(의도적 동시 업로드 2회 시도)
4. 34차 도로명-신호과속 같은 줄 배치 확인(신호과속 구간 실주행 필요)
