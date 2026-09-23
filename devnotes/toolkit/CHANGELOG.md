# Toolkit CHANGELOG

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
