# Toolkit CHANGELOG

## 2026-10-07 (256차)
- `jerk_sim/sim_jerk.py` 신규(사용자가 256cha에 올린 파일, 수정 없음)와 `jerk_sim/run_final.py` 신규(256cha 작성): 정차 앞차 접근 장면의 `JerkCostEgo` 5/8/12/20 폐루프 비교(README 256차 추가 참고). 670f72c 기록 실차 로그(route 00000492 세그먼트 4)로 실행해 12행 표를 만들었다(256cha 샌드박스). 다른 toolkit 파일은 변경 없음.

## 2026-10-06 (255차)
- `gap_replay/ext2.py` 신규(사용자가 255cha에 올린 파일, README 255차 추가 참고): `gap_replay.py extract`보다 필드가 많은 병합 추출(accelCmd, aEgo, 레이더 yRel/modelProb, 계획 소스 등). 670f72c 기록 실차 로그(route 0000048e 세그먼트 144~161)로 실행해 pkl을 만들었다(255cha 샌드박스). 다른 toolkit 파일은 변경 없음.

## 2026-10-06 (252차)
- `gap_replay/gap_replay.py` 신규(README 252차 추가 참고): `extract`(rlog.zst -> longitudinalPlan 20Hz 병합 pkl, initData 파라미터 포함)와 `replay`(`longitudinal_gap_recovery.py`의 `LeadGapState`를 로그 입력으로 재생해 로그 desiredDistance와 충실도·거리비별 마진 비교, 구/신 커밋 사본 비교 지원). 670f72c 기록 실차 로그(route 0000048e 세그먼트 144~161)로 실행해 재생 수치를 재현했다(252cha 샌드박스). 다른 toolkit 파일은 변경 없음.

## 2026-09-29 (216차)
- pytest_ci_setup.sh: 5c단계(`msgq.visionipc.visionipc_pyx` 컴파일, msgq_repo/SConscript 소스 목록 기준, 5b와 같은 setuptools 방식)와 끝 자가검증 `import msgq.visionipc.visionipc_pyx` 추가(+26/-1, README 216차 추가 참고). `test_raylib_ui.py`가 ui 프로세스 조기 종료로 실패하던 것을 빌드 후 통과로 확인했고, selfdrive/ui/tests는 1 failed / 174 passed에서 175 passed / 86 skipped / 0 failed로 바뀌었다(216cha 샌드박스). mici/tests/test_widget_leaks.py는 이 변경으로 해결되지 않는 업스트림 불일치(BigConfirmationDialogV2)라 기록만 했다. 다른 단계와 다른 toolkit 파일은 변경 없음.

## 2026-09-29 (215차)
- pytest_ci_setup.sh: 3/6 단계에 `comma-deps-raylib==6.0.0.1.post103` 별도 pip install 추가(+주석 4줄), 끝 자가검증에 `import pyray` 추가(README 215차 추가 참고). selfdrive/ui/tests의 HUD 테스트가 pyray 없이는 수집 단계에서 에러였던 것을, 세션마다 수동 설치하던 방식에서 스크립트에 포함시킨 것. 215cha 샌드박스에서 수정본 전체 실행 통과와 HUD 테스트 3개 파일 46 passed 확인. 다른 단계와 다른 toolkit 파일은 변경 없음.

## 2026-09-29 (207차)
- README.md: 207차 추가 절(pytest 밖에서 Plant를 돌릴 때 OpenpilotPrefix로 감쌀 것) 추가. 197cha 측정 스크립트는 저장소에 없는 스크래치라 toolkit에 등록하지 않기로 결정(사용자 승인, WIP.md 207cha). 스크립트 파일은 변경 없음.

## 2026-09-29 (206차 계속)
- pytest_ci_setup.sh: pip 목록에 pytest-mock 추가 + 주석 2줄(README 206차 계속 추가 참고). mocker 픽스처 테스트(test_plannerd_clock.py 등)가 pytest-mock 없이 54 errors였던 것을 설치 후 54 passed로 확인(206cha 샌드박스). 다른 단계와 다른 toolkit 파일은 변경 없음.

## 2026-09-24 (154차)
- route_decel/ 추가: replay_route_geom.py (153차 get_path_after_distance() 수정 rlog 재생 교차검증, README 154차 추가 참고). 실제 함수 원문(ast 추출)을 재구현 없이 exec하는 방식. 기존 스크립트는 변경 없음.

## 2026-09-24 (149차)
- lead_decel/ 추가: replay_gate147.py, extract_radar_flag.py (147차 감속 프리뷰 게이트 실로그 재생, README 149차 추가 참고). 실제 `_gate_raw`/`longitudinal_preview.py`를 원문 재사용하는 방식. 기존 스크립트는 변경 없음.

## 2026-09-23 (144차)
- replace_block_template.ps1에 `Invoke-Git` 헬퍼 신규 등록(핵심 발견 53+54+55가 모두 반영된 버전): stderr를 stdout과 병합하지 않음(2>&1 금지) + 이름 있는 파라미터 미선언(자동 변수 $args만 참조, `git add -A`의 `-A` 접두어 충돌 차단). 142차 FINDINGS.md 핵심 발견 54/55가 예고한 "toolkit 정식 등록"을 이번에 반영. README.md에 사용법 설명 추가. 기존 Invoke-ReplaceBlock/-CrlfNative는 변경 없음.

## 2026-09-20 (113차 계속)
- route_decel/ 추가: route_extract.py (route 감속 분석 -- extract/show/replay 3모드, README 참고). 기존 스크립트는 변경 없음.

## 2026-09-20 (109차)
- lead_decel/ 추가: closedloop_ncap.py (필요 감속 기반 명령 상한 what-if, README 참고). d_target=HFLOOR×vL 구조 폐기 결정. 기존 스크립트는 변경 없음.

## 2026-09-20 (108차 계속2)
- lead_decel/ 추가: closedloop_jlim.py (closedloop108.py + 출력단 저크 제한 J_MAX 환경변수, README 참고). 기존 스크립트는 변경 없음. 직전 채팅의 TF_FLOOR 변형 코드는 자료에 없어 등록하지 않음.

## 2026-09-20 (108차 계속)
- lead_decel/ 추가: ego_extract2.py, openloop108.py, closedloop108.py (복제본 보정·플래너 상태 재구성 검증, README 참고). 기존 스크립트는 변경 없음(mpc_replica.py 기본 a_min -3.5와 cb/sd는 낡은 값이며 새 도구가 인자로 덮어씀)

## 2026-09-20 (107차)
- lead_decel/ 추가: ego_extract.py, ego_episodes.py, replay_ext.py, real_vs_replay.py (실차 로그 대조, README 참고). 106차 추가분(gating_eval_105.py 신규, merge_lead_series.py CLI 인자)은 README에만 있고 CHANGELOG에 없어 여기에 함께 기록(2026-09-20, 106차)

## 2026-09-19 (98차)
- lead_decel/ 추가: events.py, needed_decel.py, gating_eval.py (리드 감속 게이팅 후보 평가, README 참고). gating_eval.py의 별칭 B(G2T)가 98차 채택안. 97차 스크립트 5개는 변경 없음

## 2026-09-19 (97차)
- lead_decel/ 추가: parse_lead_log.py, merge_lead_series.py, counterfactual.py, mpc_replica.py, closed_loop.py (선행차 감속 과민 반응 분석용, README 참고)
