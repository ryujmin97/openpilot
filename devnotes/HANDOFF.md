# HANDOFF

Worker: Claude (세션 9)
Date: 2026-09-13
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: 2dbe492, 8차 이후 route 감속 근본수정 1건 반영)
Note Branch: carrot-ryu-note (9차 devnotes 반영)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음
(WIP_SYNC.md 참고, 이번 세션에서는 재확인하지 않음)

작업:
완료:
- 8차에서 발견된 route 감속 오검출(고속도로 분기점 조기 과감속/원복)에 대해 사용자가
  근본수정(스파이크 제거 필터) 방향 선택
- carrot_man.py의 carrot_navi_route()에 3-샘플 median 필터 추가 (비전 curve_speed.py
  방식과 동일한 원리). Claude 샌드박스에서 GitHub 최신 코드 기준으로 미리 패치 적용,
  문법검증(py_compile), diff 검증, 합성 스파이크 제거 테스트까지 마친 뒤 사용자
  실행용 스크립트로 전달
- 사용자가 Termux에서 스크립트 실행, carrot-ryu 브랜치에 반영 완료
  (commit 0201519..2dbe492). Claude가 codeload.github.com tarball로 push된 실제
  commit 내용까지 재확인, 문법 검증 재통과 확인
- FINDINGS.md / WIP.md에 상세 기록

미완료 / 다음 세션 우선순위:
1. **실주행 재검증 필요 (최우선)** — carrot-ryu commit 2dbe492가 실제 콤마 디바이스에
   설치되어, 8차에서 문제가 있었던 것과 동일/유사한 고속도로 분기점을 다시 통과할 때
   desiredSource="route" 전환 시점의 desiredSpeed 급락(오검출)이 사라졌는지 rlog로
   재확인 필요. 확인 전까지는 "고쳐졌다"고 단정하지 않음(12절 원칙)
2. carrot-ms가 추가한 "모델 셀렉터" 코드(carrot/model_selector, web(models) 등) 자체는
   아직 분석하지 않음
3. TurnSpeedControlMode=2 / EnableSpeedTF=0 / DisableDM=2 등 사용자 의도 확인
   (오래된 보류 항목, 일부는 안전 관련)
4. carrot-wip(ajouatom/openpilot)이 carrot-ms보다 앞서 진행 중 — carrot-ms가 다음에
   rebase되는 시점에 다시 동기화 검토 필요

검증: 정적 분석 + 문법 검증 + 합성(가상) 스파이크 데이터로만 검증. 실차 검증 미실시.

주의사항:
- 이번 세션의 코드 변경(carrot_man.py 한 블록)은 GitHub API/tarball로 실제 반영 여부와
  내용을 이중 확인함(raw.githubusercontent.com은 CDN 캐시로 몇 분간 구버전을 보여줄 수
  있으니, 즉시 확인이 필요하면 codeload.github.com tarball 방식 사용 권장)
- Termux에서 heredoc에 긴 한글 텍스트를 붙여넣을 때 줄바꿈이 깨질 수 있음(이번
  세션에서 재확인됨) → 실행 실패 시 무엇이 실제로 반영됐는지 항상 GitHub에서
  재확인 후 진행
- git diff는 반드시 --no-pager 또는 GIT_PAGER=cat과 함께 사용 (안 그러면 Termux에서
  less 페이저가 꼬여 셸이 깨질 수 있음, 이번 세션에서 확인됨)
- route 감속 관련 코드는 이제 8차 이전과 다르므로, 향후 carrot-ms 동기화 시 이
  블록에서 충돌 가능성 있음(10절 "carrot-ms 대비 무엇이 왜 달라졌는지" 원칙 참고)

다음 작업 후보:
1. 실주행 재검증 (최우선, 사용자가 실제 주행 후 로그 업로드해야 진행 가능)
2. (선택) carrot-ms의 model_selector 코드 분석
3. TurnSpeedControlMode/EnableSpeedTF/DisableDM 등 사용자 의도 확인
