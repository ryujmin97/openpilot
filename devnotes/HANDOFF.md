Worker: Claude (79차 -- 항목 18 완료: ko.js gdrive 클라이언트 유형 안내 문구 수정)
Date: 2026-09-18
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `a959576f6973b44d878617399241cd35c47bf1bd`, 항목 5~10·12·17·18 전부 push 완료)
Note Branch: carrot-ryu-note (base: 이 커밋으로 갱신, 직전 base `2a3b6de1ae9c5ff56ccf47bf7d3ee0caabd8dc0e`, 78cha-fix)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스, 변경 없음).

작업:
직전 세션(78차)에서 지침 문서 4절 0단계 확인 후 이어받아, HANDOFF.md/WIP.md/CURRENT_STATUS.md가 지시한
다음 세션 최우선인 항목 18(33차, commit `789667f7`, ko.js gdrive 클라이언트 유형 안내 문구 수정:
"데스크톱 앱 유형" -> "TV 및 제한된 입력이 있는 기기 유형")을 진행했다. 원본 커밋을 `.patch`
엔드포인트로 조회(GitHub API rate limit 회피), sparse-checkout으로 `web/` 디렉터리 구조를 확인해
ko.js가 `index.html`에서 `<script>`로 직접 로드되며 build.mjs 번들 대상이 아님을 확인, npm 빌드가
불필요함을 사전에 확정했다. 반영 스크립트 최초 전달본(v1)이 BOM 누락으로 실행 중 안전하게 중단된
것을 사용자 실행 로그로 확인, BOM 포함 -v2로 재전달해 push까지 완료했다.

완료:
1. 지침 문서 v2(커밋 `2a3b6de`) 재조회, 4절 0단계 완료 확인(`git ls-remote`로 carrot-ryu
   `c197cd4e`/carrot-ryu-note `2a3b6de` 확인, 78차 보고와 일치).
2. 항목 18 원본 커밋(`789667f7`)을 `.patch` 엔드포인트로 조회: `openpilot/selfdrive/carrot/web/
   js/translations/ko.js` 한 파일, 한 줄 변경. sparse-checkout으로 이 파일이 번들 비대상임을 확인.
3. 새 베이스(`c197cd4e`)의 대상 라인이 anchor와 1회만 매치함을 sandbox에서 시뮬레이션, 변경 후
   결과가 원본 diff와 완전히 동일함을 사전 확인(9절).
4. 반영 스크립트(v1) 전달 -- 실행 중 anchor 0회 매치로 안전하게 중단(15절/18절 안전장치 정상
   동작). 원인 진단: 스크립트 자체가 UTF-8 BOM 없이 생성되어 PowerShell 5.1이 CP949로 오인식,
   스크립트 내부 한글 anchor 문자열이 로드 시점에 이미 깨져 있었음(9절 기존 규칙의 재발, 이번엔
   Claude가 직접 저지름).
5. BOM 포함 v2로 재생성/재전달, 사용자 실행으로 carrot-ryu commit
   `a959576f6973b44d878617399241cd35c47bf1bd`(커밋 메시지: `33cha: fix ko.js gdrive client id
   type desc (desktop app -> TV/limited-input device)`)로 push 완료.
6. push 후 `git ls-remote` + GitHub compare API(`c197cd4e...a959576f`)로 재검증: 변경 파일
   정확히 1개(`ko.js`), diff가 원본 33차 커밋과 완전히 동일함을 확인. raw 조회(SHA고정)로 대상
   파일 전체가 sandbox 예상 결과와 byte-exact 일치함도 확인(16절).
7. CURRENT_STATUS.md 갱신: carrot-ryu HEAD 라인을 `a959576f`(79차)로 교체, 코드 수정 현황 항목
   18을 "재적용 완료·push·byte-exact 확인"으로 갱신, 79차 서술 불릿 추가.
8. WIP.md 최상단(7절 규칙)에 79차 항목 추가: 항목 18 진행 경위, v1 BOM 실패/v2 해결 경위, 검증
   결과를 서술.
9. 이 파일(HANDOFF.md)을 79차 기준으로 전체 재작성(8절 "교체형" 규칙).

미완료(다음 세션 최우선):
1. 항목 20(36차, commit `0835b059`) -- 화면녹화 탭 업로드 UI + 라벨/햄버거 메뉴 버그 수정.
2. 항목 21(37차) -- `_ensure_folder()` TOCTOU 레이스 수정(asyncio.Lock).
3. (5~21 전부 끝난 뒤) 항목 22(39차, `797fca2e`) 본편, 항목 23(39cha-fix), 항목 26(44차) 순서로
   재개.
4. (낮은 우선순위, 여유 있을 때) WIP.md 파일 안의 "# WIP" 헤더 중복(7회 등장, 34862바이트 지점
   포함) 정리 -- 여전히 미완료 상태로 남아있음. 이번 세션 devnotes 스크립트는 StartsWith 방식으로
   맨 앞 앵커만 사용해 이 중복과 무관하게 안전하게 처리했다.
5. 위 1~3은 규모가 커 한 세션에 몰아서 끝내지 않는다(17절) -- 순서(20→21) 자체는 바꾸지 않되
   몇 개 단위로 나눌지는 다음 세션에서 사용자와 다시 정한다.

검증: 코드 diff는 GitHub compare API + raw 조회(SHA고정)로 원본 33차 커밋과 byte-exact 동일함을
확인(16절). 실차 검증: 미실시(항목 5~21 전체가 아직 실기기 미배포, git pull 금지 상태 유지 중).

주의사항:
- 이번 사례의 교훈: working-rules(9절)에 이미 명시된 ".ps1 BOM 필수" 규칙이 Claude 자신의 스크립트
  생성 과정에서 재발했다. 안전장치(anchor 1회 매치 확인, 0회/2회 시 강제진행 금지)가 정상 동작해
  대상 파일 손상은 없었지만, 향후 세션은 한글이 포함된 .ps1을 전달하기 전에 파일 자체의 BOM 유무를
  스스로 재점검할 것(예: 첫 3바이트가 EF BB BF인지 확인).
- CURRENT_STATUS.md/WIP.md는 원본이 CRLF 개행이므로, 이 파일들을 다시 다룰 때 Python으로 읽고
  쓸 경우 `newline=''`으로 원본 개행을 보존해야 한다(텍스트 모드 기본값은 개행을 자동 변환해
  전체 diff를 오염시킴 -- 이번 세션에서 CURRENT_STATUS.md 초안 작성 중 직접 겪고 즉시 수정함).
- 다음 세션은 이 파일을 신뢰하기 전에 여전히 `git ls-remote`로 carrot-ryu/carrot-ryu-note HEAD를
  먼저 확인할 것(3절 원칙은 예외 없음).

다음 작업 후보:
1. 항목 20(`0835b059`, 화면녹화 탭 업로드 UI 신규 구현 + 당근서버 라벨/햄버거 메뉴 버그 수정)
   원본 커밋 patch 조회부터 착수.
2. (여유 있으면) WIP.md "# WIP" 헤더 중복 정리 여부를 사용자와 논의.
