Worker: Claude (84차)
Date: 2026-09-18
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `435d0b58e6fc3a1012d659f379770fb48654e01f`, 84차 sdi_descr 배지 위치/글자크기 수정 커밋 push 대기)
Note Branch: carrot-ryu-note (base: 이 커밋으로 갱신, 직전 base `bdf1f7ae64b4fc6f9755e0f63d154552e7598aef`, 84차)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스, 변경 없음).

작업:
사용자가 실기기 스크린샷(2026-09-17)으로 우측하단 경로안내 박스의 "교통정보 수집지점"(sdi_descr,
카메라/POI 타입 안내) 문구가 그 위 초록색 배지 밖으로 밀려 보이는 버그를 제보. 사용자가 이 버그를
"carrot-ryu-v1 브랜치에서 고치자"고 표현했으나, v1은 20절/18절에 따라 생성 이후 수정이 금지된
아카이브 브랜치라 carrot-ryu(작업 브랜치)에 반영하는 방향으로 합의.

완료:
1. 이 버그가 지금까지 한 번도 실차로 제대로 검증된 적이 없었음을 devnotes 대조로 확인: 이 박스는
   `if sdi_descr: ... elif road_name: ...` 구조인데, FINDINGS.md 38차 항목이 "신호과속 배지
   부재로 판단 보류"라고 명시했고, HANDOFF.md 40차의 "정상 확인" 목록에도 도로명까지만 있고
   sdi_descr 케이스는 없었음 -- 즉 지금까지의 모든 실차 검증은 도로명(elif) 분기만 우연히
   캡처했던 것(12절/16절 원칙에 따른 재확인).
2. 근본 원인을 코드로 확정: `openpilot/system/ui/lib/text_draw.py`의 `get_text_draw_pos()`에
   `align="left_bottom"` 분기가 없어(다른 6개 정렬 케이스만 존재), `hud_renderer.py`의
   `_draw_text_left_bottom()`(제목/신호과속·교통정보 배지/도로명, 3곳에서 호출)이 실제로는
   `left_top`과 동일하게 동작함 -- 텍스트가 의도한 위치보다 자기 글자 높이만큼 아래로 밀려
   그려짐. carrot-ryu(`435d0b58`)와 carrot-ryu-v1(`9ccf1206`) 양쪽 다 이 버그가 동일하게
   존재함을 직접 조회로 확인.
3. 사용자 요청(공용 정렬 함수는 건드리지 말고 신호과속/교통정보 배지 텍스트만 수정 + 글자크기
   90%)에 따라, `hud_renderer.py`의 `_draw_turn_info_hud()` 중 `if info["sdi_descr"]:` 블록만
   범위를 한정해 수정. `elif road_name_text:`와 제목(`tbt_main_text`) 부분은 그대로 둠(같은
   원인이지만 이번엔 의도적으로 미수정, 10절 최소변경 원칙).
4. 수정 내용: (a) `sdi_size = int(eta_size * 0.9)`로 배지 전용 글자 크기 축소, (b) 배지
   위치(`badge_top`)를 먼저 고정한 뒤 실제 렌더링 동작(`y+6`이 텍스트 상단)에 맞춰 `label_y`를
   역산해 배지 안에 세로 중앙 정렬되도록 변경.
5. anchor 1회 매치 확인, `python3 -m py_compile` 통과 확인(리눅스 샌드박스). 반영 스크립트
   (`84cha_item_sdi_badge_fix.ps1`) 작성/전달, 실행 대기(push 미실시).

미완료(다음 세션 최우선):
1. 사용자가 `84cha_item_sdi_badge_fix.ps1`을 실행해 carrot-ryu에 push할 것.
2. push 확인되면 이 devnotes 반영 스크립트(`84cha_devnotes_carrot_ryu_note.ps1`)도 실행 확인할 것.
3. 실차 검증: sdi_descr 배지(신호과속/교통정보 수집지점 등)가 실제 카메라·POI 근처에서 초록 배지
   안에 제대로 들어오는지 확인(12절 -- 이 코드 경로는 프로젝트 전체 역사상 처음으로 검증되는 것).
4. (낮은 우선순위, 사용자 결정 대기) 제목(`tbt_main_text`)과 도로명(`road_name_text`)도 동일한
   `left_bottom` 버그의 영향을 받고 있음 -- `get_text_draw_pos()`에 `left_bottom` 분기를
   추가하는 근본 수정을 별도로 진행할지, 아니면 지금처럼 필요한 곳만 개별 보정할지 사용자 판단
   필요.
5. 항목 22(39차, `797fca2e`, 화면녹화 탭 사진 업로드 UI) 본편 착수는 이 세션에서 다루지 않음 --
   83차 기록대로 여전히 다음 우선순위 후보.

검증: py_compile 통과(리눅스 샌드박스), anchor 1회 매치 확인(Python 문자열 대조). 실차 검증:
미실시(스크립트 실행 대기 + 카메라/POI 근처 실주행 필요).

주의사항:
- 이번 발견은 핵심 발견 18/27/38(devnotes 기록과 실제 상태 불일치)과 유사하지만 다른 성격 --
  "코드가 반영됐는데 devnotes가 뒤처짐"이 아니라 "실차 검증을 했다고 기록했지만 실제로는 다른
  코드 경로(elif 분기)를 본 것"이었음. 앞으로 `if/elif`로 갈리는 UI 요소는 실차 검증 기록 시
  "어느 분기가 표시된 상태였는지"까지 구체적으로 남길 것.
- 이번 수정은 사용자 요청으로 sdi_descr 블록에만 국한됨 -- 제목/도로명은 같은 버그를 그대로
  갖고 있으므로, 나중에 그쪽에서도 비슷한 증상이 보고되면 이 4번 항목을 참고할 것.

다음 작업 후보:
1. 코드 반영 스크립트 실행/push 확인.
2. 실차에서 sdi_descr 배지 표시 확인.