# WIP

## 4차 (완료 — 종방향 PID 게인 고정 확인) — LongTuningKpV/KiV/Kf 무효화 발견

- 사용자 요청으로 "종방향 제어(가감속) 로직 분석" 착수
  (DisableDM=2 / LateralTorqueCustom 항목은 이번 세션에서 보류)
- longcontrol.py 분석 중, 커밋 a26b108d(2026-09-04)에서 현대·기아·제네시스 차량의
  종방향 PID 게인(Kp/Ki/Kf)이 코드에 고정(1.0/0.0/1.0)되어 있음을 확인
- 사용자가 보유한 LongTuningKpV=100/KiV=0/Kf=100 설정값은 제네시스 DH 2015에서
  실제로는 읽히지 않고 무시됨 (문서에도 명시된 의도된 동작, 버그 아님)
- 실제 적용되는 종방향 노브는 LongActuatorDelay / VEgoStopping / StoppingAccel 뿐임을 확인
- ACCEL_MIN/MAX(-4.0/2.5 m/s²)는 제네시스 전용 값 없이 Hyundai 계열 공통값임을 확인
- FINDINGS.md, PARAMS_REGISTRY.md, LAST_ANALYZED.md에 반영
- 코드 변경 없음 (분석/기록만), carrot-ryu는 carrot-wip과 여전히 동일
- 실차 검증: 미실시

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
