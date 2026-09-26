Worker: Claude (167cha, Claude Sonnet 5)
Date: 2026-09-26
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: 3a17435dc1d061b8b1c6a3535fcf325b66aa6c86, 167차 핵심 발견 65 수정 push 확인됨)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 02a12ac92d8a633700c5c64d8ecc091d6fe93da1, 166차 devnotes push 확인됨 -- 단 mojibake로 오염된 상태였음, 아래 참고)
carrot-ms 마지막 검토·동기화 체크포인트: `3756e6d5`(130차, 139차 재확인) -- 신규 커밋 없음. 140~166차는 재점검 없음.

작업:
1. 세션 시작 시 4절 0단계(git ls-remote)로 carrot-ryu HEAD가 8775ea0d(163차), carrot-ryu-note HEAD가 02a12ac(166차)임을 확인.
2. 같은 SHA로 HANDOFF.md/WIP.md/FINDINGS.md의 166차 최상단 항목이 깨진 한글(mojibake)로 push되어 있음을 발견(16절) -- 원인: 166차 devnotes 반영 스크립트가 BOM 없는 .ps1로 전달됨(9절 위반, 핵심 발견 21과 동일 패턴). 역디코딩 시도 결과 일부 문자가 리터럴 `?`로 유실되어 완전 복구 불가 확인.
3. 165차 이전 구간은 오염되지 않았음을 확인한 뒤, WIP.md/FINDINGS.md의 166차 최상단 블록만 경계 지정 교체(전체 재작성 아님), HANDOFF.md는 전체 교체.
4. 166차가 이월한 "핵심 발견 65 수정 방향" 결정을 사용자 승인 하에 진행: carrot-ryu에서 navi_route_speed_filt/navi_points_start_index 리셋 지점 9곳 전수 조사, 방향 (a)(navi_points_start_index만 0으로 리셋, filt는 경로가 활성으로 남는 한 유지) 채택.
5. 9절 체크리스트 전항목 수행: BOM 포함(.ps1 첫 3바이트 EF BB BF), anchor 4개 원본 SHA 대상 1회 매치 시뮬레이션, py_compile 통과, pwsh 7.4.6 파서 0 errors(대조군 확인), 로컬 bare 저장소 일반/Windows CRLF 두 모드 dry-run 동일 diff·동일 blob hash(266f845d) 확인.
6. 사용자가 반영 스크립트를 실행해 `8775ea0d..3a17435d` push 완료 -> GitHub raw 조회로 blob hash 일치 재확인.

완료:
1. carrot-ryu: 핵심 발견 65 수정(carrot_man.py, +15/-4) push 및 GitHub 재확인 완료(commit 3a17435d).
2. carrot-ryu-note: 166차 devnotes mojibake 정정(HANDOFF.md 전체교체, WIP.md/FINDINGS.md 166차 블록 교체 + 167차 신규 기록) 반영 -- 이 스크립트 자체가 그 반영 수단(교체형 파일이라 이 HANDOFF.md 문구는 반영 스크립트가 실행된 이후 시점 기준으로 작성됨).

미완료:
1. seg21(3건)/seg22(1건) 곡률 0.035 경계 흔들림 원인(진짜 커브 반응 vs 158차 계열 노이즈) 조사 -- 별도 세션으로 이월.
2. 163차(게이트 완전 제거) 자체의 실주행 검증 -- 이번 로그에도 미포함.
3. xTurn=6(톨게이트) 로그 확보 -- 여전히 미확보(114차부터 이월).

검증:
- 핵심 발견 65 수정: 9절 체크리스트 전항목(BOM/anchor 1회매치/py_compile/pwsh 파서/CRLF dry-run) 통과, 실제 push 후 blob hash 재확인 완료. 실차 검증: 미실시.
- devnotes mojibake 정정: 165차 이전 구간 무손상 확인 후 166차 블록만 경계 지정 교체, post-write recheck로 새 내용 존재/옛 내용 소거 확인.

주의사항:
- 166차 devnotes의 원본 한글 텍스트 일부는 (질문에 등장한 리터럴 `?`처럼) 완전히 복구 불가능한 손실이 있었다. 이번 정정본은 같은 정보를 이 세션이 가진 맥락(직전 HANDOFF.md 해독 결과, 채팅 기록, 코드 diff)으로 다시 서술한 것이며, 166차 원문과 글자 단위로 동일하지는 않다.
- 앞으로도 한글 등 비ASCII가 포함된 .ps1을 전달할 때는 반드시 9절 체크리스트 1번(BOM 확인)을 빠짐없이 수행한다.

다음 작업:
1. seg21/seg22 곡률 0.035 경계 흔들림 원인 조사(진짜 커브 vs 노이즈).
2. 163차 게이트 완전 제거 실차 검증.
