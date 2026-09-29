# WIP SYNC

## 체크포인트: 2026-09-29 (217차) -- DM2 계열 8건 보류 -> 제외 확정 (사용자 결정, 코드 변경 없음, carrot-ms 점검 없음)

- 결정: 사용자가 "DM2는 반영하지 않음. 제외 확정. 현행 유지"라고 결정했다(217cha). 201차 3번에서 보류로 둔 DM2(실험적 운전자 모니터링) 계열 8건(`e7b9eb1`, `13eca74`, `6262570`, `7171d42`, `2326be2`, `7bd44b5`, `847d81f`, `c771c4e`)을 제외로 확정한다. 208차에 제외한 후속 4건(`c36f6e7`, `44d2707`, `2beefa3`, `8472d35`)과 같은 결정이다.
- 사유: 사용자 결정이다. 사용자가 별도 사유를 덧붙이지는 않았다. 201차 보류 당시 기록된 근거(carrot-ryu에 `dm2.py`/`dm2d.py`/`dm2_context.py`/`steering_touch.py`가 없고, `e7b9eb1`이 기능 전체를 새로 들이고 나머지 7건이 그 위의 수정이라 일부만 반영할 수 없으며, 반영하면 운전자 모니터링 경고/잠금 동작이 바뀌는 안전 관련 변경)는 그대로다.
- 재검토 조건이던 "사용자가 DM2 도입을 결정할 때"는 폐기하지 않고 남긴다(사용자가 나중에 뒤집을 수 있음). 이 결정은 위 12건에 대한 것이다. 이후 새로 들어오는 DM2 관련 커밋은 2절 7번대로 개별 확인해 판정한다.
- 이 결정과 무관하게 그대로인 것: `f992f9c`(LFS 일반 blob 전환, 194차) 보류 유지, `fc7ee88`(UI 코어 배치) 제외 유지, `4770067`(부팅 실패 자동 Git 복구)은 201차 제외(재검토 조건 그대로, HANDOFF 미완료 12번). 마지막 검토 체크포인트는 8472d35 그대로이고 다음 점검은 그 이후 신규 커밋부터다.
- 실차 검증: 미실시(12절, 해당 없음: 코드 변경 없음).

## 체크포인트: 2026-09-29 (213차) -- carrot-ms 점검 없음, 테스트 기준선 정리 중 확인한 carrot-ryu/carrot-ms 차이 기록 (코드 변경 없음)

- carrot-ms 신규 커밋 점검((d))은 하지 않았다(사용자가 나중으로 미룸). 마지막 검토 체크포인트는 그대로 8472d35(208차)다. 이 세션에서 `git ls-remote`로 본 carrot-ms HEAD는 771f118로 8472d35와 다르다(재생성 가능성). 다음 점검 때 `git cat-file -t 8472d35`로 체크포인트 존재부터 확인하고, 없으면 커밋 메시지 기준으로 범위를 잡는다.
- 테스트 기준선 정리(WIP.md 213cha) 중 carrot-ms 원본(HEAD 771f118, raw)과 대조한 것: (1) `openpilot/selfdrive/carrot/carrot_man.py`에는 `Toss upload token is not configured`(910행)가 있고 carrot-ryu에는 없다. carrot-ryu의 `send_tmux_web`은 17차에 Google Drive zip 업로드로 교체한 자체 설계다. (2) `server/tests/test_web_upload.py`는 두 브랜치가 다르다(carrot-ms에는 import 차이와 `test_carrot_man_toss_is_exclusive_and_carrot_keeps_extra_targets`가 추가돼 있다). 그래서 carrot-ryu에서 `test_carrot_man_sends_diagnostics_to_selected_target_and_carrot_logs`가 실패한다. carrot-ryu의 의도된 차이로 기록하고 코드는 바꾸지 않았다. 이후 carrot-ms의 send_tmux_web/Toss 경로가 동기화 점검에 나타나면 이 차이를 먼저 확인할 것.
- 이 대조는 위 두 파일에 한정했다(라인 단위 전체 대조 아님).

**한계:** 코드 변경 없음, 실차 검증 미실시(12절).

## 체크포인트: 2026-09-29 (212차) -- carrot-ryu-v2 아카이브 브랜치 생성(carrot-ryu 3ddf849 스냅샷, carrot-ryu 재생성 없음, 코드 변경 없음)

- 20절 2단계만 수행: carrot-ryu HEAD 3ddf849ea3f3392c16d363d9edea6a1bc8eab041를 가리키는 carrot-ryu-v2를 생성했다(사용자 실행 PowerShell, 이 세션에서 `git ls-remote`로 재확인). carrot-ryu는 변동 없음(HEAD 3ddf849). carrot-ryu-v1(6df4268eb31442be4d8abd92817111f7b26b1bf4)도 변동 없음.
- v2 스냅샷이 담은 상태: 209~211cha 온로드 HUD 이동(시간/일자, 현재속도/CPU 온도, 브랜치/모델 문구), 202/204/205cha 종방향 수정(forceDecel, comfortBrake 2.5), 201cha 948b139 이식(held_stopping_front). 즉 HANDOFF 211cha의 코드 base와 같다.
- 20절 4~7단계(carrot-ryu 재생성, 이식 체크리스트 기반 재적용, 디바이스 배포 전 재확인)는 시작하지 않았다. 재생성 여부와 시점은 사용자가 정하며, 실행 직전 명시 승인이 필요하다. 이식 체크리스트는 아직 작성하지 않았다.
- carrot-ms 마지막 검토 체크포인트는 그대로 8472d35(208차). 이번 세션에는 carrot-ms 신규 커밋 점검을 하지 않았다.

**한계:** 코드 변경 없음, 실차 검증 미실시(12절).

## 체크포인트: 2026-09-29 (208차) -- carrot-ms c771c4e -> 8472d35 신규 7건 판정: 전부 제외 (코드 변경 없음)

- carrot-ms 마지막 검토 대상 체크포인트: c771c4e(201차) -> 8472d35(2026-09-29 carrot-ms HEAD, "Use standard DM for 20 seconds on first surrounding traffic"). c771c4e가 현재 carrot-ms 히스토리에 존재함을 확인한 뒤 `c771c4e..HEAD` 범위를 잡음(blobless bare clone + git log, 변경 파일은 `git show --numstat`).
- carrot-ryu HEAD: 058391e6a3b4a1d3ac5b2eee0e4d9a4bb2f7d044(변동 없음, 이번 세션 코드 변경 없음).
- 신규 커밋 7건 중 WIP_SYNC.md에 기존 검토 기록이 있는 것은 0건. `soundd.py`(5e0060d), `augmented_road_view.py`(a24b3a5), `2beefa3`은 diff를 읽었고 나머지는 제목/커밋 본문/변경 파일 목록과 carrot-ryu 파일 존재 여부(`git cat-file -e`) 수준이며 라인 단위 대조는 하지 않음.

**판정 (2절 7번: 종류만으로 제외하지 않고 개별 확인, 제외 사유 기록) -- 사용자 결정: 7건 전부 제외**

1. `c36f6e7`(Detect steering touch by received CAN profile across Hyundai CAN-FD) -- 제외. Ioniq 5 PE 지문 게이트 제거, `steering_touch.py` STEER_TOUCH_2AF 프로파일을 CAN-FD 전 플랫폼에 적용. carrot-ryu에 `steering_touch.py`와 그 테스트가 없고(DM2 계열 의존) DH2015는 일반 CAN이라 무관.
2. `a24b3a5`(Show passive onroad DM camera insets on C3 and C4) -- 제외. 온로드 DM 카메라 인셋 표시(신규 `dm_preview.py`, `onroad/driver_preview.py`, `augmented_road_view.py` 2개에서 `DriverStateRenderer` -> `DriverPreview`). 제어와 무관한 UI 변경이고 carrot-ryu에 `driver_preview.py`/`dm_preview.py`가 없어 UI 렌더 경로 신규 도입이 필요, C3 렌더 영향을 실기기 없이 판단하기 어려움(10절).
3. `44d2707`(Apply driver monitoring mode changes live without resetting attention history) -- 제외. `dm2.py`/`dm2d.py`/`monitoring/config.py` 수정, carrot-ryu에 해당 파일 없음(201차 보류 `e7b9eb1` 위의 수정).
4. `2a14472`(docs: preserve Ioniq 5 acceleration investigation) -- 제외. 문서 1개(`docs/ioniq5_acceleration_20260926.md` +192), 코드 변경 없음, 이 차량과 무관.
5. `2beefa3`(fix) -- 제외. `dm2.py` 1개(+12/-3), experimental일 때 `_PHONE_THRESH` 0.98. carrot-ryu에 `dm2.py` 없음.
6. `5e0060d`(Move C4 DM inset beside gear and protect DM warning volume) -- 제외. C4 인셋 배치(a24b3a5 의존)와 `soundd.py`의 `dm_warning_volume`(driverDistracted2/3, driverUnresponsive2/3 알림음의 최종 PCM 볼륨 하한/최대치, `update_alert(new_alert, alert_type)` 시그니처 확장). 볼륨 부분은 표준 DM 알림음을 바꾸는 안전 관련 변경이라 실차 검증 없이 들이지 않음. 소리만 별도 후보로 올리지 않고 제외로 확정.
7. `8472d35`(Use standard DM for 20 seconds on first surrounding traffic) -- 제외. `dm2.py`/`dm2_context.py`와 테스트 수정. carrot-ryu에 DM2 파일 없음.

**다음 점검**
- 다음 점검은 `8472d35` 이후 신규 커밋부터.
- 201차 보류 8건(DM2 계열)의 보류 상태는 이번에 변경하지 않음. 이번 DM2 후속 4건(c36f6e7, 44d2707, 2beefa3, 8472d35)은 제외로 정리. 재검토 조건: 사용자가 DM2 도입을 결정할 때(`e7b9eb1`부터 순서대로, 그때 이번 4건도 함께 재검토).
- 보류 유지: `f992f9c`(194차), DM2 계열 8건(201차). 제외 유지: `fc7ee88`, `4770067`.

## 체크포인트: 2026-09-28 (201차) -- carrot-ms 4445c29 -> c771c4e 신규 23건 판정: 948b139 이식, 4770067 제외, DM2 계열 8건 보류, jetlink 12건 + 문서 1건 제외

- carrot-ms 마지막 검토 대상 체크포인트: 4445c29(194차) -> c771c4e(2026-09-28). 4445c29가 현재 carrot-ms 히스토리에 존재함을 확인한 뒤 `4445c29..c771c4e` 범위를 잡음(blobless bare clone + git log, 변경 파일은 `git show --numstat`). 세션 시점 carrot-ms HEAD는 `c36f6e7`이며 이 커밋은 이번 범위 밖(미판정, 아래 참고).
- carrot-ryu HEAD: 69eaf32ace3666a3e7669908c47df7973201b86c(이번 세션 코드 변경 1건, 부모 bef8edf).
- 신규 커밋 23건 중 WIP_SYNC.md에 기존 검토 기록이 있는 것은 0건. 판정은 사용자 위임("너가 원하는대로 진행")에 따라 Claude가 수행. 별도 표기가 없으면 제목/변경 파일 목록/carrot-ryu 존재 여부 수준 확인이며 라인 단위 diff 대조는 하지 않음.

**판정 (2절 7번: 종류만으로 제외하지 않고 개별 확인, 제외 사유 기록)**

1. `948b139`("Keep confirmed front radar leads through braking to standstill") -- 이식 완료(carrot-ryu `69eaf32`).
   내용: `primary.py`의 `held_stopping_front` 추가(+23/-2), 테스트, Sonata cutin 케이스 1건, 문서. 실차에서 Sonata 리드를 정지까지 추종하지 못하던 문제의 수정.
   carrot-ryu 차이: 제외한 `14e2cfa`(`radar_track_state == 1` 거부)가 없어 `primary.py` 두 hunk를 한 블록으로 합침, 업스트림 릴리스 테스트의 `tentative` 케이스는 이식하지 않음(그 거부 로직이 없으면 실패). DH2015는 일반 CAN이라 상태값이 항상 0이라 실제 동작 영향 없음. 테스트 +78(업스트림 +80), 문서 +93(업스트림 +89, carrot-ryu 전용 메모 4줄 추가).
   검증: 샌드박스 pytest 420 -> 436 통과, 새 테스트를 옛 코드에 적용하면 3건 실패. 실차 검증: 미실시.
2. `4770067`("Recover failed startup with automatic Git updates and reboot") -- 제외(Claude 판단, 사용자 위임).
   내용: `launch_chffrplus.sh`의 빌드/매니저 실패 처리를 모두 복구 화면(`show_startup_failure`)으로 보내고, 복구 화면이 실패 상태에서 자동으로 Git fast-forward 후 재부팅한다(`common/startup_recovery.py`, `system/ui/startup_recovery.py`, `manager.py`, `build.py`, `text_window.py` 변경, 신규 +120/+208줄과 테스트 +193줄).
   사유: (a) 디바이스 부팅 경로 자체를 바꾸는 변경이라 실기기 부팅 검증 없이 반영하기 어렵고 10절 최소 변경 원칙과 어긋난다. (b) 자동 Git 갱신 + 재부팅은 20절 7번(디바이스 배포 전 사용자 확인)과 충돌할 수 있다. carrot-ryu는 콤마 디바이스가 추적하는 브랜치이므로 사용자 승인 없는 자동 갱신은 원치 않는 배포가 될 수 있다. (c) carrot-ryu에는 `startup_recovery.py`와 복구 UI가 없어 통째로 이식해야 한다. 재검토 조건: 사용자가 부팅 실패 자동 복구를 원한다고 판단할 때(별도 코드 세션 + 승인).
3. DM2(실험적 운전자 모니터링) 계열 8건 -- 보류(반영하지 않음, 사용자 위임 판단).
   대상: `e7b9eb1`(DM2 신규 도입: `dm2.py`/`dm2d.py`/`dm2_context.py`, cereal `log.capnp`, `params_keys.h`, `carrot_settings.json` 등), `13eca74`(DM2 타이밍 재조정), `6262570`, `7171d42`, `2326be2`(DM 초기화/리더 수정), `7bd44b5`(Ioniq 5 PE 조향 터치를 DM 입력으로 사용, opendbc Hyundai `steering_touch.py`와 `car.capnp` 변경), `847d81f`(잠금 경고 한국어 문구 1줄), `c771c4e`(주차 확인 후 DM 잠금 해제, `selfdrived.py` 포함).
   보류 사유: carrot-ryu에 `openpilot/selfdrive/monitoring/dm2.py`, `dm2d.py`, `dm2_context.py`, `opendbc_repo/opendbc/car/hyundai/steering_touch.py`가 없다(clone으로 확인). `e7b9eb1`이 기능 전체를 새로 들이고 나머지 7건이 그 위의 수정/확장이라 일부만 골라 반영할 수 없다. 반영하면 운전자 모니터링 경고/잠금 동작이 바뀌므로 별도 코드 세션과 명시적 승인이 필요하다. `7bd44b5`는 제목/파일 기준으로 CAN-FD 계열(Ioniq 5 PE)용으로 보이며 DH2015 일반 CAN과 무관해 보이나 라인 단위로는 확인하지 않음. 재검토 조건: 사용자가 DM2 도입을 결정할 때(`e7b9eb1`부터 순서대로).
4. Jetson jetlink 계열 12건 -- 제외.
   대상: `ee017db`, `87f8bed`, `01b52be`, `997f839`, `c38833a`, `c5b0a63`, `097826b`, `9a36181`, `0c4b84d`, `0f37b09`, `35d2841`, `b1df74b`.
   사유: 변경 파일이 `tools/jetlink/*`, `docs/jetson_*`, `docs/jetlink_*`, `docs/INSTALL-WINDOWS-KO.md`, `.github/workflows/jetlink-checks.yaml`이며, `35d2841`만 `openpilot/common/jetlink_peer.py`, `jetlink_status.py`, `selfdrive/modeld/jetlink/daemon.py`, `mac.py`를 건드린다. 모두 외장 Jetson 호스트/SD 이미지/Windows 설치기/Mac 앱 연동 전용이며, carrot-ryu에는 `tools/jetlink`, `selfdrive/modeld/jetlink`, `common/jetlink_peer.py`가 존재하지 않는다(clone으로 확인). 이 차량(제네시스 DH 2015 + 콤마 C3) 구성에 없는 하드웨어다.
5. `a482d02`("Record verified Sonata radar fix deployment and replay results") -- 제외.
   내용: 문서 1개(`docs/sonata_stopping_lead_continuity_20260928.md`, +25/-2)만 변경, 업스트림 쪽 배포/리플레이 결과 기록. 사유: 코드 변경 없음, 업스트림 실차/리플레이 결과라 carrot-ryu 검증 기록이 아니다. 이식한 문서(`948b139` 시점 본문)에 그 결과 기록은 넣지 않았다. 필요하면 참고용으로만 재조회.

**다음 점검**
- 다음 점검은 `c771c4e` 이후 신규 커밋부터. 이 세션에서 이미 확인된 것은 `c36f6e7`(2026-09-28, "Detect steering touch by received CAN profile across Hyundai CAN-FD") 1건이며 판정하지 않았다. 그 이후 신규 커밋은 조회하지 않았다.
- 보류 유지: `f992f9c`(LFS 일반 blob 전환, 194차), DM2 계열 8건(이번). 제외 유지: `fc7ee88`(UI 코어 배치, 194차), `4770067`.

## 체크포인트: 2026-09-28 (194차) -- carrot-ms 735a9a4 -> 4445c29 신규 11건 판정: 10건 제외, f992f9c 보류(코드 변경 없음)

- carrot-ms 마지막 검토 대상 체크포인트: 735a9a4(192차) -> 4445c29(2026-09-28 carrot-ms HEAD, "Record full installer execution and verified NAS candidate artifacts"). 735a9a4가 현재 carrot-ms 히스토리에 존재함을 확인한 뒤 `735a9a4..HEAD` 범위를 잡음(api.github.com compare는 rate limit이라 blobless bare clone + git log로 대체).
- carrot-ryu HEAD: 99754dc847c5d0353a3535a46bbeadaaf055846b(변동 없음, 이번 세션 코드 변경 없음).
- 신규 커밋 11건 중 WIP_SYNC.md에 기존 검토 기록이 있는 것은 0건.

**판정 (2절 7번: 종류만으로 제외하지 않고 개별 확인, 제외 사유 기록)**

1. Jetson 보호 이미지/설치기/Wi-Fi 복구 계열 9건 -- 제외.
   대상: `3a75293`, `5aad6df`, `f29ccd5`, `330c3a3`, `dd24f8f`, `3d88361`, `a104ebe`, `97c828a`, `4445c29`.
   사유: 변경 파일이 전부 `tools/jetlink/*`, `third_party/jetlink/*`, `docs/jetson_power_loss_protection.md`, `.github/workflows/jetlink-checks.yaml`로, 외장 Jetson 호스트/SD 이미지/Windows 설치기/NAS 후보 산출물 전용이다. 이 차량(제네시스 DH 2015 + 콤마 C3) 구성에 없는 하드웨어이며 공유 런타임 파일 변경 없음. 제목/변경 파일 목록 수준 확인이고 라인 단위 diff 대조는 하지 않음.
2. `fc7ee88`("Allow C3 UI to share little cores and core6 at nice19") -- 제외(Claude 판단, 사용자 위임).
   내용: `DisplayScheduler(include_little=...)`로 C3/C3X 온로드 UI 스레드 affinity를 core6 -> cores0,1,2,3,6(SCHED_OTHER/nice19)으로 확장. `ui.py`, `display_scheduling.py`와 테스트 3개 변경.
   사유: carrot-ryu에는 `openpilot/common/display_scheduling.py`와 그 테스트가 없다(이전 9/23 UI core6/USB core7 배치 커밋 계열을 아예 가져오지 않음). carrot-ryu `ui.py`는 core0 부트스트랩 후 core5로 옮기는 별개 구조이고 "core7은 modeld+plannerd+dmonitoringmodeld 전용이라 UI 재배치 금지" 주석이 있다. 반영하려면 UI 스케줄링 인프라 전체를 이식해야 하며 코어 배치가 제어 주기에 미치는 영향이 커서 10절 최소 변경 원칙과 어긋난다. 업스트림 자체도 실차 FPS 개선은 미검증이라고 명시.
3. `f992f9c`("Store remaining LFS artifacts as ordinary Git blobs") -- 보류(반영하지 않음, 사용자 위임 판단).
   내용: 업스트림 계정의 LFS 대역폭 소진으로 LFS 포인터 7개(`driving_supercombo.onnx` 60,792,584B, `tici/updater` 24,709,487B, `xiaoge/lane.onnx`, `xiaoge/v_asm_model.onnx`, `docs/assets/comma-logo.png`, 웹 `alert_camera.svg`/`alert_police.svg`)를 원본 내용의 일반 blob으로 교체, `.gitattributes`를 `* text=auto -filter` + `.onnx`/updater `-diff -merge -text`로 변경, setup/CI의 `git lfs pull` 제거.
   carrot-ryu 상태(clone으로 확인): `.gitattributes`가 LFS 설정 그대로이고 위 대용량 파일이 133바이트 LFS 포인터 상태.
   보류 사유: 반영하면 약 60MB급 blob이 carrot-ryu 히스토리에 들어가고 콤마 디바이스의 업데이트/체크아웃 경로가 바뀐다. 저장소 운영 방식에 관한 결정이라 이번 세션에서 확정하지 않는다. ryujmin97 계정의 LFS 대역폭 소진 여부는 확인할 수 없음. 재검토 조건: 디바이스에서 LFS pull이 실패하거나 계정 LFS 한도 문제가 확인될 때(별도 코드 세션 + 사용자 승인, 20절 버전 리셋 시점에 함께 판단해도 됨).

**한계:** 실차 검증 미실시(12절, 코드 변경 없음). 위 판정은 정적 확인(커밋 목록/변경 파일/핵심 diff/carrot-ryu 파일 존재 확인)이다.

**carrot-ryu 고유 상태(향후 재동기화 시 참고)**
- 이전 기록 유지: `openpilot/common/stopping_params.py` 없음(VEgoStopping은 `get_float * 0.01` 직접 사용).
- 추가: `openpilot/common/display_scheduling.py` 없음, `.gitattributes`는 LFS 설정(대용량 파일은 LFS 포인터).

남은 이월 항목: 변동 없음(핵심 발견 68/163차 게이트/xTurn=6 로그/pytest CI 환경/102ms wide-camera BOOT_TS gap).

## 체크포인트: 2026-09-28 (192차) -- carrot-ms 3441183 -> 735a9a4 신규 74건 전수 판정: 전부 제외 확정(코드 변경 없음)

- carrot-ms 마지막 검토 대상 체크포인트: 3441183(188차) -> 735a9a4(2026-09-28
  carrot-ms HEAD, "Record verified Jetson installer layout release"). 3441183이
  현재 carrot-ms 히스토리에 존재함을 확인한 뒤 `3441183..HEAD` 범위를 잡음.
- carrot-ryu HEAD: 6ed56f0d64df0612e3993e247d03fc199903569e(변동 없음, 이번 세션
  코드 변경 없음)
- 신규 커밋 74건 중 WIP_SYNC.md에 기존 검토 기록이 있는 것은 0건.

**판정 (2절 7번: 종류만으로 제외하지 않고 개별 확인, 제외 사유 기록)**

1. Jetson/Jetlink/설치기 계열 70건 -- 제외.
   사유: 외장 Jetson 추론 호스트(USB-C 연결), SD 이미지/설치기, NAS 배포,
   Jetlink v2 전송 등 이 차량(제네시스 DH 2015 + 콤마 C3) 구성에 없는 하드웨어
   전용 기능. 일부 커밋이 공유 파일을 건드리지만(`3a12c37`: modeld.py/
   selfdrived.py/hud_renderer.py/ui_state.py/process_config.py, `619603d`:
   modeld.py/dmonitoringmodeld.py, `cf01424`: carrot_navi.py, `12f34da`/
   `ae68f74`/`fe13538`: egpu_model.py 및 웹 번들/번역, `29667d9`/`e3809fe`:
   cluster_*.py) 전부 Jetson 연동 경로 안의 변경이라 Jetson 미사용 환경에는
   무관하다고 판단해 함께 제외. 이 70건의 제외는 커밋 제목/변경 파일 목록
   수준 확인이며 라인 단위 diff 대조는 하지 않음.
2. `eefd372`("Keep stationary Hyundai CAN FD HUD leads white") -- 제외.
   사유: `hyundaicanfd.py`(CAN FD 전용). carrot-ryu values.py 기준
   Genesis DH 2015는 HYUNDAI_GENESIS(일반 CAN)라 해당 경로가 아님.
3. `72a33fb`("Raise the stopping-speed setting minimum and repair legacy
   values") + 후속 `5e10742`("Adapt the model-selector mirror to the
   stopping-speed repair") -- 사용자 결정으로 제외(선택지 c).
   내용: VEgoStopping 최소값 1->10, 기존 10 미만 저장값을 부팅 시 자동 상향,
   `openpilot/common/stopping_params.py` 신설(`get_stopping_speed`),
   longitudinal_planner.py/carrot_modeld.py가 이를 사용. 업스트림 사유는
   Ioniq 5에서 VEgoStopping=2일 때 shouldStop이 48초 지연된 사고이며 차량
   정차 개선 효과는 업스트림도 미검증으로 명시. 이 차량의 실적용값은
   VEgoStopping=5(PARAMS_REGISTRY.md)라 반영 시 5->10으로 자동 상향되어
   정차 판단/재출발 민감도가 바뀌므로 사용자가 제외 결정.
4. `14e2cfa`("Reject tentative front tracks in radar-only primary selection")
   -- 제외(사용자 확정). 사유: `radar_motion/primary.py`에
   `point.source == "frontRadar" and point.radar_track_state == 1` 조건 1건 추가.
   carrot-ryu의 `hyundai/radar_interface.py`는 `trackState`를 CAN FD 분기
   (`canfd_group2_track_status`)에서만 채우고 일반 CAN은 `track_state = 0`으로
   남으므로, DH2015에서는 조건이 참이 될 수 없는 no-op. 10절 최소 변경 원칙에
   따라 제외.

**carrot-ryu 고유 상태(향후 재동기화 시 참고)**
- carrot-ryu에는 `openpilot/common/stopping_params.py`가 없고 VEgoStopping은
  `params.get_float("VEgoStopping") * 0.01`을 그대로 쓴다(최소값 1, 기본 50 유지).
  carrot-ms가 이후 커밋에서 `get_stopping_speed`에 의존하면 이 차이를 먼저 확인할 것.

**한계:** 실차 검증 미실시(12절, 코드 변경 없음). 위 판정은 정적 확인
(커밋 목록/변경 파일/핵심 diff/radar_interface.py 코드 경로)이며, 70건의
Jetson 계열은 라인 단위로 읽지 않았다.

남은 이월 항목: 핵심 발견 68/163차 게이트/xTurn=6 로그/pytest CI 환경/102ms
wide-camera BOOT_TS gap -- 변동 없음.

## 체크포인트: 2026-09-27 (188차) -- 3441183(happymaj11r/carrot-ms 통해 노출, 원커밋 ajouatom/carrot-wip) 반영 확정, 스크립트 작성/검증 완료 push 대기; 1f56076은 제외

- carrot-ms 마지막 검토 대상 체크포인트: 087fdca(172차) -> 3441183(신규 커밋 2건
  1f56076/3441183 전부 검토 완료, 이 커밋까지 검토 확정)
- carrot-ryu HEAD: 5d2c9b0(187차 종료 시점, 변동 없음 -- 이번 세션은 반영
  스크립트만 작성/검증, 실제 push는 아직 없음)
- carrot-ryu-note HEAD: 188차 devnotes 반영으로 이동 예정(이 커밋)

**검토 결과:**
- 1f56076("Fix camera MDPS and TCS transmit counter continuity"):
  opendbc_repo/opendbc/car/hyundai/hyundaicanfd.py 수정, CAN-FD 카메라-SCC
  차량 전용 로직. carrot-ryu의 values.py 확인 결과 Genesis DH 2015는
  HYUNDAI_GENESIS(HyundaiPlatformConfig, 일반 CAN)로 분류되어
  HyundaiCanFDPlatformConfig(GV60/G70/G80 신형 등) 대상이 아님 -> 무관, 제외.
- 3441183("Release automatic Safe mode sooner on sustained lead
  acceleration"): carrot 코어 주행모드 기능(차종 무관). RECOVERY_TIME
  6.0->3.0초, ACCEL_EXIT_THRESHOLD 1.5->1.0 m/s². 사용자 승인(b: 로직+문서+
  carrot_settings.json 전부 상세 대조 후 반영)에 따라 8개 파일 변경사항을
  구성/검증(WIP.md 188차 항목에 상세 기록) -> 188cha_carrot_ryu_sync_3441183.ps1
  작성, 사용자 실행 대기.

**한계:** 실차 검증 미실시(12절). carrot-ryu 반영 스크립트의 실제 push는 아직
없음 -- push 완료 후 이 문서의 carrot-ryu HEAD를 GitHub 직접 재확인해 갱신
필요(16절).

남은 이월 항목: 핵심 발견 68/163차 게이트/xTurn=6 로그/pytest CI 환경/102ms
wide-camera BOOT_TS gap -- 변동 없음.

## 체크포인트: 2026-09-27 (187차) -- 828fc8c(고위험 웹 리팩터) carrot-ryu 반영 결과 GitHub 직접 재확인, 이월 목록에서 제외

- carrot-ryu HEAD: f56cae36ee2554087a6db82d4cd13e1a7ed693e3(186차 종료 시점) ->
  5d2c9b07230c332142a69a271ee584899983bc86(828fc8c 반영, push 완료를 GitHub
  직접 재확인)
- carrot-ryu-note HEAD: 77d42a8c9ade7e86aed2cbbc9b43764be0306714(186차 세션
  시작 시점) -> c55c2ecee0fe9aa68d31da0353215bbf7222b432(186차 devnotes
  push 완료 확인)
- carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15
  (172차와 동일, 변동 없음 -- 이번 세션은 이월 후보 828fc8c 1건의 반영 결과
  사후 확인이며 2절 정기 점검 아님)

**828fc8c("web work", happymaj11r/carrot-ms) 반영 확인:**
- 원본 43 files changed, 1982(+)/767(-) / 반영 커밋 43 files changed,
  2039(+)/824(-) -- 변경 파일 목록 43개 전부 일치.
- 포함 범위: web_settings.py, setting.js(390줄 재작성), i18n.js,
  translations(en/ko/zh), 생성 번들(settings.js/tools.js/settings.css/
  tools.css/asset-manifest.json), index.html, 신규 검색 모듈
  (search/entries.js, search/highlight.js, search/inline.js, search/panel.js,
  search/results.js), drive-layout 기본값(area_1=vision/area_2=navigation),
  신규 테스트 다수(settings_search_*.test.mjs 등), 문서 4개(en/ko x
  carrot-web/settings).
- 신규 Params.get()/.put() 키 없음(10절 대상 아님).
- 특이사항: 반영 커밋 author 이메일이 placeholder
  (`여기에_깃허브_가입이메일@example.com`)로 남음 -- 기능 영향 없음, 참고만.

**한계:** 이번 세션은 사후 GitHub 재확인(파일 목록/커밋 메시지/신규 Params
키 부재 수준)만 수행 -- py_compile/node build 재실행/라인 단위 로직 대조는
하지 않음. 실차 검증 미실시(12절).

남은 이월 항목: 핵심 발견 68/163차 게이트/xTurn=6 로그/pytest CI 환경/102ms
wide-camera BOOT_TS gap -- 변동 없음. `828fc8c`는 이번 확인으로 이월 목록에서
제외.

## 체크포인트: 2026-09-27 (186차) -- b84621a(AGNOS 자동 설치) 반영 확정, 자동 재부팅은 제외

- carrot-ryu HEAD: 세션 시작 시 226e2e653634dfdedd4135ff46907f7b79bb2011(185차
  288e212 push 완료를 GitHub 직접 재확인 후 진행) -> 186차 반영 후
  f56cae36ee2554087a6db82d4cd13e1a7ed693e3(push 완료, GitHub 직접 재확인 완료)
- carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15
  (172차와 동일, 변동 없음 -- 이번 세션은 이월된 개별 후보 커밋 b84621a에 대한
  사용자 결정 반영이며 2절 정기 점검 아님)

185차 HANDOFF "다음 작업" 3번(b84621a 반영 여부 사용자 판단)에 대해, 사용자가
"자동 설치는 유지 + 자동 재부팅은 제거하고 수동 재부팅으로 변경"해서 반영하기로
결정.

**반영(push 완료) -- 7개 파일 (전부 기존 파일 수정, 신규 파일 없음)**
- `launch_chffrplus.sh`: 무인 설치 흐름에 맞춘 실패 메시지 문구 변경.
- `openpilot/system/hardware/tici/agnos.py`: `transient_download_error()` 신설
  (SSL/영구적 HTTP 에러는 중단, 연결/타임아웃/408/429/5xx는 계속 재시도),
  `flash_agnos_update()`가 이를 사용하도록 재작성, `--retry-network` CLI 플래그
  신설, 호출부 2곳 업데이트.
- `openpilot/system/ui/mici_updater.py` / `tici_updater.py`: 설치 시작 전
  탭/확인 게이팅 제거(부팅 시 자동 시작), 진행 중 Wi-Fi 접근 유지,
  `--retry-network` 전달. **MODIFIED**: 설치 완료 시 `HARDWARE.reboot()` 자동
  호출 대신 수동 Reboot 버튼 화면 표시(mici: 신규 `UpdaterCompletePage`, tici:
  `update_complete` 플래그로 기존 reboot-button 레이아웃 재사용).
- `openpilot/system/tests/test_agnos_update_reliability.py` /
  `test_mici_updater_compatibility.py`: 자동 설치 흐름에 맞춰 갱신.
- `openpilot/system/tests/test_agnos_updater_retry.py`: 성공 경로 assertion을
  `hardware.reboot.assert_called_once()` -> `hardware.reboot.assert_not_called()`로
  변경(수동 재부팅만 허용됨을 테스트로 고정).

**제외**
- `AGENTS.md`(carrot-ms 자체 AI 작업 로그, carrot-ryu 무관),
  `docs/cinque_v3_integration_20260919.md`(carrot-ryu에 대응 파일 없음).

**carrot-ryu 고유 수정 사항(향후 carrot-ms 재동기화 시 반드시 참고)**
- 이번에 반영된 것은 b84621a 원본이 아니라 "자동 설치 + 수동 재부팅"으로 바꾼
  버전. carrot-ms가 이 영역 후속 커밋을 내면, 재부팅 방식이 여전히 자동인지
  먼저 확인하고 이 차이를 기준으로 충돌/반영 여부를 판단할 것.
- 185차의 `managerState.rebootRequired` 알림(자체 재부팅 실행 없는 정보성
  알림)과는 서로 다른 메커니즘 -- 이번 반영으로도 관계/충돌 없음, 참고용 기록
  유지(185차 HANDOFF 주의사항 참고).

남은 이월 항목: `828fc8c`(고위험 재분류, 별도 세션 필요), 핵심 발견 68/163차
게이트/xTurn=6 로그/pytest CI 환경/102ms wide-camera BOOT_TS gap -- 변동 없음.
`b84621a`는 이번 반영으로 이월 목록에서 제외.

## 체크포인트: 2026-09-27 (185차) -- 288e212(재부팅 필요 알림) 반영, PV5 전용 2건 제외 확정

- carrot-ryu HEAD: 세션 시작 시 550ed0646d7760b22d44453642d8736252e07588(184차
  push 완료를 GitHub 직접 재확인 후 진행), 이번 세션 반영분은 push 대기(스크립트
  작성 및 로컬 bare dry-run 검증만 완료, 16절)
- carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15
  (172차와 동일, 변동 없음 -- 이번 세션은 184차 이월 항목 상세 대조, 2절 정기
  점검 아님)

184차 HANDOFF "다음 작업" 순서대로 `288e212`부터 착수. 사용자 확인에 따라
`84aa7f0`/`f0ee8f2`(PV5 내비 감속 카메라 로직)는 이 차량이 PV5가 아니므로
반영 검토 대상에서 완전 제외.

**반영(push 대기) -- 11개 파일 (8 수정 + 3 신규)**
- `openpilot/cereal/log.capnp`: `OnroadEvent.EventName.updateRebootRequired @125`,
  `ManagerState.rebootRequired @1` 추가.
- `openpilot/selfdrive/selfdrived/events.py`: `updateRebootRequired` PERMANENT
  알림 추가.
- `openpilot/selfdrive/selfdrived/selfdrived.py`: `update_reboot_alerted` 플래그
  + `update_reboot_alert()` 메서드/호출 추가.
- `openpilot/system/manager/manager.py`: `UpdateStatus` 배선(초기화/스레드/`main()`).
- `openpilot/system/manager/update_status.py`(신규): 체크아웃 커밋 비교 로직.
- `openpilot/selfdrive/selfdrived/tests/test_update_reboot_alert.py`(신규),
  `openpilot/system/tests/test_update_reboot_status.py`(신규).
- `openpilot/selfdrive/ui/translations/{app.pot,app_en.po,app_ko.po,app_zh-CHS.po}`:
  신규 msgid 2종(en/ko/zh-CHS만, 원본 patch와 반영 범위 일치). ko/zh-CHS는
  carrot-ryu 자체 항목과의 위치 충돌로 파일 끝에 삽입(내용은 원본과 동일).

**제외**
- `docs/ev5_cluster_corner_display.md`(EV5 클러스터 전용 문서, DH2015 무관).

**PV5 전용 제외 확정**
- `84aa7f0`/`f0ee8f2`(navi 7713/7714 감속, carstate.py) -- 사용자 확인(이
  차량은 PV5 아님)에 따라 반영 검토 대상에서 완전 제외.

남은 이월 항목: `828fc8c`(고위험 재분류, 별도 세션 필요), `b84621a`(반영 여부
사용자 판단 필요), 핵심 발견 68/163차 게이트/xTurn=6 로그/pytest CI 환경/
102ms wide-camera BOOT_TS gap -- 변동 없음.

- 다음 확인 시점: 사용자 스크립트 실행(push) 확인 후 GitHub 직접 재확인,
  이어서 `828fc8c` 상세 대조 착수 여부 논의.

## 체크포인트: 2026-09-27 (184차) -- cfe9251→cf288c1 실제 반영 완료, 183차 tests.yaml 분류 정정

- carrot-ryu HEAD: 세션 시작 시 480b7f7 (183차 스크립트 push 완료 확인됨), 이번 세션
  반영분은 push 대기(스크립트 작성 및 로컬 bare dry-run 검증만 완료, 16절)
- carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15
  (172차와 동일, 변동 없음 -- 이번 세션은 183차 이월 항목 상세 대조, 2절 정기 점검 아님)

183차에서 "`.github/workflows/tests.yaml`만 컨텍스트 충돌하는 순서 의존 관계"로
재분류했던 `cfe9251`/`cf288c1`을 상세 대조한 결과, carrot-ryu의 tests.yaml은
carrot-ms와 구조가 달라(개별 파일 하드코딩이 아니라 glob 방식) 애초에 수동 병합
대상 자체가 없었음을 확인(분류 정정). 실제 반영 대상은 `index.html`(viewport
meta, cfe9251)과 `navigation.js`(goToSettingParent, cf288c1)였고 둘 다 무충돌
(183차 당시 WIP_SYNC.md에도 "index.html/JS 쪽은 충돌 없음"으로 이미 기록돼
있었음). 부수적으로 옛 구현을 검증하던 기존 회귀 테스트 1건을 갱신하고 신규
테스트 2건을 추가함(상세는 WIP.md 184차 참고).

**반영(push 대기) -- 5개 파일**
- `index.html`: viewport meta `interactive-widget=resizes-content` -> `resizes-visual`.
- `js/shared/ui/navigation.js`: `goToSettingParent()` 추가, `itemsTitle.onclick` 교체.
- `tests/logs_player_transport.test.mjs`: 옛 구현 검증 단언문 갱신.
- `tests/settings_parent_navigation.test.mjs`(신규), `tests/viewport_keyboard.test.mjs`(신규).

남은 이월 항목: `288e212`/`84aa7f0`/`f0ee8f2`(중간 우선순위), `828fc8c`(고위험
재분류, 별도 세션 필요), `b84621a`(반영 여부 사용자 판단 필요), 핵심 발견
68/163차 게이트/xTurn=6 로그/pytest CI 환경 -- 변동 없음.

- 다음 확인 시점: 사용자 스크립트 실행(push) 확인 후 GitHub 직접 재확인, 이어서
  288e212/84aa7f0/f0ee8f2 순차 상세 대조.

## 체크포인트: 2026-09-27 (183차) -- 저위험 소규모 9건 상세 대조, 2건 반영 + 7건 재분류

- carrot-ryu HEAD: dd357a10fe1c57712bc390dc47dcb310271b1189 (183차 스크립트 실행 후 6개 파일 반영분 push 대기, 사용자 실행 확인은 다음 세션에서 hash 재조회로)
- carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (172차와 동일, 변동 없음 -- 이번 세션은 기존 이월 항목(저위험 9건) 상세 대조, 2절 정기 점검 아님)

172차에서 "저위험 소규모, 아직 미착수"로만 분류돼 있던 9건을 carrot-ryu 현재 HEAD(dd357a10)에 `git apply --check`로 개별 재검증.

**반영 완료 -- 2건**
- `9800be9`(Include repository owner in Carrot startup branch log) -- 충돌 없음, `GitRemote` 파라미터 키가 carrot-ryu params_keys.h에 이미 등록돼 있음을 확인.
- `cee4054`(Allow AGNOS update retry after late Wi-Fi connection) -- 충돌 없음, 참조 심볼(GreyBigButton/BigConfirmationCircleButton/NavScroller/_wifi_button 등) 실존 확인.

**재분류 -- 7건**
- `cfe9251`/`cf288c1`(Carrot Web 키보드 안정화 / 설정 헤더 네비게이션) -- `.github/workflows/tests.yaml`만 컨텍스트 충돌(두 커밋이 원본에서 같은 파일을 연속 수정하는 순서 의존 관계). index.html/JS 쪽은 충돌 없음. 중간 우선순위로 재이월, 처리 순서는 cfe9251 -> cf288c1.
- `828fc8c`("web work", 3796줄) -- web_settings.py/생성된 css·js 번들/setting.js(390줄 재작성) 다중 충돌. 172차의 "저위험 소규모" 분류가 실제 규모와 맞지 않음 -- 고위험/상세 대조 항목으로 재분류.
- `288e212`(재부팅 필요 알림) -- log.capnp에 `updateRebootRequired @125` 추가(182차 수정 영역 @62/@63과 충돌 없음 확인), 문서/번역 파일(app_ko.po/app_zh-CHS.po 등)만 컨텍스트 충돌. 중간 우선순위로 재이월.
- `b84621a`(AGNOS 자동 설치, 사용자 확인 없이) -- AGENTS.md/agnos.py/updater UI 다중 충돌. 사용자 확인 없는 자동 설치+재부팅 동작이라 반영 여부 자체를 사용자가 먼저 판단해야 하는 항목으로 재분류.
- `84aa7f0`/`f0ee8f2`(PV5 내비 감속 카메라 로직, carstate.py) -- carrot-ryu 자체 carstate.py 커스텀과 얽혀 다중 충돌. 중간 우선순위로 재이월(172차에도 "실제 검토는 필요"로 이미 명시돼 있었음).

남은 이월 항목: log.capnp @62/@63 필드 타입 정합성(182차로 종결), 핵심 발견 68/163차 게이트/xTurn=6 로그/pytest CI 환경 -- 변동 없음. 저위험 9건은 위와 같이 2건 반영 + 7건 재분류로 갱신됨.

- 다음 확인 시점: cfe9251/cf288c1 CI yaml 수동 병합, b84621a 반영 여부 사용자 확인, 828fc8c/288e212/84aa7f0/f0ee8f2 순차 상세 대조.

## 체크포인트: 2026-09-27 (181차) -- c84b175(CPU 스케쥴링) 상세 대조 완료, 제외 확정

- carrot-ryu HEAD: 67f41f87fec16ca5626f550c213b4b03eba53c0e (180차 이후 변동 없음, 이번 세션은 분석/devnotes만)
- carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (172차와 동일, 변동 없음)

c84b175(happymaj11r/openpilot, ajouatom a60f554a7dfb3a229be6fa7ae6715be5c3ae14da cherry-pick, "Run onroad displays at low priority on cores 6 and 7") 26개 파일 diff 상세 대조 완료. 신규 DisplayScheduler가 onroad 시 core6(UI)/core7(클러스터 HUD)을 공유하는 구조인데, carrot-ryu는 core6=카메라 단독, core7=modeld+plannerd+dmonitoringmodeld 전용으로 이미 코어 격리 정책을 명시적으로 유지 중(carrot_ui_sched.py 주석, 이전 camera-core5-trial 롤백 9e1a5bf). 구조적 충돌 확인. 이 커밋이 노리는 이점(오프로드 little-core 배치, onroad 저우선순위 공유)은 carrot-ryu가 이미 다른 메커니즘으로 확보하고 있어 추가 실익 없음. 카롯 클러스터 HUD/eGPU 미사용도 사용자 확인.

**반영 대상에서 완전 제외 -- 종결.**

남은 이월 항목: log.capnp @62/@63 필드 타입 정합성, 저위험 9건/핵심 발견 68/163차 게이트/xTurn=6 로그/pytest CI 환경. (c84b175, dcffb7f 모두 종결됨.)


## 체크포인트: 2026-09-27 (180차) -- dcffb7f(카메라 SOF 스타트업 phase) cherry-pick 완료, CI/AGENTS.md 누락분 추가 반영

- carrot-ryu HEAD: 67f41f87fec16ca5626f550c213b4b03eba53c0e (parent c70dad323746a265be3b68939721e69845d5e9ff = dcffb7f 핵심 cherry-pick, 그 parent 005f1202 = 179차)
- carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (172차와 동일, 변동 없음 -- 이번 세션은 기존 이월 항목 해소, 2절 정기 점검 아님)

happymaj11r/openpilot dcffb7f(원본 ajouatom 7bdd374e cherry-pick, "Match camera startup phase to bundled Panda firmware") 반영 완료. 172차 이후 장기 이월되던 개별 커밋 이월 항목(c84b175, dcffb7f) 중 dcffb7f 해소. 코드 cherry-pick 자체(c70dad323)는 이전 세션에서 push까지 완료됐으나 devnotes 기록이 누락된 채 세션이 종료된 상태를 이번 세션이 GitHub 직접 재확인(16절)으로 발견해 devnotes를 소급 반영함. 원본 diff 중 .github/workflows/tests.yaml(CI 진단 테스트 스텝)과 AGENTS.md(이슈 요약 메모)는 최초 cherry-pick에서 누락되어 있던 것을 사용자 확인 후 이번 세션에서 추가 반영(67f41f87).

남은 이월 항목: c84b175(CPU 스케쥴링) 미착수. 그 외 저위험 9건/핵심 발견 68/163차 게이트/xTurn=6 로그/log.capnp 타입 정합성/pytest CI 환경은 변동 없음.


## 체크포인트: 2026-09-27 (179차) -- 0006296 잔여 항목(carrot_settings.json/test_settings_schema.py) 반영 완료

- carrot-ryu HEAD: 005f1202b3bd1139ca97195e7cda716e70f35588 (parent 107279570bc9110fc58b9937707f9ae448343c51, 178차)
- carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (172차와 동일, 변동 없음)

carrot_settings.json UI 노출(CruiseCoastingPercent, CRUISE_CARROT 그룹)과 test_settings_schema.py 가드 테스트 반영 완료. 177차에서 이월되어오던 "설정 개수 183→184 불일치" 항목은, 0006296 원문 직접 조회 결과 CruiseCoastingPercent와 무관한 RadarTrackFlip(carrot-ryu에 존재하지 않는 별개 설정) 번들로 인한 것으로 확인되어 해결(RadarTrackFlip은 반영 범위에서 제외). carrot-ryu 자체 test 파일에는 하드코딩된 개수 assert가 없어 이 불일치가 실제 반영을 막는 요인은 아니었음.

**신규 발견:** 0006296 원문 diff를 이번에 처음 직접 확보해보니, log.capnp의 cruiseCoastingPercent 필드를 원본은 UInt8로 선언했으나 carrot-ryu는 176차에 코드 사용처 기준으로 Int32로 재구성했음(타입 불일치). carrot-ryu 자체 스키마 내에서는 문제없이 동작하나, 원본 patch 기준 정합성은 미확인 상태로 남아있음(다음 이월 항목).

남은 이월 항목(0006296 자체): log.capnp @62/@63 필드 타입/번호가 원본과 일치하는지 확인만 남음(나머지 파일은 모두 반영 완료). 별개 이월 항목(c84b175, dcffb7f)은 변동 없음.

## 체크포인트: 2026-09-27 (177차) -- 0006296(크루즈 코스팅 마진) carrot-ryu 반영 완료, push 및 재확인 완료

- carrot-ryu HEAD: 5161837541d07ece15707a2ae6e3458d02befed3 (parent d751e15, 175차)
- carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (172차와 동일, 변동 없음)

0006296 병합의 핵심 코드 5개 파일(cruise_coasting.py 신규 / longcontrol.py / longitudinal_planner.py / cereal/log.capnp / common/params_keys.h) push 완료. log.capnp(@62 cruiseCoastingTarget, @63 cruiseCoastingPercent) / params_keys.h(CruiseCoastingPercent, 기본값 0)는 원본 patch diff를 그대로 적용한 게 아니라 코드 사용처 기준으로 최소 재구성해 추가한 것임 -- 원본 patch의 나머지 부분(test_cruise_coasting.py / carrot_settings.json / test_settings_schema.py) 반영 시 이 필드/키와의 정합성을 다시 확인해야 함(WIP.md 177차 참고).

남은 이월 항목(test_cruise_coasting.py, carrot_settings.json UI, test_settings_schema.py, c84b175, dcffb7f)은 변동 없음.

## 체크포인트: 2026-09-27 (176차) -- 0006296(크루즈 코스팅 마진) 상세 병합·검증 완료, push 대기

- carrot-ryu HEAD: d751e15ec0d5ab28022d28d7de4a6be9022b125d (175차 이후 변경 없음, 이번 세션 코드는 아직 push 전)
- carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (172차와 동일, 변동 없음 -- 이번 세션은 개별 커밋 병합 작업, 2절 정기 점검이 아님)

**0006296 "Add opt-in cruise coasting margin with protected braking" (happymaj11r/openpilot, cherry-picked from ajouatom 4320337) -- 상세 병합 완료**
- 16개 파일 중 13개(docs 2건, cereal/log.capnp, params_keys.h, test_settings_schema.py, carrot_settings.json, cruise_coasting.py 신규, test_cruise_coasting.py 신규 등)는 git apply --check 클린 통과 확인(단, test_ci_check.py/test_generate.py는 carrot-ryu 자체 설정 개수(184)가 이미 패치 기준(183->184)과 어긋나 있어 최소 변경 원칙에 따라 이번 반영 범위에서 제외 -- 별도 이월 항목).
- 핵심 종방향 파일 2개(longitudinal_planner.py, longcontrol.py)는 carrot-ryu 자체 커스텀(cutin_predecel_limit/force_slow_decel/accel_limits_turns 등)과 컨텍스트가 겹쳐 블록치환 방식으로 수동 병합(원본 diff와 라인 단위 대조 완료, 로직 누락 없음 확인).
- 원본 패치 자체의 결함 발견: longcontrol.py coasting relief 조건의 math.isfinite() 3회 호출에 import math가 없음(happymaj11r 원본에도 없음, carrot-ryu 병합 중 새로 만든 게 아니라 upstream 결함을 그대로 들여올 뻔한 것). carrot-ryu 병합본에는 import math 추가로 수정.
- 병행 발견: 신규 테스트가 기존 공용 픽스처 make_cp()(test_longcontrol_hyundai_tuning.py)에 openpilotLongitudinalControl 필드를 요구하는데 carrot-ryu 기존 버전엔 없어 테스트 57개 실패 -> make_cp()에 필드 추가로 해결(carrot-ryu 자체 테스트 인프라 보정, 0006296 패치 범위 밖의 부수 수정).
- 검증: py_compile 전체 통과, pytest 137/138 통과(1건은 cereal 빌드 환경 부재, 신규 버그 아님).
- 다음 확인 시점: 반영 스크립트 실행 후 GitHub 직접 재조회로 실제 push 확인(16절).

## 체크포인트: 2026-09-27 (172차) -- carrot-ms 재점검 재개(130/139차 이후 장기 이월분), 53건 1차 분류 + 1건 반영

- carrot-ryu HEAD: c6d8a2066c0839cf24509c375ef646022dd42119 -> 172cha 스크립트 실행 후 726198908c27a58a220f0bb581af137a492c6a63(carrot-ms) 반영분 push 대기(실행 확인은 다음 세션에서 hash 재조회로)
- carrot-ryu-note HEAD: bdd07e6323d0207a1425e50a0ad06d8fffabb4b2 (이 스크립트 반영 전)
- carrot-ms(happymaj11r/openpilot) 이전 체크포인트: 3756e6d5702ff6ebd2c54d12f2e25e587dca4d99 (130/139차, 신규 커밋 없음으로 종료)
- carrot-ms 신규 HEAD: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (`git ls-remote`로 재확인, 2026-09-27) -- 3756e6d5는 rebase 없이 신규 로그에 원본 해시 그대로 존재(순수 추가), 그 사이 신규 53건(2026-09-22~09-26)

**분류 원칙**: 2절대로 carrot-wip 존재 여부/모델셀렉터 관련 여부로 사전 필터링하지 않고 53건 전부 개별 판단.

**제외 확정 (브랜드/하드웨어 무관, 근거 명확) -- 26건**
- CANFD 전용 7건: `e7356cd` `e6c79a2` `ea4869c` `3597fb6` `d352449` `e3ea61a` `07b3504` -- hyundaicanfd.py/safety_hyundai_canfd* 전용, DH2015는 CHECKSUM_6B|LEGACY
- EV5 전용 4건: `06a184c` `557b8f1` `c6af9f0` `c775009`
- 기타 차종 전용 3건: `2b13ef8`(Ioniq5) `087fdca`(Ioniq9) `4443bd7`(Staria EV 신규등록)
- VW 전용 2건: `3056687` `a47b838`
- OS04C10(C4 카메라 센서) 전용 3건: `b580146` `698bb09` `738a0f1` -- C3 무관
- eGPU 전용 1건: `1131286`
- 문서/CI만 변경(런타임 무영향) 7건: `93cf545` `be27dd6` `53c2ef5` `4d76b53` `b18e0db` `ad76558` `2083c3b`

**추가 제외 확정 (코드 조회 후 죽은 분기/의존성 부재로 판정) -- 2건**
- `e32d389`(정지 시 CANFD 준비/재시도 기본화, carcontroller.py) -- `CP.flags & HyundaiFlags.CANFD` 게이팅 확인, DH2015는 비CANFD라 항상 거짓인 죽은 분기
- `dbe279b`(레이더 좌우반전 옵션) -- `radarcan.py` 의존, 그 파일이 carrot-ryu에 없음(9f8619b1, 129차 제외 결정에 자동 종속, 404 확인)

**검증 후 제외 (코드는 살아있으나 이 차량에서 항상 비활성) -- 1건**
- `feb1ce7`(CameraSCC hint, carstate.py) -- `camera_scc_hint_enabled = (HyundaiCameraSCC == 0) and not CAMERA_SCC_flag`로 게이팅. PARAMS_REGISTRY.md 기준 이 차량은 `HyundaiCameraSCC=1`이라 조건이 항상 거짓 -- 반영해도 효과 없는 죽은 분기.

**반영 완료 (git apply --check 실통과 + py_compile/JSON 검증, 172cha 스크립트로 push) -- 1건**
- `726198908c27a58a220f0bb581af137a492c6a63`(happymaj11r, 단축 `7261989`) "Reject stationary roadside pairs as corner cut-in motion evidence" -- radar_motion/controller.py, trajectory_cutin.py, cutin_validation_cases.json, 테스트 2개. carrot-ryu 현재 HEAD(`c6d8a206`)에 `git apply --check` 단독 통과 확인(로컬 bare 저장소 시뮬레이션까지 실행, numstat/커밋 결과 확인). py_compile 4개 파일 통과, JSON 유효성 통과. corner cut-in 오검출(정지 노변 물체를 컷인으로 오판)을 배제하는 방향이라 93~117차 종방향 커스텀 영역과 맞닿아 있음 -- 실차 검증은 미실시.

**반영 후보이나 실제 재검증 결과 충돌 발생 (다음 세션 수동 병합 필요, 보류) -- 2건**
- `ca60022`(정지 선행차, 연속 시각/전방 위치 증거로 L1 승격, radar_motion/primary.py + cutin_validation_cases.json) -- `git apply --check` 단독 실패. 원인: `cutin_validation_cases.json`의 `"cases": [` 직후 삽입을 시도하는데, carrot-ryu에는 이미 그 위치에 별도로 반영된 케이스(`k8-306-4-slow-left-suv-5227` 등)가 먼저 들어가 있어 컨텍스트가 어긋남(의미적 충돌 아님, 삽입 위치만 문제). primary.py 쪽은 아직 상세 대조 전.
  - 부수 발견: `ca60022`(primary.py) 검토 중, carrot-ryu의 primary.py에 이번 53건과 무관한 별도 미검토 항목(`STATIONARY_DISTINCT_HANDOFF` -- 정지 물체 근접 재식별 로직)이 있음을 발견. carrot-ryu에는 있지만 WIP_SYNC.md/FINDINGS.md 어디에도 검토 기록 없음 -- 별개 이월 항목으로 등록.
- `786c597`(lead braking 지속성, radar_motion/controller.py + 신규 lead_dynamics.py) -- `git apply --check` 단독 실패. 원인: `.github/workflows/carrot-route-vault-publish.yaml`의 46번째 줄 근방이 carrot-ryu에서 이미 달라져 있어 컨텍스트 불일치(CI 구성 차이로 추정, 상세 확인 전). controller.py 쪽은 `7261989`와 같은 파일을 건드리므로 `7261989` 반영 이후 base로 재확인 필요.

**중간 우선순위, 상세 대조 미실시 (다음 세션 이월) -- 4건**
- `1ae25ef`(radar path normals 안정화, predictor.py) -- 문서는 Carnival 사례지만 코드는 공용 파일. carrot-ryu 161~162차 자체 커스텀(곡률 슬루 제한/경로 소진 방지)과 같은 영역이라 수동 병합 필요.
- `0006296`(opt-in coasting margin, cereal/log.capnp) -- 스키마 변경 동반, longitudinal_planner.py(카롯 종방향 커스텀 최다 밀집 파일)와 겹쳐 신중한 수동 대조 필요.
- `c84b175`(cores 6/7 저우선순위 배치) -- 9f8619b1/3756e6d5 camera core5 트라이얼(`d384a57`/`c6cc00e` 시도 -> `9e1a5bf`로 업스트림 스스로 롤백)의 후속 정리. 26개 파일 대규모 변경이라 이번엔 상세 분석 미실시.
- `dcffb7f`(카메라 startup phase / Panda 펌웨어 매칭) -- C3 하드웨어 공통일 가능성 있으나 C++ 드라이버 레벨이라 별도 검토 필요.

**저위험 소규모 후보, 아직 미착수 -- 9건**
`cfe9251` `cf288c1` `828fc8c`(Carrot Web UI 안정화) / `9800be9` `288e212`(로그 표기·리부트 안내) / `b84621a` `cee4054`(AGNOS 자동 업데이트 설치/재시도) / `84aa7f0` `f0ee8f2`(navi 7713/7714 감속 관련, carstate.py -- 카롯 내비 감속 기능 영역이라 저위험으로 분류했지만 실제 검토는 필요)

- 다음 확인 시점: 다음 세션에서 위 "반영 후보이나 충돌" 2건부터 파일 단위 수동 병합, 이후 중간 우선순위 4건 순서로 진행.

## 체크포인트: 2026-09-22 (130차) -- carrot-ms 정기 점검, 신규 커밋 없음 확인(변경 없음)

- carrot-ryu HEAD: b3ac7c95fcf9db39800ec8e873e73e7def37a177 (변경 없음)
- carrot-ryu-note HEAD: 03078ceb65699a9838c16e7df404f52998a203eb (변경 없음, 129차 push 확인 완료 상태. 이 130차 devnotes 스크립트는 실행/push 대기)
- carrot-ms(happymaj11r/openpilot) HEAD: 3756e6d5702ff6ebd2c54d12f2e25e587dca4d99 (129차 체크포인트와 동일, `git ls-remote`로 재확인 -- 신규 커밋 없음)
- 다음 확인 시점: 다음 세션 시작 시 `git ls-remote`로 가볍게 재확인.

## 체크포인트: 2026-09-22 (129차) -- carrot-ms 9f8619b1/3756e6d5 최종 판단: 반영 보류(제외 확정), 128차 이월 2건 종결

- carrot-ryu HEAD: b3ac7c95fcf9db39800ec8e873e73e7def37a177 (변경 없음, 코드 변경 없는 세션)
- carrot-ms(happymaj11r/openpilot) HEAD: 3756e6d5702ff6ebd2c54d12f2e25e587dca4d99 (변경 없음, 128차 체크포인트와 동일)
- 128차에서 이월된 후보 2건(9f8619b1, 3756e6d5)의 최종 처리를 이번 세션에서 확정.

**9f8619b1** "Isolate radar CAN preprocessing from card and reduce fusion cost" -- happymaj11r/openpilot에서 커밋 패치를 직접 조회(github.com/.../commit/9f8619b1.patch, 18개 파일 +640/-54)하고, carrot-ryu 현재 HEAD(b3ac7c95)를 실제 `git clone`(blobless)한 뒤 `git apply --check`로 상세 대조(11절: 추측 아님). 결과: 핵심 코드 16개 파일(card.py/신규 can_batch.py·radarcan.py/radard_dpath.py/radar_motion/controller.py·predictor.py·trajectory_cutin.py/신규 테스트 3개/test_leads.py/process_replay.py/process_config.py/car.capnp) 전부 충돌 없이 적용됨(card.py/predictor.py/process_config.py는 우리 기존 dead-code 삭제분(radar_state 인자 제거, carrot_bluetooth 미등록, predictor 미사용 함수 2개)과 라인 오프셋만 있고 패치가 건드리는 영역과 겹치지 않음을 실제 diff로 확인). 적용 후 13개 Python 파일 `py_compile` 전부 통과, 저장소 전체 grep으로 `self.RI`/`RadarInterfaceBase`/`state_update()` 시그니처 등 외부 참조 0건까지 확인해 dangling reference 없음을 실증. 실패한 2개(`.github/workflows/tests.yaml`, `AGENTS.md`)는 CI 워크플로/carrot-ms 내부 메모 문서로 우리 차량 로직과 무관.

**[제외 확정, 사용자 승인 2026-09-22]** 코드 충돌은 없지만 다음 근거로 반영하지 않음:
1) 이 리팩터의 동기(EV9/Ioniq5의 card-camerad core6 스케줄링 경합으로 인한 카메라 프레임 드랍/IFE 에러, docs/radar_process_isolation.md)를 DH2015에서 관찰/진단한 적이 없음 -- 우리 실재 문제가 아니라 타 차량 증상 대응.
2) 원문서 자체가 "C3/C4 device timing/camera improvements are NOT yet validated"라고 명시 -- carrot-ms 쪽도 실기기 미검증 상태.
3) 새 프로세스(radarcan, core4 FIFO51)의 CAN/carState IPC 배치 결합(`MAX_INPUT_AGE_NS=100ms` 타임아웃 등)이 리드 감지 경로에 새로운 실패 지점을 추가함 -- 97~114차 종방향 게이팅(GATE_M 등)이 아직 실차 미검증 상태로 쌓여있는 시점에 같은 경로에 미검증 아키텍처 변경까지 겹치는 것은 10절 최소변경 원칙에 어긋남.
4) DH2015는 `EnableRadarTracks=0`/`EnableCornerRadar=0`으로 `RadarInterface.update_carrot()`이 SCC 고정 단일점만 다루는 가벼운 연산(93차 확정)이라, 이 리팩터로 얻는 core6 완화 효과가 우리 차엔 작을 가능성.

재검토 트리거: (a) carrot-ms/carrot-wip에 이 아키텍처의 실제 C3/C4 기기 검증 결과가 후속 커밋으로 올라올 때, (b) 우리 실차 로그에서 card/camerad 경합으로 인한 프레임 드랍 등 실제 증상이 관찰될 때.

**3756e6d5** "Trial camera and IRQ placement on core5 with UI on little cores" -- 128차에서 이미 9f8619b1(radarcan.py)에 구조적으로 종속됨을 확인(회귀테스트가 radarcan.py 존재를 전제). 9f8619b1 제외 확정에 따라 자동 제외(변경 없음).

이로써 128차에서 발견된 신규 10건(97~114차 이후 carrot-ms rebase분)이 전부 분류 종결됨: 128차 제외 8건(CAN FD 전용 4 + 테스트/무관 브랜드 1 + VW 전용 1 + 클러스터 2) + 129차 제외 2건(9f8619b1, 3756e6d5) = 10건 전부 제외, 반영 0건.

- 다음 확인 시점: carrot-ms HEAD가 3756e6d5에서 바뀌었는지 다음 2절 점검(129차 이후 세션)에서 git ls-remote로 확인.

## 체크포인트: 2026-09-22 (128차) -- carrot-ms 4bb4b510→3756e6d5 rebase 확인, 신규 10건 전수 분류(7건 제외 확정 · 2건 후보 이월)

- carrot-ryu HEAD: b3ac7c95fcf9db39800ec8e873e73e7def37a177 (변경 없음, 127차 test_latcontrol.py 수정/삭제 상태)
- carrot-ryu-note HEAD: ff34025bee37cceabada4af716b4c7e93d8838b1 (변경 없음, 127차 devnotes push 확인 완료 상태. 이 128차 devnotes 스크립트는 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
- carrot-ms(happymaj11r/openpilot) HEAD: 3756e6d5702ff6ebd2c54d12f2e25e587dca4d99 (이전 체크포인트 4bb4b510, 116차 대비 rebase 발생 -- `git merge-base --is-ancestor`로 4bb4b510이 3756e6d5의 조상이 아님을 확인, 0절에 명시된 "매번 재생성" 현상 실제 발생. 해시 체인 대신 커밋 메시지 기준으로 대조: 4bb4b510 쪽 400개 + 3756e6d5 쪽 410개 로그를 제목 기준 diff한 결과 OLD-only 0건(누락/스쿼시 없음, 비교 신뢰 가능) + NEW-only 10건 확인, 전부 2026-09-21 ajouatom 저자·carrot-wip cherry-pick)

10건 분류 결과(전부 개별 diff를 직접 열어 대조, 11절):

1) [제외, CAN FD 전용] e6baf4f9(CANFD 정지 준비/soft-hold, hyundaicanfd.py+CanfdStopRetry) / eebecda0(PV5 카메라 경고 수정, canfd_wrapped_navi 분기) / fb808e4e(PV5 카메라 상태 유지, 같은 함수 후속) / 3225e8c6(HUD lead 좌우 스무딩) -- 4건 전부 carcontroller.py 소스에서 `if self.CP.flags & HyundaiFlags.CANFD:` 블록 안 또는 canfd_wrapped_navi 전용 코드임을 diff로 직접 확인. DH 2015(HyundaiFlags.CHECKSUM_6B|LEGACY, 89차 확정)는 이 분기 자체가 실행되지 않는다.
2) [제외, 테스트/무관 브랜드] 9513408e -- process_replay 테스트 인프라(migration.py/process_replay.py) 정리 + KIA_EV6 안전플래그 이름 리네임(오타 수정). 런타임 동작 변화 없음.
3) [제외, VW 전용/사실상 무영향] 7ff3a457 -- radar_motion/timing.py에 신설된 front_radar_distance_delay_s()가 `car_params.brand == "volkswagen"`일 때만 0.0을 반환하고, 그 외(Hyundai 포함)는 기존 float(CP.radarDelay)에 max(0.0, ...) 클램프만 추가되어 사실상 동일하게 동작함을 diff로 확인.
4) [제외, 사용자 확인] c42437d9(Carrot Cluster L1 텍스트 크기 유지) / e2fe3e72(Carrot Cluster 스케줄링 우선순위 조정) -- 사용자가 Carrot Cluster(별도 raylib 보조화면) 기능을 사용하지 않고 향후 계획도 없음을 확인(2026-09-22).
5) [후보, 다음 세션] 9f8619b1 "Isolate radar CAN preprocessing from card and reduce fusion cost" -- RadarInterface/liveTracks를 card.py 동기 처리에서 core4 FIFO51 신규 워커(radar/radarcan.py, radar/can_batch.py)로 분리하는 브랜드 무관 아키텍처 리팩터. card.py/radar_motion/predictor.py/radar_motion/controller.py/radard_dpath.py를 함께 건드림 -- carrot-ryu의 기존 radar_motion 커스텀(93~95차 정지-lead 인계 검토 등)과의 충돌 여부를 상세 대조해야 해서 이번 세션엔 착수하지 않기로 함(사용자 승인, 2026-09-22).
6) [후보, 다음 세션 · 5)에 구조적으로 종속] 3756e6d5(현재 carrot-ms HEAD) "Trial camera and IRQ placement on core5 with UI on little cores" -- camerad+camera IRQ를 core6→core5로, UI 렌더링을 cores0~3으로 옮기는 실험적 배치. **독립 반영이 불가함을 코드로 확인**: 신규 회귀테스트(system/tests/test_camera_cpu_placement.py::test_camera_move_keeps_control_and_model_placements)가 `"openpilot/selfdrive/carrot/radar/radarcan.py": (4, "Priority.CTRL_LOW")`를 전제로 검증하는데, radarcan.py는 5)가 새로 만드는 파일이라 carrot-ryu 현재 HEAD(b3ac7c9)에는 아예 존재하지 않는다(raw 조회 404로 확인). 같은 날 커밋 순서(9f8619b1 10:41 -> 3756e6d5 22:13)로도 뒤 커밋이 앞 커밋 위에 쌓인 구조임을 확인했다. 또한 커밋 메시지/docs(camera_core5_trial.md) 자체가 "No target build or vehicle result is claimed"라고 명시하고, 대응 대상 증상도 아이오닉5 C4의 와이드카메라 SOF 갭(101ms)이라 DH2015+C3에는 재현 근거가 없다 -- 5) 반영 여부와 함께 다음 세션에서 재논의하기로 함.

- 다음 확인 시점: 5)/6) 두 항목의 반영 여부를 사용자와 논의할 때(5)를 먼저 검토하고, 반영하기로 하면 그 위에서 6)을 재검토, 5)를 반영하지 않으면 6)도 자동 보류). carrot-ms HEAD가 3756e6d5에서 다시 바뀌었는지는 착수 전 `git ls-remote`로 가볍게 재확인.

carrot-ms → carrot-ryu 동기화 이력 (carrot-ms는 매번 rebase되어 commit hash가 바뀌므로,
hash가 아닌 "커밋 메시지/내용 기준"으로 추적. 2절 참고)

## 체크포인트: 2026-09-21 (116차) -- carrot-ms 4bb4b510(camera_sync 스큐 허용오차 10ms→20ms) 적용 승인 및 반영 스크립트 준비

- carrot-ryu HEAD: 0e1bef52eb36eb01d683898be4561c243083c160 (변경 없음, 115차 dead code 배치 반영 상태). carrot-ms(happymaj11r/openpilot) HEAD: 4bb4b5104542f0f133c3034315d5f3786f90df84 (변경 없음, 신규 커밋 없음).
- 4bb4b510 개별 판단 갱신: [적용 승인] 115차에서 "후보, 반영 보류"로 남겨둔 4bb4b510을 상세 분석(diff, DH2015+C3X 실행 경로 추적, 10ms 하드리밋의 실패 사례 원인, 20ms 완화의 부작용 범위) 후 순수 upstream 버그 수정(콤마 C3X 기기 공통, 차량 브랜드/EV9 전용 아님)으로 재확인. 사용자 승인(2026-09-21).
- 반영 방식: camera_sync.py에 MAX_CAMERA_SKEW_NS 상수 추가 + 임계값 교체, test_camera_sync.py에 회귀 테스트 4종(파라미터라이즈 포함 10 케이스) 추가. carrot-ms 4bb4b510 파일과 byte-exact 동일하게 반영 예정(상세는 WIP.md 116차 참고). 사용자 스크립트 실행 대기 -- push 확인 전까지 "반영 완료"로 간주하지 않는다(16절).
## 체크포인트: 2026-09-21 (115차 계속) -- 2절 7번 항목("모델셀렉터와 무관한 커밋 기본 제외") 폐지

- carrot-ryu-note push 2358da1(2절 2번 항목 carrot-wip 배타 필터 폐지 + 아래 115차 체크포인트) 이후 추가 반영. carrot-ryu HEAD fa75aeab(변경 없음), carrot-ms HEAD 4bb4b510(변경 없음).
- 사용자 승인(2026-09-21): 2절 7번 항목도 2번 항목과 같은 취지로 폐지. 모델셀렉터 관련 여부(클러스터 HUD, PC 시뮬레이터 등 커밋 종류)로 신규 커밋을 미리 제외하지 않고, 전부 개별 분석해 제외 시 사유를 이 파일에 기록한다. 반영은 계속 사용자 승인 후에만(4번). PROJECT_INSTRUCTIONS_carrot-ryu.md 2절 7번 항목 갱신(19절 절차).
- 참고: 16절 "carrot-ms에 새 커밋(모델셀렉터 관련)이 있는데 ..." 문구와 1절 표의 "콤마 모델셀렉터" 설명은 이번에 바꾸지 않았다(범위 밖, 필요하면 별도 논의).

## 체크포인트: 2026-09-21 (115차) -- 2절 carrot-wip 배타 필터 폐지, carrot-ms 신규 1건(4bb4b510) 후보 기록

- carrot-ryu HEAD: fa75aeab7b63233db4c4942021675f0536ee7160 (변경 없음)
- carrot-ms(happymaj11r/openpilot) HEAD: 4bb4b5104542f0f133c3034315d5f3786f90df84 (111차 체크포인트 a23a77b 대비 신규 1건, git 프로토콜로 재확인)
- 신규 1건: 4bb4b510 "Tolerate bounded camera timestamp jitter without dropping valid EV9 frames" -- carrot-wip(ajouatom/openpilot) 현재 HEAD(d2973b3f)의 cherry-pick으로 확인(git show -s로 동일 제목/해시 대조). 기존 2절 필터("carrot-wip에 없고 carrot-ms에만 있는 커밋만 추린다")를 그대로 적용했다면 자동 제외됐을 커밋.
- 2절 필터 폐지(사용자 승인, 2026-09-21): 위 4bb4b510을 실제로 열어본 결과 openpilot/selfdrive/modeld/camera_sync.py의 receive_camera_pair() 카메라 SOF 페어링 허용오차를 10ms 고정값에서 20ms bounded로 완화하는 변경이었고, 이 함수는 openpilot/selfdrive/modeld/modeld.py와 carrot/model_selector/carrot_modeld.py 양쪽 실행경로에서 호출되며 use_extra_client 조건(와이드카메라 보유 여부로 결정되는 일반 로직, eGPU/EV9 전용 게이트 아님)에 걸림 -- carrot-wip에 이미 있다는 사실만으로 내 차량 관련성을 미리 걸러내면 안 된다는 것이 실증됨. 앞으로는 carrot-ms 체크포인트 이후 신규 커밋 전체를 개별 분석한다(PROJECT_INSTRUCTIONS_carrot-ryu.md 2절 갱신, 19절 절차).
- 4bb4b510 개별 판단: [후보, 반영 보류] carrot-ryu 현재 camera_sync.py blob(b810d2aa)이 이 커밋의 pre-image blob과 byte-exact 일치 확인(git hash-object) -- 반영한다면 상수 1개 추가 + 1줄 교체뿐인 깔끔한 단일 파일 변경. 다만 커밋 메시지 자체가 "Vehicle validation remains outstanding"이라고 명시해 upstream도 실차 미검증 상태 -- 사용자 판단으로 이번 세션엔 반영하지 않고 후보로만 기록.
- 다음 확인 시점: carrot-ms HEAD가 4bb4b510에서 다시 바뀌었는지, 또는 사용자가 4bb4b510 반영 여부를 다시 논의할 때.

## 체크포인트: 2026-09-20 (111차) -- carrot-ms e324f67 이후 신규 21건 전수 분류, 전부 반영 보류 확정

- carrot-ryu HEAD: a430d114f17e8b9579392071f7828324cc8bb329 (변경 없음, 110차 GATE_M_LO/HI 0.8/1.0. 이번 세션은 재검증만 수행: SHA 고정 조회로 long_mpc.py 70행 확인 + 격리 환경에서 test_lead_gate_margin.py 재실행 8 passed)
- carrot-ryu-note HEAD: bf20985ed47844ed7fa5af3865e6dac314f8c38f (110차 devnotes push 확인 완료. 이번 111차 devnotes 반영은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
- carrot-ms(happymaj11r/openpilot) HEAD: a23a77b1aa8b007d6b22bb19f2a1992b84d9b7d4 (이전 체크포인트 e324f67, 93/95차 확정 대비 신규. `git rev-list --count e324f67..a23a77b` = 21건. 21건 전부 `git merge-base --is-ancestor`로 carrot-wip(ajouatom/openpilot) HEAD 2723a8eba98404c4fa86701a2d2a49543a1028e9에 없음을 확인 -- carrot-ms 고유 추가분(모델셀렉터/부가기능)임을 확인)
- 21건 분류(전부 제외, 사용자 승인 2026-09-20):
  1) 블루투스 리모컨(Cinque v3) 페어링/HID/크루즈 제스처 11건(6ec3369/5bad3dd/5e595fd/471b477/fedc90c/a7c6e38/5077775/a5b5c64/532d866/794bfdb/6ea8936) -- [제외] 사용자가 해당 리모컨 미보유 확인
  2) Cinque v3 하드웨어 통합/브랜치 정리 3건(d4599bf/851bccb/7624951) -- [제외] 1)과 세트, 하드웨어 종속
  3) World Model 실험 브랜치 기록 2건(079bf07/0b33895) -- [제외] AGENTS.md 문서만 수정, 코드 변경 없음("no user-facing behavior changes")
  4) Hyundai 리드 표시 횡위치 보정 1건(8b5a9ae) -- [제외] opendbc_repo/opendbc/car/hyundai/hyundaicanfd.py만 수정(CAN FD 전용). DH 2015는 HyundaiFlags.CHECKSUM_6B|LEGACY로 CAN FD 미해당(89차 확정) -- 기존 f19d404/8e85a02/5ae4a25와 동일 근거
  5) C3 eGPU 이미지 준비/워프 검증 4건(4ecede0/cd6dfef/495caf5/a23a77b) -- [제외] 사용자가 eGPU 미보유 확인
- AGNOS_VERSION 별도 확인: launch_env.sh가 5bad3dd에서 "19.6.3-carrot" -> "19.8-carrot-bt1"로 바뀌어 a23a77b까지 그대로 유지됨. 커밋 메시지("Trial AGNOS 19.8 native Bluetooth with pinned Cinque v3 runtime")와 후속 문서(5e595fd, "remote input validation pending")로 볼 때 범용 안정판이 아니라 Cinque v3 블루투스 리모컨용 트라이얼 빌드임을 확인 -- 1)과 같은 사유로 제외.
- 다음 확인 시점: carrot-ms HEAD가 a23a77b에서 다시 바뀌었는지 다음 2절 점검 때 git ls-remote로 확인. carrot-ms가 "-bt1"이 아닌 안정판 AGNOS 19.8(또는 그 이상)을 내놓으면 재검토.
## 체크포인트: 2026-09-19 (95차) -- carrot-ms e324f67 이후 신규 커밋 없음 재확인, carrot-ryu 25f21d4 디바이스 실배포 확인(20절 7항)

- carrot-ms(happymaj11r/openpilot) HEAD: e324f6735d3606800045ed6b28f41e79b17e5498 (변경 없음, git ls-remote 재확인 -- 93차 체크포인트와 동일)
- 디바이스 배포 확인: 사용자가 도구 탭 "브랜치 변경"(브랜치 목록에서 carrot-ryu 재선택 -> 재체크아웃/재빌드)으로 origin/carrot-ryu 전환 실행. 사용자 업로드 tmux 로그 2건(변경 전/후)의 metadata.json git_commit + tmux.log 부팅 로그("Carrot GitBranch = ...")로 carrot-ryu-v1(c81aef07) -> carrot-ryu(25f21d406d23bfb79ad45a67890cc39e3ad9e67b, 93차 최종 HEAD와 일치) 전환을 직접 재확인. 디바이스가 61차 force reset으로 히스토리가 갈라져 있어 git pull이 아니라 "브랜치 변경"(재체크아웃)이 필요했음을 사용자가 확인.
- 첫 실차 UI 검증 결과 상세는 CURRENT_STATUS.md 95차 계속 참고(스크린샷 캡처 체인 항목30~36 + 경로안내 박스 항목13~19 첫 실차 확인).
- 다음 세션 우선순위: 항목1·2 및 carrot-ms 4건(b4f751f4 등, 종방향 관련)의 실주행 검증, 사용자 업로드 route 로그(qcamera.ts+rlog.zst) 분석 목적 확인 후 진행.

## 체크포인트: 2026-09-19 (93차 계속) -- 557e6f6a 반영 완료 확인, e324f67 제외 확정, 89차 검토대상 4건 종결

- carrot-ryu HEAD: 25f21d406d23bfb79ad45a67890cc39e3ad9e67b (93cha: reapply carrot-ms 557e6f6a, 부모 9eced40. `git ls-remote`+blobless clone으로 재검증: 변경 파일 1개 +3/-1, 결과 blob d04b52ce89e5가 원본 post-image와 일치)
- carrot-ryu-note HEAD: bd69ab0139874c7e36d6f58552923a291fc98a92 (93차 devnotes push 확인 완료, 4개 파일 sha256 일치. 이 devnotes 스크립트 실행/push 대기)
- carrot-ms(happymaj11r/openpilot) HEAD: e324f6735d3606800045ed6b28f41e79b17e5498 (변경 없음, `git ls-remote` 확인)
- 89차 검토대상 4건 처리 현황(최종):
  1) b4f751f4 -> [반영 완료] carrot-ryu 260565f
  2) 4d1a3ded -> [반영 완료] carrot-ryu f1e920d
  3) ec95363a -> [반영 완료] carrot-ryu 9eced40
  4) 557e6f6a -> [반영 완료] carrot-ryu 25f21d4
- e324f67(정지 lead 인계) -> [제외 확정, 사용자 승인] 새 분기는 서로 다른 레이더 점 2개가 있어야 하는데, 이 차량 설정(HyundaiCameraSCC=1, EnableRadarTracks=0, EnableCornerRadar=0)에서는 `radar_interface`가 SCC 고정 ID 점 하나만 발행해 발동 불가. 재검토 트리거: EnableRadarTracks>0 또는 EnableCornerRadar 활성화. 상세는 WIP.md 93차 계속.
- 61차 리셋 이후 carrot-ms 신규 16건 전부 분류 종결: 반영 4건 + 제외 12건.
- 다음 세션 우선순위: carrot-ms에 e324f67 이후 신규 커밋이 있는지 확인(2절) -> 없으면 36개 항목 + 재적용분 실차 검증 준비.

## 체크포인트: 2026-09-19 (93차) -- ec95363a push 확인, 557e6f6a 상세 대조 완료·반영 스크립트 준비

- carrot-ryu HEAD: 9eced40e12dba9ecaa71fe4bd25a812d39d956ce (92cha: reapply carrot-ms ec95363a, 부모 f1e920d. `git ls-remote`+blobless clone으로 재검증: 변경 파일 8개 +185/-39, 8개 결과 blob이 원본 patch post-image와 전부 일치). 557e6f6a 반영 스크립트 `93cha_item_557e6f6a_carrot_ryu.ps1` 실행/push 대기(HEAD 변경 전).
- carrot-ryu-note HEAD: 1f983041cd7d662f6aaae789d77c0030a1ca2190 (92차 devnotes push 확인 완료, 이 devnotes 스크립트 실행/push 대기)
- carrot-ms(happymaj11r/openpilot) HEAD: e324f6735d3606800045ed6b28f41e79b17e5498 (변경 없음, `git ls-remote` 확인)
- 89차 검토대상 4건 처리 현황(갱신):
  1) b4f751f4 -> [반영 완료]
  2) 4d1a3ded -> [반영 완료]
  3) ec95363a -> [반영 완료] carrot-ryu 9eced40 (92차 스크립트 실행 결과를 93차에서 push/blob 재검증)
  4) 557e6f6a -> [상세 대조 완료, 반영 스크립트 준비, 실행/push 대기] precompiled_worker.py 1파일(+3/-1). pre-image blob(1c2e2a3b5e)이 carrot-ryu 9eced40과 byte-exact 일치, 신규 참조 값(width/height/input_bytes/manifest['format']/manifest['pickle']['sha256']) 모두 정의·존재 확인, 적용 결과 blob d04b52ce89가 원본 post-image와 일치, py_compile 통과. pytest 미실시.
- e324f67(정지 lead 인계): 판단 이월 그대로.
- 다음 세션 우선순위: 557e6f6a 반영 스크립트 실행/push 확인 -> e324f67 필요 여부 판단 -> 36개 항목+재적용분 실차 검증.

## 체크포인트: 2026-09-19 (92차) -- ec95363a 상세 대조 완료, 반영 스크립트 준비

- carrot-ryu HEAD: f1e920d5c391d3ce44f647f29913a8b996a1a7c2 (변경 없음, ec95363a 반영 스크립트 `92cha_item_ec95363a_carrot_ryu.ps1` 실행/push 대기)
- carrot-ryu-note HEAD: 521f0ebc55d363c8f3335d62799fafb87bd070da (91차 계속2 기준, 이 devnotes 스크립트 실행/push 대기)
- carrot-ms(happymaj11r/openpilot) HEAD: e324f6735d3606800045ed6b28f41e79b17e5498 (변경 없음)
- 89차 검토대상 4건 처리 현황(갱신):
  1) b4f751f4 -> [반영 완료]
  2) 4d1a3ded -> [반영 완료]
  3) ec95363a -> [상세 대조 완료, 반영 스크립트 준비, 실행/push 대기] 6개 기존 파일의 pre-image blob이 carrot-ryu 현재 blob과 byte-exact 일치(90차 b4f751f4가 건드린 model_renderer.py 포함 -- 시간순 충돌 없음 확인), 신규 파일 2개(render_diagnostics.py/test_render_diagnostics.py)는 미존재 확인. 별도 clone에서 `git apply --check` 통과, 적용 후 8개 파일 py_compile 전부 통과. pytest는 샌드박스 컴파일 의존성 부재로 미실시.
  4) 557e6f6a -> [미반영] ec95363a 다음 순서, precompiled_worker.py 1파일(+3/-1)
- e324f67(정지 lead 인계): 판단 이월 그대로.
- 다음 세션 우선순위: ec95363a 반영 스크립트 실행/push 확인 -> 557e6f6a 착수 -> e324f67 필요 여부 판단.

## 체크포인트: 2026-09-19 (91차 계속2) -- carrot-ms 4d1a3ded 반영 완료 확인

- carrot-ryu HEAD: f1e920d5c391d3ce44f647f29913a8b996a1a7c2 (91cha-2: reapply carrot-ms 4d1a3ded, 부모 260565f. `git ls-remote`+별도 clone으로 재검증 완료)
- carrot-ryu-note HEAD: 34c5c9bb13af6e64edc793aaf0462f47e48d0cb0 (91차 계속 devnotes push 확인 완료)
- carrot-ms(happymaj11r/openpilot) HEAD: e324f6735d3606800045ed6b28f41e79b17e5498 (변경 없음)
- 89차 검토대상 4건 처리 현황(갱신):
  1) b4f751f4 -> [반영 완료] carrot-ryu 260565f (90차, 91차에서 검증)
  2) 4d1a3ded -> [반영 완료] carrot-ryu f1e920d (91차 계속에서 스크립트 작성, 91차 계속2에서 push/blob/계약 재검증 완료)
  3) ec95363a / 557e6f6a -> [미반영] 다음 순서. ec95363a는 착수 전 상세 대조 필요(augmented_road_view.py/road_markings.py 레인 대시 영역, render_diagnostics.py 신규 파일, 테스트 파일 4개; 변경 파일 8개 +185/-39). 557e6f6a는 openpilot/selfdrive/modeld/precompiled_worker.py 1파일(+3/-1).
- 계약 재점검(샌드박스, check_contracts.py, carrot-ryu f1e920d 기준): modeld-mirror PASS(반영 전 260565f는 FAIL). 나머지 FAIL 4건은 tinygrad_repo 부재로 인한 샌드박스 한계이며 반영 전후 동일.
- e324f67(정지 lead 인계): 판단 이월 그대로.
- 다음 세션 우선순위: ec95363a 상세 대조(변경 8개 파일, augmented_road_view.py/road_markings.py/render_diagnostics.py 우선) -> 반영 여부 정리 -> 승인 시 9절 방식 착수. 이후 557e6f6a, e324f67 필요 여부 판단.
## 체크포인트: 2026-09-19 (91차 계속) -- carrot-ms 4d1a3ded 반영 준비, 스크립트 실행/push 대기

- carrot-ryu HEAD: 260565f187a2d934f0e27464457eee63c8ec233a (변경 없음. 4d1a3ded 반영 스크립트 `91cha2_4d1a3ded_carrot_ryu.ps1` 실행/push 대기 -- 다음 세션이 `git ls-remote`로 실제 HEAD를 확인할 것)
- carrot-ryu-note HEAD: b55388c6b700885b0c3f5bde66e9e6f3618adf8c (91차 devnotes 반영 확인 완료)
- carrot-ms(happymaj11r/openpilot) HEAD: e324f6735d3606800045ed6b28f41e79b17e5498 (91차와 동일)
- 89차 검토대상 4건 처리 현황:
  1) b4f751f4 -> [반영 완료] carrot-ryu 260565f (90차, 91차에서 검증)
  2) 4d1a3ded -> [반영 스크립트 준비, 실행/push 대기] 사용자가 처리 순서를 Claude 판단에 위임(2026-09-19). 90차 반영으로 `modeld-mirror` 계약(check_contracts.py)이 FAIL인 상태를 해소하는 직접 후속이라 먼저 선택.
  3) ec95363a / 557e6f6a -> [미반영] 반영 승인 기록 없음. 4d1a3ded 다음 순서로 진행 예정이며 ec95363a는 착수 전 상세 대조 필요(augmented_road_view.py/road_markings.py 레인 대시 영역, render_diagnostics.py 신규 파일, 테스트 파일 4개; 변경 파일 8개 +185/-39). 557e6f6a는 openpilot/selfdrive/modeld/precompiled_worker.py 1파일(+3/-1).
- 4d1a3ded 상세(happymaj11r Hermes Agent, 2026-09-18): "Adapt model selector mirror to shared camera pairing". carrot/model_selector/carrot_modeld.py(미러)에서 자체 FrameMeta와 25 ms 고정 수신 루프를 제거하고 공유 camera_sync.receive_camera_pair()를 호출. carrot/model_selector/upstream_baseline/modeld.py.baseline 스냅샷은 check_contracts.py --sync-baselines로 갱신됨(parse_model_outputs.py.baseline은 변경 없음). +11/-80, 파일 2개. 의도적 미포팅: precompiled_runner의 fused backend publish, dropped-frame 로그 문구(미러는 prepare_only에서 정책 추론을 건너뛰므로 기존 문구가 정확).
- 충돌위험 사전 확인: 두 파일의 4d1a3ded 직전(pre-image) blob이 carrot-ryu 260565f blob과 동일(carrot_modeld.py 1d9eb7ecc5409f7eca1bed94d8911fd13615325e, modeld.py.baseline 59ea2ab20b420acc54875cde6914600f2d07f882). 스크립트의 Replace-Block 블록(3개+4개)을 pre-image에 순차 적용한 결과가 4d1a3ded의 blob(9a5a62c678b5f4ce5fef789e28e2a6ec3c870da1 / 2ebe83365471da975dfb005b986ead5b7baa0dad)과 byte 일치함을 확인.
- 계약 점검(샌드박스, check_contracts.py): modeld-mirror -- carrot-ms b4f751f4 FAIL / carrot-ms 4d1a3ded PASS / carrot-ryu 260565f FAIL. 나머지 FAIL 4건은 tinygrad_repo 부재(샌드박스 한계)로 세 상태 동일. 반영 후 carrot-ryu에서 modeld-mirror가 PASS가 되는지는 반영 뒤 재확인 대상.
- 영향 범위: 모델 셀렉터 미러(carrot_legacy) 경로만. DH 2015에서 이 경로가 실제로 쓰이는지는 미확인. 미러가 쓰이지 않는다면 동작 영향은 없고 계약 baseline 정합만 맞춰진다.
- e324f67(정지 lead 인계): 판단 이월 그대로.
- 정정: 앞 91차 체크포인트의 "기지 이슈"(이 파일의 널바이트 1개)는 이번에 정정했다(널바이트 + 2015190f58a4380a433ee0130e6374455dddc2e -> 02015190f58a4380a433ee0130e6374455dddc2e).
- 다음 확인 시점: 사용자가 반영 스크립트를 실행한 뒤 `git ls-remote`로 carrot-ryu HEAD 확인 -> 부모가 260565f이고 변경 파일이 2개뿐인지 확인하고, 이 파일의 4d1a3ded 항목을 "반영 완료"로 갱신. 이후 ec95363a 착수 전 상세 대조.
## 체크포인트: 2026-09-19 (91차) -- 90차 코드 push(b4f751f4 재적용) 사후 동기화/검증, carrot-ms 신규 1건(e324f67) 발견

- carrot-ryu HEAD: 260565f187a2d934f0e27464457eee63c8ec233a (부모 0923f83. 90차 커밋 1개 추가: "90cha: reapply carrot-ms b4f751f4 - camera pair sync, curve release confirm window, path_geometry extraction", 2026-09-19 13:06 +0900). 이번 세션은 코드 미변경.
- carrot-ms(happymaj11r/openpilot) HEAD: e324f6735d3606800045ed6b28f41e79b17e5498 (89차 체크포인트 f19d404a 대비 1건 추가, `git rev-list --count f19d404a..HEAD` = 1)
- 89차 검토대상 4건의 처리 현황:
  1) b4f751f4 -> [반영 완료] carrot-ryu 260565f (90차). 이번 세션에서 원본과 독립 대조 검증(아래).
  2) 4d1a3ded / ec95363a / 557e6f6a -> [미반영] 반영 승인 기록 없음. 커밋 발생 순서(4d1a3ded -> ec95363a -> 557e6f6a)대로 사용자 승인 후 착수. ec95363a의 augmented_road_view.py/road_markings.py 레인 대시 영역과 render_diagnostics.py 신규 파일은 착수 전 상세 대조 필요(89차 이월 사항 그대로).
- b4f751f4 반영 검증(정적/샌드박스, 실차 아님): carrot-ms b4f751f4 패치와 carrot-ryu 260565f 패치를 index 줄 제외하고 diff -- 15개 파일 660줄 동일, 차이는 carrot_man.py 헝크 헤더 시작 줄번호 1줄(1457 vs 1481, carrot-ryu 쪽 위치가 24줄 뒤)뿐. 변경 .py 11개 py_compile 통과, 단위 테스트 47개(camera_sync 5/path_geometry 8/curve_speed 22/precompiled_runner 12) 통과. 90차 세션 자체의 승인/검증 경위는 devnotes에 기록이 없어 확인하지 못했다.
- 신규 e324f67 (ajouatom, 2026-09-19 08:22 +0900, "(cherry picked from commit 1130b07462259e1f6c3950bbe4aeef3b8adc6c61)"): 정지 상태로 유지되던 전방 레이더 lead를 5 m object-spacing 게이트 밖에서도 비전 lead로 인계하는 조건을 추가(비전 매처가 고품질 전방 타깃을 선택하고, 거리/횡방향 비용이 유리하며, 비전 거리 오차가 2.5 m 이하이고 유지 오차의 절반 이하이며, 0.5 s 지속될 때만). 변경 파일 2개(openpilot/selfdrive/carrot/radar_motion/primary.py +29, tests/test_radar_motion_predictor.py +85, 합계 +112/-2).
  - 분류: CAN FD/Group3 전용이 아닌 radar_motion 공용 코드라 제외 근거(values.py 플래그 기준)가 성립하지 않는다 -> [검토대상, 보류]. DH 2015(LEGACY)가 이 경로를 실제로 타는지와 필요 여부는 아직 판단하지 않았다.
  - 충돌위험 사전 확인: 두 파일의 carrot-ms e324f67 직전(pre-image) blob과 carrot-ryu 260565f의 blob이 동일(primary.py 59a10980f606b378aee66b36ef6be19d9bf9d6b8, test_radar_motion_predictor.py 3783b522c130bd7e2a8b663c9f25dc7b7880562a) -- 반영하기로 결정되면 충돌 없이 적용 가능한 상태. 반영 여부는 사용자 결정.
- 기지 이슈(이번 세션 미정정): 이 파일 116행에 널바이트 1개(57차 항목 fork point 해시 자리, 정상 표기 02015190f58a4380a433ee0130e6374455dddc2e). 정정 여부는 사용자 결정.
- 다음 확인 시점: 남은 3건(4d1a3ded -> ec95363a -> 557e6f6a) 및 e324f67의 반영 여부를 사용자와 정할 때. carrot-ms HEAD가 e324f67에서 다시 바뀌었는지는 착수 전 `git ls-remote`로 가볍게 재확인.
## 체크포인트: 2026-09-19 (89차) -- carrot-ms 신규 15건(706efb47 이후) 전수 분석, 반영은 다음 세션 이월

- carrot-ryu HEAD: 0923f8396dacbb61a23e1c394751d8014ddddf5f (변경 없음, 코드 미변경 -- 이번 세션은 분석/기록만)
- carrot-ms(happymaj11r/openpilot) HEAD: f19d404a47a24806f876ee9d2148c112655816d2 (88차 994683d5 대비 2건 추가 확인: 8e85a02/f19d404a)
- 마지막 검토 완료 체크포인트(706efb47, 61차 20절 리셋 베이스) 대비 GitHub compare API 기준 ahead_by 15, 88차에서 처음 발견된 13건 + 이번에 추가 확인된 2건 = 총 15건. api.github.com rate limit(60/시간) 소진으로 이번 세션은 `git clone --filter=blob:none`(partial clone) 방식으로 커밋별 diff를 직접 대조했다(bash_tool 있는 세션의 대체 수단, 0단계 원칙과 별개).
- 우리 차량(HYUNDAI_GENESIS = 제네시스 DH 2015-16)의 values.py 플랫폼 정의를 재확인: `flags=HyundaiFlags.CHECKSUM_6B | HyundaiFlags.LEGACY`로, CAN FD/RADAR_GROUP3 플래그 모두 없음을 확정.

15건 분류 결과:
1) [제외, CAN FD 전용] 0beb200a/de6ee634/a6c8220/34cf65fb (CAN FD stop retry 실험+게이팅+주행중 설정반영) -- carcontroller.py에 필드가 추가되나 CAN FD 분기(hyundaicanfd.py) 안에서만 소비되어 LEGACY(비-CANFD) 차량인 DH에는 동작 영향 없음.
2) [제외, CAN FD 전용] 5ae4a25(CAN FD SCC HUD leadOne)/8e85a02(CCNC 전방객체 leadOne)/f19d404a(Hyundai CAN FD 표시 nearest lead) -- 전부 hyundaicanfd.py/CCNC 한정.
3) [제외, Radar Group3 전용] ee8d4353(Group3 레이더 객체ID CAN 슬롯 이동 버그수정) -- DH는 RADAR_GROUP3 플래그 미설정, radar_interface.py의 group3 분기 자체가 우리 차량 경로에서 호출 안 됨.
4) [제외, CI/문서/테스트픽스처] 845e725b(.github/workflows tests.yaml만 수정, 1절 원칙상 로컬 clone 작업이라 CI 무관) / 21b71f00(AGENTS.md 문서 5줄) / 994683d5(EV9 전용 cutin_validation_cases.json 회귀 테스트 데이터 추가, 코드 동작 변화 없음).
5) [검토대상, 보류 -- 사용자 결정으로 이번 세션엔 코드 미반영] b4f751f4(카메라 프레임 페어링 버그수정: 25ms 미만 간격 거부 문제 해소 + 커브 탈출시 0.25초 확인 윈도우로 조기 해제 방지 + path 투영코드를 path_geometry.py로 추출, 동작 동일/성능만 개선) / 4d1a3ded(위 리팩터에 맞춘 model_selector 미러 carrot_modeld.py 동기화, 6절 침습지점 관리 원칙) / ec95363a(레인 대시 렌더링 배치 처리 + UI 진단로그 추가, 렌더 결과물 동일) / 557e6f6a(모델 워커 진단로그 1줄 추가).
   - 충돌위험 사전 확인: 위 4건이 건드리는 정확한 함수/파일(model_renderer.py의 _build_path_polygon_update_line_data2_carrot / _dist_carrot / _dist3_carrot 3개, modeld.py 프레임 수신부, curve_speed.py의 VisionCurveSpeed 클래스)을 carrot-ryu 현재 코드(0923f83 기준)와 diff 대조한 결과 **byte-identical(fork 이후 무수정)**임을 확인 -- 순수 리팩터/버그수정이라 우리 커스텀과 충돌 없이 적용 가능할 것으로 판단됨. 단, ec95363a가 건드리는 augmented_road_view.py/road_markings.py 레인 대시 영역과 render_diagnostics.py 신규 파일은 이번 세션에서 상세 대조는 하지 않음(다음 반영 착수 세션에서 필요).
- 사용자에게 4건 반영 여부를 문의한 결과, "코드 반영 없이 WIP_SYNC.md 기록만 먼저" 진행하기로 결정. 실제 반영(9절 방식)은 다음 세션 이후 별도 승인 하에 착수.
- 다음 확인 시점: 위 4건(b4f751f4→4d1a3ded→ec95363a→557e6f6a 순, 커밋 발생 순서) 반영을 착수할 때 -- ec95363a의 augmented_road_view.py/road_markings.py 상세 대조부터 시작. 또는 carrot-ms HEAD가 f19d404a에서 다시 바뀌었는지 가벼운 git ls-remote 점검할 때.
## 체크포인트: 2026-09-17 (64차) -- 20절 이식 항목 4(13차 원본: 시계 좌측 경계 잘림 수정) 재적용

- carrot-ryu HEAD: 4e3b44a81f2fc79c3b6f23ebaee40a1bc73d370b (63차 429f105e 위에 13차 원본
  재적용 커밋 1개 추가)
- 63차에서 이월된 이식 후보 중 항목 4(13차, 2adced8 기준)를 새 베이스 위에 재적용, commit
  4e3b44a8로 push 완료. 원본이 작은 단일 함수 diff였고 12차 재적용 이후 해당 함수가 변경되지
  않아, Replace-Block으로 그대로 적용해 원본과 결과 blob까지 완전히 일치시킴.
- git ls-remote + commit diff로 반영 내용이 원본 13차 커밋과 정확히 일치함을 확인.
- 다음 확인 시점: 다음 이식 대상(스크린샷 후속 수정 / Google Drive 파이프라인 / 종방향 안전장치
  등) 순서를 다음 세션에서 사용자와 정할 것.

## 체크포인트: 2026-09-17 (63차) -- 20절 이식 항목 3(12차 원본: 시계 초단위+스크린샷 버튼) 재적용

- carrot-ryu HEAD: 429f105e16853b5230d7eb7a082de2b817a3d8e9 (62차 706efb47 위에 12차 원본
  재적용 커밋 1개 추가)
- 62차에서 이식 대상으로 확정된 "코드 수정 현황" 항목 3(12차, 684b30d 기준)을 새 베이스 위에
  재적용, commit 429f105e로 push 완료. 착수 스크립트가 CRLF/LF 불일치로 한 차례 중단됐다가
  원인(저장소 루트 .gitattributes의 "* text=auto") 확정 후 Replace-Block에 CRLF->LF 정규화를
  추가해 재시도, 성공적으로 반영됨.
- git ls-remote + commit diff로 반영 내용이 의도한 3개 파일(hud_renderer.py 7곳, 신규 파일 2개)과
  정확히 일치함을 확인.
- 12차 "원본" 그대로이며, 이후 세션들에서 누적된 스크린샷 관련 후속 수정(항목 25·26~28·30~36번)은
  아직 미반영. 다음 확인 시점: 이 항목들을 언제/어떤 순서로 이어서 반영할지 다음 세션에서 결정.

## 체크포인트: 2026-09-17 (62차) -- 61차 코드 리셋(carrot-ryu=carrot-ms) 결과를 devnotes에 사후 동기화

- carrot-ryu HEAD: 706efb47b81cf9cb02888ee536a156d8f1fc1d91 (carrot-ms와 동일. 리셋 이전 HEAD 9ccf1206은 carrot-ryu-v1에만 보존)
- 직전 61차 세션에서 20절 리셋(carrot-ryu를 carrot-ms 현재 HEAD로 force-push)을 실제로 실행·push까지 완료했으나, 뒤이어 준비하던 devnotes 61차 갱신 스크립트는 무료 사용량 소진으로 사용자에게 전달되지 못한 채 세션이 끊김.
- 62차 세션 시작 시 4절 0단계 재확인 과정에서 코드 브랜치(706efb47, 이미 리셋됨)와 devnotes(60차 상태, ff9d0e77 그대로)가 서로 다른 시점을 가리키는 것을 16절 원칙에 따라 발견·보고, 사용자 확인 후 devnotes를 코드 브랜치 실제 상태에 맞춰 사후 동기화.
- 이 시점부터 carrot-ryu에는 지금까지의 커스텀 코드(carrot-ryu-v1의 "코드 수정 현황" 36개 항목)가 전혀 없는 상태. 기존 2절 개별 선별 반영 이월분(종방향/Hyundai CAN/eGPU 클러스터 등)은 carrot-ms 최신 베이스에 이미 포함된 것으로 간주해 20절 리셋으로 흡수, 별도 반영 불필요.
- 다음 확인 시점: 36개 항목 이식을 세션별로 진행할 때마다 해당 항목의 재반영 여부를 이 파일에 기록. 이식이 상당 부분 끝나기 전까지 디바이스 git pull 금지 상태 유지.


## 체크포인트: 2026-09-16 (60차) -- devnotes 파일 오염 발견 및 복구

- carrot-ryu HEAD: 9ccf1206a034c5fb5e5f35201553f9fc4e5237e5 (변경 없음, 코드 미변경)
- carrot-ms(happymaj11r/openpilot) HEAD: 904fd107b529f4636846bedcf645e102fce007b7 (59차와 동일, 변경 없음)
- 이번 세션 본래 목적(20절 리셋 착수 여부 확인)과 별개로, 세션 시작 시 SHA 고정 조회 중
  devnotes/HANDOFF.md(59차분)에 이 WIP_SYNC.md 전체 내용이 PowerShell 히어스트링 조각과
  함께 잘못 이어붙어 있고, 실제 devnotes/WIP_SYNC.md는 0바이트로 커밋되어 있음을 발견.
  59차(또는 그 이전) 반영 스크립트의 히어스트링 종료 처리 오류로 추정.
- HANDOFF.md 안에 남아있던 원문을 정확한 경계로 추출해 이 파일을 복구. 57~59차
  체크포인트를 포함해 내용 손실은 없었음(끝부분 히어스트링 종료 따옴표만 누락된 상태로
  파일이 끝나 있었음).
- 20절 리셋(carrot-ms 베이스 재생성) 착수 여부는 이번 세션에서 다시 확정되지 않음 --
  HANDOFF.md 60차 미완료 1번 참고, 다음 세션 최우선.

## 체크포인트: 2026-09-16 (59차) -- 브랜치 버전 관리 정책 신설

- carrot-ryu HEAD: 9ccf1206a034c5fb5e5f35201553f9fc4e5237e5 (변경 없음, 코드 미변경)
- carrot-ms(happymaj11r/openpilot) HEAD: 904fd107b529f4636846bedcf645e102fce007b7 (58차와 동일, 변경 없음)
- 사용자 제안으로 2절 개별 커밋 선별 반영 방식의 누적 부담 완화를 위해 "carrot-ryu-vN
  아카이브 + carrot-ms 베이스 재생성" 정책을 합의(PROJECT_INSTRUCTIONS_carrot-ryu.md
  20절 신설). carrot-ryu 브랜치명은 디바이스 배포 대상이라 고정 유지, 리셋 시점마다
  직전 상태를 carrot-ryu-vN으로 아카이브한 뒤 carrot-ms 최신 베이스로 재생성 +
  CURRENT_STATUS.md "코드 수정 현황" 리스트를 체크리스트로 이식하는 방식.
- 이번 세션에서 1) ryujmin97/openpilot에 1절 지침과 어긋나게 남아있던 c3-ms-dev
  브랜치 삭제, 2) 현재 carrot-ryu(commit 9ccf1206) 스냅샷을 carrot-ryu-v1으로 생성
  (반영 스크립트 실행 대기).
- 다음 확인 시점: 사용자 승인 후 실제 20절 리셋(carrot-ms 베이스 재생성 + v1 코드
  이식) 착수 시. 이때 기존 2절의 25건 클러스터 분류 작업(위 58차 체크포인트)을
  이어갈지, 20절 재생성으로 대체할지 먼저 확정 필요.

## 체크포인트: 2026-09-16 (58차)

- carrot-ryu HEAD: 9ccf1206a034c5fb5e5f35201553f9fc4e5237e5 (변경 없음)
- carrot-ms(happymaj11r/openpilot) HEAD: 904fd107b529f4636846bedcf645e102fce007b7 (변경 없음, 57차와 동일)
- fork point 이후 신규 25건(57차 체크포인트 목록)을 오래된 시간순으로 1차 분류. 각 커밋 diff를 carrot-ryu 현재 코드와 직접 대조해 관련성/충돌 가능성 판정(상세 diff 대조는 채팅 세션 로그 참고, 재분석 시 git show로 재현 가능).

1) 8dcd32f7 sensord update — 제외. tizi(comma 3X) 전용 자력계 코드 + capnp 스키마 정리, comma C3에 기능 영향 없음. carrot-ryu가 관련 코드를 fork 시점과 동일하게 보존 중이라 충돌 없음.
2) 6f63ad35 Prefer external navigation exclusively while connected — 반영 후보(관련성 높음, 충돌 없음). carrot_serv.py의 _vehicle_speed_camera/bump/school_zone/section_zone_enabled, _legacy_sdi_suppressed 등 해당 함수 전부 carrot-ryu에서 fork 시점과 동일함을 라인 단위로 확인. 외부내비(Waze 등)+차량 순정 CAN내비 동시 사용 시 중복 감속/카운트다운 문제를 해소하는 실질 개선. 다만 "외부내비 연결 시 순정 내비 전체 비활성화"로 동작이 기존보다 강해지므로, 반영 전 사용자가 원하는 동작(동시 사용 원하는지)인지 확인 필요.
[클러스터 A: 종방향 gap/lead-response 대개편 — 보류, 다음 세션 최우선]
3) 154f819e / 4) 48b57971 / 10) 6c1a4499 / 12) 1d956ec7 / 13) 0201cd19 / 14) 33427531 / 15) 3cff6956 / 16) 64921a81 / 21) 25af28f1 / 25) 904fd107 (10건)
  - carrot-ms/wip 쪽은 longitudinal_safe_follow.py를 삭제하고 driving_mode.py를 신설하는 등 gap/lead-response 로직을 대규모 재설계.
  - carrot-ryu도 fork 이후 "longitudinal: move lead response into MPC costs", "longitudinal: align queued model stops to vehicle gap", "radar: ease future following demand for confirmed cut-outs" 등 같은 영역을 독자적으로 재설계해 옴 → 양쪽이 병행 발전한 대표적 고위험 지점. 단순 문자열 치환이 아니라 클러스터 전체를 함께 놓고 설계 의도부터 비교해야 함.
  - 14) 33427531(설정명 "lead response"→"following responsiveness")은 40차 체크포인트에서 이미 "커스텀 UI 한국어 문자열과 충돌 가능성" 경고된 항목과 동일 커밋.
5) dd245c7c / 8) df0027f7 / 9) 544dffe — 문서(docs)만 변경, 각각 클러스터 A(5)/클러스터 C(8,9)의 반영 여부에 종속. 별도 위험 없음.
[클러스터 B: 현대/제네시스 CAN 상태 — 보류]
6) 0b0c282c / 17) 66e75d87 (2건) — opendbc hyundaicanfd.py/carstate.py 수정. DH 2015(현대/제네시스 그룹) CAN 파싱과 직접 관련. carrot-ryu의 Hyundai CAN 커스텀(클러스터 표시 등)과 겹치는지 라인 단위 대조 미실시, 다음 세션 필요.
[클러스터 C: Cinque v2 eGPU 모델 — 보류]
7) b483035d (+ 문서 8,9) — big_model.py 등 eGPU 모델 교체. carrot-ryu도 fork 이후 "Download verified eGPU models with their matching isolated runtime", "Deliver the big eGPU model outside Git LFS" 등 독자적 eGPU 커밋 존재 → 병행 발전 가능성, 대조 필요.
11) 9d50f986 — 제외. GitHub Actions CI/문서 링크체크 툴링만 변경(.github/workflows 등). 1절 원칙대로 로컬 임시 clone 방식으로만 작업하며 CI 파이프라인 미사용 → 무관.
[저위험 — 개별 값만 확인하면 됨]
18) 685ec5ce SpeedFromPCM 기본값 0→2 / 19) 59617d38 내비감속 기본값 200→120 — carrot_settings.json 기본값만 변경. carrot-ryu가 이미 다른 기본값으로 커스텀했는지 다음 세션에 대조 필요.
20) 6b370dc7 Carrot Web 설정 페이지 인라인 검색 추가(js/css, 14파일) — carrot-ryu의 자체 Web UI 확장(로그 업로드/경로안내 등)과 파일 겹침 여부 미확인.
[빌드 인프라 — 별도 판단 필요]
22) e9b3b89b acados를 nightly_c4 번들→패키지 의존성으로 전환 / 23) c5f6e95b json11·Catch2를 벤더링→패키지 의존성으로 전환 — 대규모 삭제+uv.lock 변경. 우리 빌드 환경 호환성 확인 없이는 판단 불가.
24) ce8cbffe Disable C3XL fan supply — 제외. comma C3X/C3XL 전용 팬 제어, 사용자 기기(comma C3)와 무관.

- 다음 세션 우선순위: (a) 클러스터 A(종방향 gap/lead-response, 10건) 정밀 대조, (b) 클러스터 B(Hyundai CAN, 2건) 정밀 대조, (c) 클러스터 C(eGPU, 3건) 정밀 대조, (d) 저위험 3건(18,19,20) 개별 확인 후 반영, (e) 빌드 인프라(22,23)는 위 정리 후 판단. 6f63ad35는 사용자 의도 확인 후 반영 스크립트 작성.
- 다음 확인 시점: 위 클러스터 분석 착수 시, 또는 carrot-ms HEAD 재변경 여부 가벼운 점검 시.## 체크포인트: 2026-09-16 (57차)

- carrot-ryu HEAD: 9ccf1206a034c5fb5e5f35201553f9fc4e5237e5 (커밋메시지 "55cha: flip render-texture screenshot vertically" 기준)
- carrot-ms(happymaj11r/openpilot) HEAD: 904fd107b529f4636846bedcf645e102fce007b7 (2026-09-16)
- fork point(carrot-ryu가 갈라져 나온 carrot-ms 커밋): 02015190f58a4380a433ee0130e6374455dddc2e(6~7차 체크포인트와 동일) -- git merge-base --is-ancestor로 현재 carrot-ryu HEAD의 조상임을 재확인.
- **모델 셀렉터 전용 커밋 41건 전수 조사**: carrot-wip(ajouatom)/carrot-ms(happymaj11r)를 각각 --filter=blob:none bare clone 후 커밋 메시지 집합 비교(api.github.com rate limit 회피, 2절 방식)로 carrot-ms 전용 커밋 117건을 추출, 그중 model_selector/eGPU/modeld mirror 관련 41건을 필터링. git merge-base --is-ancestor <commit> 02015190f5로 표본 10건(최초 도입~최신 mirror 갱신 전 구간 포함) 전수 검증한 결과 **전부 fork point의 조상 -> 이미 carrot-ryu에 반영됨. 신규 반영 대상 0건**. carrot-ryu의 carrot/model_selector/도 fork 이후 무수정 상태이며 upstream 침습 지점 6곳(README 명시) + params_keys.h 등록 모두 정상 확인.
- **40차에서 "모델셀렉터/Cinque v2"로 분류했던 3건**(Consolidate Carrot development with Cinque v2 / Record Cinque v2 delivery verification / Use Cinque v2 eGPU model from PR 38823)은 이후 carrot-wip 본류에 흡수(merge)돼 더 이상 carrot-ms 전용이 아님 -- 앞으로는 일반 carrot-wip 동기화 경로로 유입됨.
- **fork point 이후 carrot-ms 전용 신규 커밋 25건**(git log 02015190f5..carrot-ms, 40차의 23건 + 이후 2건: ce8cbffe "Disable C3XL fan supply", 904fd107 "Fix stopping acceleration at -0.5"). 개별 반영 여부 미검토.
- **[57차, 설계 방향 확정]** 사용자 요청으로 분석 범위를 모델셀렉터 한정에서 위 25건(fork point 이후 carrot-ms 전체 신규 커밋)으로 확대. 다음 세션 작업 순서 합의: (1) 25건 각각이 제네시스 DH 2015(우리 차량)에 실제로 필요한지 판단해 무관한 것 제외(2절 5단계와 동일 절차), (2) 필요 판정된 것만 개별 diff 분석, (3) carrot-ryu가 이미 쌓아온 자체 커스텀 코드(로그 업로드/스크린샷/경로안내 UI 등)와 겹치는 파일이 있는지, 충돌하거나 로직이 상충하는 부분이 있는지 확인. 이번 세션은 이 설계까지만 진행, 실제 커밋별 분석은 다음 세션으로 이월.
- 다음 확인 시점: 위 25건 개별 검토를 시작할 때, 또는 carrot-ms HEAD가 다시 바뀌었는지 가벼운 git ls-remote 점검할 때.
## 체크포인트: 2026-09-15 (40차)

- carrot-ryu HEAD: bdde832654a6bbf2e3e598ea7937e61a153832a8 (39cha-fix, "40차 계속2" devnotes 세션 기준 최신)
- carrot-ms(happymaj11r/openpilot) HEAD: c5f6e95b8ee1d7daaf62acbfbe920e4ee22d4c8b (2026-09-15)
- 7차 체크포인트(커밋 메시지 "Recover evil-merge resolutions from carrot-wip PR #516 and PR #517", 당시 hash 0201519...)가 현재 carrot-ms 히스토리에 그대로 남아있어, `git log 0201519..HEAD`로 구간 diff를 직접 확인함(2절: hash가 아닌 커밋 메시지 내용 기준 추적). 신규 커밋 23건 발생(rebase로 예전 hash는 무효, 이 diff는 07차 체크포인트 커밋이 아직 히스토리에 남아있어 우연히 가능했던 것으로, 다음에 또 rebase되면 이 방식도 안 통할 수 있음 -- 그때는 메시지 텍스트로 개별 대조 필요).
- 분류: 종방향 튠 다수(7건: lead acceleration/tau/gap response 관련), 파라미터 기본값 변경 2건(SpeedFromPCM, 내비 감속), 현대차 클러스터 2건, **모델 셀렉터/Cinque v2 eGPU 3건**(11번 on-the-horizon 항목과 직결 -- "Consolidate Carrot development on carrot-wip with Cinque v2", "Use Cinque v2 eGPU model from comma PR 38823", "Record Cinque v2 delivery verification and documentation scope"), 설정 리네이밍 1건("Rename lead response setting to following responsiveness" -- 우리 커스텀 UI 한국어 문자열과 충돌 가능성 있어 확인 필요), 의존성/빌드 2건(json11/Catch2, acados), 테스트/CI 2건, 네비게이션 1건("Prefer external navigation exclusively while connected"), 기타 1건(sensord update).
- 결론: 7차 이후 carrot-ryu가 자체 커스텀 코드(39~40차 등)를 계속 쌓아왔으므로, 6차 때처럼 carrot-ryu를 carrot-ms HEAD로 전면 재생성하는 방식은 이제 쓸 수 없음. 23건 중 어떤 것을 cherry-pick할지 선별 검토가 필요하나, 이번 세션에서는 체크포인트 기록까지만 하고 개별 커밋 diff 분석/cherry-pick 판단은 다음 세션으로 이월.
- 다음 확인 시점: 위 23건 중 어느 것을 반영할지 사용자와 함께 검토를 시작할 때, 또는 시간이 지나 carrot-ms HEAD가 또 바뀌었는지 가벼운 `git ls-remote` 점검할 때.

## 체크포인트: 2026-09-13 (7차)

- carrot-ryu HEAD: 02015190f58a4380a433ee0130e6374455dddc2e
- carrot-ms(happymaj11r/openpilot) HEAD: 02015190f58a4380a433ee0130e6374455dddc2e
  → carrot-ryu와 완전히 동일
- 결론: 6차 세션에서 carrot-ryu를 carrot-ms HEAD로 전면 재생성한 이후,
  carrot-ms에 새로운 커밋(rebase)이 전혀 없음. 이번 점검 시점 기준 반영 대상 커밋 0건
- 참고: carrot-wip(ajouatom/openpilot) HEAD는 bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1로
  6차 시점 이후에도 계속 진행 중. 그러나 carrot-ms가 아직 이를 따라 rebase하지 않았으므로,
  지침 2절 원칙대로 carrot-wip을 직접 비교/반영 대상으로 삼지 않음
  (carrot-ms가 다음에 rebase될 때 다시 검토)
- 다음 확인 시점: 사용자가 요청하거나, 시간이 좀 지난 뒤 carrot-ms HEAD가 바뀌었는지부터
  재확인 (git ls-remote로 HEAD hash만 비교하면 되므로 가벼운 점검)

## (6차 이전 이력 - 참고용)

6차 세션에서는 carrot-wip 대비 carrot-ms에만 있는 커밋 117개(모델 셀렉터 관련 약 58개,
무관한 것 약 59개)를 확인했으나, 선별 cherry-pick 대신 carrot-ryu 자체를 carrot-ms
HEAD(0201519...)로 전면 재생성하는 방식으로 처리함(당시 carrot-ryu에 사용자 코드가 없어
안전하게 가능했음). 따라서 그 시점까지의 carrot-ms 커밋은 모두 반영된 것으로 간주하며,
이 파일은 그 이후부터 발생하는 "신규 커밋"만 추적하는 목적으로 사용한다.