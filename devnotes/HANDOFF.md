Worker: Claude (99차, Claude Sonnet 5)
Date: 2026-09-19
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `25f21d406d23bfb79ad45a67890cc39e3ad9e67b`, 반영 스크립트 실행/push 대기 -- 이번 세션 코드는 아직 GitHub에 없음)
Note Branch: carrot-ryu-note (base: `d5cc1df04546b7e9b6612c393337db2d9ebd6b00`, 이번 devnotes 반영도 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(변경 없음, 이번 세션 git ls-remote로 재확인) -- 93차와 동일.

작업:
98차에서 결정된 B안(G2T) 리드 감속 게이팅을 long_mpc.py에 반영하는 코드 설계/구현. 4절 0단계로 지침 문서(v2, `d5cc1df`)/HANDOFF.md/CURRENT_STATUS.md/WIP.md(98차) 확인 -> carrot-ryu의 long_mpc.py를 독립 clone으로 읽고 삽입 위치 확정 -> 3가지 결정사항(tFollow 절대값 처리/Params 노출 여부/로그 기록 여부)을 사용자에게 확인받음 -> 최소 변경안 4블록 설계 -> 반영 스크립트 작성/샌드박스 검증(9절 체크리스트 포함) -> devnotes 기록.

완료:
1. carrot-ryu `25f21d4`, carrot-ms `e324f67` 재확인(변경 없음).
2. long_mpc.py 코드 조사: 게이트 입력(dRel/vLead/vEgo)이 `process_lead()` 안에서 이미 접근 가능함을 확인, `update()` 시그니처 변경 없이 `process_lead(self, lead, lead_index)`로만 확장하면 되는 것을 확정. `process_lead()`가 파일 밖에서 호출되지 않음을 grep으로 확인(파급 범위 없음).
3. 사용자 결정 3건 확정(WIP.md 99차 참고): (a) tFollow 절대시간차 한계는 B안 그대로 반영 후 실차 로그로 관찰, (b) 임계값은 코드 상수로 고정(Params 미노출, params_keys.h 등록 불필요), (c) 게이트 값은 `cloudlog.debug`로 g<1일 때만 초당 1회 기록.
4. 최소 변경안 4블록(GATE_* 상수 / `_gate_raw()`+`process_lead()` 배선 / `reset()` 상태 초기화 / 호출부 2곳 `lead_index` 인자)을 확정, base `25f21d4` 위에 Python으로 시뮬레이션해 anchor 전부 1회 매치 + `py_compile` 통과 확인.
5. 반영 스크립트(`99cha_lead_gate_carrot_ryu.ps1`) 작성: Replace-Block 패턴(CRLF->LF 정규화 포함), `Get-PythonCmd`(py -3 -> python3 -> python, EOF 공급) + `py_compile` 검증, 전체쓰기 WriteAllText(UTF8 무BOM) + BOM 최종 확인, anchor 치환 결과 재확인, 임시폴더 자동 삭제. 스크립트 파일 자체는 한글 주석 포함이라 UTF-8 BOM으로 저장.
6. 9절 "전달 전 필수 자가검증 체크리스트" 1~7번을 명령 출력과 함께 수행: (1) `.ps1` 첫 3바이트 `EF BB BF` 확인, (2) `git clone`에 `core.autocrlf=false` 포함 확인, (3) `finally` 블록에 임시폴더 삭제 확인, (4) `Get-PythonCmd` 패턴 기본 적용 확인(샌드박스에 pwsh가 없어 이 함수 자체의 실행은 못 했고, 아래 미완료 참고), (5) 대상 파일 전체쓰기가 `WriteAllText(...,UTF8Encoding($false))`만 쓰는지 확인 + 결과 BOM 없음 확인, (6) 치환 결과 텍스트를 다시 읽어 확인하는 로직이 있는지 확인, (7) 전달할 `.ps1` 파일에서 실제 `$Old`/`$New` 4쌍을 정규식으로 추출해 SHA 고정 원본(`25f21d4`)에 재시뮬레이션 -> anchor 전부 1회 매치, `py_compile` 재통과, 사전 설계 시뮬레이션과 diff 없음(스펠링 차이 하나는 초안 쪽 오타였고 전달 파일이 맞는 표기임을 확인).

미완료(다음 세션 최우선):
1. 사용자가 `99cha_lead_gate_carrot_ryu.ps1` 실행 -> push. 다음 세션 시작 시 `git ls-remote`로 carrot-ryu HEAD가 바뀌었는지 먼저 확인(16절), 바뀌었으면 GitHub API/raw(SHA 고정)로 변경 파일이 long_mpc.py 1개, diff가 이 세션 설계와 일치하는지 재확인.
2. devnotes 반영 스크립트(`99cha_devnotes_carrot_ryu_note.ps1`, WIP.md 최상단 삽입 + HANDOFF.md 전체교체) 실행/push 확인.
3. 실차 배포 후 swaglog에서 `lead_gate` 태그로 게이트 동작 관찰: 평상시(특히 tFollow가 짧은 구간)에 g가 얼마나 자주/얼마나 낮게 내려가는지가 이번 세션 결정 (a)의 실증 근거가 됨. 문제가 확인되면 임계값을 tFollow 연동으로 재설계할지 다음 세션에서 판단.
4. 가능하면 97~98차에서 분석한 과민 반응 사례(#5/#8/#22류, 32/33·37/38·123/124 구간)가 실차에서도 완화되는지 확인.
5. carrot-ms 4건, 화면녹화 탭 사진 업로드 UI(22·23·26)/Drive 파이프라인(5~10·12·17·18·20·21)/녹화 버튼 깜빡임(28) 실차 검증 이월(97~98차와 동일, 이번 세션과 무관하게 계속 이월 중).

검증: 정적 분석/오프라인 시뮬레이션이며 실차 검증: 미실시. 코드 변경은 Python 시뮬레이션(anchor 매치, 치환 결과, py_compile)까지만 확인했고, PowerShell 구문 자체의 실행 검증은 샌드박스에 pwsh가 없어 못 했다(수동 육안 검토만 함, Windows PowerShell 5.1 실행 검증도 아님) -- 사용자 실행 시 예기치 못한 PowerShell 구문 오류가 있으면 안전장치(anchor 불일치/py_compile 실패 시 중단)가 작동해 반영 사고는 없을 것으로 예상하나, 오류 메시지를 그대로 전달해 달라고 안내할 것.

주의사항:
- carrot-ryu는 이번 세션에서 아직 전혀 반영되지 않았으며 `25f21d4` 그대로다.
- 게이트는 leadOne/leadTwo 양쪽에 독립 적용된다(`self._gate_g[0]`, `[1]`). 98차 분석은 leadOne(주 추종 리드) 기준이었으므로, leadTwo 쪽 동작은 별도로 확인된 적이 없다.
- MPC 솔버가 리셋되면(`self.reset()`) 게이트 상태도 중립(g=1)으로 초기화된다 -- 의도한 동작이나 명시적으로 확인한 적은 없다.
- `process_lead()`가 이 파일 안에서만 쓰이는 것은 grep으로 확인했지만, 이 grep은 `openpilot/selfdrive/controls`와 `openpilot/selfdrive/controls/lib/longitudinal_mpc_lib` 범위만 대상으로 했다(레포 전체 스캔은 아님) -- 다른 위치에서의 참조 가능성은 낮지만 완전히 배제되지는 않았다.
- 스크립트 전달 시 9절 체크리스트 1~7번을 명령 출력과 함께 응답에 포함했다. 앵커는 기억이 아니라 최신 SHA 원본에서 복사/재추출했다.
- 사용자가 "완료"만 보고하고 로그를 주지 않은 경우에도 완료로 가정하지 말고 GitHub에서 직접 재확인(16절).
- 반영 전에 세션이 끊기면 샌드박스의 미반영 산출물(스크립트 등)이 사라진다. 이번 스크립트 2개는 이미 사용자에게 전달됐으므로 이 문제는 해당 없음.

다음 작업 후보:
1. 세션 시작 시 carrot-ms에 `e324f67` 이후 신규 커밋이 있는지 확인(2절).
2. 99cha 스크립트 2개 실행 확인 -> push 재확인.
3. 실차 배포 후 lead_gate 로그 관찰, 필요시 임계값/tFollow 연동 재설계 논의.
4. carrot-ms 4건 + Drive/화면녹화 관련 이월 항목 실차 검증(위 미완료 5번).
