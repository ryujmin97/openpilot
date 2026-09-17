Worker: Claude (78차 -- 항목 17 완료: Google Drive drive.file 스코프+폴더 자동생성 복귀)
Date: 2026-09-18
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `c197cd4e627c6f266e6f5529d152d1984a47fcd6`, 항목 5~10·12·17 전부 push 완료)
Note Branch: carrot-ryu-note (base: 이 커밋으로 갱신, 직전 base `227bde467c10329714d2f32d5f22820b08c64015`, 77차-fix)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스, 변경 없음).

작업:
직전 대화에서 사용자가 항목 17(32차, commit `c704371a`, Google Drive drive.file 스코프+폴더
자동생성 복귀) 반영 스크립트(챗지피티 작성)를 실행해 새 베이스(`27d81a4`) 위에 재적용, commit
`c197cd4e`로 push까지 완료했다. 하지만 devnotes(CURRENT_STATUS.md/WIP.md/HANDOFF.md) 3개 파일
편집이 HANDOFF.md 작성 전에 끊겨 아무것도 push되지 못한 채 대화가 종료됐다. 이번 세션은 그 이어받기:
세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu가 이미 `c197cd4e`인데 carrot-ryu-note는 여전히
`227bde4`(77차-fix)에 머물러 있음을 확인해 devnotes 미반영 상태를 확정한 뒤, CURRENT_STATUS.md/
WIP.md 편집을 처음부터 재확인/재작성하고 이 파일(HANDOFF.md)까지 완성해 같은 세션 번호(78차)로
한 번에 push한다. 아울러 재발 방지를 위해 이번에 드러난 이슈들을 핵심 발견 39로 devnotes에
명시적으로 기록한다(사용자 요청: "같은 실수를 반복하지 않도록 기록").

완료:
1. 지침 문서 v2(커밋 `227bde4`) 재조회, 4절 0단계 완료 확인.
2. `git ls-remote`로 세션 시작 체크포인트 확인: carrot-ryu `c197cd4e`(이미 항목 17 push 완료),
   carrot-ryu-note `227bde4`(77차-fix, devnotes 미반영) -- 두 브랜치 HEAD가 서로 다른 세션의
   진행 상태를 반영하고 있음을 확인(16절, 핵심 발견 39-(4)).
3. 독립 clone + GitHub 원본 커밋 blob 대조로 항목 17 push 결과를 재검증: 새 HEAD
   (`c197cd4e627c6f266e6f5529d152d1984a47fcd6`)의 `openpilot/selfdrive/carrot/gdrive_upload.py`
   blob hash(`e6a5832f07af9a3249942b9f4d64df28ffe4a5a7`)가 원본 32차 커밋(`c704371a`)의 결과
   blob hash와 완전히 일치함을 확인(byte-exact, 16절). diffstat도 직전 대화의 실행 로그와 동일
   (89 changes, 53 insertions(+), 36 deletions(-)).
4. CURRENT_STATUS.md 갱신: carrot-ryu HEAD 라인을 `c197cd4e`(78차)로 교체, 코드 수정 현황 항목
   17을 "새 베이스 위 재적용 완료·push·byte-exact 확인"으로 갱신, 78차 서술 불릿 추가, 핵심 발견
   39(스크립트 버그 3종 + devnotes 미반영 위험) 섹션 신설.
5. WIP.md 최상단(7절 규칙)에 78차 항목 추가: 스크립트 버그 3건의 원인/수정 경위, byte-exact
   재검증 결과, devnotes 유실 직전 사례와 그 원인을 서술.
6. 이 파일(HANDOFF.md)을 78차 기준으로 전체 재작성(8절 "교체형" 규칙).

미완료(다음 세션 최우선):
1. 항목 18(33차, commit `789667f7`) -- ko.js gdrive 클라이언트 유형 안내 문구 수정(항목 10 위에
   적용, 항목 17 다음).
2. 항목 20(36차, commit `0835b059`) -- 화면녹화 탭 업로드 UI + 라벨/햄버거 메뉴 버그 수정.
3. 항목 21(37차) -- `_ensure_folder()` TOCTOU 레이스 수정(asyncio.Lock).
4. (5~21 전부 끝난 뒤) 항목 22(39차, `797fca2e`) 본편, 항목 23(39cha-fix), 항목 26(44차) 순서로
   재개.
5. (낮은 우선순위, 여유 있을 때) WIP.md 34862바이트 지점의 "# WIP" 헤더 중복 정리 -- 여전히
   미완료 상태로 남아있음.
6. 위 1~4는 규모가 커 한 세션에 몰아서 끝내지 않는다(17절) -- 순서(18→20→21) 자체는 바꾸지
   않되 몇 개 단위로 나눌지는 다음 세션에서 사용자와 다시 정한다.

검증: 코드 diff는 독립 clone + blob hash 대조로 원본 32차 커밋과 byte-exact 동일함을 확인(16절).
devnotes 미반영 상태는 `git ls-remote`로 직접 재확인(추측 아님, 11절). 실차 검증: 미실시(항목
5~21 전체가 아직 실기기 미배포, git pull 금지 상태 유지 중).

주의사항:
- 이번 사례의 핵심 교훈(핵심 발견 39-(4)): 대화가 중간에 끊기면 컨테이너 안에서 편집 중이던
  devnotes 파일 내용은 전부 사라지고, 그 시점까지 실제로 GitHub에 push된 것만 남는다. 코드 push가
  확인되면 devnotes 3개 파일 편집을 뒤로 미루지 말고 같은 응답 또는 바로 다음 응답에서 이어서
  완성해 push까지 끝내는 편이 안전하다. 다음 세션은 두 브랜치의 `git ls-remote` HEAD가 서로 다른
  세션의 상태를 가리키고 있지 않은지(코드는 최신인데 devnotes만 뒤처짐, 또는 그 반대) 항상 먼저
  확인할 것(4절 0단계와 별개로 코드 브랜치도 매 세션 시작 시 반드시 `git ls-remote`로 확인).
- 다른 AI(챗지피티)가 작성한 반영 스크립트를 실행할 때는 이 프로젝트의 검증 계층(9절 anchor
  1회 매치, `git apply --check`, `py_compile`)과 별개로 스크립트 자체의 로직 버그(이번엔 PowerShell
  배열 매치 시맨틱, 파이프라인 인코딩 손상, 축약 SHA 등 3가지) 가능성을 항상 열어두고, 실행 로그로
  단계별 성공/실패를 구분해 스크립트 버그와 실제 코드 문제를 혼동하지 않는다(핵심 발견 39-(1)~(3)).
- 다음 세션은 이 파일을 신뢰하기 전에 여전히 `git ls-remote`로 carrot-ryu/carrot-ryu-note HEAD를
  먼저 확인할 것(3절 원칙은 예외 없음).

다음 작업 후보:
1. 항목 18(`789667f7`, ko.js gdrive 클라이언트 유형 안내 문구 수정) 원본 커밋 patch 조회부터 착수.
2. (여유 있으면) WIP.md "# WIP" 헤더 중복 정리 여부를 사용자와 논의.
