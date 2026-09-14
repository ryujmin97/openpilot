# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 베이스 브랜치: carrot-ms (happymaj11r/openpilot). ryujmin97/openpilot에는 carrot-ms/carrot-wip을 미러링하지 않음(7차 세션에서 삭제 완료)
- carrot-ryu HEAD: a7a912c1 (24차 스크린샷 사진 스트립, GitHub push 완료 확인 -- api.github.com/raw.githubusercontent.com으로 직접 재조회). 23차 Google Drive 연결 UI(272834b) 다음 커밋.
- carrot-ryu HEAD 근처에 "token test"라는 내용 없는 빈 커밋(2c33603, 10차 위)이 있음(사용자의 git 인증 테스트로 추정, 코드/devnotes 영향 없음)
- carrot-ms 동기화 상태: 6차 세션 이후 신규 커밋(rebase) 없음 확인(7차). 8차~24차 세션에서는 동기화 재점검 없음
- 참고: carrot-wip(ajouatom/openpilot)은 계속 진행 중이나, carrot-ms가 아직 rebase하지 않아 직접 비교 대상 아님
- PROJECT_INSTRUCTIONS_carrot-ryu.md는 22차 버전(4절 0번 단계 보고 의무화)이 최신. 이 세션 중 다른 경로(작성자 "Ryu <ryu@example.com>")로 실수로 9차 구버전에 덮어써졌다가(commit 7d44f2f), 같은 작성자가 직접 22차(98fad93) 상태로 복구함(commit c7b86a0). 현재 정상.

## 코드 수정 현황 (실차 재검증 전부 미실시)
1. route 감속 오검출 근본수정(9차, 2dbe492) -- GitHub 반영됨
2. RES/+ 인게이지 속도 안전장치(10차, e1e587b) -- GitHub 반영됨
3. 온로드 시계 초단위 표시 + 스크린샷 버튼(12차, 684b30d) -- GitHub 반영됨
4. 온로드 시계 좌측 화면 경계 잘림 수정(13차, 2adced8) -- GitHub 반영됨
5. gdrive_upload.py 신규 추가(15차, 183bef9) -- Drive OAuth device flow + resumable 업로드 백엔드, GitHub 반영됨
6. 대시캠 업로드(로그탭 "전송") zip+Drive 전환(16차, dae901c 본편 + cc734e1 hotfix) -- GitHub 반영됨
7. send_tmux_web() Drive 업로드 전환(17차, commit 2869149) -- GitHub 반영됨
8. dashcam 업로드 연결 테스트 버튼(api_dashcam_upload_test)을 Google Drive 기준으로 전환(18~20차, commit ad055dd4) -- GitHub 반영됨
9. params_keys.h에 CarrotGDriveClientId/Secret/RefreshToken 등록(22차, commit 48c2e081) -- GitHub 반영됨
10. web settings log_upload에 Google Drive 계정 연결 UI 추가(23차, commit 272834b) -- GitHub 반영됨. 단, 사용자 실기기에서 Client ID/Secret 입력란이 보이지 않는 문제 보고됨 -- 24차 계속2에서 조사, 렌더링 로직 자체는 정상 확인(시뮬레이션), 대신 백엔드 LOG_UPLOAD_TARGETS에 "gdrive" 누락 버그 발견(미수정, 승인 대기). 입력란 미노출은 스크롤 가설이 유력(미검증). 상세: FINDINGS.md 참고
11. 화면녹화 탭 스크린샷(.png) "사진" 스트립 추가(24차, commit a7a912c1) -- GitHub 반영됨 (raw.githubusercontent.com으로 신규 파일 존재 직접 확인)

## 핵심 발견 1~8 (12차까지, 요약)
1. 현대기아/제네시스 종방향 PID 게인 코드 고정(LongTuningKpV/KiV/Kf 무시)
2. (안전, 확인 필요) DisableDM=2는 DM 끄고 Carrot Vision WebRTC 원격 스트리밍 켬
3. LateralTorqueCustom=0이라 opendbc 실측 기본값 사용 중
4. (안전, 확인 필요) route 기반 커브 감속 실제 켜짐(TurnSpeedControlMode=2)
5. T_FOLLOW/traffic_stop/curve_speed 체인 모두 MPC까지 연결됨
6. (8~9차) route 감속 고속도로 분기점 오검출 median 필터로 근본수정(2dbe492), 실차 재검증 대기
7. (10차) 출발 가속 중 +RES 인게이지 급감속 -> 안전장치 추가, 정확한 트리거 조건 미확인
8. (12차) 스크린샷 backend/frontend(kind 구분) 변경 -- 24차에서 실제 구현 완료(GitHub 반영 확인)

## 핵심 발견 9 (13차)
온로드 좌측 상단 시계가 HH:MM:SS(8자, font_size=100)로 center_bottom 정렬되며 고정 x(rect.x+170) 기준으로는 텍스트 절반 폭이 화면 좌측 경계를 넘어가 첫 글자가 잘리는 버그. 12차 초 단위 표시 추가로 발생한 회귀로 추정. 텍스트 실측 폭 기반 x 보정으로 수정.

## 핵심 발견 10 (15~23차) -- 대시캠/tmux 업로드 및 연결 테스트를 Carrot/Toss에서 Google Drive로 전환
- 배경: 기존 Carrot/Toss 업로드 서버(shind0.synology.me, op.wjcloud.kr)를 사용자 개인 Google Drive로 대체하기로 결정.
- gdrive_upload.py: OAuth2 Device Authorization Grant(브라우저 없는 콤마 기기에서 폰/PC로 인증 코드 입력) + resumable 업로드(8MB 청크, multipart 5MB 제한 회피). 고정 DRIVE_FOLDER_ID 사용(폴더 자동생성 안 함).
- 대시캠 업로드(16차): 세그먼트 파일들을 zip(ZIP_STORED)으로 묶어 단일 업로드.
- tmux 진단 업로드(17차): tmux.log+toggle_values.json+metadata.json을 zip(ZIP_DEFLATED)으로 묶어 동일 업로드 함수 재사용.
- 연결 테스트 버튼(18~20차): api_dashcam_upload_test가 gdrive_upload.test_connection()을 호출.
- 파라미터 등록 버그 수정(22차): params_keys.h에 3종 등록, 15~20차 백엔드가 실제로는 한 번도 정상 동작할 수 없었던 상태였음을 수정.
- 프론트엔드 연결 UI(23차): web_settings에 Drive 연결 버튼/Client ID·Secret 입력/인증 코드 표시 UI 추가(commit 272834b). 사용자 실기기에서 드롭다운은 바뀌었으나 입력란이 안 보이는 문제 보고 -- 원인 미확정(브라우저 캐시 가설, 미검증).
- 미완료: docs/carrot_web_upload.md 미갱신, 실제 Drive 계정 업로드 테스트/실차 검증 전부 미실시, 입력란 미노출 원인 조사.

## 핵심 발견 11 (17~20차) -- diff(git apply) 방식의 실전 한계, 결국 예외적 보조로 격하
17~18차에서 diff/git apply가 두 차례 실전 문제(corrupt patch, 조용한 미반영)를 일으켜 19~20차에 문자열 블록 치환(Replace-Block, 치환 전 블록 정확히 1회 매치 검증)으로 전환. 22, 24차에서도 동일 방식으로 정상 반영/검증 확인.

## 핵심 발견 12 (22차) -- Google Drive 연동 파라미터 3종이 params_keys.h에 미등록되어 실전에서 항상 실패했을 버그
gdrive_upload.py(15차)가 사용하는 CarrotGDriveClientId/Secret/RefreshToken이 params_keys.h에 미등록되어 Drive "연결" 버튼을 누르는 순간부터 항상 UnknownKeyName -> HTTP 500으로 실패했음. 22차에서 수정(commit 48c2e081). 상세: FINDINGS.md 2026-09-14 항목.

## 핵심 발견 13 (24차) -- devnotes 기록 누락과 미반영 작업을 "이어서 진행" 요청 시 구분해야 함
23차는 코드가 실제 GitHub에 반영되어 있었지만 devnotes만 누락된 경우였고, 24차는 처음에는(세션 시작 시점) devnotes/스크립트까지 다 준비됐지만 실제 GitHub에는 전혀 반영되지 않은 경우였다가, 세션 도중 사용자가 스크립트를 실행해 실제로 반영 완료됨(commit a7a912c1, GitHub API로 직접 재확인). "GitHub의 현재 상태를 먼저 직접 확인"(3절/16절)하지 않으면 두 상태를 구분할 수 없다는 것이 이번 세션에서 실증됨.

## 핵심 발견 14 (24차 계속2) -- Google Drive 연결 UI 입력란 미노출: 백엔드 LOG_UPLOAD_TARGETS에 "gdrive" 누락
23차에서 프론트엔드 드롭다운에만 value="gdrive" 옵션을 추가하고 server/services/web_settings.py의 LOG_UPLOAD_TARGETS = {"carrot", "toss"}는 갱신하지 않아, "gdrive" 선택이 백엔드에서 유효하지 않은 enum 값으로 취급됨. Client ID/Secret 입력란(web-gdrive-connect 컴포넌트) 자체의 렌더링 로직은 Node.js 시뮬레이션으로 정상 확인됨 -- 실기기에서 안 보인다는 증상은 렌더링 버그가 아니라 스크롤(.web-settings-group__body{overflow:auto}) 때문일 가능성이 유력(미검증). LOG_UPLOAD_TARGETS 수정은 사용자 승인 대기 중, 아직 미적용. 상세: FINDINGS.md 2026-09-14 항목.

- 미확인: carrot-ms 모델 셀렉터 코드 미분석
- 다음 작업: LOG_UPLOAD_TARGETS "gdrive" 추가(승인 대기, FINDINGS.md 참고), 실기기 스크롤 확인, 실제 Drive 연결 테스트(사용자 액션 필요), docs 갱신, 코드 수정 11건 전부 실주행 재검증, 모델 셀렉터 코드 분석
- 보류 확인 항목: TurnSpeedControlMode=2 / EnableSpeedTF=0 / LeadAccelResponse=0 / DisableDM=2 / LateralTorqueCustom=0 / AutoRoadSpeedLimitOffset / SpeedFromPCM