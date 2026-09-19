Worker: Claude (89차)
Date: 2026-09-19
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `0923f8396dacbb61a23e1c394751d8014ddddf5f`, 변경 없음 -- 이번 세션은 코드 미변경)
Note Branch: carrot-ryu-note (base: `c76f2385d8dfce5e971f0fa653b0734f9c473304`, 88차 devnotes 위. 이번 세션 WIP_SYNC.md/WIP.md/HANDOFF.md 갱신, 반영 스크립트 실행/push 대기)
carrot-ms 마지막 검토/동기화 체크포인트(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스). **[89차]** carrot-ms(happymaj11r/openpilot) 현재 HEAD `f19d404a47a24806f876ee9d2148c112655816d2`가 이 체크포인트보다 15개 커밋 앞서 있음을 확인, 15건 전부 개별 diff 분석 완료, WIP_SYNC.md에 정식 체크포인트로 기록.

작업:
88차 HANDOFF의 미완료 3번("carrot-ms 신규 13건 diff 분석 착수")을 이어받아 진행했다. 세션 시작 시 carrot-ms를 재조회한 결과 706efb47 대비 15건으로 늘어나 있었다(88차 이후 2건 추가: 8e85a02/f19d404a). api.github.com REST API가 rate limit(60/시간)에 걸려 있어, `git clone --filter=blob:none --no-checkout`(partial clone)으로 각 커밋의 `git show --stat`/`git show -- <file>`을 직접 조회하는 방식으로 전환해 15건 전부의 변경 파일과 diff를 확인했다.

우리 차량(HYUNDAI_GENESIS, 제네시스 DH 2015-16)이 `opendbc/car/hyundai/values.py`에서 `flags=HyundaiFlags.CHECKSUM_6B | HyundaiFlags.LEGACY`로 정의되어 CAN FD가 아니고 RADAR_GROUP3 플래그도 없음을 재확인한 뒤, 이를 근거로 CAN FD 전용 7건(0beb200a/de6ee634/a6c8220/34cf65fb -- CAN FD stop retry 계열, 5ae4a25/8e85a02/f19d404a -- CAN FD lead/CCNC HUD 계열)과 Radar Group3 전용 1건(ee8d4353)을 반영 대상에서 제외 확정했다. CI 워크플로만 바꾼 845e725b, 문서 5줄만 바꾼 21b71f00, EV9 전용 테스트 픽스처만 추가한 994683d5도 코드 동작 변화가 없어 제외.

남은 4건(b4f751f4/4d1a3ded/ec95363a/557e6f6a, 카메라 프레임 페어링·커브 리팩터·모델셀렉터 미러·UI 렌더 배치·진단로그)은 차량과 무관한 일반 코드라 검토 대상으로 분류했다. 각 커밋이 건드리는 정확한 함수(model_renderer.py의 `_build_path_polygon_update_line_data2_carrot`/`_dist_carrot`/`_dist3_carrot`, modeld.py의 카메라 프레임 수신부, curve_speed.py의 `VisionCurveSpeed` 클래스)를 carrot-ryu 현재 코드(`0923f83` 기준)와 직접 diff 대조해 fork 이후 완전히 무수정(byte-identical)임을 확인 -- 순수 리팩터/버그수정이라 우리 커스텀과 충돌 없이 적용 가능할 것으로 판단된다. 다만 ec95363a의 `augmented_road_view.py`/`road_markings.py` 레인 대시 영역은 이번 세션에서 상세 대조까지는 하지 않았다.

사용자에게 이 4건의 반영 여부를 문의한 결과, "코드 반영 없이 WIP_SYNC.md 기록만 먼저" 진행하기로 결정되어, 이번 세션은 코드 변경 없이 devnotes 3개 파일(WIP_SYNC.md/WIP.md/HANDOFF.md)만 갱신한다.

완료:
1. carrot-ms 신규 15건(706efb47 대비) 전수 diff 분석 -- CAN FD 전용 7건 + Radar Group3 전용 1건 + CI/문서/테스트픽스처 3건, 총 11건 제외 확정.
2. 남은 4건(b4f751f4/4d1a3ded/ec95363a/557e6f6a)의 대상 함수가 carrot-ryu에서 fork 이후 무수정임을 diff로 확인, 충돌위험 낮음으로 판단.
3. 위 분석 결과를 WIP_SYNC.md에 정식 체크포인트(89차)로 기록.
4. devnotes 반영 스크립트(`89cha_devnotes_carrot_ryu_note.ps1`) 작성.

미완료(다음 세션 최우선):
1. 위 devnotes 반영 스크립트를 사용자가 실행해 WIP_SYNC.md/WIP.md/HANDOFF.md를 push할 것.
2. 검토대상 4건(b4f751f4 -> 4d1a3ded -> ec95363a -> 557e6f6a, 커밋 발생 순서) 반영 여부를 사용자와 재논의해 승인받은 뒤 9절 방식으로 착수 -- 특히 ec95363a가 건드리는 augmented_road_view.py/road_markings.py 레인 대시 영역은 착수 전 상세 대조 필요.
3. 36개 항목(1~36) 전부의 실차 검증(88차에서 이월, 여전히 미실시).
4. WIP.md 파일 맨 끝(1차 세션 기록)의 mojibake 처리 여부, "# WIP" 헤더 중복 정리 여부 -- 기존부터 이월 중, 사용자 판단 필요.

검증: `git ls-remote`로 carrot-ryu(`0923f83`, 변경없음)/carrot-ryu-note(`c76f238`, 88차 상태) 실제 HEAD 확인. carrot-ms(happymaj11r/openpilot) HEAD를 `git ls-remote`로 `f19d404a` 확인, `api.github.com/repos/happymaj11r/openpilot/compare/706efb47...f19d404a`로 ahead_by 15/커밋 15건 전부 확인. api.github.com rate limit 소진 이후에는 `git clone --filter=blob:none`(partial clone)으로 각 커밋의 `git show`를 직접 조회해 API 재개를 기다리지 않고 분석을 완료했다. carrot-ryu의 model_renderer.py/modeld.py/curve_speed.py 관련 함수를 raw.githubusercontent.com(SHA고정, `0923f83`)으로 조회해 carrot-ms의 b4f751f4 이전(pre-image) 버전과 diff 0(byte-identical)임을 확인. 실차 검증: 미실시(이번 세션은 GitHub 조회/분석만, 코드 변경 없음).

주의사항:
- api.github.com REST API가 60회/시간 rate limit에 자주 걸리는 상황이 반복되고 있다(88차 이전에도 유사 패턴 있었을 가능성). bash_tool이 있는 세션에서는 이번 세션처럼 `git clone --filter=blob:none --no-checkout` partial clone + `git show`로 우회 가능함을 이번에 실증했다 -- 앞으로 rate limit에 걸리면 이 방식을 기본 대체 수단으로 사용할 것.
- 검토대상 4건은 diff 대조 결과 저위험으로 판단됐으나, 이는 정적 대조일 뿐 반영 승인은 아니다. 18절 원칙대로 사용자 명시적 승인 없이 다음 세션이 임의로 반영을 진행해서는 안 된다.
- 15건 중 제외로 분류된 CAN FD/Radar Group3 전용 커밋들은 "우리 차량에 불필요"이지 "잘못된 커밋"이 아니다. DH 2015 플랫폼 특성(LEGACY CAN, non-CANFD) 때문에 구조적으로 무관한 것뿐이므로, 향후 유사한 CAN FD 관련 신규 커밋이 또 발생해도 같은 기준(values.py 플래그 확인)으로 빠르게 제외 판단 가능하다.

다음 작업 후보:
1. devnotes 반영 스크립트(`89cha_devnotes_carrot_ryu_note.ps1`) 실행/push 확인.
2. 검토대상 4건 반영 착수 여부 사용자와 재확인, 승인 시 ec95363a의 augmented_road_view.py/road_markings.py 상세 대조부터 진행.
3. 36개 항목 전부 실차 검증 착수.
4. WIP.md mojibake/헤더 중복 정리 여부 사용자 확인.