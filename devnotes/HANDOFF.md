Worker: Claude (154cha, Claude Sonnet 5)
Date: 2026-09-24
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: f23d05fef4690a01af27e108f98cc01992f11869, 153차 코드 -- 이번 회차 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 153차 devnotes push 완료 상태, `5c480a1af537bc0be7d799aea8cac45871947250`)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 세션 재확인 -- 신규 커밋 없음. 140~154차는 재점검 없음)

작업:
1. 세션 시작 4절 0단계로 지침 문서(v2, commit `5c480a1`) 조회. HANDOFF.md(153차 기록, base code HEAD `44bfd33d`/note base `26fa4b1`)와 실제 GitHub 상태(carrot-ryu `f23d05f`, carrot-ryu-note `5c480a1`)가 다름을 확인(16절).
2. `f23d05f`의 commit patch/blob hash(`eb8a53c4`)와 `5c480a1`의 commit message를 직접 조회해, 153차 코드+devnotes가 실제로는 이미 push 완료돼 있음을 확정(HANDOFF.md 미완료 1·2번 해소).
3. 153차 HANDOFF 미완료 3번(seg71/92/93 교차검증)을 사용자 업로드 rlog 4세그먼트(seg70/71/92/93, `8e8b0d1a` 기록)로 수행. 재구현 없이 실제 소스 함수 원문을 ast로 추출해 exec하는 재생 도구(`replay_route_geom.py`) 신규 작성.
4. OLD(`8e8b0d1a`)/NEW(`f23d05f`) `get_path_after_distance()`를 로그 실제 입력(xPosLat/Lon/Angle, navRoute 폴리라인, carState.vEgo)으로 20Hz 재생, 로그 `naviPaths`와 대조해 재생 충실도 확인 후 집계 지표로 비교.
5. 결과를 WIP.md 154차/CURRENT_STATUS.md/toolkit README·CHANGELOG에 기록.

완료:
1. 153차 코드(`f23d05f`)+devnotes(`5c480a1`) push 완료 재확인(16절 괴리 해소, 코드 변경 없음).
2. seg70/71/92/93 rlog 재생 교차검증 완료(open-loop) -- 4개 세그먼트 전부 153차와 동일 패턴(폴리라인 정점 간격 133~252m 중앙값, 300m 초과 구간 19~46%) 재확인.
3. route 급변(로그/수정전 재생/수정후 재생, 20km/h 초과 프레임간): seg70 102/105/29, seg71 375/364/10, seg92 131/141/25, seg93 118/117/12 -- 트리거(첫 세그먼트≥300m) 연관 급변이 수정 후 크게 감소.
4. 무회귀 확인: 비트리거 사이클(3,082개) 전부 수정 전후 출력 0건 차이.
5. desiredSpeed 영향 확인: route가 실제 source가 된 seg70/92에서, route-source des 급변 39/47건 중 36/40건이 트리거와 겹침 -- 151차 관찰(분기 flicker)의 원인이 153차 수정 대상과 대부분 일치함을 뒷받침.
6. 신규 발견(이월 등록): 분기/톨게이트 통과 직후(xDist<0) 구간에도 트리거 연관 요동이 나타남 -- 152차 게이트(TurnSpeedControlMode==2 한정) 적용 여부는 로그의 TurnSpeedControlMode 값을 확인 못해 미결.
7. toolkit 신규 등록: `devnotes/toolkit/route_decel/replay_route_geom.py`(extract/run/report 3모드), README.md/CHANGELOG.md 갱신.

미완료(다음 세션 최우선 순으로):
1. **실차 검증 여전히 미실시** -- `f23d05f`(153차) 이후 코드가 탑재된 디바이스의 분기(xTurn=4)/톨게이트(xTurn=6) 실주행 로그 필요(이번 회차는 153차 이전 코드로 기록된 로그의 open-loop 재생일 뿐).
2. 152차·153차 코드의 디바이스 배포(git pull) 여부 여전히 미확인(151~154차 이월).
3. **신규**: 분기/톨게이트 통과 직후(xDist<0) 구간 요동에 152차 게이트가 실제로 적용되는지(TurnSpeedControlMode 값) 확인.
4. **신규**: 잔여 비트리거 급변(세그먼트당 10~25건, 153차 수정과 무관)의 원인 분석 미착수.
5. 147차 코드가 탑재된 디바이스의 실주행 로그 검증(148~153차 이월, 변동 없음).
6. "선행차가 설정 차간거리 근처에서 급제동" 시나리오 정량 미검증(148~150차 이월, 변동 없음).
7. 148차 v1 `2>&1` 재발의 FINDINGS.md 정식 등록 여부 결정(148차 이월, 변동 없음).
8. 이전 이월: diff/블록 추출 스크립트(147차 코드 반영용, 임시) toolkit 미등록(변동 없음).

검증:
- devnotes 재생 도구: 실제 소스 함수 원문(ast 추출) 그대로 exec해 재구현 없이 검증, 로그 `naviPaths`와 대조한 재생 충실도(비트리거 93.3~98.2% 3m 이내 일치) 확보 후 집계 지표로만 결론.
- 실차: 미실시(업로드 로그 4개 전부 `8e8b0d1a`, 153차 수정 이전 코드 기록 -- open-loop 재생일 뿐 실차 검증 아님).

주의사항:
- 이번 회차는 devnotes+toolkit만 변경, carrot-ryu 코드 변경 없음(코드 HEAD는 153차 `f23d05f` 그대로).
- 153차 수정은 "route 폴리라인 정점 간격이 300m보다 성긴 구간에서 발생하는 진행방향 역행 보간점" 문제만 고친 것이며, 분기 자체의 감속(TBT 등)이나 폴리라인이 애초에 성긴 구간에서의 "감속 정보 부재"까지 해소하지 않는다 -- 154차 seg70 t≈38~39s 상세 대조가 이를 재확인.
- 트리거 사이클의 재생 충실도(62.3~73.3%)가 비트리거보다 낮은 것은 도구 결함이 아니라 버그 자체의 위치 민감성(153차 합성 좌표 검증과 동일 성질) 때문이며, 집계 지표(급변 건수/경로 길이/무회귀)로만 결론을 냈다.

다음 작업:
1. `f23d05f`(153차) 이후 코드 탑재 디바이스의 분기/톨게이트 실주행 로그로 실차 검증.
2. 분기/톨게이트 통과 직후 구간의 TurnSpeedControlMode 확인 + 152차 게이트 적용 여부 검토.
3. 152차·153차 디바이스 배포(git pull) 여부 확인.
