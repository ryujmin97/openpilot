# HANDOFF

Worker: Claude (45차-정정 -- carrot-ryu-note devnotes 중간 초안 push를 최종 상태로 재동기화, 코드는 이미 최종본대로 정상)
Date: 2026-09-16
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: `99b49a113e48ddaeebf83074b04e42d417a88612`, 45차 최종본 -- Linux sandbox 빌드 logs.js 전체교체 + asset-manifest 해시. sha256/`node --test` 737/737 검증 완료. 실기기 검증은 아직 미실시)
Note Branch: carrot-ryu-note (이 커밋으로 devnotes 재동기화. 참고: 이 커밋 직전 46차 세션이 PROJECT_INSTRUCTIONS_carrot-ryu.md를 v2로 재작성하고 CURRENT_STATUS.md 1줄을 갱신했음(commit `8f8209f`) -- 이 커밋은 그 위에서 이어받아 작업함. 지침 문서는 이제 v2가 최신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 체크포인트 이후 신규 23건 확인, WIP_SYNC.md 40차 체크포인트 반영 스크립트 실행 여부 미확인(계속 이월)

작업:
직전 devnotes 커밋(`0b0d322`, "bundle-not-rebuilt root cause + rebuild fix")의 실제 파일 내용이 세션 마지막에 전달된 최종 devnotes 스크립트와 다르다는 것을 재확인 절차 중 발견(핵심 발견 31 참고). carrot-ryu 코드는 최종본대로 정상 push/검증됐음을 커밋 메시지 전문 비교 + sha256 비교로 재확인했고, devnotes만 그보다 앞선 중간 초안 상태로 남아있었던 것으로 결론.

완료:
- carrot-ryu(코드) 최종 반영 상태 재검증: commit `99b49a1`의 커밋 메시지가 `45cha_apply_bundle_carrot_ryu.ps1`의 의도와 100% 일치, `js/generated/logs.js` sha256 `9236a383...` 일치, `formatLogBytes` 리터럴 0회 확인.
- devnotes 재동기화: WIP.md/FINDINGS.md에 핵심 발견 31(정정 경위) 추가, 이 파일과 CURRENT_STATUS.md를 실제 최종 상태 기준으로 전체 교체.
- shallow clone(`--depth 1`) 상태에서 `git show --stat`이 grafted root 취급되어 무관한 파일이 대량 나열되는 착시 현상을 확인하고 배제(핵심 발견 31 부수 발견).

미완료 (다음 세션 이월, 44차/45차와 동일):
1. [최우선] carrot-ryu HEAD(`99b49a1`)를 comma 실기기에 배포해 화면녹화 탭 사진 목록 렌더가 더 이상 `formatLogBytes is not defined`로 크래시하지 않는지 실기기 검증.
2. [최우선, 1번과 함께] 44차 미완료 항목: 사진 목록이 크래시 없이 렌더되는지, delete all videos가 사진까지 지우는지 실기기 재검증.
3. [이월, 44차] 녹화 버튼 깜빡임 실기기 재검증(녹화 중에만 실제로 깜빡이는지).
4. [이월, 41차] 로그탭 새로고침 아이콘 실기기 검증.
5. [이월] 37차 락 수정의 실제 동시성 재현 검증.
6. [이월] 34차 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
7. [이월] 28~30차 레이아웃 정밀 재검증.
8. [이월] 실차 재검증(8~45차 코드 변경 전부, 12절 원칙).
9. [이월] 실기기에서 직접 디버깅: 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부(핵심 발견 16과 연결).
10. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 + 대응 테스트 삭제/갱신.
11. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
12. [이월] carrot-ms 모델 셀렉터 코드 분석 착수. WIP_SYNC.md 40차 체크포인트 반영 확인 필요.
13. [신규, 사용자 승인 필요] 핵심 발견 31의 재발 방지 제안(스크립트 파일명 버전 표시 규칙화) 채택 여부 결정.

검증: 이 커밋 자체는 devnotes 텍스트 정정만 포함하며 코드 변경 없음. carrot-ryu 코드는 위 "완료" 항목의 sha256/테스트 재확인으로 검증됨. **실기기 검증은 여전히 미실시.**

주의사항:
- **같은 세션에서 동일 대상 스크립트를 다시 만들 때는 파일명을 반드시 다르게 할 것**(예: `-v2`, `-final`). 이번처럼 구버전 로컬 파일이 재실행될 위험을 원천 차단(핵심 발견 31).
- **`git clone --depth 1` 뒤 `git show --stat HEAD`로 "실제 변경 파일 목록"을 검증하지 말 것.** 부모 커밋이 없어 착시가 발생한다(핵심 발견 31 부수 발견). 검증 시에는 `--depth 5` 이상으로 clone하거나 `git show --stat <sha>^..<sha>`처럼 명시적으로 범위를 지정할 것.
- devnotes 커밋이 push 로그상 "성공"으로 보여도, 파일명 충돌 등으로 의도한 스크립트가 아닌 다른 파일이 실행됐을 수 있으므로, 중요한 devnotes 반영 후에는 이번처럼 실제 파일 내용(WIP.md 최상단 등)을 스크립트 원본과 직접 대조할 것.

다음 작업 후보:
1. carrot-ryu HEAD(99b49a1) 실기기 배포 + 크래시 해소 확인(최우선)
2. 44차 3건(사진목록 크래시/전체삭제 범위/녹화버튼 깜빡임) 실기기 재검증
3. 41차 로그탭 새로고침 아이콘 실기기 검증
4. 핵심 발견 31 재발 방지 제안 채택 여부 확인
5. WIP_SYNC.md 40차 체크포인트 반영 확인 + carrot-ms 신규 23건 중 모델 셀렉터 3건 cherry-pick 검토 착수