# HANDOFF

Worker: Claude (57차 -- carrot-ms 동기화 분석 범위를 모델셀렉터에서 fork 이후 전체 신규 커밋으로 재설정, 설계 논의만·코드 변경 없음)
Date: 2026-09-16
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `9ccf1206a034c5fb5e5f35201553f9fc4e5237e5`, 55cha flip fix. 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `1781fca871981f4c4e16e07c2e3cc2a9eb0698b9`, 56차 시점 devnotes. 이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 40차 체크포인트(23건) 이후 2건 추가로 확인됨(총 25건, fork point `02015190f5` 이후). WIP_SYNC.md 57차 체크포인트 참고.

작업:
사용자가 "carrot-ms 모델셀렉터 분석 착수"를 요청. 41개 모델셀렉터 전용 커밋을 조사했으나 전수 조상관계 검증 결과 전부 이미 carrot-ryu에 반영돼 있음을 확인. 사용자가 이를 바탕으로 분석 범위를 "fork point 이후 carrot-ms 신규 커밋 전체(25건)"로 재설정하도록 지시, 이번 세션은 이 설계 방향 확정까지만 진행.

완료:
1. carrot-wip(ajouatom)/carrot-ms(happymaj11r)를 각각 blob 없이 bare clone해 커밋 메시지 집합 비교(api.github.com rate limit 회피) -> carrot-ms 전용 117건 중 모델셀렉터 관련 41건 특정.
2. `git merge-base --is-ancestor`로 41건 중 대표 10건(도입~최신) 전수 검증 -> 전부 carrot-ryu fork point(`02015190f5`)의 조상, 신규 반영 대상 0건 확정.
3. carrot-ryu의 `carrot/model_selector/` 21개 파일이 fork 이후 무수정, README 명시 upstream 침습 지점 6곳 + params_keys.h 등록 전부 정상 배선됨을 직접 조회로 확인.
4. 40차에서 "모델셀렉터/Cinque v2 3건"으로 분류했던 커밋들이 이후 carrot-wip 본류에 merge돼 더는 carrot-ms 전용이 아님을 확인(일반 carrot-wip 동기화 경로로 전환).
5. fork point 이후 carrot-ms 신규 커밋이 25건(40차의 23건 + 2건)임을 `git log 02015190f5..carrot-ms`로 확정, WIP_SYNC.md 57차 체크포인트에 기록.
6. **부수 발견**: CURRENT_STATUS.md 항목 36(55차 image_flip_vertical 수정)이 "반영 스크립트 실행 대기"로 남아있었으나, `git ls-remote`로 carrot-ryu HEAD가 이미 `9ccf1206`(커밋메시지 "55cha: flip render-texture screenshot vertically")로 push 완료돼 있음을 확인(16절/핵심 발견 27과 동일 패턴).

미완료 (다음 세션 최우선):
1. [신규] fork point 이후 carrot-ms 신규 커밋 25건(WIP_SYNC.md 57차 체크포인트 목록)을 개별 검토: (a) 제네시스 DH 2015에 필요한지 판단해 무관한 것 제외, (b) 필요한 것만 diff 분석, (c) carrot-ryu 자체 커스텀 코드(로그 업로드/스크린샷/경로안내 UI 등)와 충돌·상충 여부 확인.
2. [부수 발견] CURRENT_STATUS.md 항목 36을 "반영 완료(commit 9ccf1206)"로 정정 필요.
3. [이월] 핵심 발견 31/37을 9절 정식 규칙으로 채택할지 확인(19절).
4. [이월, 37차] 락 수정 동시성 재현 검증.
5. [이월, 34차] 도로명-신호과속 같은 줄 배치 확인.
6. [이월] 28~30차 레이아웃 정밀 재검증.
7. [이월] "선택 다운로드" 버튼 실제 동작 미확인.
8. [이월] test_web_upload.py 데드코드 3개 삭제/갱신.
9. [이월] docs/carrot_web_upload.md 갱신.

검증: 이번 세션은 코드 변경이 없어 실차 검증 대상 없음(12절). git 조상관계 검증(merge-base --is-ancestor)과 raw 파일 직접 조회로 코드 배선 상태만 정적 확인.

주의사항:
- 이번 세션 코드 변경 전혀 없음, carrot-ryu HEAD는 `9ccf1206`(55cha) 그대로.
- api.github.com이 세션 내내 rate limit에 걸려 bare clone(--filter=blob:none) + 로컬 git log/merge-base 방식으로 전환해 조사함(1절 원칙과 일치, 앞으로도 대량 커밋 비교가 필요하면 이 방식 우선 고려할 만함).
- CURRENT_STATUS.md 항목 36 표기 오류(위 부수발견)는 다음 세션에서 바로잡을 것.

다음 작업 후보:
1. fork point 이후 25건 개별 검토 착수(최우선, 위 미완료 1번)
2. CURRENT_STATUS.md 항목 36 표기 정정
3. 나머지는 위 미완료 3~9번과 동일(이월)