# HANDOFF

Worker: Claude (58차 -- carrot-ms fork 이후 신규 25건 오래된순 1차 분류, 코드 변경 없음)
Date: 2026-09-16
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `9ccf1206a034c5fb5e5f35201553f9fc4e5237e5`, 55cha flip fix. 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `b8d6c4afd59d0a29a2e031f9926df396a678bd18`, 57차 시점 devnotes. 이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): fork point(`02015190f5`) 이후 신규 25건, 57차와 동일(carrot-ms HEAD 변경 없음). 이번 세션에서 25건 전부 1차 분류 완료(WIP_SYNC.md 58차 체크포인트).

작업:
사용자 지시로 fork point 이후 carrot-ms 신규 25건을 오래된 시간순으로 순차 분석. 각 커밋의 diff를 carrot-ryu 현재 코드와 직접 대조해 (a) 콤마 C3 + 제네시스 DH 2015 관련성, (b) carrot-ryu 자체 커스텀 코드와의 충돌 가능성을 판정.

완료:
1. 25건 전체를 --filter=blob:none bare clone(happymaj11r/openpilot, ryujmin97/openpilot 각각)으로 로컬 조회, `git show --stat`/`git show <path>`로 개별 검토.
2. 오래된 순으로 8dcd32f7(sensord) -> 6f63ad35(외부내비 우선) -> 154f819e~904fd107 구간(gap/lead-response, Hyundai CAN, eGPU 등)까지 순차 대조.
3. 3건 제외 확정: 8dcd32f7(sensord -- tizi 전용 무관), 9d50f986(CI/문서 툴링 무관), ce8cbffe(C3XL 팬제어 -- C3X 전용 무관).
4. 1건 반영 후보 확정: 6f63ad35(외부내비 우선) -- 관련 함수(`_vehicle_speed_camera_enabled` 등 7개)를 carrot-ryu 현재 코드와 라인 단위 대조해 fork 시점과 동일함을 확인, 충돌 없음.
5. 나머지 21건을 3개 고위험 클러스터(종방향 gap/lead-response 10건, Hyundai CAN 2건, eGPU 3건) + 저위험 3건 + 빌드 인프라 2건으로 분류, 클러스터별 위험 근거(carrot-ryu의 병행 발전 커밋 목록)를 WIP_SYNC.md에 기록.

미완료 (다음 세션 최우선):
1. [최우선] 종방향 gap/lead-response 대개편 클러스터(154f819e, 48b57971, 6c1a4499, 1d956ec7, 0201cd19, 33427531, 3cff6956, 64921a81, 25af28f1, 904fd107 -- 10건) 정밀 diff 대조. carrot-ryu의 "longitudinal: move lead response into MPC costs" 등 자체 재설계와 실제 충돌 여부 확인. carrot-ms 쪽은 longitudinal_safe_follow.py 삭제 + driving_mode.py 신설로 로직을 재설계했음에 유의.
2. Hyundai CAN 상태 클러스터(0b0c282c, 66e75d87 -- 2건) 정밀 대조(opendbc hyundaicanfd.py/carstate.py).
3. Cinque v2 eGPU 클러스터(b483035d, df0027f7, 544dffe -- 3건) 정밀 대조, carrot-ryu 자체 eGPU 커밋(8341c01c "Download verified eGPU models...", 2c872877 "Deliver the big eGPU model outside Git LFS")과의 관계 확인.
4. 저위험 3건 개별 확인 후 반영 여부 결정: 685ec5ce(SpeedFromPCM 기본값 0->2), 59617d38(내비감속 기본값 200->120), 6b370dc7(Carrot Web 설정 검색 UI).
5. 빌드 인프라 2건(e9b3b89b acados 패키지화, c5f6e95b json11/Catch2 패키지화) -- 위 항목 정리 후 별도 판단, 빌드 환경 호환성 확인 필요.
6. 6f63ad35(외부내비 우선) 실제 반영은 사용자가 "외부내비 연결 시 순정 내비 완전 비활성화" 동작을 원하는지 확인 후 진행.
7. [이월] CURRENT_STATUS.md 항목 36을 "반영 완료(commit 9ccf1206)"로 정정.
8. [이월] 핵심 발견 31/37을 9절 정식 규칙으로 채택할지 확인(19절).
9. [이월, 37차] 락 수정 동시성 재현 검증.
10. [이월, 34차] 도로명-신호과속 같은 줄 배치 확인.
11. [이월] 28~30차 레이아웃 정밀 재검증.
12. [이월] "선택 다운로드" 버튼 실제 동작 미확인.
13. [이월] test_web_upload.py 데드코드 3개 삭제/갱신.
14. [이월] docs/carrot_web_upload.md 갱신.

검증: 이번 세션 코드 변경 전혀 없음, 실차 검증 대상 없음(12절). 판정은 `git show`/`git diff` 직접 대조로만 수행한 정적 분석.

주의사항:
- 종방향 gap/lead-response 영역은 carrot-ms와 carrot-ryu가 fork 이후 독립적으로 병행 재설계해 온 대표적 고위험 지점. 단순 문자열 블록 치환으로 접근하지 말고, 다음 세션에서 클러스터 전체를 한 번에 놓고 설계 의도부터 비교할 것.
- 25건 원본 목록은 WIP_SYNC.md 57차 체크포인트, 개별 판정 상세는 58차 체크포인트 참고.
- CURRENT_STATUS.md 항목 36 표기 오류는 여전히 미정정 상태(57차부터 이월).

다음 작업 후보:
1. 종방향 클러스터(A) 정밀 분석 착수(최우선, 위 미완료 1번)
2. Hyundai CAN 클러스터(B) 정밀 분석
3. eGPU 클러스터(C) 정밀 분석
4. 저위험 3건 확인 및 반영 스크립트 작성
5. CURRENT_STATUS.md 항목 36 표기 정정(이월)