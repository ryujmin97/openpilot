# WIP

## 3차 (완료 — 파라미터 베이스라인 기록) — 현재 적용 설정값 스냅샷

- 사용자가 콤마 디바이스에서 export한 params_backup-4.json 수령
- CarSelected3="Hyundai Genesis 2015-16"로 차량 매칭 확인
- DisableMinSteerSpeed=1이 실제로 적용되어 있음을 확인 (2차 FINDINGS와 일치)
- 원본 파일을 devnotes/params_snapshots/2026-09-12_params_backup-4.json으로 보관
- PARAMS_REGISTRY.md에 주요 커스텀 값(조향 토크, 종방향 튜닝, 크루즈 프로파일 등) 요약 기록
- DisableDM=2, LateralTorqueCustom=0 등 의미 미확인 항목을 다음 분석 후보로 등록
- 실차 검증: 해당 없음 (기록 작업)

## 2차 (완료 — 저속조향 제한 분석) — minSteerSpeed / SMDPS

- CAR.HYUNDAI_GENESIS minSteerSpeed=60km/h 하드코딩 확인
- DisableMinSteerSpeed Params 토글이 carrot-wip에 이미 구현되어 있음을 확인
  (interfaces.py + carrot_settings.json UI 노출)
- 코드 수정 없이 설정값 변경만으로 해결 가능 판단
- 실차 검증: 미실시

## 1차 (완료 — 브랜치 세팅) — 프로젝트 구조 초기화

- carrot-wip: 원본 참고 브랜치 확인
- carrot-ryu: carrot-wip에서 분기하여 생성
- carrot-ryu-note: orphan 브랜치로 생성, devnotes 폴더 구조 세팅
- 실차 검증: 미실시
