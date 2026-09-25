# FINDINGS

## 핵심 발견 61 (162차) -- 경로 소진(핵심 발견 59)을 candidate3(슬루 필터)와 분리해 정보량(len(path)) 기준으로 직접 차단: freeze-or-fallback 설계

**배경**: 핵심 발견 59가 발견한 "원본 폴리라인 점이 2~3개뿐이면 곡률이 사실상 0이 되어 route 후보가 300(무제한)으로 튀는 현상"은 161차에서 candidate3(사이클간 ±1.0km/h 슬루)의 게이트(최대 곡률<0.003)에 걸리긴 하지만, 161차 자체가 "슬루는 이 현상의 근본 원인(정보 부족)을 고치지 못한다"고 명시적으로 이월했다. 162차에서 이 수정안을 설계/구현했다.

**핵심 발견 59의 candidate3만으는 부족한 이유(수치)**: candidate3의 ±1.0km/h/cycle 제한은 20Hz 기준 ±20km/h/초다. 핵심 발견 59가 관측한 최장 지속시간(seg17, 약 30초) 동안 슬루만 작동한다면 이론상 300 근처까지 충분히 도달할 수 있어(예: 60km/h에서 240km/h 차이를 따라잡는 데 12초), "차단"이 아니라 "지연"에 불과하다.

**설계**: `get_path_after_distance()`가 반환하는 `path`(원본 폴리라인 점, resample 이전)의 길이를 정보량 신호로 직접 사용한다. `len(path) < ROUTE_PATH_MIN_POINTS(=4)`면 그 사이클에서 계산된 곡률/out_speed를 신뢰하지 않고, 직전에 정보가 충분했던 값(`self.navi_route_speed_filt`)을 그대로 유지(freeze)하거나(값이 없으면 도로제한속도 `nRoadLimitSpeed`로 폴백)한다. 두 경우 모두 `navi_route_speed_filt`는 그 사이클에 갱신하지 않아, "정보가 충분했던 마지막 값"이 오염되지 않는다. candidate3의 슬루 로직은 `route_info_sufficient`가 참인 사이클에서만 그대로 동작하도록 분기해, 두 로직이 서로 다른 상황(정보 부족 vs. 곡률 잡음)을 각각 담당하게 했다.

**부수 효과**: `path`가 완전히 빈 기존 else 분기(내비게이션 비활성/도착 등, out_speed가 초기값 300 그대로 남는 경로)도 `len([]) < 4`로 자동으로 이 보호 아래 들어와 함께 안전해졌다(수정 전에는 candidate3의 슬루만 걸렸는데, 위와 동일한 이유로 근본 차단이 아니었음).

**검증**: `carrot_navi_route()`의 꼬리 로직(경로 소진 판정 -> freeze/폴백 -> candidate3 슬루)만 분리한 합성 테스트(`test_exhaustion_logic.py`) 5개 케이스로 확인 -- (1) 소진+이전값 존재 시 300이 아니라 이전값을 그대로 유지, (2) 소진+이전값 없음 시 도로제한속도로 폴백, (3) 소진이 600사이클(20Hz 기준 30초) 연속돼도 값이 이전값에서 전혀 드리프트하지 않음(300 방향으로 조금도 새지 않음 -- candidate3 단독 대비 실질적 개선점), (4)/(5) 정보가 충분한 사이클에서는 candidate3의 기존 슬루/무슬루 동작이 그대로 유지됨(회귀 없음). `py_compile` 통과. 로컬 bare 저장소(실제 carrot-ryu HEAD `f4a62db9` 트리를 그대로 미러링)를 대상으로 clone->patch(base64 전체교체)->commit->push 전 과정을 두 모드(정상 LF 체크아웃 / `core.eol=crlf`로 Windows CRLF 체크아웃 시뮬레이션)에서 실행 -- 두 모드 모두 동일한 diff(1 file changed, 27 insertions(+), 9 deletions(-))와 동일한 post-image blob hash(`2868c646`)를 만들었다. 전체교체(base64 payload를 그대로 덮어쓰는 방식) 자체가 원본 파일의 CRLF/LF 체크아웃 여부와 무관하게 동일한 결과를 낸다는 것도 이번에 확인됐다 -- Replace-Block(문자열 블록 치환) 계열이 반복적으로 겪은 CRLF 앵커 매칭 실패(핵심 발견 44/46/48/50/60)가 이 방식에서는 구조적으로 발생하지 않는다.

**해석/한계**: `ROUTE_PATH_MIN_POINTS=4`는 161차가 관측한 "2~3점" 사례를 근거로 정한 값이며, 이번 세션에서 실제 로그(seg11/17/23)로 재검증하지 않았다. 이 값이 너무 높게 잡히면 "실제로 곧은 도로인데 원본 웨이포인트가 원래 널찍한 경우"까지 과도하게 걸러 route 속도를 불필요하게 낮게 유지할 위험이 있으나, 이 방향의 오차는 과속이 아니라 과소평가라 안전한 방향이다(11절: 실제 로그 재검증은 다음 세션 이월).

**수정 여부**: 있음(코드 변경, `carrot_man.py`). 반영 스크립트(`162cha_code_carrot_ryu.ps1`) 실행/push 대기.

**실차 검증**: 미실시(합성 로직 테스트 + 로컬 git dry-run 전용).

## 핵심 발견 60 (161차 계속) -- 161차 v1 코드 반영 스크립트가 CRLF->LF 정규화 없이 전달되어 실제 실행에서 앵커 0건 매칭(핵심 발견 44/46/48/50과 동일 원인 재재발)

**배경**: 161차 devnotes 반영(v1)은 정상 push됨(`021d1b8..033c0b4`)으나, 같은 세션의 코드 반영(carrot_man.py, candidate3) v1 스크립트를 사용자가 실행하자 클론까지는 성공했지만 첫 Replace-Block 앵커가 `found 0 matches`로 즉시 중단(9절 "1회가 아니면 중단" 규칙대로 안전 중단, 파일 미변경).

**확인된 원인**: v1 스크립트를 직접 읽어보니, 대상 파일(`carrot_man.py`)을 원문 그대로(바이트 단위) 읽어 앵커 텍스트와 `.Replace()`하는 구조로, CRLF->LF 정규화 로직이 없었다. 이 저장소의 `.gitattributes`(`* text=auto`)는 checkout 시 OS 설정에 따라 텍스트 파일을 CRLF로 변환할 수 있고(`core.autocrlf=false`는 이 변환을 막지 못하는 별개 스위치), 사용자의 Windows 환경에서 실제로 CRLF로 체크아웃되어 LF 기준으로 작성된 앵커가 전혀 매치되지 않았다. 핵심 발견 44(85차)/46(117차)/48(121차)/50(133차)와 정확히 동일한 메커니즘의 재재발.

**메타 원인**: 전달 전 자가검증 체크리스트(9절) 2번·9번이 요구하는 "CRLF 재현 검증"을 v1 전달 시점에 실제로 수행하지 않고 전달했다(서술만으로 충분하다고 오판). 세션이 무료 사용량 한도로 중단되며 사용자가 v1을 그대로 실행하게 됨.

**수정**: 패치 스크립트를 CRLF-무관 방식으로 재작성 -- 대상 파일을 바이너리로 읽어 원본이 CRLF를 포함하는지(`had_crlf`) 먼저 판별하고, 매칭은 항상 LF로 정규화한 사본에서 수행하며, 저장 시 원본이 쓰던 개행 방식(CRLF 또는 LF)을 그대로 복원해 diff가 불필요하게 커지지 않도록 했다(v2).

**검증**: 이번 세션에서 실제로 로컬 bare 저장소(실제 carrot-ryu HEAD `619998bb` 트리를 그대로 미러링) 대상 clone→patch→commit→push 전 과정을 두 모드(정상 LF 체크아웃 / `GIT_CONFIG_KEY_0=core.eol=crlf`로 Windows CRLF 체크아웃 시뮬레이션) 모두에서 수행 -- 두 모드 모두 10개 Replace-Block이 정확히 1회씩 매치되고, `git show --numstat`으로 동일하게 "1 file changed, 19 insertions(+)"를 확인했으며 diff 내용도 동일했다(BOM 없음, py_compile 통과, pwsh 7 파서 구문 오류 0건). GitHub 실제 저장소 push는 사용자가 v2 스크립트를 실행해야 확인된다(아직 미실행).

**일반화**: v1이 전달되기 전 9절 체크리스트를 "지켰다"는 서술이 아니라 실제 실행 결과(출력)로 증빙해야 한다는 원칙(핵심 발견 42/45)이 이번에도 유효했다 -- 이번 세션은 v1 전달 시점에 그 증빙이 빠졌던 것이 재발의 직접 원인이다.

**실차 검증**: 미실시(로그 재생/정적 검증 전용).

## 핵심 발견 59 (161차) -- 경로 폴리라인이 300m 룩어헤드 안에서 2~3점으로 줄어들면 두 점을 잇는 직선의 곡률이 사실상 0이 되어 route 후보 속도가 무제한(300×배율)으로 튄다; 이번 로그에서는 route가 desiredSpeed의 binding 소스가 된 적이 없어 실차 영향 없음(des_jumps_route=0)

**배경**: candidate3(route 후보 근접-직선 슬루 필터) 파라미터 검증 중 seg11/17/23의 특정 구간에서 route 후보 속도가 300(×1.2=360)으로 튀는 걸 발견, 처음엔 `out_speed_of()`가 `speeds` 리스트가 비었을 때 반환하는 기본값(300)으로 오인했다.

**실제 메커니즘**: `run_one()`/`carrot_navi_route()`가 `get_path_after_distance()`로 얻는 잔여 경로점(`npath_o`)이 2~3개뿐이어도, `resample()`(10m 간격 재보간)은 두 점 사이 직선을 따라 여전히 9개 이상의 점을 만들어내므로 곡률 계산 자체는 실행된다. 다만 원본 점이 2~3개뿐이라 재보간된 선이 완전한 직선이 되어 곡률이 사실상 0(관측값 ~1e-19)이 되고, `V_CURVE_LOOKUP_BP/VALS`에서 곡률 0의 속도가 `V_CRUVE_LOOKUP_VALS[0]=300`(무제한)이라 out_speed=300이 나온다. 즉 "계산 실패로 인한 기본값"이 아니라 "정보 부족으로 직선이라고 잘못 가정한 정상 계산 결과"다. seg17에서는 이 상태가 최장 약 30초 지속됐다(t≈27.5~58s 구간 대부분).

**실차 영향 확인**: `toolkit/replay_route_geom.py report`의 `des_jumps_route`(desiredSpeed가 src='route'인 상태에서 20km/h 넘게 변한 사이클)를 seg1/8/11/15/17/23/31 7개 세그먼트에서 확인. seg11/17/23은 `route_src_cycles=0`(이 구간에서 route가 `min(speed_n_sources)`의 binding 후보가 된 적이 없음) -> `des_jumps_route=0`으로, 이번 로그에서는 실제 desiredSpeed에 영향이 없었다. 반면 seg8/15/31(160차 C-군집)은 `route_src_cycles=180/150/300`, `des_jumps_route=5/5/3`으로 route가 실제로 binding 소스였고 진짜 desiredSpeed 급변으로 이어졌다.

**해석**: 이 현상 자체(경로 소진 시 route 후보가 무제한으로 뜨는 것)는 구조적으로 재현 가능한 정상 계산 결과이지만, 다른 소스(도로제한속도 등)가 대개 더 낮은 값으로 binding되어 실질적 위험으로 이어지지 않는 것으로 보인다. 다만 이번 7개 세그먼트만의 관측이라 일반화하기엔 이르고, route가 유일하게 낮은 후보가 되는 상황(예: 도로제한속도가 매우 높거나 다른 소스가 비활성인 경우)에서는 다를 수 있다.

**수정 여부**: 없음(코드 미변경). candidate3(161차)의 적용 범위 밖으로 명시적으로 제외 -- candidate3의 게이트(최대 곡률<0.003)는 이 현상의 구간에도 걸리지만(곡률이 진짜 0에 가까우므로), candidate3는 "이전 값 근처로만" 제한하는 슬루 필터라 이 현상의 근본 원인(정보 부족)은 고치지 못한다.

**실차 검증**: 미실시(로그 재생, open-loop).

## 핵심 발견 58 (159차) -- 핵심 발견 57(곡률 잡음이 V_CURVE_LOOKUP_BP 급경사 구간에서 증폭)은 메커니즘은 맞지만 영향 범위가 좁았고, 158차 후보 수정안 2번은 코드상 효과가 없다

**배경**: 158차가 "잔여 비트리거 route 급변 223건"의 근본 원인을 곡률 재계산 잡음 + lookup 테이블 급경사로 확정하고 후보 수정안 4가지(2번 추천)를 냈다. 159차에서 사용자가 1번(테이블 첫 구간 완화)이 더 근본적이지 않느냐고 물어 같은 rlog(38세그먼트, `f23d05f`)로 재점검했다.

**확인한 것**: (1) `carrot_serv.py`의 최종 목표속도는 `min(speed_n_sources)`라 route 후보가 다른 소스보다 높으면 영향이 없다. 급변 223건의 낮은 쪽 route 후보는 중앙값 약 168km/h이고, 자차속도+20km/h 이하(임시 기준)인 건 13건뿐이다(210건 94%는 영향 없는 영역). (2) route가 source인 2,432사이클 중 desiredSpeed가 20km/h 넘게 튄 건 19건(0.8%)이며 트리거 관련은 0건, 18건은 안내 지점 접근 구간(xTurnInfo 1/3/4). (3) 158차가 든 사례 곡률(0.0015~0.0023)은 첫 구간이 아니라 테이블 2~4번째 구간(기울기 20~34)이고, 가장 가파른 곳은 κ<0.0015(기울기 ~120). (4) 후보 2번(`abs(curvature)<0.02` 상향)은 lookup 뒤 road_limit 바닥 조건이라 잡음 곡률(≤0.003)에는 이미 적용 범위 안이어서 상향해도 효과가 없다. 효과를 내려면 κ<0.003 같은 새 하한이 필요한데 그러면 반경 ~330m 이상 커브를 무시한다.

**해석**: 메커니즘(테이블 기울기 + 매 사이클 곡률 재계산 잡음)은 유효하나 "잔여 급변 = 감속 문제"로 읽으면 과장이다. 실제 영향 가능성은 안내 지점 부근 desiredSpeed 급변 19건이며, 이것이 곡률 잡음인지 안내 지점 근처 경로 기하 자체의 급변인지는 미분리(159차 이월). 1번안은 잡음을 5km/h 이하로 누르려면 80~130km/h 대역을 평탄화해야 해서 실제 커브 반응을 왜곡하므로 입력(곡률) 쪽 필터가 더 맞다는 판단(정적 계산 기반).

**수정 여부**: 없음(코드 미변경). 158차 후보 수정안 중 2번 추천은 철회, 나머지는 미채택. 세부는 WIP.md 159차 참고.

**실차 검증**: 미실시(로그 재생과 정적 계산, open-loop).
## 핵심 발견 57 (158차) -- V_CURVE_LOOKUP_BP 첫 구간(곡률 0→1/800, 속도 300→150km/h)이 테이블에서 가장 가파르고, 직선에 가까운 도로에서도 매 사이클 곡률 재계산 잡음(0.0005~0.001 단위)이 이 구간을 통과하며 20~80km/h대 route 속도 급변으로 증폭된다(154차가 발견한 "잔여 비트리거 route 급변"의 근본 원인)

**배경**: 154차가 153차 `get_path_after_distance()` 수정과 무관하게 세그먼트당 10~25건 남아있던 route 값 급변("잔여 비트리거 급변")을 발견했으나 원인 미확정으로 이월. 157차도 재확인만 하고 조사하지 않음.

**원인**: `carrot_man.py`의 `curv_speeds()`는 매 20Hz 사이클마다 차량 현재 위치에서 새로 300m 앞 경로를 `get_path_after_distance()`로 잘라 `resample()`(10m 간격)한 뒤, 그 점들에서 `calculate_curvature()`(3점, 표본 간격 `sample=4`≈40m)로 곡률을 구해 `np.interp(abs(curvature), V_CURVE_LOOKUP_BP, V_CRUVE_LOOKUP_VALS)`로 속도를 찾는다. `V_CURVE_LOOKUP_BP=[0, 1/800, 1/670, ...]`/`V_CRUVE_LOOKUP_VALS=[300, 150, 120, ...]`의 첫 구간(곡률 0~0.00125)은 테이블 전체에서 가장 가파른 기울기(0.00125당 150km/h)다. 차량이 몇 m 전진할 때마다 재보간되는 곡률 표본 3점의 위치가 미세하게 흔들리고, 이 흔들림이 만드는 곡률 변화(실측 0.0004~0.0025 범위, 실제 급커브 아님)가 하필 이 급경사 구간에 자주 걸려 20~80km/h대 속도 스윙을 만든다. `abs(curvature)<0.02`일 때 `max(speed, road_limit)`로 바닥은 보장되지만 위쪽 제한이 없고, `out_speed_of()`의 후진 감속-제한 루프도 관찰된 사례 전부에서 `vmin==out`으로 그대로 통과시켜(현재 속도/거리 조건상 제약이 안 걸림) 이 잡음을 걸러주지 못한다.

**근거**: route `00000449--b34152b780`(38세그먼트, 기록 커밋 `f23d05f`) 중 navRoute 있는 32개 세그먼트를 `route_decel/replay_route_geom.py`로 재생(old=new=`f23d05f` 동일 커밋), 38,401사이클 중 route 급변 223건, 그중 트리거(첫 폴리라인≥300m) 사이클과 겹치는 건 1건(0.4%)뿐 -- 99.6%가 153차 수정과 무관한 영역. seg3/seg8/seg22/seg32에서 급변 직전/직후 곡률 배열 최댓값을 직접 대조해 동일 패턴(미세 곡률 변화 → V_CURVE_LOOKUP_BP 첫 구간 → 급변) 재현 확인.

**영향 범위**: `curv_speeds()`/`V_CURVE_LOOKUP_BP`를 쓰는 모든 route 기반 목표속도 계산(직선~완만한 도로 구간 전반), TBT(xTurn 3/4/6) 여부와 무관.

**수정 여부**: 158차에서 후보 4가지 제시(WIP.md 158차 참고), 미채택/미반영. 사용자 승인 후 별도 세션에서 진행.

**실차 검증**: 미실시(로그 재생, open-loop).
## 핵심 발견 56 (155차) -- 업로드용 zip을 `tempfile` 기본 경로에 만들면 콤마 기기에서는 `/tmp`(tmpfs 150M)라, 선택 세그먼트 합계가 150M를 넘는 순간 `[Errno 28] No space left on device`로 실패한다

**배경**: 로그탭 대시캠 세그먼트 전체선택(38개) → "선택 전송"이 `로그 전송 오류: [Errno 28] No space left on device`로 실패했다. `/data`는 71G가 남아 있었다(사용자 `df -h` 보고, 이전 세션 인용).

**확인된 원인**: `upload_jobs.py`의 `build_zip()`이 zip 스테이징 디렉터리를 `tempfile.mkdtemp(prefix="carrot_dashcam_")`(dir 인자 없음)로 만들어 Python 기본 임시 경로를 썼고, 콤마 기기에서 이는 `/tmp`(tmpfs, RAM 기반, 150M)이다. `ZIP_STORED`(무압축)라 zip 크기 = 원본 합계이며 해당 route(38세그먼트)의 qcamera.ts+rlog* 합계가 약 460M라 150M 초과 시점에 `zf.write()`가 `OSError(ENOSPC)`로 실패했다. 디스크 여유(`/data`)와 임시 경로의 여유는 서로 다른 파일시스템이라는 점이 원인 파악의 핵심이었다.

**수정안**: zip 스테이징 경로를 `DASHCAM_UPLOAD_TMP_DIR`(`CARROT_DATA_DIR/tmp/dashcam_upload` = `/data/carrot/tmp/dashcam_upload`)로 옮기고 `mkdtemp(..., dir=...)`로 지정한다(155차, `config.py` +5/`upload_jobs.py` +7/-1). 정리는 기존 `finally: shutil.rmtree`가 그대로 담당한다.

**검증**: 정적 분석 + 로컬 bare 저장소 시뮬레이션(두 체크아웃 모드)뿐이다. 실기기에서 38세그먼트 전송 재현은 미실시.

**일반화**: (1) 용량이 입력에 비례하는 임시 파일(zip/변환 결과 등)은 `tempfile` 기본 경로에 두지 말고 용량이 큰 파티션(`/data` 하위)을 `dir=`로 명시한다 -- 콤마 기기의 `/tmp`는 RAM 기반 150M다. (2) 대신 `/data`에 만든 임시 파일은 재부팅으로 지워지지 않으므로, 강제 종료 시 잔존물을 정리할 방법(시작 시 청소 등)을 함께 고려해야 한다(155차 시점에는 미구현, 이월). (3) "여유 공간 부족" 오류는 어느 마운트가 부족한지 먼저 특정한다(`df -h <경로>`로 그 경로의 파일시스템을 확인).

## 핵심 발견 54 (142차) -- `Invoke-Git` 헬퍼가 파라미터명을 `Args`로 선언해 `git add -A`의 `-A`를 `-Args`로 오인, 즉시 실패

**배경**: 140차에서 핵심 발견 53 수정으로 도입된 `Invoke-Git`(`param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args) { ... }`) 헬퍼가 140~141차 devnotes 반영 스크립트에서는 문제없이 쓰였다. 142차 devnotes 반영 스크립트가 처음으로 `Invoke-Git -C $Tmp add -A`를 호출했는데, 로컬 bare 저장소 dry-run(9절 체크리스트 9번) 도중 `Missing an argument for parameter 'Args'` 오류로 즉시 실패했다.

**확인된 원인**: PowerShell은 명명 파라미터를 호출 시 축약(접두어) 매칭한다. `Invoke-Git`이 `$Args`라는 이름으로 파라미터를 선언해 두면, 뒤이어 넘어오는 토큰이 정확히 `-A`일 때 이를 `-Args`의 유일한 접두어 후보로 해석해 값 하나를 소비하려 하고, `-A` 다음에 값이 없으면(`git add -A`에서 `-A`가 마지막 옵션인 경우) `Missing an argument` 오류로 즉시 죽는다. `git add -A` 조합을 이 헬퍼로 호출한 것은 142차가 처음이라 140/141차에서는 드러나지 않았다.

**수정안**: `Invoke-Git`에서 `param()` 선언 자체를 없애고 함수 본문에서 PowerShell 자동 변수 `$args`(전달된 인자 배열)만 참조하도록 변경했다. 이름을 선언하지 않으면 애초에 접두어 매칭이 일어나지 않아 `-A`뿐 아니라 향후 등장할 수 있는 다른 단일 옵션(`-a`, `-al` 등)과도 충돌하지 않는다.

**검증**: 로컬 bare 저장소(일반 체크아웃 + Windows CRLF 재현 두 모드)에서 `Invoke-Git -C $Tmp add -A`를 포함한 전체 시나리오를 재실행해 두 모드 모두 정상 완료, commit diff가 예상과 byte 단위로 일치함을 확인했다(142차, 리눅스 pwsh 재현 -- Windows PowerShell 5.1 실제 실행은 아님).

**일반화**: 이름 있는 파라미터로 나머지 인자를 받는 wrapper 함수(`ValueFromRemainingArguments`)를 만들 때는, 그 파라미터 이름이 감싸는 대상 명령(`git` 등)이 받을 수 있는 임의의 단일 옵션 이름과 접두어로 겹치지 않는지 확인하거나, 아예 파라미터를 선언하지 않고 자동 변수 `$args`만 쓴다. `Invoke-Git` 계열 헬퍼는 앞으로 항상 `param()` 미선언 + `$args` 참조 형태를 기본값으로 채택한다.

## 핵심 발견 55 (142차) -- 핵심 발견 54를 고치는 과정에서 `2>&1`을 실수로 재도입, 핵심 발견 53(139차)이 그대로 재발

**배경**: 위 핵심 발견 54의 `-A` 충돌을 고치는 v1 수정에서, `Invoke-Git`의 구현을 `$out = & git @args 2>&1`로 다시 작성했다. 이 v1이 사용자에게 전달돼 실제 Windows PowerShell 5.1에서 실행됐다.

**확인된 원인**: `2>&1`로 stderr를 stdout에 병합하는 것은 139/140차 핵심 발견 53이 이미 정확히 지목하고 제거했던 바로 그 패턴이다. `-A` 충돌 수정에만 집중하느라 `Invoke-Git`을 재작성하면서 이미 해결돼 있던 별개의 문제(스트림 비병합)를 함께 건드린다는 것을 인지하지 못했다. 사용자 실행 로그에서 `git clone`의 정상 진행 메시지("Cloning into ...")만으로 `NativeCommandError`가 발생, `$ErrorActionPreference="Stop"`으로 즉시 중단됨을 확인했다. 리눅스 컨테이너(pwsh)의 로컬 bare 저장소 dry-run 두 모드는 이 회귀를 잡아내지 못했는데, 이는 핵심 발견 53 자체가 이미 명시한 한계(컨테이너와 Windows PowerShell 5.1 사이의 native stderr 처리 차이는 컨테이너 dry-run만으로 재현 불가)와 정확히 같은 이유다.

**수정안**: `Invoke-Git`을 `2>&1` 없이 `& git @args`(스트림 비병합, 콘솔에 그대로 출력)로 되돌리고 `$LASTEXITCODE`만으로 성공/실패를 판단하도록 v2로 수정했다. `-A` 충돌 수정(핵심 발견 54, `param()` 미선언)은 그대로 유지했다.

**검증**: v2를 로컬 bare 저장소(일반/Windows CRLF 재현 두 모드) dry-run으로 재검증(정상 완료, diff/blob hash 일치) 후, 사용자가 실제 Windows PowerShell 5.1에서 v2를 실행해 carrot-ryu-note가 `9b1877f`에서 `0fd412f`로 push됨을 확인했고, GitHub compare API(`9b1877f...0fd412f`, ahead_by 1, 파일별 diffstat이 로컬 dry-run 예측치와 일치)로 직접 재확인했다(16절).

**일반화**: 핵심 발견 53(개별 문제 하나)이 한 번 고쳐졌다고 해서 그 수정이 이후 세션에서도 안전하게 유지된다고 가정하지 않는다. `Invoke-Git` 같은 공통 헬퍼를 다른 버그(핵심 발견 54 등) 때문에 다시 손댈 때는, 그 수정이 이미 확정된 다른 핵심 발견의 조건(여기서는 "stderr를 `2>&1`로 병합하지 않기")을 깨뜨리지 않는지 재작성한 코드를 줄 단위로 직접 대조해 재확인한다(핵심 발견 44의 "체크리스트 서술만 대조하지 말고 코드 자체를 읽어 확인하라"는 원칙과 동일 계열). `devnotes/toolkit/replace_block_template.ps1`에 `Invoke-Git`을 정식 등록할 때는 핵심 발견 54+55가 모두 반영된 버전(파라미터 미선언 + stderr 비병합)을 그대로 채택한다.

## 핵심 발견 53 (139차) -- Windows PowerShell 5.1에서 `git <cmd> 2>&1 | Write-Host` 패턴이 git의 정상 진행 메시지(stderr)를 오류로 오인해, 성공한 명령인데도 `$ErrorActionPreference="Stop"`으로 즉시 중단됨

**배경**: 139차 코드 반영 스크립트(`139cha_unused_imports_code_carrot_ryu.ps1`)와 devnotes 반영 스크립트(`139cha_devnotes_carrot_ryu_note.ps1`)를 사용자가 실제 Windows PowerShell(5.1, `powershell -ExecutionPolicy Bypass -File`)에서 처음 실행했을 때, 두 스크립트 모두 `git clone` 단계에서 `git : Cloning into '...'...`가 `NativeCommandError`로 출력되며 즉시 `finally`(임시 폴더 정리)로 넘어가 아무 것도 반영되지 않은 채 종료됐다. 두 스크립트는 리눅스 컨테이너에서 pwsh 7.4.6으로 로컬 bare 저장소 일반/Windows CRLF 재현 두 모드 dry-run까지 통과한 뒤 전달된 것이었는데도 실제 Windows PowerShell 5.1 환경에서 재현됐다.

**확인된 원인**: `git clone`은 진행 상황("Cloning into '...'...", "done." 등)을 정상적으로 stderr에 출력한다(exit code 0, 실패 아님). 그런데 스크립트가 `git clone ... 2>&1 | Write-Host` 형태로 stderr를 stdout에 합쳐 파이프로 넘겼고, Windows PowerShell은 native 명령의 stderr 라인이 이렇게 합쳐질 때 이를 `ErrorRecord`(NativeCommandError)로 감싸 오류 스트림에 실어보낸다. 스크립트 최상단에 `$ErrorActionPreference = "Stop"`이 설정돼 있었기 때문에, 이 `ErrorRecord`가 파이프라인에 나타나는 순간 (명령 자체는 성공했음에도) 터미네이팅 예외로 전환돼 `try` 블록이 그 자리에서 중단됐다. `git -C $Tmp commit`/`git -C $Tmp push`도 동일한 `2>&1 | Write-Host` 패턴을 썼으나 clone 단계에서 이미 죽었으므로 도달하지 못했다. 컨테이너 검증에서 재현되지 않았던 이유는, 그 환경이 pwsh 7.4.6(리눅스)이었고 이번 실패는 Windows PowerShell 5.1(`powershell.exe`)에서만 확인됐기 때문으로 추정된다 -- 두 런타임 사이에 native 명령 stderr 병합을 오류 스트림으로 승격하는 조건에 실질적인 차이가 있는 것으로 보이나, 정확한 버전별 분기 조건까지는 이번 조사에서 확정하지 못했다.

**수정안**: 두 스크립트 모두 `Invoke-Git` 헬퍼 함수를 추가해 `git clone`/`git add`/`git commit`/`git push` 4곳의 호출 방식을 `git ... 2>&1 | Write-Host`에서 `& git @GitArgs`(스트림 병합 없이 콘솔에 그대로 출력) + 직후 `$LASTEXITCODE` 명시적 확인(`0`이 아니면 그 자리에서 throw)으로 교체했다. 수정본을 리눅스 컨테이너에서 로컬 bare 저장소로 재검증(clone → pre/post-image guard → anchor 치환 → py_compile → commit/push)한 결과, git의 정상 진행 메시지가 여전히 stderr로 출력됨(도구 출력의 stderr 필드에 표시)에도 스크립트가 중단되지 않고 끝까지 정상 실행됨을 확인했다. 이후 사용자가 실제 Windows PowerShell 5.1에서 수정본을 실행해, carrot-ryu의 4개 파일 import 삭제와 carrot-ryu-note의 WIP.md/HANDOFF.md 139차 기록이 모두 반영된 것을 GitHub raw 조회로 직접 재확인했다(16절).

**검증**: 리눅스 컨테이너(pwsh 7.4.6, 로컬 bare 저장소) 재검증 + 사용자의 실제 Windows PowerShell 5.1 실행 결과를 raw.githubusercontent.com 직접 재조회로 확인(16절/20절 원칙). Windows PowerShell 5.1과 pwsh 7.4.6 사이의 정확한 동작 차이 자체를 통제된 비교 실험으로 재현하지는 못했다 -- 이번 조사는 실전 실패 로그와 수정 후 실전 성공(raw 재조회) 확인에 근거한다.

**일반화**: 9절의 반영 스크립트가 `git` 등 외부 명령을 호출할 때는 `2>&1`로 stderr를 병합해 `Write-Host`로 넘기는 패턴을 쓰지 않는다. 대신 (1) 네이티브 명령은 스트림을 병합하지 않고 그대로 콘솔에 출력되게 두고, (2) 직후 `$LASTEXITCODE`를 명시적으로 확인해 0이 아니면 그 자리에서 throw하는 방식(`Invoke-Git` 패턴)을 기본으로 쓴다. 리눅스 컨테이너(pwsh 7.4.6)에서의 dry-run 통과만으로 "Windows PowerShell 5.1에서도 동일하게 동작한다"고 단정하지 않는다 -- 두 런타임 간 native 명령 stderr 처리 방식에 차이가 있을 수 있으므로, 가능하면 `devnotes/toolkit/replace_block_template.ps1`류의 재사용 헬퍼에도 이 `Invoke-Git` 패턴을 반영해 다음 회차부터 기본으로 재사용한다.

## 핵심 발견 52 (136차 계속) -- 136차 v1 코드 반영 스크립트의 py_compile 검증 단계가 `Push-Location $Tmp` 이전에 상대경로로 중복 호출되어, 실행 위치가 clone 폴더 밖일 때 예외로 조용히 죽고 로그 순서만 보면 "정리 완료 후 에러"로 오인됨

**배경**: `136cha_mojibake_fix_code_carrot_ryu.ps1`(v1) 실행 로그 끝에 있어야 할 "완료: carrot-ryu에 136cha 커밋이 push되었습니다" 메시지가 없고, 대신 `py.exe : [Errno 2] No such file or directory: 'openpilot/selfdrive/controls/lib/desire_lib/maneuver_classifier.py'`가 출력됐다. GitHub 재조회로 carrot-ryu 대상 파일의 blob hash가 여전히 pre-image(`0021af97d7`, 수정 전)임을 확인해 push가 실제로 일어나지 않았음을 확정했다(16절, "완료" 메시지 없는 로그를 성공으로 단정하지 않음).

**확인된 원인**: 스크립트 7단계(py_compile 검증)에 `$RelPath`(상대경로)로 py_compile을 한 번 더 호출하는 중복 코드가 `Push-Location $Tmp` **이전**에 있었다. 이 호출 시점의 실제 작업 디렉터리는 clone 임시 폴더가 아니라 사용자가 PowerShell을 실행한 `C:\WINDOWS\system32`였기 때문에 상대경로를 찾지 못해 `FileNotFoundError`가 발생했고, `$ErrorActionPreference="Stop"`에 의해 예외로 전환됐다. 이 예외로 스크립트가 죽으면서 `finally` 블록(임시 폴더 삭제)이 먼저 실행된 뒤 콘솔에 에러 메시지가 출력돼, 로그만 보면 "정리 완료 다음에 에러가 난 것"처럼 순서가 뒤바뀌어 보였다. 이 시점은 8단계(commit/push) 이전이라 git 명령은 한 번도 실행되지 않았다 -- 15절/18절의 강제진행 금지 안전장치가 작동한 것이 아니라 단순히 그 지점에서 예외로 스크립트가 죽은 것이며, 저장소 손상 위험은 없었다.

**수정안**: 중복 호출 제거, 절대경로(`$FilePath`) 사용, `Push-Location`/`Pop-Location` 자체를 제거(작업 디렉터리를 옮기지 않고 항상 절대경로만 사용하는 패턴, 9절 10번 `-C` 원칙과 동일한 취지)한 v2(`136cha_mojibake_fix_code_carrot_ryu_v2.ps1`)를 작성/전달했다. v2 실행으로 commit `41e4c056d8db2ceb38fe93c114ca5a3be3d8de8f` push 완료를 GitHub에서 직접 재확인: `.patch` 조회로 변경 파일 1개(+2/-2), 결과 blob hash가 사전에 계산한 post-image(`b552e1655d`)와 byte-exact 일치, 첫 3바이트 BOM 아님, `py_compile` 통과.

**검증**: v2의 push 결과는 GitHub API/raw 조회로 재확인했다(위 수정안 문단). v1의 정확한 예외 발생 지점(상대경로 py_compile 호출)은 사용자가 전달한 로그와 스크립트 원문 대조로 확인한 것이며, 샌드박스에서 Windows PowerShell 5.1 환경을 직접 재현해 실측하지는 않았다.

**일반화**: 외부 프로세스(py_compile 등)를 호출하는 모든 지점은 상대경로가 아니라 절대경로만 써야 한다는 점이 이번 사고로 재확인됐다. `Push-Location`으로 작업 디렉터리를 바꾸는 방식은 이후 코드에서 상대경로 호출이 섞여 들어갈 여지를 남기므로, 애초에 `Push-Location`/`Set-Location`을 쓰지 않고 모든 파일 접근을 절대경로(`Join-Path $Tmp ...`)로 고정하는 편이 더 안전하다(9절 PowerShell 필수 규칙과 동일 원칙).

## 핵심 발견 51 (133차) -- `git hash-object <절대경로>`를 `-C` 없이 호출하면 프로세스 CWD 기준으로 리포지토리를 찾아 로컬 core.autocrlf override를 무시하고 전역 설정을 적용, 내용이 같아도 "base drifted"로 오탐

**배경**: 133cha_devnotes_toolkit_instructions.ps1 최초 실행에서 FINDINGS.md pre-image guard가 실제 내용은 GitHub 최신과 동일한데도 "changed since this script was authored"로 안전 중단됐다(사용자 로그, commit/push 없음, 9절/15절/18절 정상 동작).

**확인된 원인**: 스크립트의 pre-image guard와 최종 해시 출력 두 곳이 `$actual = (git hash-object $p).Trim()` 형태로, `-C` 없이 절대경로만 넘겨 git을 호출하고 있었다. Git은 대상 리포지토리를 인자 경로가 아니라 **명령을 실행하는 프로세스의 현재 작업 디렉터리**에서 위로 탐색해 찾는다. 사용자 PowerShell의 시작 위치가 `C:\WINDOWS\system32`(clone 폴더 밖)였으므로, git은 clone 시 지정한 로컬 override(`core.autocrlf=false`, `$Tmp/.git/config`)를 전혀 적용받지 못하고 사용자 PC의 전역/시스템 git 설정(Windows Git 기본값인 `core.autocrlf=true`로 추정)을 그대로 사용해, FINDINGS.md(원본 CRLF)를 LF로 변환한 가상 blob의 해시를 계산했다. 같은 파일에 대해 바로 옆에서 `git -C $DevPath hash-object FINDINGS.md`(상대경로+`-C`)를 호출하면 정확한 해시가 나옴을 직접 대조해 확정했다(샌드박스에서 global core.autocrlf=true로 설정하고 PowerShell 프로세스 CWD를 clone 폴더 밖에 둔 채 재현).

`Repair-FromBlob`(9절 9번 재현 검증 과정에서 이번 세션에 추가한, git object store에서 원본 바이트를 직접 복원하는 방어 코드)로 작업 트리 파일 자체는 이미 정확히 복원돼 있었음에도 이 문제가 발생했다 -- 원인이 파일 내용이 아니라 "해시를 계산하는 그 명령 자체"의 리포지토리 탐색 방식에 있었기 때문이다. 즉 132차(핵심 발견 50, `.gitattributes`의 `* text=auto`로 인한 checkout 시 CRLF 변환)와는 완전히 다른, 별개의 메커니즘이다.

**재현/수정**: 샌드박스에서 동일 커밋(`48f2ff17`) 기준 로컬 bare 저장소를 만들고, 전역 `core.autocrlf=true` + PowerShell 프로세스 CWD를 clone 폴더 밖(리포지토리 밖의 임의 디렉터리)에 둔 상태로 원본 스크립트를 실행해 동일하게 재현했다. `git hash-object $p` 두 곳을 모두 `git -C $Tmp hash-object $p`로 수정한 뒤, 동일 조건(global autocrlf=true/false 양쪽, CWD를 clone 폴더 밖에 둔 상태)으로 각각 끝까지 재실행해 pre-image guard 6개 전부 통과·anchor 1회 매치·최종 blob hash 7개 파일 전부 byte-exact 일치함을 확인했다. 사용자가 이 수정본(v2)을 실제로 실행해 carrot-ryu-note `49146b3`으로 성공 push했음을 GitHub 직접 재조회로 최종 확인했다.

**재발방지(19절 절차로 반영)**: PROJECT_INSTRUCTIONS_carrot-ryu.md 9절 체크리스트에 신규 항목(10번) 추가 -- 스크립트 안에서 저장소 상태를 읽는 모든 git 명령(`git hash-object`/`git status`/`git diff` 등)은 절대경로만 넘기지 말고 항상 `-C <clone 경로>`를 명시할 것.

**검증**: 로컬 bare 저장소 기준 global autocrlf=true/false 두 모드 + PowerShell 프로세스 CWD를 clone 폴더 밖에 둔 상태로 각각 끝까지 실행(blob hash byte-exact 일치), 사용자 실제 실행 로그 및 carrot-ryu-note `49146b3` GitHub 직접 재조회(API rate limit로 REST API는 실패, clone 프로토콜로 대체)로 실제 push 성공 확인. 실차 검증: 해당 없음(devnotes 반영 스크립트 자체의 버그, 12절 무관).

## 핵심 발견 50 (133차) -- 132차 v1 anchor 0회 실패는 핵심 발견 44/46/48과 동일 원인이 재발한 것이며, 121차가 이미 반증된 "core.autocrlf=false로 구조적 차단" 결론을 재확인 없이 재채택한 것이 근본 원인

**배경**: 132차 코드 반영 스크립트(`132cha_unused_imports.ps1`, v1)를 사용자가 실행하자 `carrot_serv.py anchor match count: 0`으로 안전 중단됐다(commit/push 없음, 15절/18절 안전장치 정상 동작). "이전에도 같은 에러가 있지 않았냐"는 질문을 계기로 조사했다.

**확인된 원인**: (1) GitHub SHA 고정 원본(`3759a300`)과 앵커 텍스트를 바이트 단위로 대조 -- 3개 파일 전부 1회 정확히 매치(앵커 텍스트 오류 아님, GitHub blob은 LF·CR 0개). (2) v1 스크립트 코드를 직접 읽어보니 CRLF->LF 정규화 로직이 아예 없이 `$Content.Replace()`를 바로 수행하는 구조였음 -- 63차/85차(핵심 발견 44)/117차(핵심 발견 46)/120차/121차(핵심 발견 48)에서 이미 정립된 방어 패턴이 이번 스크립트에는 반영되지 않았던 것. 원인 자체는 새 메커니즘이 아니라 정확히 44/46/48과 같은 `.gitattributes`의 `* text=auto`다(`core.autocrlf=false`는 checkout 시 이 변환을 막지 못하는 별개 스위치).

**메타 원인(재발 자체의 원인)**: 121차 v1의 HANDOFF.md는 "CRLF 재현(9절 9번 b)이 셸 호출 경계 문제로 완전한 재현엔 이르지 못했으나, 실제 스크립트의 `--config core.autocrlf=false`가 구조적 방어선"이라고 자체 결론 내렸다. 그러나 이 "`core.autocrlf=false`만으로 구조적으로 차단된다"는 결론은 핵심 발견 46(117차)에서 이미 명시적으로 반증된 내용이며, 121차 v1의 실제 실패(같은 문서 항목) 자체가 그 반증의 재현이었다. 즉 재현 실패/생략을 안전 근거로 재확인 없이 재채택하는 패턴이, 9절/18절에 명문 규칙 없이 서술로만 남아있었기 때문에 132차에서 다시 반복됐다.

**재현/수정**: 실제 carrot-ryu(`3759a300`)를 clone해 로컬 bare 저장소를 만들고, pwsh 7.4.6(GitHub 릴리스 tarball, Linux)을 설치해 v1 로직을 일반/CRLF(`GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.eol GIT_CONFIG_VALUE_0=crlf`) 두 모드로 실행 -- CRLF 모드에서 사용자 로그와 동일하게 앵커 0회로 재현됨. CRLF->LF 정규화 + 치환 결과 재확인(핵심 발견 42 패턴)을 추가한 `132cha_unused_imports_v2.ps1`을 작성해 같은 두 모드로 재실행, 앵커 3개 모두 1회 매치·`py_compile` 통과·두 모드 결과 blob hash가 3개 파일 전부 byte-exact 일치함을 확인(9절 체크리스트 9번). 사용자가 v2를 실행해 carrot-ryu commit `15f9831e`로 성공 push했음을 이번(133차) 세션에서 GitHub 직접 재조회로 최종 확인했다.

**재발방지(19절 절차로 반영)**: 9절 체크리스트 2번/9번(b), 18절에 각각 "`core.autocrlf=false`만으로는 CRLF 체크아웃이 차단되지 않는다"와 "재현 실패/생략을 안전 근거로 재채택하지 않는다"를 명문화하고, 문자열 블록 치환 공통 헬퍼(`devnotes/toolkit/replace_block_template.ps1`, `Invoke-ReplaceBlock`/`Invoke-ReplaceBlock-CrlfNative`)를 신설해 새 스크립트가 매번 이 정규화 로직을 새로 작성하지 않고 재사용하도록 했다.

**검증**: 로컬 bare 저장소 일반/CRLF 두 모드 실행(blob hash byte-exact 일치), carrot-ryu `15f9831e` GitHub 직접 재조회로 v2 성공 push 확인, `replace_block_template.ps1` 기능 테스트(CRLF 작업 트리 사본에 대해 anchor 1회 매치 + 정규화 정상 동작). 실차 검증: 해당 없음(devnotes/스크립트 진단, 12절 무관).

## 핵심 발견 49 (126차) -- test_latcontrol.py 3-인자 생성자 호출 불일치는 carrot-ryu 회귀가 아니라 carrot-wip/carrot-ms 원본부터 존재하는 문제

**배경**: 125차에서 발견한 `test_latcontrol.py::test_saturation`의 `TypeError`(WIP.md 125차 기록, HANDOFF 125차 미완료 3번)의 원인/도입 시점을 조사했다.

**조사 방법**: (1) carrot-ryu(`a0f4c5a5f`)를 blobless partial clone해 대상 5개 파일(`controls/tests/test_latcontrol.py`, `controls/lib/latcontrol.py`/`latcontrol_pid.py`/`latcontrol_torque.py`/`latcontrol_angle.py`, `controls/lib/tests/test_latcontrol.py`)의 `git log --oneline`을 확인 -- 전부 61차 리셋의 단일 스쿼시 커밋(`Squash carrot-wip lebowski updates`) 하나만 나오고, 그 이후 carrot-ryu 자체 커밋에서 수정된 적이 없다. (2) happymaj11r/openpilot(carrot-ms, `3756e6d5702ff6ebd2c54d12f2e25e587dca4d99`)와 ajouatom/openpilot(carrot-wip, `3d93b7eed6caf284a70a853b14c4ed9f9a4c49b2`)에서 동일 5개 파일을 직접 raw 조회해 carrot-ryu와 대조.

**확인**: 5개 파일 전부 carrot-ryu/carrot-ms/carrot-wip 사이에 byte 단위로 동일했다. `controls/tests/test_latcontrol.py::test_saturation`은 `controller(CP.as_reader(), CI, DT_CTRL)`로 3-인자 호출하지만, `LatControl`(base)/`LatControlPID`/`LatControlTorque`/`LatControlAngle` 4개 클래스 생성자는 원본부터 전부 `__init__(self, CP, CI)` 2-인자만 받는다. 즉 **이 불일치는 carrot-ryu의 61차 베이스 리셋이나 그 이후 개별 커밋 반영에서 생긴 회귀가 아니라, carrot-wip 원본 자체에 이미 존재하던 깨진 테스트가 carrot-ms를 거쳐 변경 없이 상속된 것**이다.

**추가 발견(부수적)**: `controls/lib/tests/test_latcontrol.py`라는 별도의 중복 테스트 파일이 존재한다. 이 파일은 생성자 호출은 2-인자로 맞지만, `interfaces[car_name]`을 `(CarInterface, CarController, CarState, RadarInterface)` 4-튜플로 언패킹하는 옛날 opendbc 인터페이스 API를 사용해 현재 opendbc 버전과는 그 나름대로 어긋나 있다(이것도 carrot-ms/carrot-wip에 동일하게 존재, carrot-ryu에서 만든 게 아님).

**처리 방향**: 18절상 carrot-ms/carrot-wip 원본은 수정 대상이 아니다. carrot-ryu 로컬에서만 테스트 파일을 고치는 방안은 이번 세션에서는 보류(원인 확정까지만 수행, 실차 로직과 무관한 낮은 우선순위 항목).

**검증**: carrot-ryu/carrot-ms/carrot-wip 3개 저장소 직접 raw 조회 + 5개 파일 전체 대조(11절 원칙, 추측 없이 원본 확인). 실차 검증: 해당 없음.

## 핵심 발견 48 (121차) -- B그룹 v1 스크립트에서 핵심 발견 46/44(Windows CRLF checkout)가 재발: pre-blob 해시 가드는 EOL 불일치를 잡지 못하고, `core.eol=crlf` 재현 테스트가 없으면 Linux 검증만으로는 놓친다

**배경**: 120차 A그룹 스크립트는 CRLF 정규화와 `core.eol=crlf` 재현 양성 테스트를 갖췄지만, 121차 B그룹 v1(`121cha_deadcode_batchB_code_carrot_ryu-v1.ps1`)은 LF 앵커만 매칭했고 채팅 사본에는 `core.eol=crlf` 테스트 기록이 없다. 사용자 PC(Windows PowerShell 5.1)에서 v1은 사전 blob 가드 5개를 통과한 뒤 3단계에서 `max_abs anchor matched 0 times (expected 1)`로 안전 중단됐다(commit/push 없음). 원인은 핵심 발견 46과 같은 `.gitattributes`의 `* text=auto`다(carrot-ryu `b98620e8` GitHub blob은 CR 0개, Windows 작업 트리는 CRLF).

**재현(121차, 샌드박스)**: 실제 carrot-ryu `b98620e8`을 clone해 로컬 bare 저장소를 만들고, `GIT_CONFIG_GLOBAL`에 `core.eol=crlf`를 둔 pwsh 7.4.6(Linux)에서 v1을 실행했다. 사용자 로그와 같은 지점(104행)에서 같은 메시지로 중단됐다. 같은 조건에서 v2는 4개 파일 모두 `working-tree EOL: CRLF`로 감지하고 끝까지 통과했다.

**왜 사전 blob 가드가 통과했나**: 가드는 `git hash-object <경로>`를 쓰는데, 경로를 주면 커밋 시점과 같은 EOL 정규화(clean 변환)를 거쳐 LF 기준 blob 해시를 계산한다. 그래서 "파일 내용이 기대한 blob과 같다"는 보증은 되지만, 작업 트리 바이트가 LF라는 보증은 아니다. 앵커 매칭은 작업 트리 바이트를 그대로 읽기 때문에 따로 정규화가 필요하다.

**수정안(121차 v2에 적용)**: 읽을 때 CRLF를 LF로 정규화해 앵커를 매칭하고, 편집 후 원래 EOL로 되돌려 쓴다(`Read-TextLf`/`Write-TextLike`). git이 add 시점에 LF로 정규화하므로 사후 blob은 LF 기준 기대값과 byte-exact로 일치한다. 대안으로 핵심 발견 46처럼 clone에 `--config core.eol=lf`를 주는 방법도 있다. 어느 쪽이든 Windows 체크아웃을 재현한 양성 테스트로 확인해야 한다.

**제안(19절 승인 필요, 아직 지침에 반영하지 않음)**: 9절 자가검증 체크리스트에 "코드 저장소를 대상으로 하는 스크립트는 샌드박스에서 `core.eol=crlf`를 준 환경으로 양성 실행한 출력을 전달 시 포함한다"를 추가하는 안. 현재 체크리스트 7번(앵커 시뮬레이션)은 EOL 조건을 명시하지 않아 이번 재발을 막지 못했다.

**검증**: 샌드박스 재현(v1 실패/v2 통과), 사용자 PC 실행 로그(v2 성공), GitHub 직접 재조회로 커밋 `2efdd2e2`의 blob 4개가 기대값과 일치함을 확인. 실차 검증 대상 아님(devnotes/체크아웃 설정 문제, 12절 무관).

## 핵심 발견 46 (117차) -- `.gitattributes`의 `* text=auto`로 인한 Windows CRLF checkout이 다시 재현됨, 원인 제거로 대응(85차 핵심 발견 44는 대증 처방이었음)

**배경**: 핵심 발견 44(85차)는 `Invoke-ReplaceBlock` 함수 자체의 CRLF 정규화 누락을 고쳐 증상을 막았을 뿐, 원인인 `.gitattributes`의 `* text=auto`는 그대로 두었다. 117차에서 같은 원인이 다른 경로(치환 전 "CR 포함" 안전검사)로 다시 걸렸다.

**재현(119차, Linux)**: carrot-ryu `df7da7d5` tarball에 `.gitattributes`가 `* text=auto`만 있음을 확인. 별도의 작은 저장소로 `core.autocrlf=false`만 준 clone과 `--config core.eol=crlf`/`--config core.eol=lf`를 각각 준 clone을 비교한 결과, `core.eol=crlf`는 working tree에 CR이 들어가고(`* text=auto`가 checkout 시 LF blob을 CRLF로 변환), `core.eol=lf`는 CR이 0이었다. GitHub에 저장된 blob 자체는 CR 0(LF)임도 확인했다 -- 저장소 쪽 문제가 아니라 checkout 옵션 문제다.

**117차 "CR 0개" 확인이 무효였던 이유**: 샌드박스 `/bin/sh`(dash)에서 `grep -c $'\r'`은 CR 2개가 있는 테스트 파일에도 0을 반환했다(같은 파일에 `bash`/`python3`은 정확히 2를 반환). 117차 원인 자체는 이미 core.eol 문제로 확정돼 있었고, 119차는 그 근거를 Linux에서 독립 재현하고 "CR 0개" 검사의 신뢰도 문제를 추가로 확인한 것이다.

**수정안(117차에서 이미 적용, 119차는 검증만)**: clone에 `--config core.eol=lf`를 추가해 원인 자체를 제거. 셸 내장 문자열 매칭(`grep -c $'\r'` 등)에 의존한 CR 검사는 쓰지 않고, python 등으로 바이트 단위 확인한다(9절에 이미 반영됨).

**검증**: Linux 샌드박스 재현(core.eol 비교), GitHub blob CR 0 확인, dash/bash/python의 `grep -c $'\r'` 동작 차이 실측. 실차 검증 대상 아님(devnotes/체크아웃 설정 문제, 12절 무관).

## 핵심 발견 47 (118차) -- CRLF `.ps1` + 큰따옴표 문자열 안 백틱 이스케이프로 앵커/커밋 내용이 조용히 손상될 수 있음

**배경**: 118차 노트 스크립트 v1이 WIP.md 앵커 확인에서 안전 중단됐다(commit/push 없음). 원인 둘은 118차 HANDOFF/WIP에 이미 기록했으나 FINDINGS.md에는 미기록 상태였다.

**재현(119차, pwsh 7.4.6을 GitHub Releases에서 받아 샌드박스에 설치해 실측)**:
- CRLF로 만든 `.ps1`의 `@'...'@`(작은따옴표 here-string)에는 CR이 그대로 섞여 들어간다(CRLF 원본은 CR=1, 같은 내용을 LF로 바꾼 원본은 CR=0). LF 기준인 GitHub 원본(CR 0)과 바이트 단위로 어긋나 `Anchor match count != 1: got 0`이 된다.
- 큰따옴표 문자열 안의 백틱은 이스케이프 문자다. 백틱 다음 문자에 따라 결과가 다르다: `22b101f6` `df7da7d5`처럼 뒤가 일반 문자면 백틱만 사라지고(마크다운 코드 표기 소실), `0e1bef52`처럼 뒤가 `0`이면 NUL(0x00), 뒤가 `a`이면 BEL(0x07), `b`이면 BS(0x08), `f`이면 FF(0x0C) 등 **제어문자로 치환**되는 경우가 있음을 실측했다. 118차 기록은 "백틱이 사라진다"로만 적었으나, 해시가 0/a/b/f 등으로 시작하면 눈에 안 보이는 제어문자가 대신 남는 더 나쁜 경우가 있다.

**수정안(118차에서 이미 적용)**: 여러 줄 앵커/본문은 작은따옴표 here-string(`@'...'@`)만 쓰고, 스크립트 자체는 LF로 생성하며, 스크립트 안에서 읽어들인 내용의 CRLF는 매칭 전 정규화한다. 백틱으로 감싸는 마크다운 코드 표기가 필요한 문자열은 애초에 큰따옴표 문자열에 직접 넣지 않는다.

**검증**: pwsh 7.4.6 실측(작은따옴표 here-string CRLF 잔존 확인, 큰따옴표 문자열 안 백틱 뒤 문자별 제어문자 치환 결과 확인). Windows PowerShell 5.1에서 직접 재현한 것은 아니며, 118차 사고의 원인 설명이 실측과 일치함을 확인한 것이다. 샌드박스에 pwsh를 설치할 수 있음을 이번에 처음 확인했다(95차 FINDINGS에는 "샌드박스에 PowerShell이 없다"고 적혀 있었음) -- 앞으로는 `.ps1`을 서술이 아니라 실제 pwsh 실행으로 시뮬레이션할 수 있다.

## 2026-09-20 (113차 계속) -- 46~50초 급제동의 원인은 운전자 브레이크(pedalPressed)로 확정: 113차 항목의 "원인 소스 미규명" 정정, 새 배율을 같은 로그에 산술 재계산

**정정 대상**: 바로 아래 113차 항목의 "46~50s 제동 원인 소스는 미규명"과 "desiredSpeed가 vEgo보다 높은데도 감속이 시작됐다" 부분. 18절에 따라 113차 항목은 수정하지 않고 이 항목을 위에 추가한다.

**근거(같은 세그먼트 155 rlog를 재업로드받아 이 세션에서 직접 파싱, toolkit `route_decel/route_extract.py`)**:
- 46.00s에 selfdriveState가 enabled -> disabled(alertType `pedalPressed/userDisable`)로 바뀌고 onroadEvents에 pedalPressed가 50.0s까지 이어진다. carState.brakePressed=True는 46.02~50.6s, 이 구간 carControl.longActive=False, accel 명령 0.00(46.02~50.8s). vEgo 108.3 -> 78km/h, aEgo 약 -1.2~-2.4 m/s^2는 **운전자가 브레이크를 밟아 생긴 감속**이지 시스템 출력이 아니다.
- 이 구간에서 longitudinalPlan.aTarget이 aEgo를 그대로 따라간 것은, selfdriveState가 enabled가 아닐 때 longitudinal_planner.py의 reset_state가 a_desired를 aEgo로 초기화하기 때문이다(carrot-ryu `a430d114` 소스 143~167행 확인). 이 구간의 desiredSpeed/route 값은 제어에 쓰이지 않았다.
- 브레이크 직전의 시스템 자체 감속: 44.8s부터 accel 명령 -0.09 -> -0.79(45.8s), aEgo -0.76(46.0s). 출처는 vturn(97~111). 이때 steerOverride 이벤트(44.75s, 44.95~45.56s, 운전자 조향)도 있었다. 운전자가 46.00s에 브레이크를 밟은 이유는 로그로 알 수 없다.
- 45.4s에 nRoadLimitSpeed 100 -> 40, xTurnInfo 4 -> 6(톨게이트), xDistToTurn 약 564m로 갱신. 50.84s부터 vCruise 120 -> 87(disabled 상태에서 바뀜, 원인은 조사하지 않음).
- 따라서 "급감속"이 이 46~50s 구간을 가리킨다면 route/vturn 목표속도 문제가 아니라 운전자 제동이다. 사용자가 체감한 구간이 어느 쪽인지는 확인하지 않았다.

**새 배율(113차 반영, carrot-ryu `c7b5a010`)을 같은 로그에 산술 재계산**(`route_extract.py replay ... 1.35`; route=값/1.35로 원시값을 되돌린 뒤 map_turn_speed_factor와 같은 공식 적용, 플래너/차량 시뮬레이션이 아님):
- (20Hz 전체 행 기준) 새 목표는 안내 지점 205m 이전에는 대체로 vEgo보다 높고, 205m(38.1s)에 처음 vEgo 아래로 내려갔다가 원시값 요동으로 149m(40.06s)까지 다시 위로 올라가는 순간이 있으며, 그 뒤로는 계속 아래에 머문다(차이 -0.6 이하로 시작해 41.2~44.0s(113~28m)에는 -4.3~-8.1km/h, 목표 약 101.1 vs vEgo 106.6~109.2). 기존 130 대비, 계속 아래에 머무는 시점 기준으로 vturn 인수(44.2s)보다 약 4.1초, 처음 내려간 시점 기준으로 약 6.1초 먼저다. 새 목표 101.1은 vturn 최저값 97과 4km/h 차이라 인수 시 낙차도 작아진다.
- 한계: 설계에 쓴 같은 로그로 확인한 것(표본 밖 검증 없음), 플래너가 이 목표에 어떤 감속 크기로 반응할지는 모름, 실차 검증 미실시. guide 배율을 1.0으로 낮추면 같은 구간 목표는 약 96.3(-10~-13km/h).

## 2026-09-20 (113차) -- 112차 원인 진단 정정: route 정체는 "v_ego 미반영"이 아니라 MapTurnSpeedFactor 배율(x1.35) 때문이고, 130->97 급락은 route가 아니라 vturn(비전)

**정정 대상**: 아래 112차 항목의 "route 목표속도가 v_ego를 반영하지 않는 구조적 원인"과 "v_ego 100/120/145km/h 어느 값이어도 출력 동일" 서술. 18절에 따라 112차 항목은 수정하지 않고 이 항목을 위에 추가한다.

**근거 1 -- 코드(이 세션에서 carrot-ryu `a430d114` 소스로 재확인)**: carrot_man.py carrot_navi_route()는 v_ego를 이미 쓴다(`v_ego_kph = self.sm['carState'].vEgo * 3.6`, 역산 루프의 `time_delay = (v_ego_kph - target_speed) / accel_limit_kmh`). 112차 시뮬레이션 스크립트가 남아 있지 않아 v_ego 무관 결과가 왜 나왔는지는 재현하지 못했다. route 원시값에는 carrot_serv.py update_navi()에서 역산 적분이 끝난 뒤 `route_speed = max(route_speed * self.mapTurnSpeedFactor, AutoCurveSpeedLowerLimit)`로 배율이 곱해진다.

**근거 2 -- 로그(직전 대화에서 재업로드된 rlog, 세그먼트 155; 이 세션에는 로그 파일이 없어 재확인하지 못함, 직전 분석 결과를 옮겨 적음)**:
- 기기 MapTurnSpeedFactor=135(저장소 기본 90). 130.0km/h = route 원시값 96.3 x 1.35. 정체 구간(41.2~44.0s, 57샘플)에서 route/1.35 = 96.30~97.41로 거의 고정.
- 배율 적용 후 목표(130)가 vEgo(107~109)보다 높아 route는 감속 지령을 내지 못했고 차는 오히려 가속. 배율이 없었다면 원시값은 36초대부터 vEgo보다 낮았다.
- 44.2s의 130->97 급락은 route가 아니라 vturn(비전)이 커브 22m 전에 처음 커브를 보고 낮은 값을 내놓은 것(desiredSpeed=min). route는 44.2s 이후에도 132~136.
- 그 급락 구간의 실제 감속은 약했다(aEgo 최저 -0.22 m/s^2).
- 실제로 세게 감속한 구간은 46~50s(aEgo -1.4~-2.2, 브레이크, 109->78km/h). 이때 desiredSpeed는 102~118로 vEgo보다 높은데도 감속이 시작됐다 -> 이 제동의 원인 소스는 **미규명**. 45.4s에 nRoadLimitSpeed 100->40, route 원시값 135->86 변화는 확인. (주의: longitudinalPlan.speeds 마지막 값은 예측 끝점이라 "현재 목표"가 아님)
- 비전이 커브를 못 볼 때 route 원시 중앙값 105.8 vs |vturn| 146 -> 일반 굽이에서는 route가 더 보수적이라 135 배율이 타당. 비전이 실제 커브를 볼 때는 route 원시값 = |vturn|의 0.99배(표본 18개, 전부 이 한 커브)라 1.35는 과함. 원시값만으로는 두 경우를 구분할 수 없어(완만한 굽이 101~103 vs 진짜 커브 96~101) 배율 값 하나로는 두 요구를 함께 만족시킬 수 없다.
- xTurnInfo 주석 기준 이 커브는 4(우측 분기) 앞, 46~50s 제동 구간은 6(tg, 톨게이트로 보임) 앞.

**결론/조치**: 112차의 두 후보(v_ego 캡핑, route<->vturn 전환 rate limit)는 채택하지 않는다(캡핑은 정체 중 가속만 막고 감속을 앞당기지 못함, rate limit은 전환 시 실제 감속이 -0.22뿐이라 개선 근거 없음). 사용자 결정으로 분기(xTurnInfo 3/4)·톨게이트(6) 안내 지점 200~300m 구간에서만 route 배율을 1.35 -> 1.05로 낮추는 코드를 작성(WIP.md 113차, carrot_serv.py map_turn_speed_factor). 일반 굽이는 기존 배율 유지.

**한계**: 근거가 분기 1건(+톨게이트 1건)뿐이고 실차 검증 미실시. 1.05와 200/300m 값은 이 한 건의 원시값(<=190m에서 96~101)에서 정한 초기값이며 다른 분기/톨게이트 로그로 확인 필요. 46~50s 제동 원인 소스는 규명하지 못했다.

## 2026-09-20 (112차) -- 라우트(내비 경로) 감속이 130km/h에서 정체되다 급감속하는 현상: route 목표속도가 v_ego를 반영하지 않는 구조적 원인 확인

**증상**: 사용자 제보 -- 라우트 감속이 130km/h에서 멈췄다가 뒤늦게 급감속되는 느낌.

**재현/근거**: 업로드된 실주행 rlog(제네시스 DH, 세그먼트 00000438--9c260778c7--155, 약 60초)를 parse_route.py(신규, toolkit 미등록 -- 1회성 조회 스크립트)로 파싱. carState/carrotMan을 시간 정렬해 보면 t=41.2~43.9초(2.7초) 동안 desiredSource=="route"이고 desiredSpeed가 정확히 130.0km/h로 고정된 채 유지됨. 이 구간 동안 실제 vEgo는 106.6->109.6km/h로 계속 증가. t=44.2초에 desiredSource가 vturn(비전 커브)으로 전환되며 130->127->121->111->104->97로 0.6초 만에 급락. 증상이 로그에 그대로 재현됨.

**원인(코드+시뮬레이션)**: route 목표속도는 carrot_man.py의 carrot_navi_route()가 생성. GPS 경로를 곡률로 변환한 뒤 먼 지점->가까운 지점 방향으로 역산(backward integration, V_CURVE_LOOKUP_BP/VALS + AutoNaviSpeedDecelRate 고정 상수)해 "그 지점에서 낼 수 있는 최고 속도" 상한선을 계산. 이 역산 루프를 그대로 재현해 시뮬레이션한 결과, 같은 도로 형상이면 v_ego가 100/120/145km/h 어느 값이어도 출력이 완전히 동일했음(carrot_navi_route 자체에 CS.vEgo 입력이 관여하지 않음). 즉 route 목표속도는 "지금 얼마나 빠른지"가 아니라 그 순간의 도로 곡률 형상 + 고정 감속상수만으로 정해지는 순수 물리적 상한선. 이 상한선이 실제 속도보다 높게 유지되는 구간에서는 desiredSpeed가 전혀 내려가지 않다가, 상한선 자체가 꺾이거나 매 프레임 재계산되는 vturn(비전 커브)이 먼저 낮은 값을 내놓는 순간 min()에 의해 갑자기 꺾임 -- 이것이 "정체 후 급감속"의 실체.

**한계**: 이번 로그에는 route 폴리라인 원본 좌표/곡률 배열이 남아있지 않아(carrotMan의 route= 디버그 문자열과 desiredSpeed/Source만으로 역추적), 2.7초 정체가 이 알고리즘 구조만의 문제인지 GPS/내비 위치 갱신 주기(로그 실측 약 1Hz, gpsLocation 61건/60초) 요인이 더해진 것인지는 분리하지 못함.

**수정안**: 미적용(이번 세션은 분석만). 방향성 후보만 기록 -- (a) carrot_navi_route()의 역산 시작점 또는 감속 목표를 v_ego 기준으로도 캡핑, (b) route와 vturn 소스 전환 시 min() 스냅 대신 완만한 전환(rate limit). 코드 변경 전 vturn 쪽과의 상호작용/우선순위 로직 추가 조사 필요.

**검증**: 정적 분석 + 로그 파싱 + 역산 로직 Python 재현 시뮬레이션만 수행. 코드 수정 없음. 실차 검증: 미실시.

## 2026-09-19 (95차) -- 같은 "Anchor match count != 1: got 0"이라도 원인이 CRLF가 아니라 앵커 텍스트 오기입일 수 있다: Linux 재현으로 두 원인을 구분한다(핵심 발견 45)

**증상**: 95차 devnotes 반영 스크립트 `95cha_devnotes_v2.ps1` 실행 시 WIP_SYNC.md 치환은 통과했으나 CURRENT_STATUS.md 치환에서 `Anchor match count != 1: got 0`으로 중단됐다(DEBUG 출력은 "부분 문자열조차 못 찾음"). commit/push 이전이라 반영 사고는 없었다(15절/18절 안전장치 정상 동작).

**재현조건**: 앵커 문자열을 실제 파일에서 복사하지 않고, 이전 회차의 유사 문구를 기억으로 옮겨 쓴 경우. 이번에는 93차 이전 항목에 있던 `반영 스크립트 실행/push 대기. ...` 문구가 94차 항목(실제: `...적용). 실행/push 대기. ...`)에도 있다고 가정해 `반영 스크립트 ` 접두를 넣었다. 이 접두가 붙은 문구는 파일 안 다른 2곳에만 있고 앵커 위치에는 없었다.

**입력/상태/호출흐름**: 대상은 SHA `f8d92c6`의 CURRENT_STATUS.md(LF, BOM 없음). `Invoke-ReplaceBlock`은 파일과 `$Old`를 모두 CRLF->LF 정규화한 뒤 `Matches().Count`를 세므로 개행 문제가 아니었다. DEBUG 블록이 앵커 앞 20자(`반영 스크립트 실행/push 대기. 실차`)의 위치를 못 찾았다는 사실 자체가 접두 불일치를 가리키고 있었다.

**원인 구분법(핵심)**: 중단된 스크립트의 앵커를 같은 SHA의 SHA 고정 raw 원본에 Linux에서 그대로 대조한다. 핵심 발견 44(85차)는 Linux에서 1회 매치였고 Windows checkout의 CRLF가 원인 후보였다. 이번에는 Linux에서도 0회였다. 즉 "Linux 0회 = 앵커 텍스트 또는 베이스 불일치, Linux 1회 + Windows 0회 = 체크아웃 개행/인코딩 문제"로 갈린다. 접두를 뺀 앵커는 1회 매치됐다.

**수정안**: `$csOld`/`$csNew`의 접두를 실제 문구로 정정한 `95cha_devnotes_v3.ps1`. 앵커는 항상 최신 SHA 원본에서 복사하고(6절), 전달 전에 *전달할 .ps1 파일에서* 앵커/치환 문자열을 그대로 추출해 SHA 고정 원본에 시뮬레이션(매치 1회 + 치환 결과)한다. 핵심 발견 42·44와 같은 원칙이다: 서술이 아니라 실제 코드/실제 원본을 대조한다.

**부수 발견 1 (검증 코드 자체의 결함)**: v3에 치환 결과 검증(핵심 발견 42)을 추가하며 "치환 후 파일 맨 앞 200자가 치환 전과 같은가" 검사를 넣었는데, WIP_SYNC.md 앵커는 파일 약 128번째 바이트에서 시작해 정상 치환도 이 검사에 걸렸다(시뮬레이션에서 발견, 100자로 수정). 새로 추가하는 검증 코드도 제품 코드처럼 실제 원본에 시뮬레이션해야 한다.

**부수 발견 2 (FINDINGS.md 혼합 개행)**: FINDINGS.md는 상단 889줄이 CRLF이고 890행 이후 48줄(44차 이후 하단에 추가된 항목)은 LF인 혼합 개행이다. LF 정규화 후 전체 재작성하면 889줄이 전부 diff로 잡히므로 이 파일은 개행 보존 삽입만 쓴다(95차 계속 반영 스크립트가 그렇게 처리).

**검증**: v3 push(carrot-ryu-note `5e67047`, 부모 `f8d92c6`) 후 SHA 고정 raw와 `git clone --depth 2`로 3개 파일을 재확인했다(앵커 결과, 개행 유지, BOM 없음, HANDOFF 마지막 개행). 샌드박스에는 PowerShell이 없어 스크립트 로직은 Python으로 시뮬레이션했으며(실제 PowerShell 실행 검증이 아님), 실제 실행 결과는 사용자 PC 로그와 push 후 재조회로 확인했다. 실차 검증 대상 아님(12절 무관).

## 2026-09-16 (60차) -- PowerShell 히어스트링은 닫는 `'@` 직전 개행을 항상 제거한다(핵심 발견 37)

**증상**: 60차 devnotes 반영 스크립트로 HANDOFF.md/WIP_SYNC.md/WIP.md/CURRENT_STATUS.md 4개 파일을 `[System.IO.File]::WriteAllText`로 교체한 뒤 SHA 고정 raw 조회로 재검증한 결과, HANDOFF.md만 파일 맨 끝의 개행 문자 1개가 사라져 있었음(그 외 내용은 완전 동일). WIP_SYNC.md/WIP.md/CURRENT_STATUS.md는 우연히 문제가 드러나지 않았음.

**재현조건**: PowerShell 단일따옴표 히어스트링(`$Var = @'` ... `'@`)에 원본 콘텐츠를 그대로 담아 파일에 쓰는 모든 경우(9절 "교체형" 파일 반영 패턴 전체에 해당).

**입력/상태/호출흐름**: `$Var = @'``r``n<콘텐츠>``r``n'@` 형태로 스크립트를 작성하면, PowerShell은 히어스트링을 파싱할 때 여는 줄(`@'`) 다음 줄부터 닫는 줄(`'@`) 바로 앞 줄까지를 내용으로 인식하되, 그 경계에서 콘텐츠의 마지막 개행 문자(닫는 `'@` 바로 앞의 `` `r``n ``)는 항상 잘라내고 변수에 담는다. 즉 콘텐츠가 실제로 개행으로 끝나 있었든 아니든, 히어스트링을 거치는 순간 그 마지막 개행은 사라진다.

**원인**: 이번 60차 반영 스크립트를 작성할 때, "닫는 `'@`가 반드시 줄 시작에 오도록 콘텐츠 뒤에 `` `r``n ``을 보장해서 붙인다"는 안전장치(히어스트링 자체가 깨지는 것을 막기 위한 것, 59차 오염 사고의 재발 방지 목적)만 검증했고, 그 개행이 PowerShell 파싱 단계에서 자동으로 잘려나간다는 점은 반영하지 못했음. HANDOFF.md는 원본 콘텐츠 자체가 실제로 개행으로 끝나 있어 이 잘림이 실제 내용 손실로 이어졌고, 나머지 3개 파일은 원본이 개행 없이 끝나 있어 안전장치로 붙인 개행이 잘려나간 결과가 우연히 원본과 일치했음.

**수정안**: 히어스트링으로 담은 콘텐츠를 파일에 쓸 때는, 원본이 개행으로 끝나야 하는 파일이라면 `[System.IO.File]::WriteAllText` 호출 직전에 `$Var = $Var + "``r``n"`으로 개행을 명시적으로 다시 붙인다(히어스트링이 이미 하나를 삼켰다고 가정). 스크립트 작성 시 .ps1 파일 자체의 바이트만 놓고 "콘텐츠가 정확히 담겼는지"를 확인하는 것으로는 부족하며, PowerShell이 실행 시점에 히어스트링을 이렇게 처리한다는 점까지 검증에 포함해야 한다.

**검증**: SHA 고정 raw 조회 결과를 Python으로 원본과 바이트 단위 대조(LF 정규화 후 비교)해 발견. 실차 검증 대상 아님(devnotes 파일 문제, 12절 무관).

## 2026-09-16 (51차) -- 스크린샷에 시계/온도 HUD가 빠지는 원인: 캡처가 같은 프레임의 나머지 HUD보다 먼저 실행됨(핵심 발견 36)

**증상**: 50차 PNG 롤백 이후 스크린샷 저장 자체는 성공하지만(파일 생성 확인), 저장된 이미지에 시계/온도 등 HUD 요소가 전혀 없고 배경(카메라 뷰) 화면만 담김.

**재현조건**: 사용자가 실기기에서 스크린샷 버튼을 눌러 얻은 사진과, carrotweb 로그탭에 그 파일이 실제로 목록에 오른 화면을 함께 제공.

**입력/상태/호출흐름**: hud_renderer.py의 HudRenderer._render()는 (1) 헤더 그라디언트 -> (2) set_speed -> (3) exp_button -> (4) screenshot_button.render()(내부에서 Widget의 클릭 처리 경로를 통해 _on_click() 호출) -> (5) record_button -> (6) plot_renderer -> (7) _draw_date_time -> (8) _draw_tpms -> (9) _draw_egpu_badge -> (10) _draw_cruise_speed_animation 순서로 그린다. 기존 ScreenshotButton._on_click()은 (4) 시점에 즉시 capture_onroad_screenshot()을 호출했고, 그 안의 rl.load_image_from_screen()은 호출된 그 순간의 프레임버퍼를 읽는다.

**계산/조건/분기**: (4)는 (7)~(10)보다 먼저 실행되므로, 클릭이 눌린 그 프레임에서는 시계/온도/eGPU 배지/크루즈 애니메이션이 아직 프레임버퍼에 그려지지 않은 상태다. 즉 캡처 시점의 프레임버퍼에는 도로 배경/속도계/버튼류만 있고 (7)~(10)이 없다.

**출력**: 저장된 PNG에 시계/온도 HUD가 없고 순수 배경만 담기는 사용자 제보 사진과 정확히 일치.

**원인**: 캡처 호출이 같은 프레임 안에서 렌더 순서상 나머지 HUD보다 먼저 실행되는 구조적 타이밍 문제(export_image 자체의 실패는 아님, 50차 핵심 발견 35와는 별개의 새로운 문제).

**수정안**: _on_click()에서 캡처를 즉시 실행하지 않고 pending 플래그만 세운 뒤, _render()의 맨 끝(모든 HUD를 그린 다음)에서 그 플래그를 소비해 캡처를 실행하도록 이동. 클릭과 실제 캡처 실행이 한 프레임 늦게 분리되지만, 사용자가 버튼을 누른 그 프레임(또는 다음 프레임)의 완성된 화면을 캡처한다는 목적에는 문제가 없다.

**검증**: py_compile 통과, hud_renderer.py Replace-Block 앵커 2곳(1회 매치) 확인. **실차 검증: 미실시** -- 다음 세션 최우선.

**부가 작업**: 같은 세션에서 screenshot_capture.py에 저장 전 480p(세로 기준) 다운스케일(rl.image_resize)을 추가(사용자 요청, HUD 타이밍 문제와는 별개의 독립적 변경).

## 2026-09-16 (50차) -- 스크린샷 export_image 실패 원인을 클릭전달이 아닌 JPG export로 좁힘(핵심 발견 35)

**증상**: 49차에서 추가한 진단 로그를 반영한 뒤(commit `dfdbfff9`)에도 스크린샷 저장이 계속 실패.

**재현조건**: 사용자가 실기기에서 스크린샷 버튼을 여러 차례 눌렀고, 그 결과를 `grep -ai screenshot /data/log/swaglog.*`로 채취해 제공. git pull 전(commit `41fd34a7`, 47차)과 후(commit `dfdbfff9`, 49차) 로그가 함께 포함됨.

**분석**: git pull 이후 구간에서, raylib의 `Failed to export image` 경고 직후 매번 `screenshot_button.py:28 _on_click`에서 `capture_onroad_screenshot: export_image failed for ...` 경고가 찍힘. 이 경고 문자열은 코드상 `capture_onroad_screenshot()`이 `rl.export_image()`의 반환값이 `False`일 때만 내보내므로, 이 로그가 존재한다는 사실 자체가 (1) `_on_click()` 콜백이 정상 호출됐고 (2) 그 안에서 `load_image_from_screen()`까지 성공(다른 실패 분기 로그가 없음)했음을 뜻함. 즉 실패 지점은 오직 `rl.export_image()` 호출뿐. 이 실패는 git pull 이전(47차, 진단 로그 추가 전) 구간에도 동일하게 나타나고 있었음.

**정황(가설, 미확정)**: 46차까지(PNG 저장 시절)는 방향이 뒤집힌 채로나마 저장 자체는 성공했다는 기존 devnotes 기록(47차 항목)과, 47차에서 확장자를 `.jpg`로 바꾼 시점부터 100% 실패로 바뀌었다는 이번 grep 결과를 근거로, JPG export가 이 기기의 raylib 빌드(comma-deps-raylib==6.0.0.1.post101)에서 지원되지 않거나 stb_image_write의 JPG 인코더가 빠진 채 빌드됐을 가능성을 유력 가설로 제시. 다만 47차 커밋에는 DPI 수정(`rl.take_screenshot()` -> `rl.load_image_from_screen()`)과 확장자 변경(PNG->JPG)이 함께 들어가 있어 이 로그만으로는 두 변경 중 무엇이 실패 원인인지 분리되지 않음(11절, 확정 아님).

**다음 단계**: 변수를 분리하기 위해 저장 확장자만 `.jpg` -> `.png`로 되돌리는 반영 스크립트를 작성(load_image_from_screen() DPI 수정은 유지). 다음 세션은 이 상태로 실차 테스트해 (a) PNG로 저장 성공 시 JPG export 미지원으로 확정, (b) PNG도 실패 시 확장자와 무관한 별도 원인으로 조사 방향 전환.



## 2026-09-16 (49차) -- 스크린샷 버튼 무반응/미저장 제보: 원인 미확정, 진단 로그로 전환(핵심 발견 34)

**증상**: 사용자가 스크린샷 버튼을 눌러도 반응이 없고, 로그탭 사진 목록에 아무것도 저장되지 않는다고 제보. 실기기 로그탭 스크린샷을 보면 목록의 3개 항목이 전부 MP4(화면녹화)이며 JPG(사진)가 0건 -- 버튼을 눌러도 실제로 캡처가 한 번도 성공한 적이 없다는 것과 일치.

**분석 범위** (11절 단계적 확장 원칙에 따름):
- 클릭 전달 경로: `Widget._process_mouse_events()`(system/ui/widgets/__init__.py) -- 눌림/뗌 이벤트가 `_handle_mouse_release()`를 거쳐 `_click_callback()`을 호출하는 표준 경로. `ScreenshotButton`은 다른 버튼들과 동일한 `Widget` 기반 클래스라 이 경로 자체에 버튼 전용 문제가 있다고 보기 어려움.
- 캡처 함수: `capture_onroad_screenshot()`(47차에서 `rl.load_image_from_screen()`으로 교체된 버전) -- 로직 자체는 47차에서 GitHub 반영 및 48차에서 실기기 배포까지 확인됐으나, "캡처 버튼을 실제로 눌러본 결과물"은 아직 한 번도 확인된 적이 없었음(HANDOFF.md 48차 미완료 1번과 동일 이월 항목).
- pyray 바인딩 버전 확인: `uv.lock`에 `comma-deps-raylib==6.0.0.1.post101`(Python>=3.12)로 고정돼 있음을 확인. 해당 버전의 wheel을 sandbox에 설치해 `rl.load_image_from_screen`/`rl.export_image`가 실제로 존재함을 확인(정적 조사가 아니라 실제 설치로 검증).

**결론**: 정적 코드 리뷰만으로는 "왜 안 눌리는지" 원인을 확정할 근거를 찾지 못함. 기존 코드는 실패 시 `except Exception: return None`으로 원인 정보 없이 조용히 실패하는 구조라, 실기기 로그에도 흔적이 안 남았을 가능성이 높음(그 자체로는 버그가 아니지만 진단을 불가능하게 만드는 구조). 추측만으로 원인을 확정하지 않는다는 11절 원칙에 따라, 원인 확정 대신 다음 실차 테스트에서 원인이 드러나도록 진단 로그(`cloudlog.debug`/`warning`/`exception`)를 3개 실패 분기 + 클릭 콜백 진입 지점에 추가.

**부수 작업**: 사용자가 업로드한 "정상이어야 하는 모습" 참고 사진을 픽셀 좌표 분석(빨간 원 위치)해, 스크린샷 버튼을 화면 중앙(record 버튼 기준점, `anchor_x`)에서 좌측으로 170px(버튼폭 140 + 간격 30) 이동. record 버튼 위치는 수식상 이전과 동일하게 유지.

**검증 범위**: `py_compile`/`ast.parse` 3개 파일 통과. `hud_renderer.py`의 변경 전 블록이 파일 전체에서 정확히 1회 매치함을 Python으로 확인(9절). `cloudlog.debug/warning/exception`이 `common/swaglog.py`의 `cloudlog = SwagLogger()`(`logging.Logger` 서브클래스) 표준 메서드임을 `common/logging_extra.py` 소스로 확인. **실차 검증: 미실시** -- 다음 세션 최우선 이월(진단 로그가 실제로 남는지, 버튼 위치가 사용자 의도와 맞는지 모두 확인 필요).

**교훈**: 실차 배포까지 확인된 코드(47차)라도, "그 코드가 실제로 실행되는 경로(버튼 클릭)"까지 실증되지 않았다면 사용자가 겪는 문제의 원인일 수 있다 -- "코드 반영 확인"과 "그 코드 경로의 실제 동작 확인"은 별개임(12절, 16절과 유사 패턴).

## 2026-09-16 (47차) -- rl.take_screenshot()의 DPI 스케일 곱셈이 스크린샷 캡처 크기를 뒤바꿈(핵심 발견 33)

**증상**: 사용자가 온로드 화면 스크린샷 버튼으로 찍은 사진이 정상(가로 2160x1080, 온로드 화면 전체가 그대로 보임)이 아니라 세로(1080x2160)로 저장되고, 상단 대부분이 검정으로 채워져 있으며, 파일 용량도 정상 예시 대비 4배가량 컸음. 사용자가 "정상이어야 하는 모습" 예시 사진과 실제 저장된 사진 두 장을 함께 제공.

**분석**: 두 이미지의 실제 픽셀 크기를 직접 확인한 결과 정상 예시는 2160x1080(가로), 실제 저장본은 1080x2160(세로) -- 가로/세로가 정확히 뒤바뀜. `screenshot_capture.py`가 쓰는 `rl.take_screenshot()`은 raylib(rcore.c) 내부에서 다음과 같이 캡처 크기를 계산한다:

```
Vector2 scale = GetWindowScaleDPI();
width  = (int)(render.width  * scale.x);
height = (int)(render.height * scale.y);
```

즉 논리적 렌더 크기(2160x1080)에 `GetWindowScaleDPI()`가 반환하는 배율을 곱한 값을 캡처 크기로 쓴다. 이 기기에서는 이 DPI 배율이 등방(x/y 동일)이 아니라 비등방으로 반환되는 것으로 보이며, 그 결과 곱셈 후 가로/세로 값이 뒤바뀐 크기로 캡처가 이루어진 것으로 추정된다(정확한 배율 값 자체는 실기기 접근 없이는 확인 불가 -- sandbox는 디스플레이가 없어 실제 DPI 조회 결과를 직접 재현하지는 못했고, 증상과 raylib 소스 코드 분석으로 원인을 추론했다는 한계가 있음).

같은 파일 안에서 픽셀 카운트 자체는 2160*1080 = 1080*2160으로 동일하므로, 용량 차이(4배)는 이 뒤바뀜 버그 자체보다는 포맷 차이(정상 예시는 JPG, 실제 저장본은 PNG)에서 오는 것으로 판단 -- 사진처럼 노이즈가 많은 콘텐츠는 무손실 PNG가 손실 JPG보다 수배 커지는 것이 일반적이라, 이 부분은 "버그"가 아니라 포맷 선택의 문제였음.

**수정**:
1. **크기/방향 버그**: `rl.load_image_from_screen()`으로 교체. raylib 소스 기준 이 함수는 `GetScreenWidth()/GetScreenHeight()`(논리적 화면 크기)를 그대로 쓰고 DPI 배율을 곱하지 않으므로 위 버그의 영향을 받지 않는다. 영상 녹화 파이프라인(`GuiApplication.render()`)이 `rl.load_image_from_texture()`로 이미 같은 "DPI 배율 계산 없이 프레임버퍼 직접 읽기" 방식을 쓰고 있고, 46차에서 실차로 정상 동작이 검증돼 있어 같은 원리를 재사용한 것.
2. **용량 문제**: 저장 포맷을 PNG에서 JPG로 전환. raylib `ExportImage()`는 파일 확장자로 포맷을 판단하며 JPG는 quality=90으로 저장한다(코드 상 고정값, 별도 설정 불가). `SCREEN_RECORDING_PHOTO_EXTS`(carrot/server/config.py)에 이미 `.png`, `.jpg`, `.jpeg` 세 개가 모두 등록돼 있고, 사진 목록/썸네일 생성/파일 서빙(mimetypes.guess_type 기반) 어디에도 `.png` 전용 하드코딩이 없음을 관련 파일(catalog.py, routes.py, screenshots.js) 전수 조사로 확인 -- 그래서 백엔드/프론트엔드 추가 수정 없이 `.jpg` 저장만으로 바로 목록/썸네일/다운로드/전송이 동작할 것으로 예상(실차 검증 전까지는 "예상").

**검증 범위**: `py_compile` 구문 검증 통과. 이 세션의 sandbox에 raylib pip 패키지를 별도 설치해 `rl.export_image(image, "*.jpg")` 자체가 정상적으로 JPG 파일을 만든다는 것만 headless로 확인(실제 온로드 화면을 렌더링해 캡처하는 전체 경로는 디스플레이가 없는 sandbox에서 재현 불가). **실차 검증: 미실시** -- 다음 세션 최우선 이월.

**교훈**: raylib처럼 내부적으로 DPI 스케일을 자동 보정하는 함수(`TakeScreenshot`, 그 외 유사 계열)는 표준 PC 환경에서는 잘 동작하지만, 임베디드/비표준 디스플레이 환경에서는 DPI 배율 자체가 예상과 다르게 나올 수 있다. 같은 목적(화면 픽셀 읽기)을 위해 raylib이 제공하는 여러 API 중, 이미 프로젝트 안에서 실기기 검증까지 끝난 경로(영상 녹화의 `load_image_from_texture`)와 같은 계열의 "DPI 비의존" API(`load_image_from_screen`)가 있다면 그쪽을 우선 채택하는 것이 안전하다.
## 2026-09-16 (46차) -- 정지 프레임 육안 비교의 한계를 버튼 영역 크롭 + 프레임별 평균 RGB 수치 비교로 극복(녹화 버튼 깜빡임 실증)

이전 세션에서는 1.8초 분량 영상의 정지 프레임을 육안으로 비교했을 때 버튼 색상/투명도 차이가 뚜렷하지 않아 판단을 보류하고 사용자의 육안 확인에 의존했음(45차 이전 기록). 이번 세션에서는 같은 유형의 검증을 다음 방식으로 정량화함:
1. ffmpeg로 영상을 6fps로 프레임 추출(4초 분량 -> 24프레임, 원본 해상도 2160x1080 유지)
2. 첫 프레임에서 색상 필터(R-G>40, R>130)로 버튼 영역 픽셀 좌표를 자동 특정(x:1212-1288, y:912-988)
3. 모든 프레임에서 해당 영역의 평균 R/G/B와 밝기를 계산해 프레임별 수치 비교

결과: 밝기값이 ~99(빨강 채움, R≈193)와 ~34(어두움, R≈33) 사이를 프레임마다 규칙적으로 오갔음 -- 육안으로는 애매했던 변화가 수치로는 명확한 이진 패턴으로 드러남. 앞으로 깜빡임/색상 변화 등 시각적으로 미묘한 차이를 검증할 때는 정지 프레임 육안 비교보다 이 방식(영역 크롭 + 프레임별 픽셀 통계)을 우선 사용할 것.

## 2026-09-16 (45차-정정) -- carrot-ryu-note 45차 devnotes가 중간 초안 상태로 push됨(코드는 최종본대로 정상): 원인, 검증 방법, 재발 방지

**증상**: carrot-ryu-note commit `0b0d32247d452393b3484381d2b95e86ef7ee64e`("45cha devnotes: bundle-not-rebuilt root cause + rebuild fix")의 실제 파일 내용(WIP.md 최상단, HANDOFF.md Worker 라인, 커밋 메시지)이 세션 마지막에 전달된 최종 `45cha_devnotes_carrot_ryu_note.ps1` 스크립트의 내용과 전혀 다름을 재확인 과정에서 발견.

**검증 방법**: (1) 업로드된 두 스크립트(`45cha_apply_bundle_carrot_ryu.ps1`, `45cha_devnotes_carrot_ryu_note.ps1`)에서 커밋 메시지/Worker 라인/WIP 본문 텍스트를 grep으로 추출. (2) `git clone --depth 5 --branch carrot-ryu`와 `--branch carrot-ryu-note`로 각각 fresh clone 후 `git log -1 --format=%B`, `head devnotes/WIP.md`, `head devnotes/HANDOFF.md`로 실제 커밋 내용을 바이트 단위로 비교.

**결과**: carrot-ryu(코드) 쪽은 커밋 메시지 전문이 `45cha_apply_bundle_carrot_ryu.ps1`의 `$commitMsg`와 100% 일치, `js/generated/logs.js` sha256도 스크립트가 기대한 값과 일치 -- **코드는 최종본대로 정상 반영/검증됨**. 반면 carrot-ryu-note(devnotes) 쪽은 최종 `45cha_devnotes_carrot_ryu_note.ps1`의 `$commitMsg`("carrotweb 번들 재빌드 크로스플랫폼 비결정성 진단/우회 기록")나 `$WipEntry`("핵심 발견 30 (45차) -- carrotweb 생성 번들 재빌드는...")와 전혀 다른, 그보다 앞선 중간 단계(1차 시도가 아직 실패하지 않았던 시점 -- "반영 스크립트 작성 완료, 실행 대기" 문구가 남아있는 등)의 텍스트가 커밋돼 있음을 확인.

**원인 추정**: 같은 세션 안에서 파일명이 동일한(`45cha_devnotes_carrot_ryu_note.ps1`) devnotes 스크립트가 두 차례(중간 초안 -> 최종본) 만들어졌고, 사용자 PC Downloads 폴더의 파일명 충돌(구버전이 남아있거나 최종본이 `(1)` 등으로 다르게 저장)로 사용자가 실행한 파일이 최종본이 아닌 구버전이었을 가능성이 가장 높음. 직접 재현/확정은 못 함(사용자 PC 로컬 상태를 조회할 수단 없음).

**부수 발견 (착시 배제)**: `git clone --depth 1` 후 `git show --stat HEAD`를 돌리면 부모 커밋이 로컬에 없어 해당 커밋이 grafted root(부모 없는 최초 커밋)로 취급되고, diff가 빈 트리 대비로 계산되어 devnotes 폴더의 관련 없는 파일(PARAMS_REGISTRY.md, PROJECT_INSTRUCTIONS_carrot-ryu.md, params_backup json 등)까지 전부 "추가"로 나열됨. 세션 중 이를 "예상 밖 파일(LAST_ANALYZED.md)이 커밋에 섞였다"는 이상 징후로 오인할 뻔했으나, `--depth 5`(부모 포함) clone으로 재확인해 실제 diff는 딱 4개 파일(WIP/FINDINGS/HANDOFF/CURRENT_STATUS.md)이었음을 확인, 착시로 결론.

**대응**: 이 커밋(45차-정정)으로 WIP.md/FINDINGS.md에 이 사실을 기록하는 항목을 최상단에 추가(기존 45차 항목은 audit trail 보존을 위해 수정하지 않고 그대로 둠)하고, HANDOFF.md/CURRENT_STATUS.md는 실제 최종 상태(코드 push 완료/검증됨, 실기기 검증은 아직 미실시)로 전체 교체함.

**재발 방지 제안**: 한 세션 안에서 같은 대상(코드/devnotes)에 대해 스크립트를 다시 작성할 때는 파일명에 버전 표시를 붙여(예: `-v2`, `-final`) 이전 로컬 파일과 절대 겹치지 않게 한다. 사용자 승인 시 지침 문서(9절/18절 인근)에 정식 규칙으로 추가 검토.

## 2026-09-16 (44차) -- 사진 목록 렌더 크래시(formatLogBytes 미import) / delete_all_videos 폴더 범위 누락 / 녹화 버튼 깜빡임 부재, 원인 확정 및 수정

### 증상 1: 화면녹화 탭에서 파일 체크박스 선택 시 `formatLogBytes is not defined` 토스트
- 재현조건: 화면녹화 탭 -> 파일 체크박스 선택(스크린샷 5 참고).
- 호출흐름: 체크박스 선택 -> 선택 합계 크기 표시 로직(screenshots.js 162번째 줄, `formatLogBytes(totalBytes)`) 호출 -> `formatLogBytes`가 스코프에 없어 ReferenceError.
- 원인: `screenshots.js` 3번째 줄 import문에 `formatLogBytes`가 빠져 있었음(`formatRelativeEpoch`, `hydrateLogsLazyImages`, `isLogsPageActive`, `unobserveLogsLazyImages`만 import). `runtime.js` 256번째 줄에 정의, 1108번째 줄에 export돼 있고 `dashcam.js`/`screenrecord.js`는 정상 import 중이라 이 파일만의 누락.
- 39cha-fix(40차, commit bdde8326)에서 같은 파일의 `formatRelativeEpoch` 누락은 고쳤으나, 같은 파일에 있던 `formatLogBytes` 누락은 그때 점검 범위 밖이었음(개별 항목 렌더 62번째 줄에서도 쓰여 사진 목록 자체가 렌더되지 않는, 단순 "합계 표시 오류"보다 더 근본적인 문제였음).
- 수정: import문에 `formatLogBytes` 추가. (44차 코드 반영 스크립트, 아직 사용자 실행 대기)

### 증상 2 (사용자 요청): "delete all videos"가 캡쳐 사진을 지우지 않음
- 재현조건: 도구탭 -> User/System -> delete all videos.
- 원인: `dispatcher.py`의 `delete_all_videos` 액션(비동기 job 처리 682번째 줄, 동기 REST 처리 1164번째 줄) 둘 다 `paths = ["/data/media/0/videos"]` 하드코딩. 캡쳐 사진(.png)은 `screenshot_capture.py`가 `SCREEN_RECORDING_DIRS[1]`(`/data/media/0/screenrecord`)에 저장하도록 설계돼 있어, 영상 폴더만 도는 기존 로직이 사진 폴더를 건드리지 못함.
- 수정: 두 곳 모두 `config.py`의 `SCREEN_RECORDING_DIRS`(영상+사진 후보 폴더 7개 전체, `catalog.py`가 실제 파일 목록 조회에도 쓰는 동일 소스) 기준으로 변경. import문에 `SCREEN_RECORDING_DIRS` 추가.

### 증상 3: 녹화 버튼이 색만 바뀌고 깜빡이지 않음
- 사용자 설명(직접 질의응답으로 확인): "평상시 흰색테두리 정상, 누르면 빨간색으로 채워짐, 깜박이지는 않음, 또 누르면 다시 흰색테두리 투명으로 복귀".
- 코드 확인 결과 사용자 설명과 정확히 일치하는 구현이었음(42차 `record_button.py`) -- 버그가 아니라 "깜빡임 로직 자체가 없음"이 원인.
- 수정: `hud_renderer.py`가 카메라 감지/CPU·메모리 과열 경고 표시에 이미 쓰는 `_blink_timer`(0~15 순환 프레임 카운터, 189번째 줄 초기화·1465번째 줄 증가) 재사용. `record_button.py`에 `set_blink_phase(on: bool)` 메서드를 추가하고, `hud_renderer.py`의 렌더 호출 직전에 `self._record_button.set_blink_phase(self._blink_timer <= 8)`를 배선. 녹화 중일 때만 채움/테두리를 번갈아 그리고, 녹화 안 할 때는 42차와 동일(흰 테두리, 안 깜빡임).

### 공통 패턴 (핵심 발견 28 참고)
증상 1·2 모두 "실제 참조/순회 대상이 원래 구현 이후 넓어졌는데, 코드(import 목록/하드코딩 경로)가 함께 갱신되지 않음"이라는 동일한 패턴. 42차 이후 반복적으로 같은 파일을 건드리게 되므로, 이후 이 파일들을 다시 수정할 때는 grep으로 실제 참조 대상 목록이 현재 설계와 일치하는지 먼저 교차 확인할 것.

### 반영 스크립트 경로 오류 사전 발견 (핵심 발견 29 참고)
44차 반영 스크립트를 준비하며 대상 파일 경로를 `selfdrive/...`(레포 루트 기준으로 가정)로 초안 작성했으나, `git clone` 전체 리허설로 재검증한 결과 ryujmin97/openpilot 레포 루트에는 `openpilot`(실제 콤마 코드, `selfdrive`가 그 안에 있음)과 `carrot` 두 서브디렉터리가 공존하는 구조임을 확인 -- 정확한 경로는 `openpilot/selfdrive/...`. anchor 매치(Python 시뮬레이션, 전부 1회) 뿐 아니라 스크립트가 clone하는 실제 디렉터리 구조에서 대상 파일 존재 여부까지 `git clone`으로 재확인한 뒤 스크립트를 완성함(9절/6절 원칙 확장 적용).

검증: `py_compile`(dispatcher.py, hud_renderer.py, record_button.py) + `node --check`(screenshots.js) 통과. Replace-Block 앵커 5곳 전부 최신 GitHub HEAD(`4f81ab75`) 기준 정확히 1회 매치 확인(Python 시뮬레이션). 실제 `git clone` 리허설로 대상 파일 경로 존재 확인. **실차/실기기 검증은 미실시**(12절) -- 스크립트 실행 후 다음 세션에서 진행.


## 2026-09-15 (38차) -- raw.githubusercontent.com 브랜치-head 캐시 지연 재현(핵심 발견 21 재확인) 및 실기기 검증 상세 근거

**배경**: 37차 코드/devnotes push 직후, carrot-ryu-note 브랜치-head raw URL(`raw.githubusercontent.com/.../carrot-ryu-note/devnotes/HANDOFF.md`)로 HANDOFF.md/CURRENT_STATUS.md를 재조회했더니 37차 이전(36차) 내용이 그대로 반환됨. commit-pinned raw URL(`raw.githubusercontent.com/.../4b28547/devnotes/HANDOFF.md`)로 같은 파일을 다시 조회하자 37차 내용이 정상 확인됨 -- 33차에서 발견된 캐시 지연 현상(핵심 발견 21)이 이번에도 동일하게 재현됨. commit diff 엔드포인트는 두 경우 모두 정확했음. 향후에도 push 직후 devnotes 재조회 시에는 commit-pinned raw URL 또는 commit diff 엔드포인트를 우선 사용할 것.

**실기기 검증 상세 근거(38차)**: 사용자 제보 스크린샷 9장을 이미지별로 대조.
- 이미지1(온로드 HUD 14:47:37): 경로안내 박스 정상 표시, 도착 텍스트-회전아이콘 겹침 없음(34차 목표 1 달성 확인). 도로명 "대덕대로989번길"은 박스 바깥쪽 하단에 IP 주소와 같은 줄로 표시 -- 34차 WIP 기록("박스 안쪽, 신호과속과 같은 줄")과 정확히 일치하는지는 신호과속 배지 부재로 판단 보류.
- 이미지2~4(대시캠 탭 로그 전송 플로우): "로그 전송" 확인 다이얼로그 라벨이 "구글 드라이브"로 정상 표시(36차 라벨 버그 수정 확인), 전송 결과 "완료 1/1" 정상.
- 이미지5(화면녹화 탭): "화면녹화 기록이 없습니다" -- 36차 업로드 UI(체크박스 등) 테스트 대상 부재, 스크린샷(.png) "사진" 스트립만 존재.
- 이미지6(도구 탭): Git Commands/User System 메뉴 -- 이번 검증 항목과 직접 관련 없음(참고용으로 함께 제출된 것으로 보임).
- 이미지7(화면녹화 탭 햄버거 메뉴): "로그 메뉴"에 정렬 옵션만 존재, "최근 로그 업로드" 섹션 없음 -- 36차 탭 분기 수정 확인.
- 이미지8(구글드라이브 앱 내 드라이브): "CarrotWeb Logs" 폴더 1개만 존재.
- 이미지9(CarrotWeb Logs 폴더 내부): 파일 3개(HYUNDAI_GENESIS_541384... 14:52, tmux_HYUNDAI_GENESIS_... 14:50, tmux_HYUNDAI_GENESIS_... 14:48) -- 모두 같은 폴더에 위치. 다만 시간 간격(수 분)으로 인해 37차 락이 방어 대상으로 삼는 "거의 동시 호출" 레이스의 직접 재현은 아니며, tmux 항목 2건은 carrot_man.py의 send_tmux_web()(37차 FINDINGS에서 언급된 별도 프로세스 경로)에서 발생한 것으로 추정됨 -- 즉 이번 관찰은 오히려 "락이 보호하지 못하는 프로세스 경계를 넘나드는 호출들도 결과적으로 폴더가 겹치지 않았다"는 정황이며, 동시성 레이스 자체를 테스트한 것은 아님(원인 확정 아님, 추정).
## 2026-09-15 (37차) -- Drive 폴더 2개 생성(핵심 발견 23 증상 4) 원인 확정: _ensure_folder() TOCTOU 레이스 컨디션

**배경**: 35차에서 사용자가 Google Drive "내 드라이브"에 "CarrotWeb Logs" 폴더가 2개 생성된 것을 스크린샷으로 제보(증상 4). 당시 코드 조사로 `_ensure_folder()`의 300초 캐시와 이름검색/자동생성 흐름을 확인했으나, "300초 이상 간격" 또는 "Drive Files.list의 eventual consistency 지연" 중 어느 쪽이 실제 원인인지는 호출 시각을 알 수 없어 확정하지 못하고 "우선순위 낮음, 미확정"으로 이월했음.

**원인 확정**: `gdrive_upload.py`(294~331행, 37차 수정 전 기준) `_ensure_folder()`의 순서는 다음과 같음.
```
① cache_age/cached_id 확인 -> 캐시 유효하면 즉시 반환
② (캐시 미스) Drive Files.list(name='CarrotWeb Logs')로 검색  <- 여기서 API 왕복 대기
③ 검색 결과 없으면 Files.create()로 새 폴더 생성            <- 여기서도 API 왕복 대기
④ 생성/검색된 id를 _folder_verified_cache에 기록
```
①~④ 사이에 어떤 형태의 락(lock)도 없음. 즉 두 호출이 ①을 거의 동시에 통과하면(둘 다 캐시 미스), 첫 호출이 아직 ②~③의 API 왕복(보통 수백ms)을 끝내지 못한 상태에서 두 번째 호출도 ②를 실행하게 되고, 이 시점엔 아직 폴더가 존재하지 않으므로 두 호출 모두 files.list에서 빈 배열을 받아 각자 ③에서 폴더를 생성함. 즉 300초 캐시 만료나 Drive API의 eventual consistency와는 무관하게, **캐시가 채워지기 전의 좁은 레이스 윈도우**만으로 재현 가능한 결정론적 버그임.

**두 호출이 실제로 어떻게 겹쳤는가**: 35차 증상 1(대시캠 탭 개별/그룹 전송)과 증상 3(햄버거 메뉴 "최근 로그 업로드")은 둘 다 `server/features/dashcam/upload_jobs.py`의 `run_upload_segments()`를 거쳐 `gdrive_upload.upload_file_resumable()` -> `_ensure_folder()`를 호출하며, 각 요청은 `asyncio.create_task(run_job(job))`(upload_jobs.py:315)로 서로 독립된 백그라운드 job이 됨. 두 UI 요소(대시캠 탭 전송 버튼, 전역 햄버거 메뉴)는 서로를 비활성화하지 않으므로, 사용자가 짧은 시간 안에 둘 다 눌렀다면(35차 세션에서 여러 증상을 연달아 테스트하던 정황과 부합) 두 job이 겹쳐 실행되며 위 레이스가 그대로 발생할 수 있음.

**재현 및 수정 검증(목 테스트)**: 실제 aiohttp/Drive API 없이, `session.get`/`session.post`를 50ms 지연 후 응답하는 가짜 객체로 교체하고 `asyncio.gather`로 `_ensure_folder()`를 동시에 2번 호출하는 스크립트를 작성해 실행함.
- 수정 전 코드(GitHub 현재 버전, commit 0835b059 기준): 폴더 생성 API가 2번 호출됨(`create_calls: ['CarrotWeb Logs', 'CarrotWeb Logs']`) -- 버그 재현 성공.
- 수정 후 코드(37차, `_folder_lock` 추가): 폴더 생성 API가 1번만 호출되고(`create_calls: ['CarrotWeb Logs']`), 두 호출 모두 동일한 folder_id를 반환함 -- 수정 확인.
이 테스트는 aiohttp/openpilot.common.params 등 외부 의존성을 최소 스텁으로 대체한 것으로, 실제 Google Drive API나 실기기 환경을 사용하지 않았다는 한계가 있음(정적/목 검증 수준, 실차 검증 아님).

**수정**: `gdrive_upload.py`에 모듈 레벨 `_folder_lock = asyncio.Lock()`을 추가하고, `_ensure_folder()`의 캐시확인~검색~생성~캐시기록 전체를 `async with _folder_lock:`으로 감쌈(문자열 블록 치환, 20차 기본 방식).

**남은 한계(의도적으로 범위 밖, 사용자 승인)**: `carrot_man.py`의 `send_tmux_web()`(945행)은 웹서버(`server/app.py`)와 별도 프로세스에서 `asyncio.run()`으로 실행됨. 프로세스가 다르면 `_folder_lock`과 `_folder_verified_cache` 모두 프로세스별로 독립된 메모리이므로, 이번 수정으로는 "웹서버 쪽 업로드"와 "carrot_man.py의 tmux 진단정보 전송"이 우연히 겹치는 교차 프로세스 레이스까지는 막지 못함. 근본 해결책은 최초 생성된 folder_id를 `CarrotGDriveFolderId` 같은 신규 Params 키에 영구 저장해 두 프로세스가 공유하는 방식(22차에 등록한 Client ID/Secret/RefreshToken과 동일 패턴)이며, 사용자와 논의 후 이번 세션에서는 최소 수정(인프로세스 락)만 반영하기로 확정함. 근본 수정이 필요해지면(예: 실기기에서 폴더가 다시 중복 생성되는 사례가 재현되면) 이 옵션을 재검토할 것.

**교훈**: "추정, 미확정"으로 이월했던 항목도 실제 코드의 동시성 구조(락 유무, 호출 경로가 별도 asyncio task로 갈라지는지)를 직접 추적하면 결정론적으로 확정할 수 있는 경우가 있음. 특히 Google API의 "eventual consistency"처럼 외부 요인으로 돌리기 쉬운 증상일수록, 자체 코드에 동시성 제어가 있는지부터 먼저 확인할 가치가 있음.
## 2026-09-15 (35차) -- Drive 업로드 관련 실기기 이슈 3건 원인 특정 + 화면녹화 탭 신규 스펙 확정

**배경**: 32차(drive.file+폴더자동생성)가 실기기에서 실제로 동작해 Drive 연결 자체는 성공했다고 사용자가 확인함(핵심 발견 20 이후 첫 실기기 결과). 다만 사용자가 스크린샷 3장 + Drive 폴더 중복 스크린샷으로 예상 밖의 동작 4가지를 제보.

**증상 1 (당근서버 라벨)**: 대시캠 탭에서 로그 전송(1세그먼트/10.8MB, 5세그먼트/51.5MB) 다이얼로그에 "당근서버"라는 라벨이 표시됨. 사용자 확인: 실제 전송을 누르면 Drive로 정상 전송됨(기능은 정상, 표시만 오류).

**원인 1**: `web/src/features/logs/dashcam.js` `dashcamUploadConfirmHtml()`(1260~1293행) 중 targetLabel 결정 로직(1277~1279행)이 `"toss"` 케이스만 분기하고 `"gdrive"` 분기가 없어 else로 떨어져 `web_log_upload_target_carrot`("당근서버")를 반환함. `web/js/translations/ko.js` 580~582행에 `web_log_upload_target_carrot`/`_toss`/`_gdrive` 세 키가 모두 이미 정의돼 있어(578~582행), gdrive 분기 추가만으로 해결 가능. en.js에도 대응 키 존재 확인(다국어 영향 없음).

**증상 2 (화면녹화 탭에 선택/전송 버튼 없음)**: 사용자가 화면녹화 탭 화면을 보고 직접 확인, "화면녹화 화면에서는 선택과 전송 버튼이 없음"이라고 제보.

**원인 2**: `web/src/features/logs/screenrecord.js`(영상 목록, 285줄 전체)와 `screenshots.js`(사진 스트립, 107줄 전체)를 각각 전체 검토한 결과 selection state, 체크박스 마크업, 업로드 호출이 코드에 전혀 존재하지 않음(재생/다운로드 관련 액션만 `data-action="play-screenrecord"`, `data-action="download-screenrecord"`, `data-action="view-screenshot"`). `server/features/screenrecord/routes.py`도 `register()`에 등록된 엔드포인트가 videos/thumbnail/video/download/photos/photo류의 조회·다운로드뿐, 업로드 엔드포인트 없음. 즉 버그가 아니라 애초에 미구현.

**증상 3 (화면녹화 탭에서 햄버거 메뉴로 "전송"을 눌렀는데 대시캠 로그가 감)**: 사용자가 화면녹화 탭에서 상단 우측 햄버거(줄 3개) 버튼을 누르면 전송 메뉴가 뜬다고 제보. 그런데 실제 전송된 내용은 이미지1·2에서 확인된 것처럼 qcamera/rlog(대시캠 세그먼트 구성 파일)였음 -- 화면녹화 영상 파일이 아님.

**원인 3**: `runtime.js`의 `logsMenuButton`/`openLogsMenu()`/`logsMenuChoices()`(112~178행)는 대시캠/화면녹화 탭이 아니라 로그 페이지 전체에 걸쳐 있는 전역 버튼이며, 탭 상태를 전혀 참조하지 않음. 메뉴의 "최근 로그 업로드(2/5/10)" 항목은 `LOGS_MENU_UPLOAD` 액션으로 `dashcam.js`의 `uploadRecentDashcamSegments(count)`(1770~1787행)를 호출하고, 이 함수는 `/api/dashcam/recent`로 대시캠 세그먼트만 가져와 `uploadDashcamSegments()`로 넘김 -- 화면녹화 탭에서 열었는지 여부와 무관하게 항상 대시캠 로그만 업로드함. 사용자가 화면녹화 탭에서 이 메뉴로 "전송"한 것이 실제로는 최근 대시캠 로그 업로드였던 것으로 설명됨.

**증상 4 (Drive에 "CarrotWeb Logs" 폴더 2개 생성)**: 사용자가 Google Drive "내 드라이브"에서 동일한 이름의 폴더가 2개 생성된 것을 스크린샷으로 확인.

**원인 4 (추정, 미확정)**: `gdrive_upload.py`의 `_ensure_folder()`(294~331행)는 이름으로 Drive에 질의해 있으면 재사용, 없으면 생성하며, 결과를 인메모리 `_folder_verified_cache`에 300초간만 캐싱함(298~301행). 증상 1(대시캠 탭 개별/그룹 전송)과 증상 3(햄버거 메뉴 "최근 로그 업로드")이 서로 다른 시점에 각각 이 함수를 호출했을 것으로 보이며, (a) 두 호출 사이 300초 이상 간격이 있었거나 (b) Drive Files.list API가 방금 생성된 폴더를 검색 결과에 즉시 반영하지 못하는 잘 알려진 지연(eventual consistency)에 걸렸을 가능성이 유력함. 다만 코드 조사만으로는 실제 호출 시각을 알 수 없어 확정 불가 -- 우선순위 낮음으로 이월(기능 동작 자체에는 지장 없고, 사용자가 Drive에서 폴더 하나를 수동 정리 가능).

**사용자 확정 스펙 (다음 세션 최우선 작업)**: 화면녹화 탭에 (1) 영상목록을 실제로 노출하고, (2) 각 항목 파일명(저장시간 포함) 앞 체크박스 + 뒤 다운로드/전송 버튼, (3) 목록 상단 전체선택 버튼 + 다운로드/전송 버튼을 신규 구현. `dashcam.js`의 기존 선택 UI/업로드 확인 다이얼로그 패턴을 그대로 재사용하는 방향으로 설계할 것(증상 1의 targetLabel 버그도 이 참에 함께 수정 권장). 백엔드에는 화면녹화 업로드 엔드포인트가 없으므로 `gdrive_upload.py`의 `upload_file_resumable()`을 재사용해 신규 추가 필요.

**교훈**: 32차 이후 처음으로 실기기 검증 결과가 들어왔는데, 정적 코드 리뷰만으로 예측했던 것과 달리 UI 요소(햄버거 메뉴)가 탭 경계를 넘어 다른 데이터를 조작하는 설계상 허점이 실사용 중 자연스럽게 드러남. 향후 유사한 "탭별 격리"가 필요한 UI를 검토할 때는 전역 컨트롤(페이지 상단 고정 버튼 등)이 실제로 활성 탭을 인지하는지 별도로 확인할 것.
## 2026-09-15 (34차) -- 세션 시작 시 확인한 회차(32차)와 실제 최신 회차(33차) 사이 불일치 재확인

**증상**: 세션 시작 시 4절 절차로 HANDOFF/CURRENT_STATUS를 조회했을 때는 32차(c704371a)까지만 반영된 상태였으나, 사용자가 실제 실행한 push 로그(`789667f7..9fdefb3d`)를 보니 부모 커밋이 `789667f7`로, 그 사이 다른 경로에서 33차(ko.js 문구 수정)가 이미 진행되어 있었음.

**원인**: 사용자가 반영 스크립트를 실행하는 시점까지 시간차가 있고, 그 사이 다른 세션/경로에서 병행 작업이 있었던 것으로 추정. 스크립트 자체는 실행 시점에 항상 최신 브랜치를 clone하므로(6절), 코드 자체는 최신 위에 정상적으로 쌓였고 충돌도 없었음 -- 다만 Claude가 작업 도중 사용하던 세션 번호 라벨(`[33차]`, 코드 주석/커밋 메시지)이 실제 순서와 어긋나게 됨.

**영향**: 코드 로직/반영 자체에는 문제 없음(정상적으로 33차 위에 34차 커밋이 쌓임). devnotes 회차 번호 표기만 실제 순서(34차)로 바로잡아 기록. 이미 커밋된 코드 주석의 `[33차]` 표기는 과거 기록이므로 임의로 재작성하지 않음(18절 원칙과 동일하게 취급).

**교훈**: Base Commit 원칙(6절)에서 "스크립트 작성과 실행 사이 시간차 동안 다른 경로로 파일이 바뀔 수 있다"고 이미 경고하고 있던 상황이 실제로 재현됨. 코드 파일처럼 내용이 겹치는 변경뿐 아니라, devnotes 회차 번호 같은 "순서" 자체도 이 시간차의 영향을 받을 수 있음이 확인됨. 반영 완료 로그를 받으면, 커밋 해시 앞부분(`OLD..NEW`)의 OLD가 세션 시작 시 확인했던 HEAD와 다를 경우 그 사이 무엇이 반영됐는지 먼저 확인하는 절차를 권장.
## 2026-09-15 (33차) -- raw.githubusercontent.com이 쿼리스트링 캐시버스터를 무시하고 이전 내용을 반환하는 현상 관찰

**증상**: 33차 ko.js 수정 커밋(`789667f7`)이 GitHub에 정상 push된 것을 `git push` 로그와 `github.com/.../commit/<sha>.diff`로 확인했음에도, 같은 파일을 `raw.githubusercontent.com/.../carrot-ryu/.../ko.js?nocache=<timestamp>` 형태로 재조회하면 한동안 여전히 수정 전 텍스트("데스크톱 앱 유형")가 반환됨.

**추정 원인**: `raw.githubusercontent.com`은 Fastly CDN을 경유하며, 커밋 반영 직후 일정 시간 동안 이전 응답을 계속 서빙하는 것으로 보임. 20차·22차 세션에서도 유사하게 "이전 버전이 캐시되어 있었다"는 사례가 있었으나, 이번엔 `nocache` 쿼리스트링을 붙였음에도 재현됨 -- 즉 쿼리스트링 캐시버스터가 이 CDN에는 효과가 없거나 제한적임을 시사.

**임시 대응(이번 세션)**: `github.com/<owner>/<repo>/commit/<sha>.diff` 엔드포인트(git 커밋 자체를 직접 반영하므로 캐시 지연이 없는 것으로 관찰됨)로 교차 검증해 실제 반영을 확정함. `api.github.com` contents API도 대안이 될 수 있으나 이번 세션 중 비인증 rate limit(60/시간)에 걸려 사용 불가했음.

**제안(19절 절차 대상, 아직 미승인)**: 16절/20절의 "raw.githubusercontent.com 재조회로 확인" 절차에 "즉시 재조회 시 캐시로 이전 내용이 보일 수 있으므로, 그 경우 `github.com/.../commit/<sha>.diff`로 교차 검증 후 판단할 것 -- 캐시된 이전 내용만 보고 곧바로 '미반영'으로 단정하지 않는다"는 단서 추가를 다음 세션에 사용자에게 제안할 수 있음. 이번 세션에서는 코드 변경이 아니므로 제안만 기록하고 문서 자체는 수정하지 않음.
## 2026-09-15 (32차) -- drive.file 스코프 + 폴더 자동생성 복귀로 31차 근본 원인(핵심 발견 19) 우회 반영

**배경**: 31차(핵심 발견 19)에서 Google Device Authorization Grant가 전체 drive 스코프를 정책적으로 차단한다는 근본 원인이 확인되어, 사용자에게 3가지 대안(① drive.file+폴더자동생성 복귀, ② Authorization Code Flow 전면 재설계, ③ Drive 대체)을 제시하고 결정을 기다리는 상태로 세션이 종료됨.

**진행**: 커밋 `c704371a`(메시지에 `31cha device-flow block fix`로 명시)로 대안 ①이 선택·반영됨을 이번 세션에서 GitHub 커밋 로그/diff 직접 조회로 확인함. `gdrive_upload.py`의 스코프를 `drive` -> `drive.file`로 좁히고, 고정 `DRIVE_FOLDER_ID` 접근 방식을 c3-ms-dev 원본과 동일한 "이름으로 폴더 검색, 없으면 자동생성"(`_ensure_folder`) 방식으로 되돌림.

**미해결/주의**:
1. 이 변경 자체가 실제로 device flow에서 정상 동작하는지(31차에서 겪은 `Invalid device flow scope` 에러가 실제로 사라지는지)는 아직 실기기로 검증되지 않음 -- drive.file 스코프가 device flow에서 허용된다는 것은 외부 사례 기반 추정이었지 이 프로젝트에서 직접 확인된 사실은 아님(31차 FINDINGS 단서 참고).
2. 기존에 사용자가 미리 만들어둔 폴더(구 DRIVE_FOLDER_ID)는 더 이상 쓰이지 않고, 앱이 "CarrotWeb Logs"라는 새 폴더를 자동으로 만들게 되므로, 기존 폴더에 쌓여있던 파일과 새 폴더가 분리됨(필요시 사용자가 수동으로 옮겨야 함 -- devnotes에는 이 이관에 대한 언급이나 조치가 없음, 다음 세션에서 사용자에게 안내 필요).
3. 이번 커밋에 대한 세션별 WIP/HANDOFF 기록이 남아있지 않아, 실제로 어떤 경로(세션/스크립트/직접 웹 편집)로 이 커밋이 만들어졌는지는 devnotes만으로는 알 수 없음 -- 다음에 유사한 "기록 없는 반영"이 발견되면 16절 원칙대로 우선 GitHub 실제 상태를 기준으로 진행.
## 2026-09-15 (31차) -- Google Drive 연동(15차~) 설계가 Device Authorization Grant의 스코프 제약과 근본적으로 충돌함

**증상**: 실기기에서 "웹 설정 > 로그 업로드" 화면의 Google Drive 연결(Device Authorization Grant, gdrive_upload.py)이 클라이언트 ID/보안 비밀번호를 올바르게 입력하고 클라이언트 유형(TV 및 제한된 입력이 있는 기기)과 동의 화면 스코프 등록까지 정상인 상태에서도 "Invalid device flow scope: https://www.googleapis.com/auth/drive" 에러로 항상 실패함.

**조사 경과**: (1) 클라이언트 ID 형식 문제 -> 배제(재입력 후에도 동일), (2) UI 안내 문구(ko.js)가 요구 클라이언트 유형("데스크톱 앱 유형")을 실제 요구사항("TV 및 제한된 입력이 있는 기기")과 다르게 안내하는 버그 발견했으나 -> 사용자가 이미 올바른 유형으로 발급받아 적용했다고 확인되어 배제, (3) 동의 화면 스코프 미등록 -> 사용자 확인으로 배제.

**확정 원인**: 코드 조사가 아닌 외부 사례 조사로 확인됨 -- Google은 OAuth 2.0 Device Authorization Grant(RFC 8628, "TV 및 제한된 입력이 있는 기기" 흐름)에서 전체 Google Drive 스코프(https://www.googleapis.com/auth/drive)의 사용을 수년 전부터 정책적으로 차단하고 있음. 이는 클라이언트 유형/동의 화면 설정과 무관하게 Google 인증서버 단에서 스코프 자체를 거부하는 것으로, 사용자 측 설정으로는 우회 불가능함. (Calendar 등 다른 API 스코프는 동일 device flow에서 정상 동작하는 것으로 보아, Drive 전체 스코프 특유의 제약으로 판단. 다만 Google 공식 문서에서 이 제약을 명시적으로 문서화한 출처는 못 찾았고, 다수의 독립적인 개발자 보고 사례로 확인한 것임 -- 완전히 공식적으로 확정된 사실은 아니라는 점은 유의.)

**설계 충돌**: gdrive_upload.py(15차)는 c3-ms-dev 원본의 drive.file(비민감) 스코프 + _ensure_folder()(폴더 자동 생성) 방식을, "이미 만들어둔 고정 폴더(DRIVE_FOLDER_ID)에 ID로 바로 접근"하기 위해 의도적으로 전체 drive 스코프 + _verify_folder()(존재 확인만) 방식으로 변경했음(코드 주석에 사유 명시). 이 변경이 이번에 확인된 Google의 device flow 스코프 제약과 정면으로 충돌하는 조합이었던 것으로 보이며, 15차 시점에는 이 제약이 검증되지 않은 채 설계에 반영된 것으로 추정됨.

**미해결(다음 세션 결정 필요)**: 사용자에게 3가지 대안 제시함 --
1. drive.file 스코프 + 폴더 자동 생성 방식(c3-ms-dev 원본)으로 복귀. Device flow 유지 가능성 높으나 실제 검증 안 됨. 기존에 미리 만들어둔 폴더 재사용 불가(앱이 새 폴더를 만들게 됨).
2. Device flow를 버리고 표준 Authorization Code Flow(콤마 기기 자체 웹서버가 redirect URI를 로컬 네트워크로 수신하는 구조)로 전면 재설계 -- 작업량 큼, LAN IP/포트 고정 문제 등 새 이슈 예상.
3. Google Drive 자체를 다른 저장 수단으로 대체.
사용자 결정 대기 중.

**부가 발견(별도 수정 필요, 이번 세션 미수정)**: web/js/translations/ko.js의 web_gdrive_client_id_desc 문구가 "Google Cloud OAuth 클라이언트 ID (데스크톱 앱 유형)"으로 돼 있으나, 실제 필요한 유형은 "TV 및 제한된 입력이 있는 기기"임(gdrive_upload.py 주석과 불일치). 이번 에러의 직접 원인은 아니었으나(사용자가 이미 올바른 유형으로 발급받음), 다른 사용자/향후 재시도 시 혼란을 줄 수 있는 명백한 버그이므로 다음 세션에서 문구 수정 필요.

## 2026-09-15 (30차) — HANDOFF.md 미반영 기록과 실제 GitHub 상태 불일치

**증상**: 29차 세션이 작성한 HANDOFF.md에는 "사용자가 코드 반영 스크립트를 아직 실행하지 않음 — 실행 전까지 이 레이아웃 변경은 GitHub에 반영된 것이 아님"이라고 명시돼 있었음. 그런데 30차 세션 시작 시 4절 절차(0~3번)를 따라 carrot-ryu 최신 커밋을 직접 조회한 결과, 29차 커밋(67a8e10)뿐 아니라 그 이후의 30차 커밋(34bb41bc)까지 이미 GitHub에 push돼 있는 상태였음. CURRENT_STATUS.md 역시 27차(5f5e49d0) 기준에서 갱신되지 않은 채 남아 있었음.

**원인 추정**: 29차 세션이 스크립트 전달까지만 하고 세션이 종료된 뒤, 사용자가 실제로 스크립트를 실행해 반영을 완료했으나, 그 반영 사실이 별도로 devnotes(HANDOFF/CURRENT_STATUS)에 기록되지 않은 채 다음 세션이 곧바로 이어서 코드를 추가로 수정(30차 커밋)한 것으로 보임 — 즉 "코드 반영"과 "devnotes 갱신"이 서로 다른 시점/세션에 이루어지면서 devnotes 갱신이 누락된 채 다음 작업이 진행된 사례.

**핵심 발견 13(24차)과의 관계**: 24차에서 이미 "devnotes 기록 누락"과 "실제 미반영" 두 상태를 구분해야 한다는 원칙이 문서화됐으나, 이번 사례는 그와 유사하되 조금 다른 변종 — devnotes가 "미반영"이라고 잘못 기록한 상태에서, 실제로는 반영이 됐을 뿐 아니라 그 위에 한 세션치 작업(30차)이 이미 더 진행돼 있던 경우. 단순히 "반영 여부"만 확인해서는 부족하고, HEAD 자체가 devnotes에 기록된 것보다 더 앞서 있을 수 있다는 점까지 확인해야 함을 보여줌.

**재발 방지**: 이미 문서화된 4절 0~3번 절차(이 지침 문서 → HANDOFF.md → CURRENT_STATUS.md → carrot-ryu 최신 commit 확인)를 매 세션 빠짐없이 순서대로 밟는 것 자체가 재발 방지책 — 특히 3번(carrot-ryu 최신 commit 확인)을 건너뛰지 않는 것이 이번처럼 devnotes 기록과 실제 GitHub 상태가 어긋난 경우를 조기에 잡아낼 수 있는 유일한 방법. 이번 건은 기존 규칙을 정상적으로 따른 결과(30차 세션이 3번 단계를 밟아 스스로 발견함) 조기에 잡힌 사례이므로, 별도의 새 규칙 추가는 필요 없다고 판단함(19절 절차 대상 아님).

## 2026-09-14 (26차) — Google Drive 연결 UI 미노출: 정적 코드 리뷰와 실기기 스크린샷이 모순됨(원인 미확정)

**증상**: 실기기 "웹 설정 > 로그 업로드"에서 업로드 서버를 "구글 드라이브"로 선택해도 Client ID/Secret 입력란(web-gdrive-connect 컴포넌트, 23차 추가)이 보이지 않고, 대신 "당근서버 주소"/"토스서버 주소" 입력란(web-upload 컴포넌트의 carrot/toss 전용 필드)이 계속 보임.

**정적 코드 리뷰 결과(carrot-ryu HEAD d338afb7 기준)**:
- schema.js의 log_upload 그룹에 web-upload / web-gdrive-connect 두 항목 모두 정상 등록.
- components.js의 web-gdrive-connect는 isVisible을 별도 정의하지 않아, WebSettingsComponents.isVisible()의 기본 폴백 로직 `(component.settingKeys || []).every(...)` 가 적용됨. settingKeys가 undefined이므로 빈 배열의 every()는 항상 true -> 이 컴포넌트는 이론상 항상 visible이어야 함.
- web-upload 컴포넌트 내부의 "당근서버 주소"/"토스서버 주소" 필드는 각각 `target === "carrot"` / `target === "toss"` 일 때만 hidden 속성이 풀리도록 구현돼 있음. 즉 target이 "gdrive"이면 이 두 필드는 코드상 반드시 숨겨져야 함.
- web/js/generated/tools.js(배포용 esbuild 번들)를 소스와 직접 대조한 결과, 위 로직이 토씨 하나 다르지 않게 동일하게 반영돼 있었음(문자열 치환/축약 없이 로직 그대로 minify됨). web/css/generated/tools.css에도 .web-gdrive-settings 관련 셀렉터가 전부 포함, 숨김 규칙 없음.

**모순**: 실기기 스크린샷은 "구글 드라이브"가 선택된 상태에서 (a) carrot/toss 필드가 보이고 (b) gdrive 전용 필드가 안 보이는, 코드와 정반대의 상태를 보여줌. 즉 정적 코드 리뷰만으로는 원인을 찾지 못함.

**가설(미검증)**:
1. 실기기 브라우저가 최신 tools.js/tools.css를 서빙받지 못하고 캐시된 구버전을 쓰고 있을 가능성 (Samsung Browser 캐시)
2. scons 빌드 과정에서 이번 코드 변경분에 대해 esbuild 번들 재생성이 실제로는 안 됐을 가능성 (과거 devnotes에 기록된 것과 유사한 유형의 문제)
3. (낮은 가능성) 서버 쪽이 별도의 오래된 정적 파일 경로를 서빙하고 있을 가능성

**검증 방법(다음 세션에서 실기기로 수행 필요)**:
- 콤마 기기 터미널 탭에서 실제 서빙되는 tools.js 파일 내용에 "web-gdrive-connect" 문자열이 존재하는지 직접 grep
- 브라우저 강제 새로고침(캐시 무시) 또는 시크릿 모드로 재접속해 동일 현상 재현 여부 확인
- (선택) tools.js 파일의 수정시각/해시가 carrot-ryu HEAD(d338afb7) 반영 이후인지 확인

**부가 발견(코드 위치 미조사)**: 화면녹화 탭의 세그먼트 "전송" 다이얼로그가 업로드 서버를 "구글 드라이브"로 선택한 상태에서도 라벨을 "당근서버"로 표시함. 실제 업로드는 gdrive로 라우팅되는 것으로 보이나(최종적으로 "Google Drive가 연결되어 있지 않습니다" 에러 발생) 라벨 텍스트가 하드코딩됐을 가능성. 다음 세션에서 조사 필요.

## [2026-09-14] web_upload.py/dashcam upload.py 데드코드 및 test_web_upload.py 낡은 테스트 의심 (25차)

### 배경
- LOG_UPLOAD_TARGETS "gdrive" 누락 버그(24차 계속2 발견) 수정을 진행하면서, 사용자가 "관련 죽은 코드도 같이 삭제"를 요청해 조사함.

### 조사 1: 처음 보고를 정정 -- web_upload.py의 UPLOAD_TARGETS/selected_upload_settings()는 살아있는 코드
- `web_upload.py`: `UPLOAD_TARGETS = {"carrot", "toss"}`, `selected_upload_settings()`는 "gdrive"를 모르고 무조건 "carrot"으로 되돌리는 것은 맞으나, 이 함수는 `carrot_man.py`의 `_tmux_toss_only()`(958줄 `send_tmux_carrot_logs`, 1054줄 `send_tmux_discord`에서 호출)가 실제로 사용 중. `_tmux_toss_only()`는 "target이 toss인지"만 판별하는데, "gdrive"가 "carrot"으로 잘못 되돌려져도 결과적으로 "toss가 아니다"는 결론은 동일해 현재 시점 실사용 동작 버그는 없음. 하지만 함수 자체는 삭제 대상이 아님.

### 조사 2: 진짜 죽은 코드 3개 확인 (프로덕션 호출자 없음, grep으로 저장소 전체 재확인)
- `web_upload.py`의 `tmux_web_target()`: `send_tmux_web()`이 17차에 Google Drive 직접 업로드로 재작성되면서 더 이상 호출하지 않음. 현재 `server/tests/test_web_upload.py`에서만 참조(489, 503, 508, 514번째 줄).
- `server/features/dashcam/upload.py`의 `resolve_upload_target()`, `upload_target_settings()`: 같은 파일 안에서도, 다른 어떤 파일에서도 프로덕션 코드가 호출하지 않음. `server/tests/test_web_upload.py`에서 `resolve_upload_target`을 최소 6곳(397, 467, 702, 747, 767, 786번째 줄)에서 monkeypatch로만 참조.
- 이 3개 함수를 지우면 `web_upload.py`의 `os` 관련 상수(DEFAULT_TMUX_WEB_UPLOAD_URL)와 `dashcam/upload.py`의 `selected_upload_settings`/`read_web_settings` import 2개도 함께 미사용이 되어 정리 대상.

### 조사 3: test_web_upload.py 자체가 16차 전환 이전 기준으로 낡아있을 가능성 (미확정, 실행 검증 못함)
- `resolve_upload_target`을 monkeypatch하는 테스트 중 397번째 줄 부근의 `test_dashcam_upload_completion_notifies_web_server_and_discord`가 `upload_jobs.upload_folder_to_web`, `upload_jobs.send_web_upload_complete`도 함께 monkeypatch함.
- 그런데 `upload_jobs.py`를 직접 확인한 결과 이 두 함수는 더 이상 존재하지 않음 -- 16차에서 세그먼트 업로드를 "세그먼트/파일별 개별 HTTP 업로드"에서 "선택된 세그먼트를 zip으로 묶어 `gdrive_upload.upload_file_resumable()`로 단일 업로드"로 전면 재작성하면서 제거된 것으로 보임(`upload_jobs.py`의 `run_upload_segments()` 함수 docstring에 "기존에는... upload_folder_to_web... 통지했다"라고 과거형으로 명시되어 있음).
- `monkeypatch.setattr(obj, name, value)`은 기본적으로 `obj`에 `name` 속성이 실존해야 성립하므로(그렇지 않으면 AttributeError), 이 테스트는 16차 이후 실행하면 이미 실패했을 가능성이 높음. 다만 이번 세션에서는 pytest를 실제로 돌려보지 못해(openpilot 전체 런타임 의존성 없이 이 테스트 파일만 단독 실행이 어려움) 확정하지 못함 -- "가능성 높음"으로만 기록.
- 이 발견이 사실이라면, `resolve_upload_target` 등 3개 함수를 단순 삭제하는 작업이 "16차 전환 이후 갱신되지 않고 방치된 테스트 뭉치 전체 정리"로 범위가 커질 수 있음.

### 결론 및 다음 조치 (사용자 결정, 미착수)
- 사용자와 협의 결과, 이번 세션은 확실한 버그(LOG_UPLOAD_TARGETS)만 수정하고, 데드코드 3개 삭제 + test_web_upload.py 정리는 다음 세션으로 이월하기로 결정.
- 다음 세션 시작 시 권장 순서: (1) test_web_upload.py를 실제로 실행해(또는 최소한 관련 픽스처/모듈 임포트만이라도) 몇 개 테스트가 실제로 깨져 있는지 먼저 정량적으로 확인 -> (2) 16차 이후 낡아진 테스트 목록 확정 -> (3) 데드코드 3개 삭제 + 대응 테스트 삭제/갱신을 한 번에 진행.

## [2026-09-14] Google Drive 연결 UI Client ID/Secret 입력란 미노출 문제 조사 (24차 계속2)

### 배경
- 23차(commit 272834b8)에서 web_settings에 Google Drive 연결 UI(web-gdrive-connect 컴포넌트)를 추가했으나, 사용자 실기기에서 "업로드 서버" 드롭다운은 "구글 드라이브"로 바뀌는데 그 아래 Client ID/Secret 입력란과 연결 버튼이 보이지 않는다고 보고됨(WIP.md 23~24차 참고).

### 조사 1: 캐싱 가설 기각
- server/features/static.py를 확인한 결과, index.html은 매 요청마다 Cache-Control: no-cache, no-store, must-revalidate로 서빙되고, 정적 자산(js/css)의 src/href는 요청마다 실제 파일 콘텐츠 해시(?v=<sha256>)로 재작성됨(_rewrite_index_asset_urls/_fingerprinted_asset_url). 브라우저 캐시가 낡은 번들을 계속 쓸 수 있는 구조가 아니며, 서비스 워커도 존재하지 않음(grep 결과 없음). 캐싱 가설은 기각.

### 조사 2: 렌더링 로직 자체는 정상 (Node.js 시뮬레이션으로 검증)
- schema.js: log_upload 그룹에 web_upload, web_gdrive_connect 두 항목이 정상 등록되어 있음(commit 272834b8 diff로 확인).
- components.js: "web-gdrive-connect" 컴포넌트는 settingKeys가 비어 있어 isVisible이 항상 true. 드롭다운 선택값(target)과 무관하게 항상 렌더링되는 별도 행으로 구현되어 있음(web-upload의 필드처럼 target별 조건부 hidden이 아님).
- 실제 소스 파일(schema.js/state.js/components.js/render.js)을 그대로 Node.js 환경에 복사해 renderWebSettingsDialogHtml()을 직접 실행한 결과:
  - "web-gdrive-settings" 포함: true
  - "web-upload-settings" 포함: true
  - data-gdrive-field="client_id" input 포함: true
  → 렌더링 함수 자체는 Client ID/Secret 입력란을 포함한 HTML을 정상적으로 생성함. 컴포넌트 등록/가시성 로직에는 문제가 없음이 실증됨.

### 조사 3: 발견한 확실한 버그 -- 백엔드가 "gdrive"를 유효한 값으로 모름
- server/services/web_settings.py: `LOG_UPLOAD_TARGETS = {"carrot", "toss"}` (20번째 줄), `_Field("log_upload_target", "enum", "carrot", choices=LOG_UPLOAD_TARGETS)`.
- 23차에서 프론트엔드 드롭다운에 value="gdrive" 옵션을 추가했으나, 백엔드 enum choices 목록은 갱신되지 않음.
- 영향: 사용자가 "구글 드라이브"를 선택해 저장을 시도하면, 백엔드가 "gdrive"를 무효한 enum 값으로 취급해 저장을 거부하거나 기본값("carrot")으로 되돌릴 가능성이 높음(state.js의 normalizeWebSettingValue도 동일하게 WEB_SPEC_BY_KEY의 choices를 기준으로 판단하므로 프론트엔드에서도 같은 문제가 재현됨). 이는 web-gdrive-connect 행의 렌더링과는 무관한 별개의 확실한 버그.
- 수정 방향(미적용, 사용자 승인 대기): LOG_UPLOAD_TARGETS에 "gdrive" 추가.

### 결론 및 남은 가설 (미확정)
- "Client ID/Secret 입력란이 안 보인다"는 증상은 코드 레벨 렌더링 버그로는 재현되지 않음.
- .web-settings-group__body{overflow:auto}로 스크롤 가능한 구조이므로, 실기기 화면에서 "업로드 서버" 드롭다운 아래로 스크롤하지 않아 못 봤을 가능성이 유력한 가설로 남음(미검증 -- 실기기에서 스크롤 확인 필요).
- LOG_UPLOAD_TARGETS 버그는 별개로 반드시 수정이 필요하며, 사용자 승인 후 반영 예정.

## [2026-09-14] Google Drive 연동 파라미터 미등록으로 인한 UnknownKeyName 실패 (22차)

### 배경
- HANDOFF 다음 작업 후보 "PARAMS_REGISTRY.md 파라미터 3종 등록"을 진행하기 위해 gdrive_upload.py(15~20차에 걸쳐 작성)의 실제 파라미터 이름을 GitHub에서 직접 조회함.

### 원인
- gdrive_upload.py는 PARAM_CLIENT_ID="CarrotGDriveClientId", PARAM_CLIENT_SECRET="CarrotGDriveClientSecret", PARAM_REFRESH_TOKEN="CarrotGDriveRefreshToken" 3개 Params 키를 사용.
- openpilot/common/params_keys.h에는 이 3개가 전혀 등록되어 있지 않았음(다른 모든 Carrot* 파라미터는 예외 없이 이 파일에 등록되어 있음, {PERSISTENT, ...} 형태).
- openpilot/common/params_pyx.pyx의 get()/put()은 호출 시 check_key()를 거치며, params_keys.h에 없는 키면 UnknownKeyName 예외를 던짐(101-102줄).
- gdrive_upload.py의 api_gdrive_device()(Drive 연결 시작 API, "연결" 버튼이 호출)는 client_id/secret을 저장하는 첫 단계(_params().put(PARAM_CLIENT_ID, client_id))에서 이 예외를 try/except로 받아 HTTP 500을 반환하도록 되어 있음. 즉 사용자가 로그탭 설정에서 "연결"을 눌러 client_id를 입력하는 순간부터 항상 실패하는 상태였음.
- api_gdrive_callback()(디바이스 코드 인증 완료 후 refresh_token 저장)도 동일하게 _params().put(PARAM_REFRESH_TOKEN, refresh_token)에서 실패하도록 되어 있어, 설령 앞 단계를 우회하더라도 최종 인증 완료 단계에서도 실패했을 것으로 추정.
- 15차부터 20차까지 6개 세션에 걸쳐 만들어진 Drive 연동 기능이 실제 기기 연결 테스트를 한 번도 거치지 않아(devnotes에 이미 "실차 검증 미실시"로 기록되어 있었음) 이 버그가 드러나지 않고 있었음.

### 적용한 수정
- openpilot/common/params_keys.h에 다른 Carrot* 파라미터와 동일한 패턴으로 3줄 추가:
  {"CarrotGDriveClientId", {PERSISTENT, STRING}},
  {"CarrotGDriveClientSecret", {PERSISTENT, STRING}},
  {"CarrotGDriveRefreshToken", {PERSISTENT, STRING}},
- 위치: 기존 CarrotExceptionDiscordWebhookUrl 줄과 CwebPushRecoveryBoot 줄 사이.
- carrot-ryu commit 48c2e081.

### 검증
- 문자열 블록 치환 스크립트 실행 로그: git commit/push 정상 완료 확인.
- raw.githubusercontent.com으로 commit 48c2e081 시점의 params_keys.h를 직접 재조회하여 3줄이 의도한 위치에 정확히 들어간 것을 확인(정적 검증 완료).
- ⚠ 미검증: 실제 Google Cloud Console에서 OAuth 클라이언트를 발급하고 콤마 기기에서 "연결"을 눌러 device flow 전체(디바이스 코드 발급 -> 사용자 인증 -> refresh_token 저장 -> 실제 업로드)가 끝까지 동작하는지는 여전히 미실시. params_keys.h 수정으로 최소한 "저장 시 예외 발생" 문제는 해소되었으나, 그 외 OAuth 흐름 자체(스코프, 리다이렉트 등)의 정합성은 정적 분석 수준으로만 확인됨.## [2026-09-13] 온로드 좌측 상단 시계 좌측 화면 경계 잘림 버그 원인규명 및 수정 (13차)

### 배경
- 사용자가 실제 화면 사진을 공유. 좌측 상단 시계가 "23:32:34" 대신
  "3:32:34"로 표시되어 맨 앞 "2"가 잘려 보임을 보고

### 원인
- openpilot/selfdrive/ui/onroad/hud_renderer.py `_draw_date_time()`:
  시계 텍스트(HH:MM:SS, 8자, font_size=100)를 align="center_bottom"으로
  그리며 고정 x=rect.x+170을 기준으로 삼음
- text_draw.py `get_text_draw_pos()`: center_bottom 정렬은
  draw_x = x - 텍스트폭*0.5로 계산 -> 8자 텍스트의 절반 폭이 170px을
  넘어 draw_x가 음수(화면 좌측 밖)가 됨
- 12차에서 시계 표시가 %H:%M(5자)에서 %H:%M:%S(8자)로 늘어나며 발생한
  회귀로 추정 (5자일 때는 절반 폭이 170px보다 작아 문제가 드러나지 않았을
  가능성)

### 적용한 수정
- measure_text_cached로 시계 텍스트 실측 폭을 구해, 왼쪽 여백
  (UI_CONFIG.border_size)을 보장하도록 x를 max(기존x, 최소x)로 보정
- _draw_date_time() 한 곳만 수정, 다른 로직/파일은 건드리지 않음
- 검증: git apply --check 통과, py_compile 통과(Claude 샌드박스).
  실차 검증은 미실시

## [2026-09-13] route 감속 오검출 근본수정 적용 — carrot_navi_route()에 3-샘플 median 스파이크 필터 (8차 발견에 대한 조치, carrot-ryu commit 2dbe492)

### 배경
- 8차 세션에서 실주행 로그(route 000003fb--8470375f65--21)로 확인한 route 커브 감속
  오검출(고속도로 분기점 조기 과감속 후 원복)에 대해, 사용자가 대응 방향으로
  "②근본수정(스파이크 제거 필터 추가)"을 선택.

### 적용한 수정
- 파일: openpilot/selfdrive/carrot/carrot_man.py, carrot_navi_route() 함수
- 기존: 3점(약 40m 간격) 곡률을 계산하자마자 바로 그 곡률값으로 목표속도(speed)를
  산출 → 폴리라인 노이즈로 곡률이 한 지점에서만 튀어도 그대로 급감속 목표로 반영됨.
- 변경: 곡률(curvature) 계산을 먼저 전부 끝낸 뒤, 그 리스트에 3-샘플 슬라이딩
  median 필터를 적용하고, 그 필터링된 곡률로만 목표속도를 산출하도록 구조 변경.
  같은 아이디어가 이미 비전 커브 쪽(curve_speed.py의 curve_speed() 함수, 
  "A three-node median rejects isolated yaw spikes" 주석 부분)에 적용되어 있어
  이를 route 쪽에도 동일하게 적용한 것.
- 최소 변경 원칙(10절)에 따라 함수 내 한 블록(원본 13줄 → 26줄)만 교체, 다른 로직은
  건드리지 않음.

### 검증 (실차 검증 아님 — 정적/합성 검증만)
- python3 -m py_compile로 문법 검증 통과 (Claude 샌드박스 및 실제 push된 commit
  2dbe492 기준 모두 확인).
- 합성 곡률 시퀀스([0.005, 0.006, 0.005, 0.007, 0.08, 0.006, ...] 형태로 index 4에
  고의로 스파이크 삽입)로 필터 동작 검증: 단발성 스파이크(0.08)가 주변 median으로
  완전히 치환되어 사라지고, 나머지 정상 구간 값은 그대로 유지됨을 확인.
- ⚠ 8차 로그(000003fb--8470375f65--21)는 실제 route 폴리라인 좌표 자체를 갖고
  있지 않아, 이번 수정이 "그 실제 사고 구간"에서 어떻게 동작했을지 재생(replay)
  검증은 하지 못함. 즉 이 수정이 8차에서 관찰된 증상을 실제로 없애는지는 아직
  실주행으로만 확인 가능.

### 실차 검증
- 미실시. 콤마 디바이스에 이 코드가 올라가 동일/유사 구간을 재주행하기 전까지는
  "고쳐졌다"고 단정하지 않음. 다음 실주행 시 동일 분기점 통과 시 desiredSource=
  "route" 전환 시점의 desiredSpeed 급락 여부를 rlog로 재확인 필요.

## [2026-09-13] route(경로) 커브 감속 오검출 — 실주행 로그로 최초 확인 (고속도로 분기점 조기 과감속 후 원복)

### 배경
- 사용자가 실제 콤마 디바이스로 주행 중 채증한 로그(qcamera.ts/qlog.zst/rlog.zst, route
  000003fb--8470375f65--21) 업로드.
- 증상: 고속도로 거의 직선 구간에서 좌로 약간 굽은 분기점 접근 시, 미리감속이 과하게
  걸렸다가 다시 원복되는 느낌.

### 확인된 사실 (rlog 파싱 결과, pycapnp + carrot-wip 스키마로 직접 복호화)
- t=47.3s경 carrotMan.desiredSource가 "route"로 전환되며 desiredSpeed가 67km/h로 급락.
  이 시점 xDistToTurn(분기점까지 거리)은 아직 499m로, 실제 커브와는 거리가 먼 시점.
- 시스템이 실제로 aTarget 최대 -2.0m/s²까지 감속 명령을 걸어 vEgo가 약 12초간
  96km/h→69km/h로 실제 감소함 (carControl.actuators.accel까지 물리적으로 전달됨,
  표시용 아님).
- 운전자가 t=52.1~59.6s(약 7.5초) 동안 gasPressed=True로 가속페달 개입, 69~72km/h
  유지하며 시스템 감속에 저항.
- t=54.8~57.9s 사이 route/vturn 소스 자체가 재계산되어 desiredSpeed가 115~121km/h로
  회복됨 → 최초 67km/h 목표는 실제보다 훨씬 급한 커브로 오검출된 일시적 값이었음이
  로그상 확인됨.

### 원인 (기존 5차/5차계속 정적 분석과 연결)
- carrot_man.py의 carrot_navi_route()가 내비 폴리라인 3점(40m 간격) 곡률로
  route_speed를 산출하는데, curve_speed.py(비전 버전)에 있는 median 스파이크 제거
  필터가 없음(5차 계속 분석에서 이미 지적된 구조적 리스크).
- 고속도로 분기점 부근은 폴리라인 정점 밀도/기하가 국소적으로 흐트러지기 쉬운
  지점이라 이 3점 곡률 계산이 순간적으로 실제보다 훨씬 급한 커브로 오검출 →
  route_speed가 스파이크성으로 급락 → 차가 그 구간을 지나며 리샘플링 윈도우 이동 →
  오검출 해소 → desiredSpeed가 다시 정상 수준으로 복귀. 이게 "미리 과감속 후 원복"
  체감의 정체.
- ⚠ 이번 로그는 실제 route(경로) 폴리라인 좌표 자체를 갖고 있지 않아(carrotMan/
  carState 메시지만으로 재구성), 폴리라인 기하가 실제로 어떻게 틀어져 있었는지
  위성지도 등으로 직접 대조 확인하지는 못함. 메커니즘은 신호 패턴(거리/소스/속도
  궤적)으로 강하게 뒷받침되나 100% 확진은 아님.

### 결론
- 5차 계속 분석에서 "설계상 위험 요소로 존재한다"고 정적으로만 지적했던 route 감속
  오검출 리스크가, 이번 실주행 로그로 실제 발생을 최초로 확인함.
- 버그라기보다는 필터 부재로 인한 설계상 취약점의 실제 발현 사례.

### 대응 옵션 (미결정, 사용자 선택 필요)
1. 임시완화: TurnSpeedControlMode 2→1(비전만)로 낮춰 route 소스 비활성화
2. 근본수정: carrot_navi_route()에 median/스파이크 제거 필터 추가, 또는 프레임 간
   route_speed 하락률에 clamp 적용
3. 곡률 계산 샘플 간격(현재 40m) 확대로 노이즈 민감도 완화

### 실차 검증
- 실주행 로그(rlog) 1건으로 현상 자체는 확인됨. 다만 원인 메커니즘 중 "폴리라인 기하
  왜곡" 부분은 위성지도 등 외부 자료 대조까지는 하지 못했으므로 100% 확진은 아님.
  코드 수정/최종 조치는 아직 미실시.

### 분석 근거 파일 / 데이터
- 업로드 route: 000003fb--8470375f65--21 (qcamera.ts, qlog.zst, rlog.zst)
- 파싱 도구: pycapnp + carrot-wip(ajouatom/openpilot) cereal/log.capnp, custom.capnp 스키마
- openpilot/selfdrive/carrot/carrot_man.py (carrot_navi_route, calculate_curvature)
- openpilot/selfdrive/carrot/carrot_serv.py (update_navi, speed_n_sources)
- carrot-ryu HEAD: 02015190f58a4380a433ee0130e6374455dddc2e (변경 없음, 분석만 수행)

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

## [2026-09-12] 종방향 PID 게인(LongTuningKpV/KiV/Kf)이 현대·기아·제네시스에서 고정됨 — 설정값은 실제로 미적용

### 배경
- PARAMS_REGISTRY.md에 기록된 사용자 현재값: LongTuningKpV=100, LongTuningKiV=0, LongTuningKf=100
  (스케일 적용 시 Kp=1.0, Ki=0.0, Kf=1.0)
- "종방향 제어(가감속) 로직 분석" 요청에 따라 openpilot/selfdrive/controls/lib/longcontrol.py 확인.

### 확인된 사실
- carrot-wip 커밋 a26b108d "safety: fix Hyundai longitudinal PID gains" (2026-09-04, ajouatom)에서
  현대/기아/제네시스(opendbc brand == "hyundai") 차량은 PID 게인을 다음처럼 코드에 고정함:
  - HYUNDAI_LONGITUDINAL_KP = 1.0
  - HYUNDAI_LONGITUDINAL_KI = 0.0
  - HYUNDAI_LONGITUDINAL_KF = 1.0
- `LongControl.__init__`에서 `self.hyundai_fixed_longitudinal_tuning = CP.brand == "hyundai"`이면
  즉시 `_apply_hyundai_longitudinal_tuning()`으로 위 고정값을 self.pid에 적용.
- 주기 갱신 함수 `_refresh_longitudinal_tuning()`도 동일 분기라서, Params에 저장된
  LongTuningKpV/KiV/Kf 값을 아예 읽지 않고 무시함(Hyundai 계열 한정).
  → 즉, 콤마 디바이스 설정 화면에서 이 세 값을 바꿔도 제네시스 DH 2015 실차 제어에는 반영되지 않음.
- 같은 커밋에서 문서(docs/user/ko/cruise-gap.md, settings.md)와 UI 스키마
  (carrot/server/features·services/settings.py, carrot_settings.json)도 함께 갱신되어,
  현대·기아·제네시스에서는 이 3개 항목이 설정 화면에서 숨겨지도록 의도됨.
  → "31개 항목" → "전체 31개, 현대·기아·제네시스 28개"로 문서 수정된 것이 그 근거.
- 반면 `LongActuatorDelay`, `VEgoStopping`, `StoppingAccel`은 이 고정 로직과 무관하게
  계속 Params에서 읽어 실제로 적용됨 (longitudinal_planner.py, longcontrol.py 확인).
  - 사용자 현재값: LongActuatorDelay=20(→0.2s), VEgoStopping=5(→0.05m/s), StoppingAccel=-10(→-0.1m/s²)
  - 단, `LongControl.__init__`에는 `CP.brand=="hyundai"`이고 StoppingAccel==0.0일 때만
    -50(→-0.5)으로 강제 복원하는 별도 안전장치가 있음(e79bfd5d). 사용자 값이 -10이라 이 복원은 발동 안 함.

### 결론
- 이 동작은 버그가 아니라 carrot-wip 유지보수자가 의도적으로 반영한 안전 고정값이며,
  문서에도 명시되어 있음. carrot-ryu는 carrot-wip과 코드 동일하므로 그대로 적용됨.
- 사용자가 실제로 조절 가능한 종방향 "반응성/지연" 관련 노브는 현재
  LongActuatorDelay / VEgoStopping / StoppingAccel 뿐이며, PID 게인 자체는 조절 불가.
- 최종 액추에이터 클램프는 opendbc/car/hyundai/values.py의 CarControllerParams
  (ACCEL_MIN=-4.0, ACCEL_MAX=2.5 m/s²)로, 전 Hyundai 계열 공통이며 제네시스 전용 값은 없음.

### 실차 검증
- 미실시. 코드/문서 정적 분석 기준.

### 분석 근거 커밋
- a26b108d (2026-09-04, "safety: fix Hyundai longitudinal PID gains") — 이번 발견의 핵심 커밋
- e79bfd5d (StoppingAccel 0일 때 -0.5 복원 로직)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (2026-09-12, 변경 없음)

## [2026-09-12] DisableDM=2 의미 확인 — 운전자 모니터링 완전 OFF + Carrot Vision WebRTC 활성화

### 배경
- PARAMS_REGISTRY.md에 DisableDM=2가 기본값(0)이 아닌 채로 확인되었으나 의미 미확인 상태였음.

### 확인된 사실 (openpilot/selfdrive/carrot_settings.json 설명 문구 기준)
- descr: "1.DisableDM, 2: +EnableWebRTC, reboot required"
- 즉 값의 의미: 0=기본(DM 켜짐), 1=DM 비활성화만, 2=DM 비활성화 + Carrot Vision(WebRTC 원격 스트리밍) 활성화(재부팅 필요)

### 코드 레벨 동작 (DisableDM=1과 2 공통, DM 비활성화 부분)
- system/manager/process_config.py `enable_dm()`: `DisableDM == 0`일 때만 dmonitoringd(운전자 카메라 모니터링 프로세스) 실행
  → 1이든 2든 운전자 모니터링 프로세스 자체가 아예 뜨지 않음.
- selfdrive/selfdrived/selfdrived.py 245행: `DisableDM == 0`일 때만 졸음/주의분산 lockout, 경고(driverDistracted1~3 등) 로직 수행
  → 1/2에서는 이 안전 경고·개입 잠금 로직이 전부 스킵됨.
- selfdrive/controls/controlsd.py 426행: `DisableDM == 0`일 때만 AlertLevel.three(3단계 경고) 시 forceDecel(강제 감속) 적용
  → 1/2에서는 운전자 부주의로 인한 강제 감속도 발생하지 않음.

### DisableDM=2 전용 동작 (WebRTC)
- system/manager/process_config.py `enable_webrtc()`: `DisableDM == 2 and not ClusterHud`일 때
  carrot_vision_encoderd(도로 카메라 WebRTC 인코더) 프로세스가 활성화됨 (Carrot Vision 원격 시청 기능).
- ClusterHud==1이면(계기판 클러스터가 로드 카메라를 직접 사용 중) 충돌 방지를 위해 WebRTC는 비활성화됨.

### 결론
- 사용자의 DisableDM=2 설정은 "운전자 모니터링(졸음/주의분산 감지, 관련 경고·강제감속)을 완전히 끄고,
  대신 Carrot Vision을 통한 원격 화면 시청 기능을 켠 상태"를 의미함.
- 이는 안전과 직결되는 설정이며, 사용자가 의도적으로 설정한 것인지(예: DM 카메라 미장착/오작동, 또는
  의도적 비활성화) carrot-wip 자체의 결함은 아니고 사용자 선택의 문제임.
- carrot/server/features/intro/presets.py의 3개 기본 프리셋은 모두 `DisableDM: 0`(DM 켜짐)을 기본값으로
  두고 있어, 현재 값(2)은 사용자가 프리셋에서 벗어나 직접 변경한 상태로 보임.

### 실차 검증
- 미실시. 코드/설정 문구 기준 정적 분석. 사용자에게 이 설정이 의도된 것인지 확인 필요.

## [2026-09-12] LateralTorqueCustom=0 확인 — 저장된 LateralTorque* 값은 미적용, 실제로는 기본 튜닝 사용 중

### 배경
- PARAMS_REGISTRY.md에 LateralTorqueKf=100, Friction=30, AccelFactor=2500, KiV=10, KpV=100, Kd=0이
  기록되어 있었으나 LateralTorqueCustom=0이라 "비활성 상태로 보임"이라는 잠정 메모만 있었음.

### 확인된 사실 (openpilot/selfdrive/controls/lib/latcontrol_torque.py)
- `update()`에서 매 10프레임마다 `LateralTorqueCustom` 값을 확인:
  - `> 0`이면 저장된 LateralTorqueKpV/KiV/Kf/Kd/AccelFactor/Friction 값을 읽어 PID와 torque_params에 적용.
  - `== 0`(현재 상태)이면 이 분기를 타지 않으므로 저장된 LateralTorque* 값은 전혀 읽히지도, 적용되지도 않음.
  - (0으로 막 전환된 프레임에서 1회 한정으로 기본값 복원 로직은 있으나, 이후에는 그냥 기존 기본값 유지)
- 실제 적용되는 기본 토크 튜닝은 `CarInterfaceBase.configure_torque_tune()`
  (opendbc_repo/opendbc/car/interfaces.py)이 `opendbc/car/torque_data/params.toml`에서
  차종별 실측 계수를 읽어 설정:
  - HYUNDAI_GENESIS 실측값: LAT_ACCEL_FACTOR=2.7807965280270794, FRICTION=0.0984484465421171
  - kp=1.0, kf=1.0, ki=0.1은 전 차종 공통 하드코딩값 (params.toml과 무관)
  - latAccelOffset=0.0 고정

### 결론
- 사용자가 저장해 둔 LateralTorqueKf=100 등 값은 "커스텀 토크 테이블을 쓰겠다"는 스위치
  (LateralTorqueCustom)를 켜지 않아 실제로는 전혀 사용되지 않고 있음.
- 현재 제네시스 DH 2015는 opendbc가 실측해 둔 기본 torque_data(LAT_ACCEL_FACTOR≈2.78, FRICTION≈0.098)로
  조향 토크가 계산되는 중.
- 이는 버그가 아니라 "커스텀 토크 끔" 상태의 정상 동작이며, 저장된 값 자체가 잘못된 것도 아님
  (켜기만 하면 그 값들이 그대로 적용됨). 사용자가 커스텀 토크 튜닝을 실제로 원한다면
  LateralTorqueCustom을 1 이상으로 바꿔야 함.

### 실차 검증
- 미실시. 코드 정적 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/selfdrived/selfdrived.py, openpilot/selfdrive/controls/controlsd.py,
  openpilot/system/manager/process_config.py, openpilot/selfdrive/carrot_settings.json (DisableDM)
- openpilot/selfdrive/controls/lib/latcontrol_torque.py, opendbc_repo/opendbc/car/interfaces.py,
  opendbc_repo/opendbc/car/torque_data/params.toml (LateralTorqueCustom)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (2026-09-12, 변경 없음)

## [2026-09-12] route(경로) 기반 커브 감속 체인 확인 — 실제 감속 명령까지 연결됨, 이 차량은 활성화 상태

### 배경
- "route 감속 관련 코드 분석" 요청. carrot-serv.py의 speed_n_sources에 "route"라는
  소스 이름이 있는 것을 확인하고 그 전체 체인을 추적함.

### 확인된 사실 (호출 체인)
1. carrot_man.py: carrot_navi_route() — 외부 내비 앱이 보내준 경로 폴리라인(self.navi_points,
   최대 256포인트, carrotNavi 브리지로 수신)에서 현재 위치 기준 300m 구간을 5m 간격 리샘플링 →
   3점(40m 간격)으로 곡률 계산 → 곡률→속도 룩업테이블(V_CURVE_LOOKUP_BP/VALS) 적용 →
   autoNaviSpeedDecelRate로 역순 가속도 제한 감속 프로파일 생성 → route_speed 산출
2. carrot_serv.py: update_navi() — route_speed에 mapTurnSpeedFactor 곱하고
   autoCurveSpeedLowerLimit로 하한 적용. TurnSpeedControlMode가 2/3/4일 때만
   speed_n_sources에 ("route", route_speed) 추가. 다른 소스(과속카메라 sdi, 방지턱,
   스쿨존, 비전커브 vturn, 도로제한속도 road)와 함께 최솟값을 desiredSpeed로 선택 →
   carrotMan 메시지로 publish
3. carrot_functions.py: CarrotPlanner._update_carrot_man() (451행) —
   v_cruise_kph = min(v_cruise_kph, carrot_man.desiredSpeed)
4. longitudinal_planner.py (126~130행) — self.v_cruise_kph = carrot.update(sm, v_cruise_kph, mode) →
   v_cruise로 변환되어 LongitudinalMpc의 v_cruise 상한 파라미터로 전달 → MPC가 이 상한에 맞춰
   실제 가/감속 궤적(jerk 제한 포함)을 계산 → actuator로 전달
- controlsd.py의 hudControl.setSpeed는 이 체인과 별개의 표시 전용 값이며, 실제 감속은
  4번 체인(carrot.update → longitudinal_planner → MPC)을 통해 일어남.

### 활성화 전제조건 (모두 만족해야 발동)
- TurnSpeedControlMode = 2 이상 (0: 미사용, 1: 비전만, 2: 비전+경로(TBT, ±500m 이내만),
  3/4: 경로 항상). carrot_settings.json 상 기본값은 1(비전만)이라 route 소스 기본 비활성.
- MapTurnSpeedFactor 설명에 "APN 연결시에만"이라 명시 — 폰 내비 앱이 carrotNavi 브리지로
  경로 폴리라인을 실시간 전송해야 함(navi_points_active, navd_active).
- is_onroad, SHAPELY_AVAILABLE(shapely 라이브러리)도 필요. 하나라도 빠지면
  carrot_navi_route()가 (300, 무제한)을 반환해 사실상 미작동.

### 이 차량(제네시스 DH 2015)의 실제 설정 — 활성화 상태로 확인됨
- params_snapshots/2026-09-12_params_backup-4.json 확인 결과 TurnSpeedControlMode=2
  (기본값 1이 아님) → 이 차량은 route 감속이 켜져 있는 상태.
- MapTurnSpeedFactor=100(반영비율 100%), AutoCurveSpeedLowerLimit=20(하한 20km/h),
  AutoNaviSpeedDecelRate=60(0.60 m/s² 감속률)
- ⚠ DisableDM=2와 같은 패턴: "설정은 켜져 있는데 사용자가 의도한 것인지 아직 확인 안 됨".
  폰 내비 앱 연동(APN) 자체가 실제로 붙어있는지도 미확인.

### 잠재 리스크 (정적 분석 기준)
- 곡률을 GPS 폴리라인 좌표로만 계산 — 내비 앱이 주는 폴리라인의 점 밀도/정확도에
  전적으로 의존. curve_speed.py(비전 버전)에는 있는 3노드 median 스파이크 제거 필터가
  이 route 버전(carrot_navi_route)에는 없어, GPS 노이즈로 인한 곡률 오검출 가능성 있음.
- GPS 위치/heading(bearing) 오차가 gps_to_relative_xy 변환에 그대로 전파됨.

### 결론
- 코드 자체는 완결된 파이프라인이고 실제 감속 명령까지 이어지는 것은 확인됨. 다만
  "코드가 있다 = 실차에서 항상 안전하게 작동한다"는 아니며, 외부 내비 앱 연동 안정성과
  GPS 폴리라인 품질에 성패가 좌우됨.
- 버그로 보이는 부분은 없음(설계상 위험 요소는 존재).

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/carrot/carrot_man.py (carrot_navi_route, calculate_curvature)
- openpilot/selfdrive/carrot/carrot_serv.py (update_navi, speed_n_sources)
- openpilot/selfdrive/carrot/carrot_functions.py (_update_carrot_man)
- openpilot/selfdrive/carrot/carrot_navi_control.py (parse_carrot_navi_control, NaviRouteControl)
- openpilot/selfdrive/controls/lib/longitudinal_planner.py (v_cruise_kph 계산부)
- openpilot/selfdrive/controls/controlsd.py (setSpeed, hudControl 표시부)
- openpilot/selfdrive/carrot_settings.json (TurnSpeedControlMode, MapTurnSpeedFactor 설명)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)

## [2026-09-12] T_FOLLOW/TFollowGap(차간거리) 체인 확인 — MPC 리드차 장애물 제약에 직접 반영됨

### 배경
- "종방향 코드 계속 분석" 요청으로 t_follow.py(22줄, 헬퍼 함수만 존재)에서 시작해
  실제 호출부(carrot_functions.py, long_mpc.py)까지 추적함.

### 확인된 사실 (계산 체인, carrot_functions.py)
1. _get_base_t_follow() — personality(aggressive/standard/relaxed/moreRelaxed) 4단계별
   TFollowGap1~4 값 선택. EnableSpeedTF<0이면 속도 구간별 보간으로 대체 가능(고정 브레이크포인트
   [0,30,60,90]/[0,40,80,120]/[0,50,100,150] 중 EnableSpeedTF값(-1/-2/-3)으로 선택)
2. _apply_speed_t_follow_scale() — EnableSpeedTF>0이면 저속에서 차간거리를 줄였다가
   고속으로 갈수록 원복(반대 방향 스케일링)
3. _apply_decel_hold_and_boost_t_follow() — 감속(a_ego≤-0.2) 중엔 여유거리를 즉시 늘리고
   (TFollowDecelBoost 비율, a_ego=-2.5일 때 최대 0.5초 추가), 해제 시엔 서서히만
   줄여(0.10×dt/frame) 널뛰기 방지
4. _clip_t_follow() — [0.3초, tf_max]로 클립. tf_max는 myTFollowFactor(주행모드)로 확장 가능
5. ramp_t_follow() — 거리를 늘리는 쪽만 램프(0.30 또는 0.60초/초, decel_extra 여부에 따라),
   줄이는 쪽은 즉시 반영
6. get_T_FOLLOW()에 leadAccelResponse>=4 레벨 예외 있음: 추적 중인 선행차가 양의 가속
   중이면(gap이 벌어지는 중) 속도기반 스케일을 건너뛰고 설정된 tf_base를 그대로 유지
   (gap이 벌어지는데 차간거리를 괜히 좁히지 않기 위함)
- long_mpc.py 421행: t_follow = carrot.get_T_FOLLOW(...) → desired_follow_distance() →
  MPC의 리드차 장애물 거리 제약(obstacle constraint)에 직접 반영 → 실제 추종거리/
  가감속 명령으로 이어짐 (route 감속과 마찬가지로 표시용이 아니라 실동작 경로).
- 상태 변수(_tf_decel_extra, _tf_base_last 등) 초기화 확인: __init__에서 안전하게
  초기화되어 있고 getattr fallback도 첫 프레임에서 크래시 나지 않음. 정적으로 버그
  발견되지 않음.

### 이 차량의 실제 설정값 (params_backup-4.json)
- TFollowGap1~4: 110/120/140/160 (1.10/1.20/1.40/1.60초) — openpilot 표준 범위 내, 이상 없음
- EnableSpeedTF: 0 → 속도기반 보정 미사용, personality 고정값만 사용 중
- LeadAccelResponse: 0 → 레벨4-5 예외(선행차 가속중 설정값 유지) 비활성 상태
- DynamicTFollowLC: 100(=1.0) → 차선변경시 차간거리 배율 변화 없음
- TFollowDecelBoost: 10(=0.10) → 감속시 여유거리 보정 약하게(최대 0.05초)
- (PARAMS_REGISTRY.md의 기존 "TFollowGap5 미확인" 메모는 정정: 코드상 TFollowGap1~4까지만
  존재하며 5번째 항목은 없음)

### 결론
- T_FOLLOW 체인은 정적으로 문제없이 설계되어 있고, 실제 추종거리 제어에 반영됨.
- 이 차량은 속도기반 보정(EnableSpeedTF)과 레벨4-5 예외(LeadAccelResponse)를 모두 끈
  "가장 단순한" personality 고정값 모드로 운용 중 — 의도적 설정인지, 아니면 시험해보지
  않은 기본값인지는 사용자 확인 필요.

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/carrot/t_follow.py
- openpilot/selfdrive/carrot/carrot_functions.py (_get_base_t_follow ~ get_T_FOLLOW, 189~328행)
- openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py (t_follow 사용부, 405~470행)
- openpilot/selfdrive/carrot_settings.json (TFollowGap1~4 설명/범위)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)

## [2026-09-12] traffic_stop.py(E2E 정지신호 감속) 체인 확인 — 순수 비전모델 휴리스틱, HD맵/신호색상 인식 없음

### 배경
- 종방향 분석 계속 진행: t_follow.py 다음으로 traffic_stop.py(정지선/신호 감속) 추적.

### 확인된 사실 (호출 체인)
- carrot_functions.py: check_model_stopping() — 주행모델이 예측한 미래 경로(x,y,v)만으로
  정지신호 여부 추론. 속도구간별 다른 임계값(1km/h 미만: model_x<20&&model_v<10 /
  82km/h 미만: model_x<d_rel-3, 속도별 거리상한 120~150m, model_v<3 or <v[0]*0.7, |y[-1]|<5m /
  82km/h 이상: 감지 안 함). stopSignCount/startSignCount 프레임 누적으로 trafficState(red/green/off) 결정
- XState 상태머신(e2eCruise→e2ePrepare→e2eStop→e2eStopped) — 가스/브레이크, 레이더 리드,
  trafficState에 따라 전이. is_traffic_stop_entry_allowed()로 조향각 50도 이상(회전 중)이면
  새 정지 진입 억제
- actual_stop_distance: 속도 높을수록 먼 거리 추정치를 np.interp로 깎아 보정. 빨간불 지속시
  comfort_brake를 매 프레임 0.9배씩 부드럽게 조임
- TrafficStopModelLeadMatcher(traffic_stop.py): 정차 상태에서 레이더 리드가 없을 때 모델이
  본 정차 선두차량 위치를 5프레임 연속(확률≥0.90, 거리 4~80m, 정지선과 gap 0~3m, 속도≤2m/s,
  x/y/v 표준편차 임계값 이내) 검증 후에만 obstacle로 확정 — median 필터 + confirm frame으로
  방어적으로 설계됨
- long_mpc.py(469~475행): get_traffic_stop_distance_adjust()/get_traffic_stop_obstacle_distance()로
  stop_x를 MPC obstacle(x2)로 변환, x_obstacles에 포함되어 acados MPC가 실제 감속 궤적 계산.
  50m~순항거리 구간에서 신호 obstacle을 점진적으로 노출해 급제동 방지하는 스무딩 포함

### 이 차량의 실제 설정
- TrafficLightDetectMode=2 (기본값, "정지+출발 모두 감지" — 별도 조작 없이 이미 실도로에서
  작동 중이었을 가능성 높음)
- StopDistanceCarrot=700 (7.00m), TrafficStopDistanceAdjust=0 (코드 초기값 2.5m을
  사용자가 0으로 재설정)

### 결론
- 실제 MPC까지 연결되는 진짜 감속 경로이고 방어 로직(median 필터, confirm frame, isfinite,
  std 임계값)도 탄탄함.
- 구조적 리스크: HD맵/신호등 색상 인식이 전혀 없는 순수 E2E 휴리스틱이라 주행모델의 예측
  정확도에 전적으로 의존. 회전교차로, 임시신호, 공사구간 등 모델이 학습 못한 상황에서
  놓치거나 오검출할 수 있음(버그가 아니라 이 접근 방식 자체의 근본적 한계).

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/carrot/traffic_stop.py (TrafficStopModelLeadMatcher, get_traffic_stop_*)
- openpilot/selfdrive/carrot/carrot_functions.py (check_model_stopping, XState 상태머신, 340~680행)
- openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py (440~490행, x2 obstacle 반영부)
- openpilot/selfdrive/carrot_settings.json (TrafficLightDetectMode 설명)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)

## [2026-09-12] curve_speed.py(비전 커브 감속) 확인 — 물리식 기반, 외부 의존성 없어 route 버전보다 견고

### 배경
- 종방향 분석 계속: curve_speed.py(비전 버전) 및 route 버전과의 차이 비교.

### 확인된 사실
- carrot_man.py: carrot_curve_speed() → vturn_speed() → curve_speed.py의 curve_speed() 함수 호출.
  입력은 sm['modelV2'](주행모델 예측 경로/속도/각속도)와 carState.vEgo/aEgo/vCluRatio 뿐 —
  외부 내비 앱(APN) 연동 불필요, 항상 동작 가능.
- curve_speed() 계산: 곡률=yaw_rate/velocity를 경로 각 지점에서 계산 → 3점 median 필터로
  순간 yaw 스파이크 제거(route 버전엔 없는 필터) → curve_ms=sqrt(횡가속도_예산/곡률)
  (원운동 물리공식, 룩업테이블 아님) → 감속 반응시간(액추에이터 지연 1.0초+저크 해소시간)과
  감속도(1.0 m/s²)를 감안한 거리기반 역산으로 approach_ms 산출 → 최대 180m(or v_ego*6s)
  전방 중 가장 타이트한 제약(최솟값) 선택
- VisionCurveSpeed.update(): 속도를 줄이는 쪽은 즉시 반영, 늘리는(제약 해제) 쪽은
  0.35초 대기 후 초당 7.2km/h로만 서서히 반영 — 커브 탈출 시 급가속 방지
- vturn_speed는 carrot_serv.py의 speed_n_sources에 "vturn" 소스로 포함되어 route/sdi 등과
  함께 desiredSpeed 최솟값 계산에 참여(5차 route 감속 체인 항목 참고)

### 이 차량의 실제 설정
- AutoCurveSpeedFactor=80 (기본 100%보다 낮음. 설정 설명상 "값을 높이면 허용 횡가속도가
  낮아져 목표속도가 낮아짐" → 80%는 기본보다 느슨하게, 즉 커브를 더 빠른 속도로
  통과하도록 설정된 상태). AutoCurveSpeedLowerLimit=20 (route 버전과 공유)

### route(경로) 버전과 비교
| 항목 | route(경로) | curve_speed(비전) |
|---|---|---|
| 데이터 소스 | 폰 내비 앱 GPS 폴리라인 | 주행모델 예측 경로만 |
| 외부 의존성 | APN 연결 필수 | 없음(항상 동작) |
| 스파이크 필터 | 없음 | 3노드 median 있음 |
| 신뢰도(정적 분석 기준) | 내비 앱 연동 상태에 좌우 | 상대적으로 견고 |

### 결론
- 물리식 기반으로 설계가 탄탄하고 외부 의존성이 없어 route 버전보다 작동 신뢰도가 높음.
- 다만 결국 주행모델이 예측한 미래 경로/yaw에 의존하므로, 모델의 원거리 커브 인지 정확도가
  이 기능 전체의 성패를 좌우함(E2E 모델 의존 시스템 공통 한계).

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/carrot/curve_speed.py (curve_speed, VisionCurveSpeed)
- openpilot/selfdrive/carrot/carrot_man.py (carrot_curve_speed, vturn_speed)
- openpilot/selfdrive/carrot/carrot_serv.py (speed_n_sources "vturn" 항목, 5차 항목과 공유)
- openpilot/selfdrive/carrot_settings.json (AutoCurveSpeedFactor 설명)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)

## [2026-09-12] longitudinal MPC 코스트 함수 확인 + 종방향 전체 체계 종합 — 종방향 코드 분석 1단계 마무리

### 배경
- 종방향 분석 마지막 항목: long_mpc.py의 코스트 함수(set_weights) 및 jerk_factor 연동 확인,
  이후 지금까지(4차~5차) 분석한 종방향 6개 축을 종합.

### 확인된 사실
- set_weights()는 stock openpilot의 acados 기반 MPC 프레임워크(gen_long_ocp) 그대로이며,
  carrot 고유 로직이 아님. 코스트 항목: X_EGO_OBSTACLE_COST, X_EGO_COST, V_EGO_COST,
  A_EGO_COST, a_change_cost(감가속 변화 억제), jerk_factor×J_EGO_COST(저크 억제).
  carrot은 이 프레임워크에 입력값(t_follow, v_cruise, stop_x, jerk_factor)만 주입하는 구조.
- jerk_factor는 carrot_functions.py에서 personality(4단계)/myDrivingMode에 연동되어
  0.5~1.0 사이로 결정 → 낮을수록 저크 비용↓ → 가감속 변화가 더 급격해짐(반응성↑ 승차감↓).
  이 차량은 EnableSpeedTF=0(else 분기)이라 personality=standard 기준
  myDrivingMode≠Safe면 jerk_factor=0.7.
- TFollowGap1~4(1.10/1.20/1.40/1.60초) 순서가 personality aggressive/standard/relaxed/
  moreRelaxed와 jerk_factor 배정(0.5/0.7/1.0/1.0)이 서로 일관되게 짝지어져 있음을 확인
  (설계 일관성 양호).

### 종방향 전체 체계 종합 (4차~5차 통합)
```
[LongControl PID] -- 현대차는 Kp=1.0/Ki=0.0/Kf=1.0 고정 (설정값 무시, 4차)
        |
[v_cruise 상한] <- min(route 감속, curve_speed 비전 감속, sdi카메라, 도로제한속도) -> carrotMan.desiredSpeed
        |
        v
[longitudinal MPC] <- t_follow(TFollowGap 체인) -> 리드차 obstacle
                   <- stop_dist(traffic_stop 체인) -> 정지선 obstacle(x2)
                   <- jerk_factor/a_change_cost -> 코스트 웨이트
        |
        v
   실제 가/감속 궤적(a_target) -> LongControl -> 액추에이터
```

### 결론 (종방향 코드 분석 1단계 마무리)
- route/vturn/T_FOLLOW/traffic_stop 4개 커스텀 입력 체인 모두 표시용이 아니라 실제로
  MPC까지 연결되어 물리적 가/감속 명령을 만들어내는 것을 코드 레벨에서 확인함.
- MPC 자체(acados 프레임워크)는 stock openpilot 그대로라 신뢰도가 높고, carrot의
  커스텀 입력 생성부도 전반적으로 방어적으로(isfinite, median 필터, confirm frame,
  클립/램프) 작성되어 있어 정적 분석 기준 버그는 발견되지 않음.
- 구조적 리스크 2가지: ①route 감속은 폰 내비 앱(APN) 연동 안정성에 좌우, ②traffic_stop은
  HD맵/신호색상 인식 없이 순수 E2E 모델 휴리스틱이라 모델 성능에 전적으로 의존.
- 실차 검증은 전혀 미실시. 지금까지 결론은 모두 정적 코드 분석 기준이며, 실제 동작 일치
  여부는 실차주행 로그로만 확인 가능 — 다음 단계(실차주행 → 로그분석)로 넘어가기로
  사용자와 합의됨.

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준. 다음 단계는 실차주행 후 로그분석.

### 분석 근거 파일
- openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py (get_jerk_factor,
  get_a_change_cost, set_weights, 60~343행)
- openpilot/selfdrive/carrot/carrot_functions.py (jerk_factor 결정부, 220~263행)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)
## 핵심 발견 30 (45차) -- "소스 파일 수정 완료"와 "생성 번들에 반영 완료"는 서로 다른 사실이며, 코드 리뷰만으로는 후자를 확인할 수 없다
44차에서 `screenshots.js` 소스에 누락된 import를 정확히 추가하고, 그 diff를 Replace-Block 앵커 매치/`node --check`로까지 검증했음에도 실기기 크래시가 재현됐다. 원인은 소스 수정 자체가 아니라, 그 수정을 반영한 뒤 `npm install && node build.mjs`로 생성 번들(`js/generated/logs.js`)을 다시 만드는 단계가 빠진 것이었다. 이 프로젝트는 기기가 Node를 띄우지 않고 커밋된 번들을 그대로 서빙하므로(레포 `.gitignore` 주석에 명시), 소스와 번들 중 하나라도 어긋나면 소스 리뷰나 `node --check`(문법 검사일 뿐 번들링 여부는 검증 안 함)로는 절대 못 잡는다. 확인 방법은 실제로 번들을 열어 문제의 식별자가 (a) 로컬 함수처럼 다른 이름으로 축약돼 있는지, 또는 (b) 원문 그대로 남아 미해석 외부 참조로 취급됐는지를 직접 보는 것뿐이다(원문 그대로 남아있으면 100% 번들링 실패 신호). 앞으로 `js/`, `css/` 아래 소스 파일을 고치는 모든 변경은 커밋 전 `npm install && node build.mjs`를 실제로 실행해 생성 산출물까지 diff로 확인하고, 그 생성 파일을 소스와 같은 커밋에 함께 넣을 것. 44차처럼 "소스만 고치고 번들은 그대로"인 상태로 커밋하면 겉보기엔 정상 diff처럼 보여도 실기기에서는 아무 효과가 없다.
## 2026-09-18 (84차) -- 신호과속/교통정보 수집지점(sdi_descr) 배지 이탈 버그: 실차 검증 공백 + get_text_draw_pos() align 미구현

**증상**: 사용자 실기기 스크린샷(2026-09-17)에서 우측하단 경로안내 박스의 "교통정보 수집지점"
문구가 그 위 초록색 배지 밖(아래)으로 분리되어 표시됨.

**검증 기록 재검토**: 이 박스는 `hud_renderer.py`의 `_draw_turn_info_hud()`에서
`if info["sdi_descr"]: ... elif road_name_text: ...` 구조로 그려짐. FINDINGS.md 38차 항목이
이미 "도로명 텍스트... 34차 WIP 기록과 정확히 일치하는지는 신호과속 배지 부재로 판단 보류"라고
명시했으나, 이후 HANDOFF.md 40차의 "교차로 제목/회전아이콘/895m/도착거리/ETA/도로명 순서와 여백
모두 정상 확인"이라는 문구가 sdi_descr 분기까지 포함하는 것으로 오인되어 이후 세션들에서 그대로
"검증 완료"로 취급됨. 실제로는 sdi_descr 분기(카메라/POI가 근처에 있을 때만 표시)는 이번이 처음
실차로 관찰된 것.

**원인 확정**: `openpilot/system/ui/lib/text_draw.py`의 `get_text_draw_pos(font, text, x, y,
font_size, align, y_offset)` 함수는 `align` 값으로 `center_bottom`/`center_top`/`left_top`/
`right_top`/`left_center`/`center`/`right_center` 7가지만 처리하는 `if/elif` 체인이며,
`left_bottom`에 대한 분기가 없다. 매칭되는 분기가 없으면 함수 맨 위에서 미리 설정한 기본값
(`draw_x = x`, `draw_y = y + y_offset`)이 그대로 반환되는데, 이는 `left_top`(`draw_x = x`,
`draw_y = y + y_offset`)과 완전히 동일한 결과다. `hud_renderer.py`의 `_draw_text_left_bottom()`
헬퍼(제목 `tbt_main_text`, 신호과속/교통정보 배지 `sdi_descr`, 도로명 `road_name_text` 세 곳에서
호출)는 모두 `align="left_bottom"`으로 `draw_text_ui_style()`을 호출하므로, 이 세 텍스트 전부
"y가 텍스트 하단"이라는 설계 의도와 다르게 "y+6이 텍스트 상단"으로 그려져, 자기 글자 높이(약
30~45px)만큼 아래로 밀려서 렌더링된다. `carrot-ryu`(`435d0b58`)와 `carrot-ryu-v1`(`9ccf1206`)의
`text_draw.py`를 직접 대조해 양쪽 다 동일하게 이 버그를 갖고 있음을 확인했다(즉 이 버그는 v1
스냅샷 시점부터 존재했고, 20절 리셋과 무관).

sdi_descr 케이스에서만 육안으로 뚜렷하게 드러나는 이유: 이 텍스트는 `measure_text_cached()`로
잰 크기에 맞춰 별도의 초록 사각 배지를 그 위에 먼저 그리는데(배지 크기/위치 계산은 "텍스트가
y를 하단 기준으로 그려질 것"을 전제로 함), 실제 텍스트는 그보다 한참 아래에 그려지므로 배지와
텍스트가 눈에 띄게 분리된다. 제목/도로명은 별도 배지 없이 큰 검정 박스 배경 위에 바로 그려지므로,
같은 크기만큼 밀려도 시각적으로 두드러지지 않아 지금까지 발견되지 않았던 것으로 추정(11절: 이
부분은 아직 실차로 재확인하지 않은 추정).

**수정 범위(사용자 결정)**: 공용 함수(`get_text_draw_pos()`)에 `left_bottom` 분기를 추가하는
근본 수정은 제목/도로명 위치까지 함께 바뀌게 되므로, 사용자 요청에 따라 이번에는 적용하지 않음.
대신 `hud_renderer.py`의 `if info["sdi_descr"]:` 블록만 범위를 한정해, 실제 렌더링 동작(`y+6`이
텍스트 상단)에 맞춰 배지 안에 세로 중앙 정렬되도록 `label_y`를 직접 계산하고, 배지 전용 글자
크기를 `eta_size`의 90%로 축소했다. `elif road_name_text:`와 제목 렌더링 코드는 이번 수정에서
그대로 둠 -- 즉 제목/도로명은 여전히 동일한 정렬 버그를 갖고 있는 상태.

**검증**: `python3 -m py_compile`(리눅스 샌드박스) 통과, Replace-Block anchor 1회 매치(Python
문자열 대조) 확인. **실차 검증: 미실시** -- sdi_descr 분기 자체가 프로젝트 역사상 이번이 처음
검증 대상이므로, 카메라/POI 구간에서의 실주행 확인이 특히 중요함.

**참고**: 이 사례는 실차 검증 표기 원칙(12절)의 새로운 변형 -- "검증했다고 기록된 항목"이
`if/elif`처럼 조건부로 갈리는 UI에서는, 실제로 어느 조건이 화면에 표시됐었는지까지 기록하지
않으면 다른 분기가 미검증 상태로 남아있어도 알아채기 어렵다는 것을 보여줌. 앞으로 이런 UI
요소를 실차 검증할 때는 "어느 분기(조건)가 표시된 상태였는지"를 devnotes에 명시할 것을 제안.