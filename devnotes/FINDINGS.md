# FINDINGS

## [2026-09-12] minSteerSpeed 60km/h 제한 — SMDPS 장착 차량용 해제 토글 확인

### 배경
- CAR.HYUNDAI_GENESIS (제네시스 DH 2015-16 / G80 2017) 플랫폼 설정에
  minSteerSpeed=60km/h가 하드코딩되어 있음.
  (opendbc_repo/opendbc/car/hyundai/values.py, HYUNDAI_GENESIS 블록)
- 사용자 차량은 SMDPS(조향모터) 개조로 저속 조향 개입이 물리적으로 가능한 상태.

### 확인된 사실
- opendbc_repo/opendbc/car/interfaces.py (get_params 함수)에 다음 로직 존재:
  ```
  if Params().get_bool("DisableMinSteerSpeed"):
      ret.minSteerSpeed = 0.
  ```
- 이 Params 키는 carrot-wip 자체에 이미 구현된 기능이며, 콤마 디바이스 설정 UI에도
  노출되어 있음 (openpilot/selfdrive/carrot_settings.json, 1877번째 줄 부근):
  - name: DisableMinSteerSpeed
  - title(한글): "저속조향제한해제"
  - descr: "저속조향이 안되는 차량 제한해제(SMDPS장착차량): 1"
  - 값 범위: 0(기본, 끔) ~ 1(켬)
- params_keys.h에도 PERSISTENT INT 파라미터로 등록되어 있어 재부팅 후에도 유지됨.

### 결론
- 코드 수정 불필요. 콤마 디바이스 설정에서
  "시작(START)" 그룹 → "저속조향제한해제"를 1로 설정하면
  minSteerSpeed가 런타임에 0으로 강제되어 저속 조향 제한이 해제됨.
- carrot-ryu는 carrot-wip과 동일한 상태이므로 이 기능을 그대로 사용 가능.

### 실차 검증
- 미실시. 콤마 디바이스 설정 변경 후 실제 저속 구간(60km/h 이하)에서
  조향 개입 여부와 안정성을 직접 확인 필요.

### 분석 근거 커밋
- carrot-wip HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (2026-09-12)
