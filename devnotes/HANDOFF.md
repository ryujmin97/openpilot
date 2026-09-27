Worker: Claude (190cha, Claude Sonnet 5)
Date: 2026-09-28
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit 6ed56f0d64df0612e3993e247d03fc199903569e, 189cha docs/driving_mode_recovery.md trailing newline 수정 push 완료·재확인됨. 190cha는 코드 변경 없음.)
Note Branch: carrot-ryu-note (base commit c9b0f7a0c130dacf6836ad624eea5a95df1bb973, 189차 devnotes push 완료 확인. 이번 세션 190cha devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 -> 3441183(변동 없음, 188cha에서 확정, 190cha에서 변동 없음)

작업:
1. 세션 시작 시 189cha 완료 여부를 GitHub 직접 재확인(16절) — carrot-ryu
   6ed56f0, docs/driving_mode_recovery.md blob hash bbcd9153bd1ce9daa45e731af0199ffcc0ff84d5
   일치, trailing newline 존재 확인.
2. 9절 체크리스트 8번(pwsh 파서 검증) 보완 작업 진행 — 그간 생략 원인이던
   api.github.com rate limit 문제를 releases/latest 302 redirect 방식으로 해결,
   pwsh 7.6.6 설치 성공.
3. Parser 검증 로직을 positive/negative control로 재확인(후행 쉼표 오류 정확히
   탐지, 정상 스크립트 0 error).
4. 사용자가 189cha_fix_trailing_newline.ps1 원본을 재업로드 → 소급 검증(BOM,
   파서 오류 0건) 완료.
5. 사용자 승인(19절)에 따라 PROJECT_INSTRUCTIONS_carrot-ryu.md 9절 체크리스트
   8번을 새 설치 방식으로 갱신.
6. 이 devnotes(190차) 및 지침 문서 반영.

완료:
1. 189cha 완료 상태 GitHub 직접 재확인.
2. 9절 체크리스트 8번의 rate limit 문제 해결(releases/latest redirect 방식) 및
   검증.
3. 189cha_fix_trailing_newline.ps1 소급 pwsh 파서 검증(오류 0건).
4. 지침 문서 9절 체크리스트 8번 갱신(19절 절차 완료).

미완료:
1. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보,
   pytest CI 환경(conftest.py 포함 실제 cereal 실행), 102ms wide-camera BOOT_TS
   gap.
2. (이월) carrot-ms 정기 동기화 점검(2절) — 다음 세션에서 필요 여부 판단.

검증:
- carrot-ryu HEAD를 raw.githubusercontent.com(SHA고정)으로 직접 조회해
  docs/driving_mode_recovery.md blob hash 재계산, 기대값과 일치 확인(16절).
- pwsh 7.6.6을 GitHub 릴리스 tarball(releases/latest redirect로 버전 확보)로
  직접 설치, `--version` 출력으로 정상 동작 확인.
- Parser 기반 구문 검증을 trailing-comma negative control(1 error) / 정상
  스크립트 positive control(0 error)로 대조 검증.
- 189cha_fix_trailing_newline.ps1(사용자 재업로드본) BOM 확인(`EF BB BF`) +
  pwsh 파서 오류 0건 확인.
- 실차 검증: 미실시(12절, 190cha는 코드 변경 없음).

주의사항:
- 9절 체크리스트 8번의 pwsh 설치가 이제 rate limit 없이 안정적으로 가능해졌으므로,
  앞으로 전달하는 모든 `.ps1`은 이 단계를 생략하지 않고 매번 수행할 것.
- api.github.com은 여전히 유용하지만(commit 조회 등) rate limit에 취약하므로,
  git ls-remote/raw.githubusercontent.com(SHA고정)/releases 302 redirect처럼
  rate limit 없는 대체 경로를 우선 사용하는 습관을 유지할 것.

다음 작업:
1. carrot-ms 정기 동기화 점검(2절) 필요 여부 판단.
2. 이월 항목(실차 검증들) 중 우선순위 있는 것부터 진행.
3. 9절 체크리스트 8번은 이제 모든 향후 `.ps1` 전달 시 기본으로 수행.
