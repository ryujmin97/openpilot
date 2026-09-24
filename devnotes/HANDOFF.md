Worker: Claude (152cha, Claude Sonnet 5)
Date: 2026-09-24
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 44bfd33d6ad3bb4c0470386a6ac6e98bdad37fc2, 152차 코드 push 완료 -- 부모 c0a01658f109f5fb52b98f56c4ff5e6dcde42159(147차))
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 151차 devnotes push 완료 상태, `c1d3eb88eb495a6d9256c6b5c52c1256f428b718`)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 세션 재확인 -- 신규 커밋 없음. 140~152차는 재점검 없음)

작업:
1. 세션 시작 4절 0단계로 지침 문서(v2, commit `c1d3eb8`) 조회, 151차 devnotes push(`c1d3eb8`) GitHub 직접 재조회로 확인.
2. 사용자가 업로드한 `152cha_code_carrot_ryu.ps1`(151차 분기 desiredSpeed flicker 분석 결과를 코드로 반영 -- TBT 속도제어에서 atc_desired/atc_desired_next를 speed_n_sources에서 제거하고, route 게이트를 carrot_navi_route()의 실제 가시거리(300m)로 좁힘)을 9절/핵심 발견 26 원칙에 따라 실행 전 독립 재검증.
3. 재검증 과정에서 v1 스크립트의 코드 버그 2건(BOM 누락 포함 3개 위반)을 발견, 수정한 v2로 교체.

완료:
1. 152cha 코드 스크립트 정적 검증 완료(앵커 4곳 1회 매치, 일반/Windows CRLF 재현 두 모드 결과 blob byte-exact 일치, py_compile 통과, atc 잔여 참조 없음).
2. v1의 버그 3건(`.ps1` UTF-8 BOM 누락 / pre-image hash 단계 배열 `.Trim()` 즉시크래시 / `show --stat` 단계 `-C` 중복으로 인한 커밋 후 크래시) 발견 및 수정한 `152cha_code_carrot_ryu_v2.ps1` 작성/전달.
3. 152차 코드 push를 GitHub 직접 조회로 확인(`44bfd33`, carrot_serv.py 1개 파일 +9/-9, 결과 blob `b501c0918ed2a28d41fa73fd353927be2abaacb5`가 기대 post-image와 일치).
4. 이 차량의 TurnSpeedControlMode=2가 설정 스키마상 "비전+경로(TBT)"로 정의됨을 `carrot_settings.json`으로 확인 -- 152차 수정 대상(`if self.turnSpeedControlMode == 2:` 분기)이 정확히 사용자가 말한 "TBT" 게이트임을 재확인.

미완료(다음 세션 최우선 순으로):
1. **152차 devnotes 반영 스크립트(v2) 실행/push 확인** -- 코드 쪽(`44bfd33`)은 push 확인 완료. 152차 코드의 디바이스 배포(git pull) 여부는 미확인.
2. push 후 분기(xTurn=4)/톨게이트(xTurn=6) 재실차 로그로 152차 수정의 실제 효과(desiredSpeed flicker 감소 여부) 검증 -- 151차가 범위만 좁히고 확정하지 못한 `route_speed_raw`/`carrot_navi_route()` 근본 원인은 이번 수정으로 해소된 것이 아니라는 점에 유의(11절, WIP.md 152차 참고).
3. 147차 코드가 탑재된 디바이스의 실주행 로그 검증(148~151차 이월).
4. "선행차가 설정 차간거리(m~1.25) 근처에서 급제동" 시나리오는 로그에 없어 정량 미검증(148~150차 이월).
5. 148차 v1 `2>&1` 재발(핵심 발견 53/55와 동일 패턴 3회째)의 FINDINGS.md 정식 등록 여부 결정(148차 이월).
6. 이전 이월: diff/블록 추출 스크립트(임시, 147차 코드 반영용) toolkit 미등록.

검증:
- 코드: SHA 고정 원본 대비 정적 재현(일반 모드 + Windows CRLF 체크아웃 재현 모드) 양쪽 모두 결과 blob(`b501c0918ed2a28d41fa73fd353927be2abaacb5`)이 스크립트 기대값과 byte-exact 일치, `py_compile` 통과. push 결과는 GitHub 직접 조회로 확인(carrot-ryu `44bfd33`의 carrot_serv.py blob이 기대값과 일치).
- 실차: 미실시(152차 코드의 디바이스 배포/실주행 기록 없음).

주의사항:
- 코드 반영용 원본 v1 스크립트(`152cha_code_carrot_ryu.ps1`)에는 버그 3건이 있었으므로 재실행하지 말 것(WIP.md 152차 참고). 코드 push는 이미 완료됐다.
- 152차 수정은 route 게이트의 "거리 범위"만 실제 가시거리로 좁힌 것이며, 분기점 flicker의 근본 메커니즘(경로 폴리라인/GPS 샘플링 가설)을 고친 것이 아니다 -- 재실차 검증에서 flicker가 남아있다면 11절 원칙대로 추가 분석이 필요하다.

다음 작업:
1. 이 devnotes 반영 스크립트(v2) 실행/push 확인.
2. 152차 코드가 탑재된 디바이스의 분기/톨게이트 실주행 로그를 재확보하면 미완료 2번 수행.
