# HANDOFF

Worker: Claude (40차 계속 -- 경로안내 박스 상하 여백 실기기 검증)
Date: 2026-09-15
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: bdde8326, 39차-fix formatRelativeEpoch import 반영 확인 완료, 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음(이번 세션에서도 재확인하지 않음)

작업:
직전 40차에서 만든 `fix_carrot_ryu_39cha.ps1`가 실제로 실행되어 carrot-ryu HEAD가 `bdde8326`(39cha-fix 커밋)으로 갱신됐음을 `git ls-remote` + commit patch 직접 조회로 확인. 이어서 사용자가 실기기 스크린샷(제네시스 DH 2015, 20:14:25 캡처)을 제공해, 27차 이후 계속 이월되던 "우측하단 경로안내 박스 상하 여백" 실기기 확인을 처음으로 완료.

완료:
- carrot-ryu push 검증: `git ls-remote`로 HEAD가 `bdde832654a6...`임을 확인, `github.com/.../commit/bdde8326....patch`로 커밋 메시지("39cha-fix: import missing formatRelativeEpoch in screenshots.js") 및 변경 파일(screenshots.js/logs.js/asset-manifest.json) 직접 확인.
- carrot-ryu-note push 검증: HEAD가 `ba4bbb91...`, 커밋 메시지("40cha devnotes: root-cause + fix for 39cha screenshot upload UI crash")로 devnotes 갱신 확인.
- 실차 검증(12절): 사용자 제공 스크린샷에서 경로안내 박스가 "교차로"(제목) → 회전아이콘/895m → "도착: 286.1km" → "193.6분(23:28)" → "용산2로" 순서로 정상 표시되고, 34차 `content_shift_y=20` 적용 이후 상단/하단 여백이 균등해 보임을 확인. 27차·34차 이후 이 항목이 실기기에서 확인된 것은 이번이 처음.

미완료 (다음 세션 이월):
1. [이월, 최우선] 사진 업로드 UI(체크박스/전체선택/다운로드/전송)가 `bdde8326` 반영 후 에러 없이 정상 렌더링되는지 실기기 재확인 필요(39cha-fix가 실제로 크래시를 해소했는지는 아직 스크린샷으로 확인 안 됨).
2. [이월] 화면녹화 탭 "영상" 업로드 UI(36차 구현분) 자체 동작 검증 -- 실제 화면녹화 파일 확보 후 재검증 필요.
3. [이월] 37차 락 수정의 실제 동시성(거의 동시 호출) 재현 검증.
4. [이월] 34차 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
5. [이월] 28~30차 레이아웃 정밀 재검증(육안 확인만 완료).
6. [이월] 실차 재검증(8~40차 코드 변경 전부, 12절 원칙) -- 계속 이월.
7. [이월] 실기기에서 직접 디버깅: 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부.
8. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 + 대응 테스트 삭제/갱신.
9. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
10. [이월] run_upload_segments() 설계 변경 실사용 문제 없는지 재확인.
11. [이월] carrot-ms 모델 셀렉터 코드 분석 착수(6차 이후 계속 미착수).

검증: 두 브랜치 push 모두 `git ls-remote`(API rate limit 우회) + `commit/<sha>.patch` 엔드포인트로 커밋 메시지·변경 파일을 직접 재조회해 확인(16절). 경로안내 박스 여백은 이번에 처음으로 정적 분석이 아닌 실기기 스크린샷으로 검증됨(12절). 사진 업로드 UI 자체의 실제 정상 동작은 아직 미검증.

주의사항:
- raw.githubusercontent.com은 push 직후 브랜치-head URL이 한동안 이전 내용을 반환할 수 있음(33차, 38차 재현). 이번 세션은 이 문제를 피하기 위해 commit-pinned patch 엔드포인트(`/commit/<sha>.patch`)와 `git ls-remote`를 사용함 -- 이 방식이 API rate limit에도 걸리지 않아 앞으로 기본으로 권장.
- api.github.com REST 엔드포인트는 비인증 요청 시 rate limit에 쉽게 걸림(이번 세션에서 실제 발생) -- 커밋 확인이 필요하면 REST API보다 `git ls-remote`(해시 확인) + `/commit/<sha>.patch`(내용 확인) 조합을 우선 사용할 것.
- 사진 업로드 UI(39cha-fix 대상)는 여전히 실기기 미검증 상태 -- 다음 세션 최우선.

다음 작업 후보:
1. 사진 업로드 UI(39cha-fix) 실기기 검증 (최우선)
2. 화면녹화 탭 "영상" 업로드 UI(36차) 실기기 검증(녹화본 확보 후)
3. 37차 락 수정 동시성 재현 검증
4. 34차 도로명-신호과속 같은 줄 배치 확인
5. test_web_upload.py 실행 + 데드코드 정리
6. carrot-ms 모델 셀렉터 코드 분석 착수