# HANDOFF

Worker: Claude (45차 -- 44차 소스 수정은 맞았으나 생성 번들 미재생성으로 크래시가 실기기에 남아있던 문제 발견/수정)
Date: 2026-09-16
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: e2f35619825959b23f6d937c8e00cbb0fbd02a5a, 44차. 이번 세션 반영 스크립트 작성 완료, 사용자 실행 대기)
Note Branch: carrot-ryu-note (이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 체크포인트 이후 신규 23건 확인, WIP_SYNC.md 40차 체크포인트 반영 스크립트 실행 여부 미확인(계속 이월)

작업:
사용자가 44차 반영 스크립트 실행 후에도 화면녹화 탭에서 사진을 선택하면 `formatLogBytes is not defined`가 그대로 재현된다는 스크린샷/영상을 제보(delete all videos는 정상 동작, 영상 녹화 깜빡임도 정상 확인). GitHub carrot-ryu HEAD(commit e2f35619, 44차)를 직접 조회해 소스(`screenshots.js`)는 정확히 고쳐져 있음을 확인했으나, 같이 커밋된 생성 번들(`js/generated/logs.js`)에는 `formatLogBytes` 함수 정의가 없고 호출부만 미해석 외부 참조로 남아있어 런타임에 크래시가 나는 것을 발견. 같은 소스로 `npm install && node build.mjs`를 직접 실행해 재현 -- 재생성된 번들에서는 문제가 사라지고(`formatLogBytes` 리터럴이 정상적으로 0회로 축약됨), `node --test` 737/737 통과. 변경 diff는 `js/generated/logs.js`와 `generated/asset-manifest.json`(해시 한 줄) 2개 파일로 한정됨을 확인.

완료:
- 원인 확정 (FINDINGS.md 2026-09-16(45차) 항목, 핵심 발견 30 참고): 44차 세션이 소스는 고쳤지만 `npm install && node build.mjs`로 생성 번들을 재생성하는 단계를 건너뛴 채 예전 번들을 그대로 커밋함. 기기는 Node를 띄우지 않고 커밋된 번들을 그대로 서빙하는 구조라(레포 `.gitignore` 주석에 명시), 소스만 맞고 번들이 어긋나면 겉보기엔 정상 diff라도 실기기에서는 효과가 전혀 없음.
- 반영 스크립트(`45cha_rebuild_bundle_carrot_ryu.ps1`) 작성: 기존처럼 Replace-Block 문자열 치환이 아니라, 사용자 PC에서 실제로 `git clone`(임시 폴더, `core.autocrlf=false`) 후 `npm install && node build.mjs`를 그 자리에서 실행하고, 변경된 생성 파일(`js/generated/`, `css/generated/`, `generated/asset-manifest.json`)만 골라 커밋/push하도록 작성. 빌드 후 `git status`로 예상 범위 밖의 변경이 섞이면 커밋 없이 중단(15절 강제 진행 금지). 109KB 넘는 압축 번들을 스크립트 문자열에 그대로 박아넣는 대신 빌드 과정 자체를 재현하는 방식을 택함.
- devnotes 갱신: WIP.md 45차 신규 항목 prepend, FINDINGS.md 핵심 발견 30 append, 이 파일(HANDOFF.md)/CURRENT_STATUS.md 45차 기준 전체 교체.

미완료 (다음 세션 이월):
1. [최우선] `45cha_rebuild_bundle_carrot_ryu.ps1` 사용자 실행 확인 -- push 후 carrot-ryu에 `js/generated/logs.js`/`generated/asset-manifest.json`이 실제로 바뀌었는지 `git ls-remote`+commit patch로 재확인.
2. [최우선, 1번 완료 후] 44차 미완료 항목 1~2번(사진 목록이 크래시 없이 렌더되는지, delete all videos가 사진까지 지우는지) 실기기 재검증 -- 이번 번들 재생성 전까지는 검증 자체가 불가능했던 항목.
3. [이월, 44차] 녹화 버튼 깜빡임 실기기 재검증(녹화 중에만 실제로 깜빡이는지).
4. [이월, 41차] 로그탭 새로고침 아이콘 실기기 검증.
5. [이월] 37차 락 수정의 실제 동시성 재현 검증.
6. [이월] 34차 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
7. [이월] 28~30차 레이아웃 정밀 재검증.
8. [이월] 실차 재검증(8~45차 코드 변경 전부, 12절 원칙).
9. [이월] 실기기에서 직접 디버깅: 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부(핵심 발견 16과 연결 -- 이번에 확인된 "소스-번들 불일치" 패턴이 그 미해결 이슈의 원인일 가능성도 재검토할 것).
10. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 + 대응 테스트 삭제/갱신.
11. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
12. [이월] carrot-ms 모델 셀렉터 코드 분석 착수. WIP_SYNC.md 40차 체크포인트 반영 확인 필요.

검증: `npm install && node build.mjs`를 GitHub HEAD(e2f35619) 소스에 대해 직접 실행해 재현 -- 변경 파일 정확히 2개(`js/generated/logs.js`, `generated/asset-manifest.json` 해시 1줄), `node --test tests/**/*.test.mjs` 737/737 통과. **실기기 검증은 스크립트 실행 후에만 가능하며 아직 미실시.**

주의사항:
- **소스 수정과 번들 재생성은 별개 단계다.** 앞으로 `js/`, `css/` 아래 소스를 고치는 모든 반영 스크립트는 반드시 그 자리에서 `npm install && node build.mjs`를 실행하고 생성 산출물 diff까지 커밋에 포함할 것(핵심 발견 30). 소스만 Replace-Block으로 고치고 번들은 스냅샷/미갱신 상태로 두면 안 됨.
- 번들이 깨졌는지 판단하는 방법: 문제의 식별자(이번엔 `formatLogBytes`)가 압축된 번들 안에 원문 그대로 리터럴로 남아있으면 100% 번들링 실패 신호(정상이면 다른 로컬 함수들처럼 짧은 이름으로 축약돼 원문이 사라져야 함).
- 이 스크립트는 사용자 PC에 Node.js/npm이 설치돼 있어야 동작한다(기존 "프론트엔드 빌드 시 npm run build 필요" 관례와 동일 전제).

다음 작업 후보:
1. 45cha_rebuild_bundle_carrot_ryu.ps1 실행 확인(최우선)
2. 44차 3건(사진목록 크래시/전체삭제 범위/녹화버튼 깜빡임) 실기기 재검증
3. 41차 로그탭 새로고침 아이콘 실기기 검증
4. WIP_SYNC.md 40차 체크포인트 반영 확인 + carrot-ms 신규 23건 중 모델 셀렉터 3건 cherry-pick 검토 착수
5. 37차 락 수정 동시성 재현 검증