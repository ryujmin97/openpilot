# HANDOFF

Worker: Claude (47차 -- 스크린샷 캡처 세로 뒤바뀜/과대용량 원인수정, 코드 작성 완료·push 대기)
Date: 2026-09-16
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: `99b49a113e48ddaeebf83074b04e42d417a88612`, 이번 세션 수정분은 아래 스크립트 실행 대기 -- push 후 다음 세션이 `git ls-remote`로 새 HEAD 확인)
Note Branch: carrot-ryu-note (이 커밋으로 devnotes 갱신. base: `d77dbbcb957477cf8f37261d563a0541a2903491`, 46차)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 체크포인트 이후 신규 23건 확인, WIP_SYNC.md 40차 체크포인트 반영 스크립트 실행 여부 미확인(계속 이월)

작업:
사용자가 온로드 화면의 스크린샷 버튼으로 찍은 사진 예시 2장(정상 예시 vs 실제 저장된 사진)을 제공하며, 실제 저장본이 세로(1080x2160, 상단 대부분 검정)로 나오고 용량도 4배가량 크다고 제보. 코드 조사로 원인을 확정하고 수정.

완료:
1. 원인 확정: `screenshot_capture.py`가 쓰던 `rl.take_screenshot()`은 raylib 내부에서 `render 크기 * GetWindowScaleDPI()`로 캡처 크기를 계산하는데(raylib rcore.c 소스 확인), 이 기기에서 `GetWindowScaleDPI()`가 비등방(가로/세로 배율이 다르게) 나와 가로 2160x세로 1080이어야 할 캡처가 세로 1080x가로 2160으로 뒤바뀌어 저장됨. 제공받은 두 이미지의 실제 픽셀 크기를 직접 확인(정상 예시 2160x1080 vs 실제 저장본 1080x2160)해 가설을 실증.
2. 수정: `rl.load_image_from_screen()`으로 교체. 이 함수는 DPI 배율 곱셈 없이 논리적 `GetScreenWidth()/GetScreenHeight()` 크기로 프레임버퍼를 그대로 읽어 위 버그의 영향을 받지 않음 -- 영상 녹화 파이프라인(`GuiApplication.render()`)이 `rl.load_image_from_texture()`로 동일하게 "DPI 배율 계산 없이 프레임버퍼 직접 읽기" 방식을 이미 쓰고 있고 실기기에서 정상 동작이 검증돼 있어(46차), 같은 원리를 재사용.
3. 저장 포맷을 PNG(무손실)에서 JPG로 전환(raylib `ExportImage`는 파일 확장자 기준으로 포맷을 정함, quality=90 내부 고정). `SCREEN_RECORDING_PHOTO_EXTS`(carrot/server/config.py)에 `.jpg`/`.jpeg`가 이미 `.png`와 함께 등록돼 있고, 사진 목록/썸네일/서빙(mimetypes.guess_type 기반) 로직 어디에도 `.png` 전용 하드코딩이 없음을 코드 조사로 확인 -- 백엔드/프론트엔드 추가 수정 없이 바로 인식됨.
4. `py_compile`로 새 `screenshot_capture.py` 구문 검증 통과. 이 sandbox에 raylib(pyray) pip 패키지를 별도 설치해 `rl.export_image(image, "*.jpg")`가 실제로 JPG 파일을 정상 생성함을 headless 모드로 확인(파일 존재/용량 확인, GUI 렌더 자체는 sandbox에 디스플레이가 없어 검증 범위 밖).
5. carrot-ryu 반영 스크립트 작성(파일 전체가 작아 Replace-Block 대신 전면 교체 방식) + carrot-ryu-note devnotes(WIP.md/FINDINGS.md 추가, CURRENT_STATUS.md/HANDOFF.md 전체 교체) 반영 스크립트 작성. 둘 다 실행 대기.

미완료 (다음 세션 이월):
1. [최우선, 신규] carrot-ryu 스크립트 실행 결과 확인 -- `git ls-remote`로 새 HEAD 확보, raw 조회(SHA 고정)로 `screenshot_capture.py` 실제 내용 재확인.
2. [최우선, 신규] 실차 검증(12절, 아직 전혀 안 됨): 스크린샷 버튼을 눌러 저장된 사진이 (a) 가로 2160x1080으로 정상 캡처되는지, (b) 검정 여백 없이 실제 온로드 화면 그대로 나오는지, (c) 파일 용량이 줄었는지, (d) 로그탭 사진 목록에 `.jpg` 파일이 정상적으로 뜨고 썸네일/다운로드/전송이 동작하는지 확인 필요.
3. [이월, 37차] 락 수정의 실제 동시성 재현 검증(의도적으로 거의 동시에 두 업로드 시도).
4. [이월, 34차] 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
5. [이월] 28~30차 레이아웃 정밀 재검증.
6. [이월] 46차까지 확인된 항목을 제외한 나머지 코드 변경 전체 실차 재검증(12절 원칙).
7. [이월] 실기기 터미널로 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부 확인(핵심 발견 16).
8. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개(tmux_web_target/resolve_upload_target/upload_target_settings) + 대응 테스트 삭제/갱신.
9. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
10. [이월] carrot-ms 모델 셀렉터 코드 분석 착수. WIP_SYNC.md 40차 체크포인트 반영 확인 필요.
11. [사용자 승인 필요, 이월] 핵심 발견 31의 재발 방지 제안(스크립트 파일명 버전 표시 규칙화) 채택 여부 결정.
12. [낮은 우선순위, 이월] WIP.md 파일 안 "# WIP" 헤더 중복(45차-정정에서 생긴 것으로 추정) 근본 정리 미실시.

검증: 정적 분석(raylib 소스 구조 확인, 제공받은 두 이미지의 실제 픽셀 크기 비교) + `py_compile` + sandbox 내 headless pyray로 `export_image`의 JPG 저장 동작만 확인. 실기기에서 스크린샷 버튼을 눌러본 검증은 아직 없음(위 미완료 2번).

주의사항:
- `screenshot_capture.py`는 파일 크기가 작아(40줄 내외) 9절의 "코드 파일 -- 신규/전면 재작성" 방식(전체 내용 교체)으로 반영. Replace-Block 앵커 매칭이 아니므로 별도 "1회 매치" 확인은 해당 없음.
- 이번 수정으로 새로 저장되는 스크린샷 파일 확장자가 `.png`에서 `.jpg`로 바뀐다. 기존에 이미 저장돼 있던 `.png` 파일들은 그대로 남아있고(삭제/변환 안 함), 사진 목록에는 `.png`/`.jpg` 둘 다 계속 뜬다(`SCREEN_RECORDING_PHOTO_EXTS`가 둘 다 포함).

다음 작업 후보:
1. carrot-ryu 스크립트 실행 + 실차로 스크린샷 버튼 눌러 결과 확인(최우선)
2. 34차 도로명-신호과속 같은 줄 배치 확인(신호과속 구간 실주행 필요)
3. 37차 락 동시성 재현 검증(의도적 동시 업로드 2회 시도)
4. WIP.md 헤더 중복 정리(낮은 우선순위)
5. test_web_upload.py 실행 + 데드코드 3개 삭제 착수
