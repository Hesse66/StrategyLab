[CmdletBinding()]
param(
    [ValidateSet('XAUUSD', 'BTCUSD', 'BTCUSDT')]
    [string]$Symbol = 'XAUUSD',

    [ValidateSet('M15')]
    [string]$Timeframe = 'M15',

    [ValidateSet('1m', '3m')]
    [string[]]$Windows = @('1m', '3m'),

    [string[]]$Tags1m = @('t02', 't03', 't04', 't05', 't06'),

    [string[]]$Tags3m = @('t01', 't02', 't03', 't04'),

    [string]$TerminalPath = 'C:\Program Files\MetaTrader 5 IC Markets Global\terminal64.exe',

    [string]$Runner = 'C:\Users\G3_Mb\OneDrive\Documentos\Trading\Autotrading\StrategyLab-github\MT5\run_mt5_backtests_strategy_lab.ps1',

    [string]$ProjectRoot = 'C:\Users\G3_Mb\OneDrive\Documentos\Trading\Autotrading\StrategyLab-github',

    [string]$TerminalLogRoot = 'C:\Users\G3_Mb\AppData\Roaming\MetaQuotes\Terminal\010E047102812FC0C18890992854220E',

    [int]$TesterTimeoutSeconds = 240,

    [switch]$UiExport,

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-LatestLogFile {
    param([string]$Directory)

    Get-ChildItem -LiteralPath $Directory -Filter '*.log' -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
}

function Read-FileFromOffset {
    param(
        [string]$Path,
        [long]$Offset
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return ''
    }

    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    try {
        if ($Offset -gt $stream.Length) {
            $Offset = 0
        }
        $stream.Seek($Offset, [System.IO.SeekOrigin]::Begin) | Out-Null
        $reader = [System.IO.StreamReader]::new($stream)
        try {
            return $reader.ReadToEnd()
        }
        finally {
            $reader.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }
}

function Get-BalanceFromText {
    param([string]$Text)

    $matches = [regex]::Matches($Text, 'final balance\s+([0-9]+(?:\.[0-9]+)?)\s+USD')
    if ($matches.Count -eq 0) {
        return $null
    }
    return [double]$matches[$matches.Count - 1].Groups[1].Value
}

function Get-RunMatrix {
    foreach ($window in $Windows) {
        $tags = if ($window -eq '1m') { $Tags1m } else { $Tags3m }
        foreach ($tag in $tags) {
            if ($tag -notmatch '^t\d{2}$') {
                throw "Invalid tag '$tag'. Expected format tNN."
            }
            [PSCustomObject]@{
                Window = $window
                Tag = $tag
            }
        }
    }
}

if (-not (Test-Path -LiteralPath $Runner)) {
    throw "Runner not found: $Runner"
}
if (-not (Test-Path -LiteralPath $TerminalPath)) {
    throw "MT5 terminal not found: $TerminalPath"
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logRoot = Join-Path $ProjectRoot "MT5\automation\pack_logs\$timestamp"
$testerLogDir = Join-Path $TerminalLogRoot 'Tester\logs'
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null

$matrix = @(Get-RunMatrix)
if ($matrix.Count -eq 0) {
    throw 'No runs selected.'
}

Write-Host "StrategyLab M15 pack: $($matrix.Count) runs. Logs: $logRoot" -ForegroundColor Cyan

$results = @()
foreach ($item in $matrix) {
    $caseId = "strategy_lab_${Symbol}_${Timeframe}_$($item.Window)_$($item.Tag)".ToLowerInvariant()
    $runnerLog = Join-Path $logRoot "$caseId.runner.log"
    $testerDeltaLog = Join-Path $logRoot "$caseId.tester.log"
    $beforeTesterLog = Get-LatestLogFile -Directory $testerLogDir
    $beforePath = if ($beforeTesterLog) { $beforeTesterLog.FullName } else { '' }
    $beforeLength = if ($beforeTesterLog) { $beforeTesterLog.Length } else { 0L }

    Write-Host "RUN $($item.Window)/$($item.Tag) -> $runnerLog"

    $argumentList = @(
        '-ExecutionPolicy', 'Bypass',
        '-File', $Runner,
        '-Symbol', $Symbol,
        '-Timeframe', $Timeframe,
        '-Window', $item.Window,
        '-OnlyTag', $item.Tag,
        '-TerminalPath', $TerminalPath,
        '-TesterTimeoutSeconds', $TesterTimeoutSeconds
    )
    if ($UiExport) {
        $argumentList += '-UiExport'
    }
    if ($DryRun) {
        $argumentList += '-DryRun'
    }

    $startedAt = Get-Date
    & powershell @argumentList *> $runnerLog
    $exitCode = $LASTEXITCODE

    $afterTesterLog = Get-LatestLogFile -Directory $testerLogDir
    $afterPath = if ($afterTesterLog) { $afterTesterLog.FullName } else { $beforePath }
    $offset = if ($afterPath -eq $beforePath) { $beforeLength } else { 0L }
    $testerText = if ($afterPath) { Read-FileFromOffset -Path $afterPath -Offset $offset } else { '' }
    [System.IO.File]::WriteAllText($testerDeltaLog, $testerText)

    $criticalPattern = 'Invalid stops|Market closed|MODIFY_FAILED|failed modify|retcode=10016|retcode=10018'
    $criticalMatches = @([regex]::Matches($testerText, $criticalPattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase))
    $passed = if ($DryRun) { $exitCode -eq 0 } else { ($exitCode -eq 0) -and ($testerText -match 'Test passed in|automatical testing finished') }
    $balance = Get-BalanceFromText -Text $testerText

    $results += [PSCustomObject]@{
        Window = $item.Window
        Tag = $item.Tag
        Status = if ($DryRun -and $passed) { 'DRYRUN' } elseif ($passed -and $criticalMatches.Count -eq 0) { 'PASS' } elseif ($passed) { 'PASS_WITH_WARNINGS' } else { 'FAIL' }
        ExitCode = $exitCode
        FinalBalance = $balance
        CriticalMatches = $criticalMatches.Count
        StartedAt = $startedAt.ToString('s')
        RunnerLog = $runnerLog
        TesterDeltaLog = $testerDeltaLog
    }

    Write-Host ("DONE {0}/{1}: exit={2} balance={3} critical={4}" -f $item.Window, $item.Tag, $exitCode, $(if ($null -eq $balance) { 'n/a' } else { $balance.ToString('0.00') }), $criticalMatches.Count)

    if ($exitCode -ne 0) {
        break
    }
}

$summaryPath = Join-Path $logRoot 'summary.csv'
$results | Export-Csv -LiteralPath $summaryPath -NoTypeInformation -Encoding UTF8

Write-Host "Summary: $summaryPath" -ForegroundColor Green
$results | Format-Table Window, Tag, Status, ExitCode, FinalBalance, CriticalMatches -AutoSize

$failures = @($results | Where-Object { $_.Status -eq 'FAIL' })
if ($failures.Count -gt 0) {
    exit 1
}
