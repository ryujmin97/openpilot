# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 베이스 브랜치: carrot-ms (happymaj11r/openpilot). ryujmin97/openpilot에는 carrot-ms/carrot-wip을 미러링하지 않음(7차 세션에서 삭제 완료)
- carrot-ryu HEAD: d338afb7 (25차 LOG_UPLOAD_TARGETS "gdrive" 누락 수정, 변경 없음 유지). 26차는 코드 변경 없이 조사만 진행.
- carrot-ryu HEAD 근처에 "token test"라는 내용 없는 빈 커밋(2c33603, 10차 위)이 있음(사용자의 git 인증 테스트로 추정, 코드/devnotes 영향 없음)
- carrot-ms 동기화 상태: 6차 세션 이후 신규 커밋(rebase) 없음 확인(7차). 8차~26차 세션에서는 동기화 재점검 없음
- 참고: carrot-wip(ajouatom/openpilot)은 계속 진행 중이나, carrot-ms가 아직 rebase하지 않아 직접 비교 대상 아님
- PROJECT_INSTRUCTIONS_carrot-ryu.md는 22차 버전(4절 0번 단계 보고 의무화)이 최신. 26차에서도 이 문서를 최우선 조회함.

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
10. web settings log_upload에 Google Drive 계정 연결 UI 추가(23차, commit 272834b) -- GitHub 반영됨. 실기기에서 Client ID/Secret 입력란이 계속 안 보이는 문제 진행 중(26차까지 원인 미확정, 아래 핵심 발견 16 참고).
11. 화면녹화 탭 스크린샷(.png) "사진" 스트립 추가(24차, commit a7a912c1) -- GitHub 반영됨
12. LOG_UPLOAD_TARGETS "gdrive" 누락 수정(25차, commit d338afb7) -- GitHub 반영됨

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
- 프론트엔드 연결 UI(23차): web_settings에 Drive 연결 버튼/Client ID·Secret 입력/인증 코드 표시 UI 추가(commit 272834b). 실기기에서 드롭다운은 바뀌었으나 입력란이 안 보이는 문제 계속 진행 중(26차, 아래 핵심 발견 16).
- 미완료: docs/carrot_web_upload.md 미갱신, 실제 Drive 계정 업로드 테스트/실차 검증 전부 미실시, 입력란 미노출 원인 조사(진행 중), 화면녹화 전송 다이얼로그 라벨 불일치 조사(26차 신규 발견, 미착수).

## 핵심 발견 11 (17~20차) -- diff(git apply) 방식의 실전 한계, 결국 예외적 보조로 격하
17~18차에서 diff/git apply가 두 차례 실전 문제(corrupt patch, 조용한 미반영)를 일으켜 19~20차에 문자열 블록 치환(Replace-Block, 치환 전 블록 정확히 1회 매치 검증)으로 전환. 22, 24, 25차에서도 동일 방식으로 정상 반영/검증 확인.

## 핵심 발견 12 (22차) -- Google Drive 연동 파라미터 3종이 params_keys.h에 미등록되어 실전에서 항상 실패했을 버그
gdrive_upload.py(15차)가 사용하는 CarrotGDriveClientId/Secret/RefreshToken이 params_keys.h에 미등록되어 Drive "연결" 버튼을 누르는 순간부터 항상 UnknownKeyName -> HTTP 500으로 실패했음. 22차에서 수정(commit 48c2e081). 상세: FINDINGS.md 2026-09-14(22차) 항목.

## 핵심 발견 13 (24차) -- devnotes 기록 누락과 미반영 작업을 "이어서 진행" 요청 시 구분해야 함
23차는 코드가 실제 GitHub에 반영되어 있었지만 devnotes만 누락된 경우였고, 24차는 세션 도중 사용자가 스크립트를 실행해 실제로 반영 완료됨(commit a7a912c1). "GitHub의 현재 상태를 먼저 직접 확인"(3절/16절)하지 않으면 두 상태를 구분할 수 없다는 것이 실증됨.

## 핵심 발견 14 (24차 계속2) -- Google Drive 연결 UI 입력란 미노출: 백엔드 LOG_UPLOAD_TARGETS에 "gdrive" 누락
23차에서 프론트엔드 드롭다운에만 value="gdrive" 옵션을 추가하고 server/services/web_settings.py의 LOG_UPLOAD_TARGETS = {"carrot", "toss"}는 갱신하지 않아, "gdrive" 선택이 백엔드에서 유효하지 않은 enum 값으로 취급됨. 25차에서 수정 완료(commit d338afb7). 다만 이 수정 이후에도(26차 실기기 검증) 입력란 미노출 현상은 그대로 재현됨 -> LOG_UPLOAD_TARGETS는 원인이 아니었거나, 원인 중 일부만 해결한 것으로 보임(아래 핵심 발견 16).

## 핵심 발견 15 (25차) -- web_upload.py/dashcam upload.py 데드코드 3개 + test_web_upload.py 낡은 테스트 의심
web_upload.py의 tmux_web_target()과 dashcam/upload.py의 resolve_upload_target()/upload_target_settings()는 프로덕션 호출자가 없는 진짜 죽은 코드로 확인됨(단, UPLOAD_TARGETS/selected_upload_settings() 자체는 _tmux_toss_only()가 실사용 중이라 삭제 대상 아님). test_web_upload.py의 한 테스트가 16차에 이미 제거된 코드를 monkeypatch하고 있어 낡은 테스트일 가능성 높음(직접 실행 검증은 못함). 데드코드 삭제가 예상보다 큰 작업으로 번질 수 있어 25차에서는 보류, 이월.

## 핵심 발견 16 (26차) -- Google Drive 연결 UI 미노출: 정적 코드 리뷰와 실기기 스크린샷이 모순됨(원인 미확정)
25차에서 LOG_UPLOAD_TARGETS 백엔드 버그를 고쳤음에도, 실기기 스크린샷(2026-09-14 14:47~18:41)에서는 여전히 Client ID/Secret 입력란이 안 보이고 당근서버/토스서버 주소 입력란이 보임(업로드 서버가 구글드라이브로 선택된 상태에서). carrot-ryu 최신(d338afb7) 소스를 직접 받아 정적 코드 리뷰한 결과, schema.js/components.js/tools.js(esbuild 번들)/tools.css 모두 web-gdrive-connect가 정상 등록·렌더되고, web-upload의 carrot/toss 필드는 target이 gdrive면 반드시 숨겨지도록 구현돼 있어 이론상 현재 스크린샷과 같은 현상이 나올 수 없음. 즉 코드 자체에서는 원인을 못 찾음 -> 실기기가 최신 tools.js/tools.css 번들을 실제로 서빙/로드하고 있는지 의심(브라우저 캐시 또는 esbuild 재생성 누락 가능성). 실기기 디버깅은 사용자 사정으로 다음 세션 이월. 부가로, 화면녹화 전송 다이얼로그가 업로드 서버=gdrive인데도 라벨을 "당근서버"로 표시하는 별도 불일치도 발견(코드 위치 미조사). 상세: FINDINGS.md 2026-09-14(26차) 항목.

- 미확인: carrot-ms 모델 셀렉터 코드 미분석
- 다음 작업: (최우선) 실기기 터미널로 배포된 tools.js 내용 확인해 번들 최신 여부 검증, 화면녹화 전송 다이얼로그 "당근서버" 라벨 하드코딩 조사, test_web_upload.py 실제 실행해 낡은 테스트 범위 확정, 데드코드 3개 삭제 + 대응 테스트 정리, 실제 Drive 연결 테스트(사용자 액션 필요), docs 갱신, 코드 수정 12건 전부 실주행 재검증, 모델 셀렉터 코드 분석
- 보류 확인 항목: TurnSpeedControlMode=2 / EnableSpeedTF=0 / LeadAccelResponse=0 / DisableDM=2 / LateralTorqueCustom=0 / AutoRoadSpeedLimitOffset / SpeedFromPCM