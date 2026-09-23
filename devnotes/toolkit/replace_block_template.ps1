<#
  replace_block_template.ps1
  ---------------------------------------------------------------
  CARROT-RYU 반영 스크립트가 공통으로 재사용하는 문자열 블록 치환(Replace-Block)
  헬퍼 함수 모음. PROJECT_INSTRUCTIONS_carrot-ryu.md 9절/14절 참고.

  사용법: 이 파일을 그대로 복사(dot-source)하거나, 함수 정의 블록을
  반영 스크립트 상단에 그대로 붙여넣는다. 직접 실행 대상 스크립트가
  아니라 "복사해서 쓰는 라이브러리"다.

    . "$PSScriptRoot\replace_block_template.ps1"
    Invoke-ReplaceBlock -Path $SomePath -Old $Old -New $New -Label "some_file.py"
    Invoke-Git -C $Tmp clone --branch $Branch --single-branch --config core.autocrlf=false $RepoUrl $Tmp

  왜 필요한가 (핵심 발견 44/46/48/50 재발 방지):
    carrot-ryu의 .gitattributes에는 `* text=auto`가 있다. 이 때문에
    `git clone --config core.autocrlf=false`를 지정해도, Windows에서
    checkout된 작업 트리 파일은 CRLF로 변환될 수 있다(원인은 .gitattributes,
    core.autocrlf는 무관한 별개 스위치 -- 9절 체크리스트 2번 참고). GitHub 원본
    blob은 LF이므로, 정규화 없이 LF 기준 앵커로 `.Replace()`를 시도하면 작업
    트리가 CRLF일 때 0회 매치로 안전 중단된다(핵심 발견 44/46/48). 132차
    v1(`132cha_unused_imports.ps1`)에서 다시 재발했다(핵심 발견 50) --
    이 함수를 쓰지 않고 매번 새로 작성한 스크립트에서 정규화 로직이 누락됐기
    때문이다.

  Invoke-ReplaceBlock  : LF로 정규화해 비교/치환하고, 파일을 LF로 다시 쓴다.
                         WIP.md/CURRENT_STATUS.md/HANDOFF.md/toolkit/README.md/
                         PROJECT_INSTRUCTIONS_carrot-ryu.md 등 원래 LF인 파일,
                         그리고 대부분의 코드 파일(carrot-ryu)에 사용한다.
  Invoke-ReplaceBlock-CrlfNative : 파일의 기존 개행을 건드리지 않고 있는 그대로
                         바이트 매칭한다. FINDINGS.md처럼 원본이 이미 CRLF인
                         파일에 사용한다(Invoke-ReplaceBlock으로 처리하면 파일
                         전체가 LF로 재작성되어, 손대지 않은 기존 줄까지 diff에
                         잡히는 부작용이 생긴다).
  Invoke-Git           : `git <args...>` 실행 공통 헬퍼(핵심 발견 53/54/55 재발
                         방지). stderr를 stdout과 병합하지 않고(2>&1 금지),
                         $LASTEXITCODE로만 성공/실패를 판단한다. 이름 있는
                         파라미터를 선언하지 않고 자동 변수 $args만 참조한다
                         (`git add -A`의 `-A`가 파라미터 이름과 접두어 충돌을
                         일으키는 것을 원천 차단). 사용: `Invoke-Git -C $Tmp
                         clone --branch $Branch ... `, `Invoke-Git -C $Tmp add
                         -A`, `Invoke-Git -C $Tmp commit -m $Msg`, `Invoke-Git
                         -C $Tmp push origin $Branch`.

  둘 다 공통으로 지킨다(9절 체크리스트 6/7번):
    - 매치 횟수가 정확히 1이 아니면 아무것도 쓰지 않고 즉시 throw(15절/18절
      "강제 진행 금지" 원칙).
    - 쓴 직후 파일을 다시 읽어, 옛 블록이 남아있지 않고 새 블록이 존재하는지
      재확인한다("1회 매치"는 "치환이 일어났다"만 보증하지 "결과가 의도와
      같다"는 보증하지 않는다 -- 핵심 발견 42).
#>

function Invoke-ReplaceBlock {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][string]$Old,
    [Parameter(Mandatory=$true)][string]$New,
    [Parameter(Mandatory=$true)][string]$Label
  )
  $RawContent = [System.IO.File]::ReadAllText($Path)
  $NormContent = $RawContent -replace "`r`n", "`n"
  $NormOld = $Old -replace "`r`n", "`n"
  $NormNew = $New -replace "`r`n", "`n"

  $Count = ([regex]::Matches($NormContent, [regex]::Escape($NormOld))).Count
  Write-Host "$Label anchor match count: $Count"
  if ($Count -ne 1) {
    throw "$Label`: anchor block matched $Count times (expected 1) - aborting, nothing written"
  }

  $NormContent = $NormContent.Replace($NormOld, $NormNew)
  [System.IO.File]::WriteAllText($Path, $NormContent, (New-Object System.Text.UTF8Encoding($false)))

  $Recheck = [System.IO.File]::ReadAllText($Path)
  if ($Recheck.IndexOf($NormNew) -lt 0) {
    throw "$Label`: post-write recheck cannot find new block - aborting"
  }
  if (-not $NormNew.Contains($NormOld)) {
    # Substitution-style (New does not contain Old as a substring): the old block
    # must be fully gone. For insertion-style (New = inserted text + Old), Old is
    # expected to still be present inside New, so this check is skipped there.
    if ($Recheck.IndexOf($NormOld) -ge 0) {
      throw "$Label`: post-write recheck still finds old block - aborting"
    }
  }
  Write-Host "$Label post-write recheck OK"
}

function Invoke-ReplaceBlock-CrlfNative {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][string]$Old,
    [Parameter(Mandatory=$true)][string]$New,
    [Parameter(Mandatory=$true)][string]$Label
  )
  $Content = [System.IO.File]::ReadAllText($Path)

  $Count = ([regex]::Matches($Content, [regex]::Escape($Old))).Count
  Write-Host "$Label anchor match count: $Count"
  if ($Count -ne 1) {
    throw "$Label`: anchor block matched $Count times (expected 1) - aborting, nothing written"
  }

  $Content = $Content.Replace($Old, $New)
  [System.IO.File]::WriteAllText($Path, $Content, (New-Object System.Text.UTF8Encoding($false)))

  $Recheck = [System.IO.File]::ReadAllText($Path)
  if ($Recheck.IndexOf($New) -lt 0) {
    throw "$Label`: post-write recheck cannot find new block - aborting"
  }
  if (-not $New.Contains($Old)) {
    if ($Recheck.IndexOf($Old) -ge 0) {
      throw "$Label`: post-write recheck still finds old block - aborting"
    }
  }
  Write-Host "$Label post-write recheck OK"
}

function Invoke-Git {
  # git 실행 공통 헬퍼 (핵심 발견 53(139차)+54+55(142차) 반영판, 9절 체크리스트 2번과
  # 마찬가지로 devnotes/코드 반영 스크립트가 매번 새로 작성하지 않고 재사용한다).
  #
  # - stderr를 stdout과 병합하지 않는다(2>&1 금지, 핵심 발견 53/55): Windows
  #   PowerShell 5.1은 병합된 native stderr 라인(예: `git clone`의 정상 진행
  #   메시지 "Cloning into '...'...")을 NativeCommandError로 감싸고,
  #   $ErrorActionPreference="Stop" 아래에서는 성공한 명령인데도 즉시 중단시킨다.
  # - 이름 있는 파라미터를 선언하지 않는다(핵심 발견 54): param()으로 $Args 같은
  #   이름을 선언하면 PowerShell의 접두어 매칭 때문에 `git add -A`의 `-A`처럼
  #   뒤에 값이 없는 단일 옵션이 그 파라미터 이름의 유일한 접두어 후보로 오인돼
  #   "Missing an argument" 오류로 즉시 죽는다. 자동 변수 $args만 참조하면 이런
  #   접두어 매칭 자체가 일어나지 않는다.
  #
  # 성공/실패 판단은 $LASTEXITCODE만 사용한다(native 명령 stderr 출력 자체는
  # 오류가 아니며, 콘솔에 그대로 흘려보낸다).
  & git @args
  if ($LASTEXITCODE -ne 0) {
    throw "git $($args -join ' ') failed with exit code $LASTEXITCODE"
  }
}
