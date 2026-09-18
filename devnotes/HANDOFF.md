Worker: Claude (87차)
Date: 2026-09-18
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `ba929b5f29cf88530f2fd64e28b5fc59f12e4c8b`, 86차 항목22/23/26 push 확인 + 항목24(41차, v2) 재적용 완료 기준. 이번 세션은 그 위에서 항목 30~36 재적용, 반영 스크립트 실행/push 대기)
Note Branch: carrot-ryu-note (base: `15cdf6e2e094ad479fcc9da4e980154785392889`, 86차 devnotes 기준. 이번 세션 CURRENT_STATUS/HANDOFF/WIP 갱신 + WIP.md null byte 손상 수정, 반영 스크립트 실행/push 대기)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스, 변경 없음).

작업:
세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu가 `ba929b5`, carrot-ryu-note가 `15cdf6e`로 86차 상태 그대로임을
확인(4절) -- 86차 이후 추가 push 없음. CURRENT_STATUS.md 최상단 "carrot-ryu HEAD" 줄이 82차/83차 기준(`435d0b58`)으로
오래 방치돼 있던 것을 16절에 따라 발견, 이번 세션에서 정정(코드 변경 아님).

이어서 마지막 남은 이식 항목인 30~36(스크린샷 캡처 체인 7건: DPI 스케일 버그(47차) → 진단로그+버튼위치(49차) →
PNG 롤백(50차) → 480p 다운스케일+캡처타이밍(51차) → 캡처위치 재조정/border HUD(52차) → render-texture 재설계
(54차) → 상하반전(55차))을 새 베이스(`ba929b5`) 위에 착수. carrot-ryu-v1(`9ccf1206`) 아카이브에서 이 체인의 56차
최종본(`screenshot_capture.py`/`screenshot_button.py`/`hud_renderer.py`/`system/ui/lib/application.py` 4개 파일)을
가져와 현재 베이스와 대조:
- `screenshot_capture.py`/`screenshot_button.py`: 다른 세션이 그 사이 건드리지 않아 v1과 전체교체로 안전하게
  적용 가능함을 확인, 전체교체로 반영.
- `hud_renderer.py`: 84차에서 추가된 sdi_descr 배지 위치 보정(핵심 발견 40)이 v1 아카이브 시점 이후의 변경이라
  전체교체하면 유실되므로, 49차 버튼위치 이동(anchor_x 도입, 스크린샷 버튼을 화면 중앙에서 좌측으로 이동)
  부분만 Replace-Block 2곳으로 좁혀 반영해 84차 수정을 보존.
- `application.py`: 이 저장소(20절 리셋 이후 베이스)에 처음 반영되는 파일(54차 `request_temp_capture()`
  render-texture 재사용 재설계) -- v1 아카이브와 완전히 동일하게 전체교체(diff 결과 IDENTICAL).
- `augmented_road_view.py`: 51·52차가 추가했던 캡처 호출부가 54차 재설계로 이미 다시 원복돼 있어(v1 기준
  diff 0), 이번 재적용에서 변경 없음.

독립 `git clone`에 4개 파일 적용 → `python3 -m py_compile` 4개 전부 통과, `application.py`는 v1 아카이브와
byte-exact 일치(diff 무출력)까지 확인, 구 API(`capture_onroad_screenshot`/`consume_pending_screenshot_capture`)
잔여 참조 0건, `gui_app` 싱글턴 import 경로 정상 확인(9절/16절). js/css 소스 변경이 없어 번들 재생성/
`params_keys.h` 등록 불필요. 최종 파일 4개(BOM 없음 확인)를 base64로 담아 반영 스크립트
(`87cha_items30_36_carrot_ryu.ps1`)를 작성, 완전히 별개의 두 번째 clone에 페이로드를 재현해 `py_compile`
재통과 + diff stat(4 files, +138/-20)이 최초 검증과 동일함을 재확인했다(핵심 발견 42 원칙 -- 결과 자체를
다시 확인). 9절 "전달 전 필수 자가검증 체크리스트" 전항목(비ASCII 0건/`core.autocrlf=false`/`Get-PythonCmd`
+ EOF 공급/임시폴더 자동삭제)을 스크립트 파일 grep으로 직접 대조해 통과를 확인했다.

이 코드 작업과 별개로, devnotes 갱신을 준비하며 `WIP.md`를 raw로 재조회하는 과정에서 실제 null byte(`\x00`)
손상 1건을 처음 발견했다: 57차 항목 본문 "carrot-ryu fork point(`\x00`2015190f5, ...)" 자리에 있어야 할 숫자
`0`이 널바이트로 바뀌어 있었다(같은 커밋 해시가 파일 다른 곳(606번째 줄 등)에는 `02015190f5`로 정상 표기돼
있어 원본 문자를 바이트 단위로 확정할 수 있었다). 그 외 이 파일에 다른 null byte가 없음을 전수 확인 후
`0`으로 복원. WIP.md는 평소 "이어붙이기형"(최상단 anchor 삽입만)이지만, 이번엔 파일 중간의 손상을 같은
커밋에서 함께 고쳐야 해서 9절의 "이번만 예외" 원칙에 따라 이번 회차에 한해 파일 전체를 base64로 담아
전체교체 방식으로 반영한다(다음 회차부터는 다시 anchor 삽입 방식으로 복귀). 파일 맨 끝(1차 세션 기록)에
이미 있던 별개의 인코딩 깨짐(mojibake로 추정, null byte와 무관 -- 원본 파일과 대조해 내 수정 이전부터
있었음을 확인)과 기존에 알려진 "`# WIP` 헤더 중복"(789번째 줄, "다음 작업" 목록에 낮은 우선순위로 이미
기록됨)은 7절 "임의 축소/삭제 금지" 원칙에 따라 이번 세션에서 손대지 않았다.

완료:
1. 4절/16절 원칙대로 carrot-ryu/carrot-ryu-note가 86차 상태 그대로임을 재확인, CURRENT_STATUS.md 최상단
   stale HEAD 표기(82차/83차 기준)를 86차 기준으로 정정.
2. 항목 30~36(스크린샷 캡처 체인 전체)을 carrot-ryu-v1 최종본 기준으로 새 베이스 위에 재구성(84차 sdi_descr
   수정 보존), 독립 clone 2회(최초 검증 + 완전 별개 재현)로 py_compile 통과 + byte-exact 일치 확인.
3. 반영 스크립트(`87cha_items30_36_carrot_ryu.ps1`) 작성, 9절 체크리스트 전항목 통과 확인.
4. WIP.md의 null byte 손상 1건을 발견/원인 특정/복원.
5. devnotes 반영 스크립트(`87cha_devnotes_carrot_ryu_note.ps1`) 작성: HANDOFF.md(이 파일, 전체교체) +
   CURRENT_STATUS.md(최상단 HEAD 줄 + 항목 30~36 일곱 줄 + 87차 신규 항목, Replace-Block으로 부분 갱신 --
   파일 규모상 9절 "교체형" 원칙의 실무적 예외를 이번에도 적용) + WIP.md(전체교체, null byte 수정 + 87차
   신규 항목 반영, 9절 "이번만 예외" 명시).

미완료(다음 세션 최우선):
1. 사용자가 `87cha_items30_36_carrot_ryu.ps1`을 실행해 carrot-ryu에 push할 것. 이 push가 완료되면 36개
   항목 전부(1~36) 재적용이 완료됨.
2. push 확인되면 devnotes 반영 스크립트(`87cha_devnotes_carrot_ryu_note.ps1`)도 실행해 HANDOFF.md/
   CURRENT_STATUS.md/WIP.md를 최신 상태로 반영할 것.
3. 항목 30~36(스크린샷 캡처 체인 전체: DPI/진단로그/PNG/480p/캡처타이밍/render-texture 재설계/상하반전)의
   실차 검증 -- 61차 리셋 이후 새 베이스에 처음 재적용되는 경로라 프로젝트 역사상 이 형태로는 한 번도 실차
   확인된 적 없음(12절). 36개 항목 전부가 이 시점부터 처음으로 "새 베이스 기준 실차 재검증 완료" 상태를
   목표로 삼을 수 있게 됨.
4. WIP.md 파일 맨 끝(1차 세션 기록)의 별개 인코딩 깨짐(mojibake) 처리 여부 사용자 판단 필요(이번 세션에서
   발견만 하고 손대지 않음, 새로운 이슈이므로 "# WIP" 헤더 중복과 별개로 취급).
5. WIP.md "# WIP" 헤더 중복(789번째 줄) 정리 여부(기존부터 낮은 우선순위로 이월 중).
6. 36개 항목 전부 재적용이 끝나면, 다음 큰 작업 후보로 carrot-ms 신규 커밋 cherry-pick 검토(WIP_SYNC.md),
   test_web_upload.py 실행/데드코드 3개 정리, docs 갱신, 37차 락 동시성 재현 검증 등이 대기 중(CURRENT_STATUS.md
   "다음 작업" 목록 참고).

검증: `git ls-remote`로 carrot-ryu/carrot-ryu-note 실제 HEAD가 86차 상태 그대로임을 재확인. 항목 30~36 코드는
독립 clone 2회(최초 검증 + 완전히 별개의 재현 clone)에서 py_compile 4개 전부 통과, application.py는
carrot-ryu-v1 아카이브와 byte-exact 일치, 구 API 잔여 참조 0건을 각각 확인. 반영 스크립트 자체도 9절
체크리스트 항목을 스크립트 파일 grep으로 직접 대조(서술이 아닌 코드 확인, 핵심 발견 44 교훈 적용). WIP.md의
null byte 위치는 파일 다른 곳의 동일 해시 표기와 바이트 단위로 대조해 원본 문자를 확정했고, 복원 후 파일
전체에 null byte가 0건임을 재확인. 실차 검증: 미실시(이번 세션은 코드 변경 자체가 아직 push되지 않음).

주의사항:
- CURRENT_STATUS.md 최상단 "carrot-ryu HEAD" 줄이 여러 세션(최소 82차 이후)에 걸쳐 정정되지 않고 방치된
  패턴이 재확인됨. 과거에도 유사 항목(내용 전체) 표기 지연은 핵심 발견 27/38로 문서화돼 있었으나, 이번처럼
  "최상단 요약 한 줄"만 별도로 오래 방치되는 경우는 세션들이 본문 항목/서술 갱신에 집중하며 최상단 줄을
  놓치기 쉬운 패턴으로 보임 -- 다음 세션부터 devnotes 갱신 시 최상단 HEAD 줄도 매번 함께 점검할 것.
- WIP.md의 null byte 손상은 이번 세션에서 처음 발견됐고 정확한 발생 경위는 미확정이다(과거 세션들이 "9절
  체크리스트 전항목 통과"로 기록했던 시점 중 어딘가에서 실제로는 걸러지지 못했을 가능성 -- 핵심 발견 41/42/44와
  유사 계열). 이번 수정으로 이 파일의 null byte는 0건이 됐지만, 앞으로 devnotes 전체교체 작업 시에는 "BOM
  확인"뿐 아니라 "null byte 0건 확인"도 자가검증 체크리스트에 추가하는 것을 다음 19절 절차로 제안할 가치가
  있음(이번 세션에서는 발견/수정만 하고 지침 문서 자체는 변경하지 않음 -- 사용자 승인 필요).
- 남은 미이식 항목은 이번 세션 스크립트(30~36)가 push되면 0개가 된다. 36개 항목 전부가 push 확인되면
  "36개 항목 전부 완료" 마일스톤이며, 이후 프로젝트 우선순위는 실차 검증 및 carrot-ms 신규 커밋 검토로
  전환될 예정(사용자 판단 필요).

다음 작업 후보:
1. 항목 30~36 코드 스크립트 실행/push 확인, devnotes 스크립트도 실행/push 확인.
2. 항목 30~36 전체 실차 검증(스크린샷 버튼 반응, HUD 포함 여부, 480p 다운스케일, 정방향 저장까지 한 번에).
3. WIP.md mojibake(1차 세션 기록)/헤더 중복 정리 여부 사용자 확인.
4. carrot-ms 신규 커밋 cherry-pick 검토 착수(WIP_SYNC.md 참고).
