# PARAMS REGISTRY

## DisableMinSteerSpeed
- 위치: Params (PERSISTENT, INT), params_keys.h / carrot_settings.json
- 기본값: 0
- 설정값(내 차량): 1 (SMDPS 장착으로 저속 조향 가능)
- 효과: opendbc/car/interfaces.py get_params()에서
  minSteerSpeed를 0으로 강제 (원래 HYUNDAI_GENESIS 플랫폼 기준 60km/h)
- 코드 변경 여부: 없음 (기존 carrot-wip 기능을 설정으로만 활성화)
- 실차 검증: 미실시
- 기록일: 2026-09-12
