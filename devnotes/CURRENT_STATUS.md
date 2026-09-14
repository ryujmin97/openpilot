# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 베이스 브랜치: carrot-ms (happymaj11r/openpilot). ryujmin97/openpilot에는 carrot-ms/carrot-wip을 미러링하지 않음(7차 세션에서 삭제 완료)
- carrot-ryu HEAD: ad055dd4 (20차 gdrive_upload.py test_connection() 추가 반영 완료, raw.githubusercontent.com으로 직접 재확인됨)
- carrot-ryu HEAD 근처에 "token test"라는 내용 없는 빈 커밋(2c33603, 10차 위)이 있음(사용자의 git 인증 테스트로 추정, 코드/devnotes 영향 없음)
- carrot-ms 동기화 상태: 6차 세션 이후 신규 커밋(rebase) 없음 확인(7차). 8차~20차 세션에서는 동기화 재점검 없음
- 참고: carrot-wip(ajouatom/openpilot)은 계속 진행 중이나, carrot-ms가 아직 rebase하지 않아 직접 비교 대상 아님
- **[20차]** PROJECT_INSTRUCTIONS_carrot-ryu.md가 12차 버전에서 20차 버전으로 갱신됨(9절 diff -> 문자열 치환 전환). 다음 세션은 이 파일을 GitHub에서 최우선 조회할 것.

## 코드 수정 현황 (실차 재검증 전부 미실시)
1. route 감속 오검출 근본수정(9차, 2dbe492) -- GitHub 반영됨
2. RES/+ 인게이지 속도 안전장치(10차, e1e587b) -- GitHub 반영됨
3. 온로드 시계 초단위 표시 + 스크린샷 버튼(12차, 684b30d) -- GitHub 반영됨
4. 온로드 시계 좌측 화면 경계 잘림 수정(13차, 2adced8) -- GitHub 반영됨
5. gdrive_upload.py 신규 추가(15차, 183bef9) -- Drive OAuth device flow + resumable 업로드 백엔드, GitHub 반영됨
6. 대시캠 업로드(로그탭 "전송") zip+Drive 전환(16차, dae901c 본편 + cc734e1 hotfix) -- GitHub 반영됨
7. send_tmux_web() Drive 업로드 전환(17차, commit 2869149) -- GitHub 반영됨. diff(git apply) 최초 시도 실패 후 문자열 치환 방식으로 재작업하여 성공(WIP.md 17차 회차 참고)
8. dashcam 업로드 연결 테스트 버튼(api_dashcam_upload_test)을 Google Drive 기준으로 전환(18~20차, commit ad055dd4) -- GitHub 반영됨. 반영 과정에서 diff가 조용히 실패(18차)하여 문자열 블록 치환 방식으로 재작업(19~20차, WIP.md 18~20차 회차 참고)

## 핵심 발견 1~8 (12차까지, 요약)
1. 현대기아/제네시스 종방향 PID 게인 코드 고정(LongTuningKpV/KiV/Kf 무시)
2. (안전, 확인 필요) DisableDM=2는 DM 끄고 Carrot Vision WebRTC 원격 스트리밍 켬
3. LateralTorqueCustom=0이라 opendbc 실측 기본값 사용 중
4. (안전, 확인 필요) route 기반 커브 감속 실제 켜짐(TurnSpeedControlMode=2)
5. T_FOLLOW/traffic_stop/curve_speed 체인 모두 MPC까지 연결됨
6. (8~9차) route 감속 고속도로 분기점 오검출 median 필터로 근본수정(2dbe492), 실차 재검증 대기
7. (10차) 출발 가속 중 +RES 인게이지 급감속 -> 안전장치 추가, 정확한 트리거 조건 미확인
8. (12차) 스크린샷 backend/frontend(kind 구분) 변경 아직 미반영

## 핵심 발견 9 (13차)
온로드 좌측 상단 시계가 HH:MM:SS(8자, font_size=100)로 center_bottom 정렬되며 고정 x(rect.x+170) 기준으로는 텍스트 절반 폭이 화면 좌측 경계를 넘어가 첫 글자가 잘리는 버그. 12차 초 단위 표시 추가로 발생한 회귀로 추정. 텍스트 실측 폭 기반 x 보정으로 수정.

## 핵심 발견 10 (15~18차) -- 대시캠/tmux 업로드 및 연결 테스트를 Carrot/Toss에서 Google Drive로 전환
- 배경: 기존 Carrot/Toss 업로드 서버(shind0.synology.me, op.wjcloud.kr)를 사용자 개인 Google Drive로 대체하기로 결정.
- gdrive_upload.py: OAuth2 Device Authorization Grant(브라우저 없는 콤마 기기에서 폰/PC로 인증 코드 입력) + resumable 업로드(8MB 청크, multipart 5MB 제한 회피). 고정 DRIVE_FOLDER_ID 사용(폴더 자동생성 안 함).
- 대시캠 업로드(16차): 세그먼트 파일들을 zip(ZIP_STORED, 이미 압축된 h265/zstd라 무압축)으로 묶어 단일 업로드. 성공/실패 판정이 "세그먼트별" -> "zip 전체" 단위로 바뀜, Discord 알림 항상 시도로 변경(실사용 재확인 필요, HANDOFF 4번).
- tmux 진단 업로드(17차): tmux.log+toggle_values.json+metadata.json을 zip(ZIP_DEFLATED)으로 묶어 동일한 업로드 함수 재사용. send_tmux_carrot_logs()(Discord carrot_logs 포럼용)는 무관하게 유지. GitHub 반영 완료(commit 2869149).
- 연결 테스트 버튼(18~20차): api_dashcam_upload_test가 gdrive_upload.test_connection()을 호출하도록 전환, access_token 갱신 + 폴더 조회 왕복으로 실제 연동 확인. GitHub 반영 완료(commit ad055dd4).
- 미완료: Drive 파라미터 3종(CarrotGDriveClientId/Secret/RefreshToken) PARAMS_REGISTRY.md 미등록, 프론트엔드 연결 UI 미이식, docs/carrot_web_upload.md 미갱신.
- 실제 Google Drive 계정으로의 업로드 테스트, 실차 검증 전부 미실시.

## 핵심 발견 11 (17~20차) -- diff(git apply) 방식의 실전 한계, 결국 예외적 보조로 격하
17차에서 처음으로 diff/git apply 방식을 실전 반영에 시도했으나, 채팅으로 전달된 patch의 컨텍스트 공백 줄이 손상되어 corrupt patch 에러로 실패함(carrot-ryu에는 영향 없이 안전하게 중단됨). 18차에서는 더 나쁜 형태로 재발함: git apply가 스크립트상 에러 없이 "적용 완료"로 보고했으나 실제로는 아무 것도 반영되지 않고, 삭제되어야 할 임시 patch 파일 3개만 carrot-ryu에 잘못 커밋됨(정확한 근본원인은 사용자 PC를 직접 디버깅할 수 없어 확정하지 못했으나 Push-Location/Pop-Location 반복 사용과 연관된 것으로 추정). 19~20차에서 "파일 전체 텍스트에서 블록을 통째로 찾아 .Replace()로 치환, 치환 전 블록이 정확히 1회만 존재하는지 검증 후 치환"하는 방식으로 전환해 성공. 사용자 승인 하에 9절을 개정하여 이 방식을 코드 파일 부분수정의 기본으로, diff는 예외적 보조 수단으로 격하함(19절 절차대로 PROJECT_INSTRUCTIONS_carrot-ryu.md도 함께 갱신, 20차).

- 미확인: carrot-ms 모델 셀렉터 코드 미분석
- 다음 작업: 위 미완료 항목 순차 진행(HANDOFF.md 우선순위 참고), 코드 수정 8건 전부 실주행 재검증, 모델 셀렉터 코드 분석
- 보류 확인 항목: TurnSpeedControlMode=2 / EnableSpeedTF=0 / LeadAccelResponse=0 / DisableDM=2 / LateralTorqueCustom=0 / AutoRoadSpeedLimitOffset / SpeedFromPCM