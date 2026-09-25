Worker: Claude (165cha, Claude Sonnet 5)
Date: 2026-09-25
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: 8775ea0d300a240c48bad34488aeccb9490ed711, 163차 route 게이트 제거 push 확인됨 -- 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: fbb68e7d423f87474b7fc8cc3b2377051fa80668, 164차 devnotes push 확인됨)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 재확인 -- 신규 커밋 없음. 140~165차는 재점검 없음)

작업:
1. 세션 시작 시 4절 0단계(`git ls-remote`)로 carrot-ryu-note HEAD가 `fbb68e7`(164차 devnotes)로, carrot-ryu HEAD가 `8775ea0d`(163차)로 이미 push 완료돼 있음을 확인.
2. 사용자가 실주행 rlog 42세그먼트(`0000044a--692521eced--0~41`, 2026-09-24, 약 41.35분)를 업로드, 164차 미완료 5번(MapTurnSpeedFactor 일반화 검증, road/nRoadLimitSpeed 관계) 요청.
3. rlog `initData.gitCommit`(`f23d05fef4690a01af27e108f98cc01992f11869`)이 153차 코드와 일치함을 이 세션에서 직접 capnp 디코딩으로 확인 -- 이 로그는 156~163차 이전 상태.
4. 스키마: 해당 커밋을 shallow fetch해 현재 HEAD(cereal/*.capnp+car.capnp)와 `diff -rq`로 바이트 동일함을 확인, 기존 스키마 재사용. `route_decel/route_extract.py`(113차)로 42세그먼트 전체를 이 세션에서 독립적으로 추출/병합(49,657행) -- 행수/분포가 이전 초안과 일치함을 재확인.
5. `carrot_serv.py`(현재 HEAD, 1363~1370·1522행) 직접 읽어 `limit_speed`/`nRoadLimitSpeed` 관계 확정.
6. `route=` 값이 게이트 무관 매 사이클 계산됨(1478행)을 이용해 `des_new=min(des_old, route)`로 163차 게이트 제거 효과를 오프라인 재구성, `longActive==True` 구간에서 진짜 신규 제동 요구 사례 탐색 -- 이 세션에서 독립 재계산해 0건(버퍼 2km/h)/7건(버퍼 없음, 전부 des_old==route) 확인.

완료:
1. road/limit_speed-nRoadLimitSpeed 관계 코드로 확정(164차 "무제한 placeholder 추정, 미확정" 해소) + 로그로 실증(road 소스 12,747/49,657건, 값 전부 현실적).
2. MapTurnSpeedFactor(90) 결론이 2번째 로그(다른 도로, 41분)로 일반화됨을 확인 -- longActive==True 24,610사이클 중 신규 제동 요구 0건.
3. 핵심 발견 64 신규 등록(FINDINGS.md), WIP.md 165차 항목 작성, CURRENT_STATUS.md 갱신.

미완료(다음 세션 우선순, 164차에서 이월 그대로 + 신규 없음):
1. (161차 원안 이월) candidate3 + 162차 경로 소진 수정 실기기 검증.
2. 156차 A안(잔존 zip 정리 로직) 실기기 검증, 톨게이트(xTurn=6) 구간 실차 검증 -- 이번 로그(42세그먼트)에도 xTurn=6 없음, 계속 이월.
3. (선택) zip 무결성/용량 확인, `build_zip()` 디스크 여유 확인 코드(155차 이월).
4. 148차 v1 `2>&1` 재발 FINDINGS.md 정식 등록 여부, 147차 임시 스크립트 toolkit 미등록.
5. **163차 코드(route 게이트 제거) 자체의 실차(디바이스) 검증 -- 아직 미실시** (이 로그도 153차 기록이라 검증 아님, 오프라인 시뮬레이션만).
6. (신규 이월, 165차 한계) 이번 시뮬레이션(`des_new=min(des_old, route)`)은 162차(경로 소진 방지)·156/157차(zip 임시경로) 효과는 검증하지 않는다 -- 이 로그 자체가 그 이전 코드로 기록됐기 때문. 162/163차가 실제 디바이스에 배포된 뒤 기록된 로그로 다시 검증 필요.

검증:
- `carrot_serv.py` 1363~1370·1522행 직접 확인(limit_speed 기본값 200 + 조건, nRoadLimitSpeed 로깅 지점).
- 로그 스키마 동일성: `git fetch --depth 1 --filter=blob:none origin f23d05f...` 후 cereal/*.capnp+car.capnp를 현재 HEAD와 `diff -rq`로 바이트 단위 동일 확인.
- 42세그먼트 전체 추출 성공(49,657행, 41.35분), xTurn 분포/road 값 분포/src 분포를 이 세션에서 독립 재현.
- `des_new=min(des_old, route)` 시뮬레이션: longActive==True 24,610사이클 중 신규 제동 요구(route<vE-2 & des_old>=vE-2) 0건, 엄격 기준(버퍼 없음)도 7건뿐이며 전부 des_old==route(이미 동일값, 신규 아님) -- 이 세션에서 독립 재계산으로 확인.

주의사항:
- 이번 세션은 코드 변경 없음(분석 전용). road/limit_speed 확정은 코드 읽기 기준이며 런타임 Params 값(autoRoadSpeedLimitOffset 등)의 실제 설정값까지는 로그에서 역산하지 않았다.
- des_new 시뮬레이션은 162/163차 코드가 실제로 디바이스에서 동작했을 때의 결과가 아니라, 153차 로그 위에 163차의 "게이트만 제거" 효과를 근사한 것이다(다른 163차 변경 없음 가정).

다음 작업:
1. 위 미완료 항목 중 우선순위를 다음 세션에서 사용자가 지정 -- 여전히 163차 코드의 실차(디바이스 반영 후 실주행) 검증이 최우선 후보.
2. 이 devnotes 반영 스크립트(`165cha_devnotes_carrot_ryu_note.ps1`) 실행 -> push 확인.
