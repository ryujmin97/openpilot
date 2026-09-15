# HANDOFF

Worker: Claude (40차 -- 39차 사진 업로드 UI 실기기 크래시 원인 규명 및 수정)
Date: 2026-09-15
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: 797fca2e, 이번 세션 수정 스크립트 아직 미실행 -- 실행 필요)
Note Branch: carrot-ryu-note (이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음(이번 세션에서도 재확인하지 않음)

작업:
39차에서 반영한 "화면녹화 탭 사진 업로드 UI"를 실기기에 반영한 뒤, 사용자가 "구현안됨"(예전 UI 그대로)이라고 보고. carrot-ryu HEAD/실기기 git 상태를 단계적으로 검증했으나 모두 정상(코드는 정확히 반영됨)이었고, 최종적으로 사용자가 다시 캡처한 화면에서 `formatRelativeEpoch is not defined` 에러 토스트를 확인하며 실제 원인(코드 버그, 반영 문제 아님)을 특정. 원인 수정 후 재빌드/재검증까지 완료.

완료:
- 원인 규명: `screenshots.js`가 `runtime.js`의 `formatRelativeEpoch`를 import하지 않아 사진 행 렌더링 중 ReferenceError 발생 -> 목록이 통째로 비어버림(같은 패턴의 `dashcam.js`/`screenrecord.js`는 정상 import 상태였음, screenshots.js만 39차에서 신규 작성 시 누락).
- 수정: `screenshots.js` import문에 `formatRelativeEpoch` 추가(1줄).
- 재빌드: 별도 shallow clone에서 `npm install` + `node build.mjs` 실행 -> `js/generated/logs.js` 재생성(해시 `19d4d80c...` -> `60a90928...`), `generated/asset-manifest.json` 갱신.
- 검증: `py_compile`(hud_renderer.py, routes.py) 통과, `node --check`(screenshots.js) 통과, `npm test` 737/737 통과.
- carrot-ryu 반영 스크립트(`fix_carrot_ryu_39cha.ps1`) 작성 완료 -- screenshots.js/asset-manifest.json은 anchor 1회 매치 검증 후 치환, logs.js는 전체 교체(esbuild 재빌드로 파일 전역 식별자가 재배정되어 부분치환 불가), UTF-8 BOM 포함, `--config core.autocrlf=false` clone, 임시폴더 자동삭제 포함.

미완료 (다음 세션 이월):
1. [신규, 최우선] **이번 세션이 만든 `fix_carrot_ryu_39cha.ps1`가 아직 실행되지 않음.** 다음 세션 시작 시 4절 3번 단계에서 carrot-ryu 최신 commit이 이 수정 커밋(메시지: "39cha-fix: import missing formatRelativeEpoch...")으로 갱신됐는지 반드시 확인할 것(16절).
2. [신규] 스크립트 실행 및 디바이스 재반영 후, 사진 업로드 UI(체크박스/전체선택/다운로드/전송)가 에러 없이 정상 렌더링되는지 실기기 재확인 필요.
3. [이월] 39차 사진 업로드 UI 실기기 검증 -- 위 수정 반영 후 체크박스 선택/전체선택/개별 및 선택 다운로드/전송이 실제 온로드 캡쳐 사진 파일로 정상 동작하는지 확인 필요.
4. [이월] 39차 경로안내 박스 여백 실기기 재확인 -- `content_shift_y = 20`으로 상하 여백이 실제로 균등해졌는지 스크린샷으로 확인, 필요 시 값 조정.
5. [이월] 화면녹화 탭 "영상" 업로드 UI(36차 구현분) 자체 동작 검증 -- 실제 화면녹화 파일 확보 후 재검증 필요.
6. [이월] 37차 락 수정의 실제 동시성(거의 동시 호출) 재현 검증.
7. [이월] 34차 도로명-신호과속 같은 줄 배치 확인.
8. [이월] 28~30차 레이아웃 정밀 재검증(육안 확인만 완료).
9. [이월] 실차 재검증(8~40차 코드 변경 전부, 12절 원칙) -- 계속 이월.
10. [이월] 실기기에서 직접 디버깅: 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부.
11. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 + 대응 테스트 삭제/갱신.
12. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
13. [이월] run_upload_segments() 설계 변경 실사용 문제 없는지 재확인.
14. [이월] carrot-ms 모델 셀렉터 코드 분석 착수(6차 이후 계속 미착수).

검증: py_compile/node --check/build/test(737/737) 전부 이번 세션에서 독립적으로 재실행해 통과 확인. 단, 이 스크립트가 실제로 실기기에 반영되어 에러가 사라지는지는 미실시(12절 원칙) -- 다음 세션/사용자 실행 이후 확인 필요.

주의사항:
- raw.githubusercontent.com은 push 직후 브랜치-head URL이 한동안 이전 내용을 반환할 수 있음(33차, 38차 재현). 다음 세션은 push 직후 devnotes/코드 재확인 시 commit-pinned raw URL(`/{sha}/...`) 또는 commit diff 엔드포인트를 우선 사용할 것.
- 이번 사례로 확인된 점: "화면이 예전 그대로다"류 실기기 보고는 (1) git 반영 상태 확인과 (2) 실제 브라우저 에러 화면 확인을 모두 거쳐야 진짜 원인을 알 수 있음 -- git 상태가 완벽히 정상이어도 코드 자체의 런타임 버그일 수 있음.
- `fix_carrot_ryu_39cha.ps1`가 실행되기 전까지 carrot-ryu의 `screenshots.js`/`logs.js`/`asset-manifest.json`은 여전히 39차의 버그 있는 상태임 -- 사용자가 스크립트를 실행하지 않았다면 실기기 문제도 그대로 재현될 것.

다음 작업 후보:
1. fix_carrot_ryu_39cha.ps1 실행 확인 (최우선)
2. 39차 사진 업로드 UI + 경로안내 박스 여백 실기기 검증
3. 화면녹화 탭 "영상" 업로드 UI(36차) 실기기 검증(녹화본 확보 후)
4. 37차 락 수정 동시성 재현 검증
5. 34차 도로명-신호과속 같은 줄 배치 확인
6. test_web_upload.py 실행 + 데드코드 정리
7. carrot-ms 모델 셀렉터 코드 분석 착수
