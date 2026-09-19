# WIP SYNC

carrot-ms → carrot-ryu 동기화 이력 (carrot-ms는 매번 rebase되어 commit hash가 바뀌므로,
hash가 아닌 "커밋 메시지/내용 기준"으로 추적. 2절 참고)

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