# HANDOFF

Worker: Claude (세션 15)
Date: 2026-09-14
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (gdrive_upload.py 신규 파일 1개 추가 -- apply_15_gdrive_module.ps1
  실행 결과로 반영 예정/완료. 정확한 새 HEAD 해시는 스크립트 실행 후
  다음 세션이 GitHub에서 확인)
Note Branch: carrot-ryu-note (15차 devnotes 반영, 이 커밋)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋
없음 (WIP_SYNC.md 참고, 15차에서도 재확인하지 않음)

작업:
14차에 이어 Carrotweb 로그탭 "전송" 버튼의 구글드라이브 전환 작업 계속.
이번 세션에서 tmux 진단 전송 중 "carrot/toss 선택 전송" 부분도 Drive로
바꾸기로 범위가 확대됨(단, Discord carrot_logs 포럼용 고정 전송은 제외).

완료:
- carrot-ryu의 `log_upload_target`(carrot/toss) 설정이 (1)대시캠 업로드
  (2)tmux 선택 전송 두 곳에서 공유되고 있다는 구조를 발견 -- 14차에는
  "메인 업로드와 별개 시스템"으로만 파악했던 것을 정정
- 사용자 확인으로 최종 범위 확정:
  - 대시캠 업로드(로그탭 전송) -> Drive
  - tmux 선택 전송(`send_tmux_web`) -> Drive
  - tmux carrot_logs 고정 전송(`send_tmux_carrot_logs`, Discord 포럼용)
    -> 그대로 유지 (안 건드림)
  - `log_upload_target`/`LOG_UPLOAD_TARGETS`(web_settings.py) 스키마 자체는
    무수정 (carrot_logs의 toss-only 스킵 판단에 계속 쓰이므로)
- 신규 모듈 `openpilot/selfdrive/carrot/gdrive_upload.py` 작성 완료
  (c3-ms-dev의 gdrive.py 기반, 폴더 ID 고정 + drive 전체 스코프,
  OAuth Device Flow + resumable 8MB 청크 업로드 + job 진행률 추적).
  Claude 샌드박스 py_compile 통과 확인
- 반영 스크립트 2개 준비: `apply_15_gdrive_module.ps1`(carrot-ryu에
  신규 파일 추가), 이 HANDOFF를 포함한 devnotes 스크립트(carrot-ryu-note)

미완료 / 다음 세션 우선순위:
1. **아직 아무것도 gdrive_upload.py를 호출하지 않음** -- 다음 세션에서
   실제 연결 필요:
   a. `server/features/dashcam/upload_jobs.py`의 `run_upload_segments()`
      재작성: 세그먼트(들)를 zip으로 압축 -> `gdrive_upload.upload_file_resumable()`
      호출로 교체 (기존 `upload_folder_to_web`/`create_web_upload_session`/
      `send_web_upload_complete` 호출부 제거)
   b. `carrot_man.py`의 `send_tmux_web()` 재작성: `selected_upload_settings()`
      기반 carrot/toss 분기 제거하고 tmux.log를 `gdrive_upload.upload_file_resumable()`
      로 직접 전송하도록 교체. `send_tmux_carrot_logs()`는 손대지 않음
   c. 메인 aiohttp 앱 어딘가에 `gdrive_upload.register(app)` 호출 추가
      (현재 routes.py의 `register(app)`과 같은 자리에 나란히 등록하는
      방식 검토 -- 앱 진입점 파일 위치 아직 미확인)
2. `send_discord_webhook`(대시캠 업로드 완료시 Discord 알림, `target["kind"]=="carrot"`
   일 때만 동작)은 대시캠 target이 더 이상 "carrot"이 아니게 되면 자동으로
   스킵됨 -- 별도 코드 수정 없이 자연스럽게 비활성화되는지 다음 세션에서
   재확인
3. 프론트엔드 이식: `web/src/features/logs/`의 upload_progress.js,
   upload_summary.js, dashcam.js에 Drive 연결 버튼/Client ID·Secret
   입력/인증 코드 표시 UI 추가 (c3-ms-dev의 logs.js UI 참고)
4. devnotes/PARAMS_REGISTRY.md에 신규 파라미터 3개 등록:
   CarrotGDriveClientId, CarrotGDriveClientSecret, CarrotGDriveRefreshToken
5. `docs/carrot_web_upload.md` 갱신 (Drive 기준으로, tmux 선택 전송도
   Drive로 바뀐 것 반영)
6. c3-ms-dev 원격 브랜치의 gdrive.py가 실제로 "폴더 ID 고정" 수정판인지
   재확인 필요(14차 기록과 달리 이번에 다시 받아보니 원본 상태였음 --
   carrot-ryu 포팅 자체에는 영향 없어 우선순위 낮음)
7. 실주행 재검증 여전히 미실시 (13차 시계 잘림 수정 + 12차 스크린샷
   버튼/시계 초단위 + 8~10차 route 감속/RES 인게이지 모두 실차 미검증
   -- 계속 이월)
8. 13차/14차/15차 반영이 실제로 GitHub에 push 됐는지 다음 세션 시작 시
   GitHub API로 재확인 필요

검증: 이번 세션은 설계 + 신규 모듈 작성 + py_compile까지만 진행.
`gdrive_upload.py`는 아직 어디서도 호출되지 않아 기능적으로는 아직
"연결 전" 상태. 실차 검증 해당 없음.

주의사항:
- **`log_upload_target` 설정의 이중 용도**: 이 값을 나중에 다시 만지게
  되면(예: enum에서 carrot/toss 제거) `_tmux_toss_only()`의 "Toss 전용
  스킵" 판단 로직이 깨질 수 있음 -- 반드시 `carrot_man.py`의
  `_tmux_toss_only()`/`send_tmux_carrot_logs()`를 함께 확인할 것
- **`gdrive_upload.py`는 아직 미연결 상태**: 이 파일만 반영해도 기존
  동작(Carrot/Toss 업로드, tmux 전송)에는 전혀 영향 없음(아무도 안
  부르는 새 파일이라 안전) -- 다음 세션에서 연결 작업 시작 시 비로소
  실제 동작이 바뀜
- c3-ms-dev 브랜치는 계속 "검토/포팅 참고용"으로만 취급하고, 실제 반영
  대상은 항상 carrot-ryu임(4차 세션 확인 사항 유지)
- 이번 세션은 PC(Windows, PowerShell)로 진행

다음 작업 후보:
1. upload_jobs.py의 run_upload_segments() zip+Drive 재작성
2. carrot_man.py의 send_tmux_web() Drive 재작성 (send_tmux_carrot_logs는 유지)
3. gdrive_upload.register(app) 앱 진입점에 연결
4. 프론트엔드(Drive 연결 UI) 이식
5. PARAMS_REGISTRY.md / docs/carrot_web_upload.md 갱신