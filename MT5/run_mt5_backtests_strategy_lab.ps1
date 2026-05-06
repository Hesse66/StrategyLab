[CmdletBinding()]
param(
    [ValidateSet('XAUUSD', 'BTCUSD', 'BTCUSDT')]
    [string]$Symbol = 'XAUUSD',

    [ValidateSet('M5', 'M15', 'M30', 'H1', 'H4')]
    [string]$Timeframe = 'M15',

    [ValidateSet('1m', '3m')]
    [string]$Window = '1m',

    [ValidateRange(0, 99)]
    [int]$Count = 0,

    [string]$TerminalPath = 'C:\Program Files\MetaTrader 5 IC Markets Global\terminal64.exe',

    [string]$TerminalTesterProfileRoot = 'C:\Users\G3_Mb\AppData\Roaming\MetaQuotes\Terminal\010E047102812FC0C18890992854220E\MQL5\Profiles\Tester',

    [string]$SkipUpdateToken = 'F6E72D344593E235F6D30574C8D2DCF3',

    [string]$ProjectRoot = 'C:\Users\G3_Mb\OneDrive\Documentos\Trading\Autotrading\StrategyLab-github',

    [string]$ExpertName = 'strategy_lab_ma_cross_atr_stop.ex5',

    [string]$ReportSubfolder = 'PortProbe',

    [switch]$UiExport,

    [ValidateSet('full', 'run_only', 'export_only')]
    [string]$UiPhase = 'full',

    [int]$BacktestTabX = 305,

    [int]$BacktestTabY = 792,

    [int]$MetricsPanelX = 760,

    [int]$MetricsPanelY = 760,

    [int]$MenuReportDownCount = 7,

    [int]$MenuHtmlDownCount = 2,

    [int]$PostLaunchDelaySeconds = 12,

    [int]$UiReadyDelaySeconds = 5,

    [int]$TesterTimeoutSeconds = 240,

    [int]$Deposit = 100000,

    [string]$Currency = 'USD',

    [string]$Leverage = '1:100',

    [double]$RiskPct = 0.01,

    [double]$MaxLeverage = 1.0,

    [int]$BrokerUtcOffsetHours = 0,

    [long]$MagicNumber = 20260501,

    [switch]$DryRun,

    [ValidatePattern('^t\d{2}$')]
    [string]$OnlyTag,

    [ValidatePattern('^t\d{2}$')]
    [string]$StartTag,

    [ValidatePattern('^t\d{2}$')]
    [string]$EndTag
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName Microsoft.VisualBasic

Add-Type @"
using System;
using System.Runtime.InteropServices;

public static class Win32Automation {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);

    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);

    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
    public const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
    public const uint MOUSEEVENTF_RIGHTUP = 0x0010;

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }
}
"@

function Get-TestPeriods {
    param(
        [string]$Window,
        [int]$Count
    )

    switch ($Window) {
        '1m' {
            $defaultCount = 6
            $monthsPerWindow = 1
            $anchorTo = [datetime]'2026-04-01'
        }
        '3m' {
            $defaultCount = 4
            $monthsPerWindow = 3
            $anchorTo = [datetime]'2026-04-01'
        }
        default {
            throw "Unsupported window: $Window"
        }
    }

    if ($Count -le 0) {
        $Count = $defaultCount
    }

    $periods = @()
    for ($i = 0; $i -lt $Count; $i++) {
        $toDate = $anchorTo.AddMonths(-($i * $monthsPerWindow))
        $fromDate = $toDate.AddMonths(-$monthsPerWindow)
        $periods += @{
            Tag = ('t{0:d2}' -f ($i + 1))
            From = $fromDate.ToString('yyyy.MM.dd')
            To = $toDate.ToString('yyyy.MM.dd')
        }
    }

    return $periods
}

function Convert-DateForFileName {
    param([string]$DateValue)
    return $DateValue.Replace('.', '-')
}

function Get-NormalizedTerminalPath {
    param([string]$TerminalPath)
    return [System.IO.Path]::GetFullPath($TerminalPath).ToLowerInvariant()
}

function Get-ExactTerminalProcesses {
    param([string]$TerminalPath)

    $normalizedPath = Get-NormalizedTerminalPath -TerminalPath $TerminalPath
    Get-Process terminal64 -ErrorAction SilentlyContinue | Where-Object {
        try {
            [System.IO.Path]::GetFullPath($_.MainModule.FileName).ToLowerInvariant() -eq $normalizedPath
        }
        catch {
            $false
        }
    }
}

function Stop-ExactTerminalProcesses {
    param([string]$TerminalPath)

    $matches = @(Get-ExactTerminalProcesses -TerminalPath $TerminalPath)
    foreach ($match in $matches) {
        Stop-Process -Id $match.Id -Force -ErrorAction SilentlyContinue
    }
}

function Wait-ForTesterStart {
    param([int]$TimeoutSeconds = 30)

    $logDir = 'C:\Users\G3_Mb\AppData\Roaming\MetaQuotes\Terminal\010E047102812FC0C18890992854220E\Logs'
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)

    while ((Get-Date) -lt $deadline) {
        $latestLog = Get-ChildItem -LiteralPath $logDir -Filter '*.log' -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1

        if ($latestLog) {
            $recentLines = Get-Content -LiteralPath $latestLog.FullName -Tail 80
            if ($recentLines -match 'automatical testing started') {
                return $true
            }
        }

        Start-Sleep -Seconds 1
    }

    return $false
}

function Wait-ForTesterCompletion {
    param([int]$TimeoutSeconds = 180)

    $logDir = 'C:\Users\G3_Mb\AppData\Roaming\MetaQuotes\Terminal\010E047102812FC0C18890992854220E\Logs'
    $testerLogDir = 'C:\Users\G3_Mb\AppData\Roaming\MetaQuotes\Terminal\010E047102812FC0C18890992854220E\Tester\logs'
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)

    while ((Get-Date) -lt $deadline) {
        $latestLog = Get-ChildItem -LiteralPath $logDir -Filter '*.log' -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1

        if ($latestLog) {
            $recentLines = Get-Content -LiteralPath $latestLog.FullName -Tail 120
            if ($recentLines -match 'last test passed with result "successfully finished"') {
                return $true
            }
        }

        $latestTesterLog = Get-ChildItem -LiteralPath $testerLogDir -Filter '*.log' -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1

        if ($latestTesterLog) {
            $recentTesterLines = Get-Content -LiteralPath $latestTesterLog.FullName -Tail 120
            if ($recentTesterLines -match 'Test passed in') {
                return $true
            }
        }

        Start-Sleep -Seconds 1
    }

    return $false
}

function Invoke-LeftClick {
    param([int]$X, [int]$Y)
    [Win32Automation]::SetCursorPos($X, $Y) | Out-Null
    Start-Sleep -Milliseconds 150
    [Win32Automation]::mouse_event([Win32Automation]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [Win32Automation]::mouse_event([Win32Automation]::MOUSEEVENTF_LEFTUP, 0, 0, 0, [UIntPtr]::Zero)
}

function Invoke-RightClick {
    param([int]$X, [int]$Y)
    [Win32Automation]::SetCursorPos($X, $Y) | Out-Null
    Start-Sleep -Milliseconds 150
    [Win32Automation]::mouse_event([Win32Automation]::MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [Win32Automation]::mouse_event([Win32Automation]::MOUSEEVENTF_RIGHTUP, 0, 0, 0, [UIntPtr]::Zero)
}

function Get-ActiveWindowTitle {
    $handle = [Win32Automation]::GetForegroundWindow()
    if ($handle -eq [IntPtr]::Zero) { return '' }
    $builder = New-Object System.Text.StringBuilder 512
    [void][Win32Automation]::GetWindowText($handle, $builder, $builder.Capacity)
    return $builder.ToString()
}

function Get-ActiveWindowProcessId {
    $handle = [Win32Automation]::GetForegroundWindow()
    if ($handle -eq [IntPtr]::Zero) { return 0 }
    $processId = 0
    [void][Win32Automation]::GetWindowThreadProcessId($handle, [ref]$processId)
    return [int]$processId
}

function Get-ProcessMainWindowHandle {
    param([System.Diagnostics.Process]$Process)

    $Process.Refresh()
    if ($Process.MainWindowHandle -and $Process.MainWindowHandle -ne [IntPtr]::Zero) {
        return $Process.MainWindowHandle
    }

    $targetPid = [uint32]$Process.Id
    $callback = [Win32Automation+EnumWindowsProc]{
        param([IntPtr]$hWnd, [IntPtr]$lParam)

        if (-not [Win32Automation]::IsWindowVisible($hWnd)) {
            return $true
        }

        $windowProcessId = 0
        [void][Win32Automation]::GetWindowThreadProcessId($hWnd, [ref]$windowProcessId)
        if ($windowProcessId -eq $targetPid) {
            $script:__strategyLabFoundWindow = $hWnd
            return $false
        }

        return $true
    }

    $script:__strategyLabFoundWindow = [IntPtr]::Zero
    [void][Win32Automation]::EnumWindows($callback, [IntPtr]::Zero)
    $foundHandle = $script:__strategyLabFoundWindow
    Remove-Variable -Name __strategyLabFoundWindow -Scope Script -ErrorAction SilentlyContinue
    return $foundHandle
}

function Close-BlockingForegroundWindow {
    param([System.Diagnostics.Process]$ExpectedProcess = $null)

    $title = Get-ActiveWindowTitle
    $activeProcessId = Get-ActiveWindowProcessId
    $shouldClose = ($title -like 'Strategy Tester Report*' -or $title -like '*Google Chrome*' -or $title -like '*Microsoft Edge*' -or $title -like '*Microsoft Excel*' -or $title -like '*Excel*') -and
        (-not $ExpectedProcess -or $activeProcessId -ne $ExpectedProcess.Id)

    if (-not $shouldClose) {
        return $false
    }

    Write-Warning "Closing blocking foreground window before retrying MT5 focus. Title: '$title' PID: '$activeProcessId'"
    [System.Windows.Forms.SendKeys]::SendWait('%{F4}')
    Start-Sleep -Milliseconds 900
    return $true
}

function Set-Mt5Foreground {
    param(
        [System.Diagnostics.Process]$Process,
        [int]$TimeoutSeconds = 8
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $lastTitle = ''
    $lastProcessId = 0

    while ((Get-Date) -lt $deadline) {
        $Process.Refresh()
        $windowHandle = Get-ProcessMainWindowHandle -Process $Process
        if ($windowHandle -and $windowHandle -ne [IntPtr]::Zero) {
            [Win32Automation]::ShowWindow($windowHandle, 9) | Out-Null
            [Win32Automation]::SetForegroundWindow($windowHandle) | Out-Null
            [Microsoft.VisualBasic.Interaction]::AppActivate($Process.Id) | Out-Null
        }
        else {
            Write-Warning "MT5 main window handle not available yet for PID $($Process.Id). Retrying foreground."
        }

        Start-Sleep -Milliseconds 500
        $lastTitle = Get-ActiveWindowTitle
        $lastProcessId = Get-ActiveWindowProcessId
        if ($lastProcessId -eq $Process.Id) {
            return $true
        }

        [void](Close-BlockingForegroundWindow -ExpectedProcess $Process)
    }

    Write-Warning "Could not bring expected MT5 process to foreground after $TimeoutSeconds seconds. Active PID: '$lastProcessId'. Expected PID: '$($Process.Id)'. Active window title: '$lastTitle'"
    return $false
}

function Wait-ForSaveDialogForeground {
    param(
        [System.Diagnostics.Process]$Process,
        [int]$TimeoutSeconds = 8
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $title = Get-ActiveWindowTitle
        $activeProcessId = Get-ActiveWindowProcessId
        if (($title -like '*Guardar como*' -or $title -like '*Save As*') -and
            $activeProcessId -eq $Process.Id) {
            return $true
        }
        Start-Sleep -Milliseconds 250
    }

    return $false
}

function Export-ReportViaUI {
    param(
        [System.Diagnostics.Process]$Process,
        [string]$SavePathWithoutExtension,
        [int]$BacktestTabX,
        [int]$BacktestTabY,
        [int]$MetricsPanelX,
        [int]$MetricsPanelY,
        [int]$MenuReportDownCount,
        [int]$MenuHtmlDownCount
    )

    $Process.Refresh()
    if (-not (Get-ProcessMainWindowHandle -Process $Process)) {
        Write-Warning "Could not find MT5 main window handle for export phase. Continuing with foreground retry."
    }

    Set-Mt5Foreground -Process $Process -TimeoutSeconds 20 | Out-Null

    $windowHandle = Get-ProcessMainWindowHandle -Process $Process
    if (-not $windowHandle) {
        throw 'Could not locate an MT5 window for UI export.'
    }

    $rect = New-Object Win32Automation+RECT
    [Win32Automation]::GetWindowRect($windowHandle, [ref]$rect) | Out-Null

    Set-Mt5Foreground -Process $Process -TimeoutSeconds 20 | Out-Null
    if ((Get-ActiveWindowProcessId) -ne $Process.Id) {
        throw "MT5 is not foreground before selecting Backtest tab. Active window title: '$(Get-ActiveWindowTitle)'"
    }
    Invoke-LeftClick -X ($rect.Left + $BacktestTabX) -Y ($rect.Top + $BacktestTabY)
    Start-Sleep -Milliseconds 700

    Set-Mt5Foreground -Process $Process -TimeoutSeconds 20 | Out-Null
    if ((Get-ActiveWindowProcessId) -ne $Process.Id) {
        throw "MT5 is not foreground before opening report menu. Active window title: '$(Get-ActiveWindowTitle)'"
    }
    Invoke-RightClick -X ($rect.Left + $MetricsPanelX) -Y ($rect.Top + $MetricsPanelY)
    Start-Sleep -Milliseconds 800

    [System.Windows.Forms.SendKeys]::SendWait('{HOME}')
    Start-Sleep -Milliseconds 250
    for ($i = 0; $i -lt $MenuReportDownCount; $i++) {
        [System.Windows.Forms.SendKeys]::SendWait('{DOWN}')
        Start-Sleep -Milliseconds 180
    }
    [System.Windows.Forms.SendKeys]::SendWait('{RIGHT}')
    Start-Sleep -Milliseconds 500
    for ($i = 0; $i -lt $MenuHtmlDownCount; $i++) {
        [System.Windows.Forms.SendKeys]::SendWait('{DOWN}')
        Start-Sleep -Milliseconds 250
    }
    [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
    Start-Sleep -Milliseconds 1400

    if (-not (Wait-ForSaveDialogForeground -Process $Process)) {
        throw "Save dialog did not become active before typing report path. Active window title: '$(Get-ActiveWindowTitle)'"
    }

    [System.Windows.Forms.SendKeys]::SendWait('^a')
    Start-Sleep -Milliseconds 150
    [System.Windows.Forms.SendKeys]::SendWait($SavePathWithoutExtension)
    Start-Sleep -Milliseconds 250
    [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
    Start-Sleep -Seconds 2
}

function Wait-ForReportFile {
    param(
        [string]$FilePath,
        [int]$TimeoutSeconds = 20
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Path -LiteralPath $FilePath) {
            return $true
        }
        Start-Sleep -Milliseconds 500
    }

    return $false
}

function New-ExpertSetFile {
    param(
        [string]$Path,
        [double]$RiskPct,
        [double]$MaxLeverage,
        [int]$BrokerUtcOffsetHours,
        [long]$MagicNumber
    )

    $risk = $RiskPct.ToString([Globalization.CultureInfo]::InvariantCulture)
    $maxLev = $MaxLeverage.ToString([Globalization.CultureInfo]::InvariantCulture)
    $content = @"
InpFastLen=30||30||1||300||N
InpSlowLen=104||104||1||500||N
InpAtrLen=70||70||1||300||N
InpStopMult=5.1||5.1||0.1||20.0||N
InpNoiseLookback=25||25||1||100||N
InpMaxNoCross=1||1||0||50||N
InpAllowLong=true||true||0||true||N
InpAllowShort=true||true||0||true||N
InpBreakevenStopEnabled=true||true||0||true||N
InpBreakevenTriggerMfeR=0.25||0.25||0.01||5.0||N
InpBreakevenLockR=1.0||1.0||0.01||5.0||N
InpTimeDecayExitEnabled=true||true||0||true||N
InpTimeDecayBars=40||40||1||300||N
InpTimeDecayMinMfeR=0.35||0.35||0.01||5.0||N
InpHybridTimeDecayTriageEnabled=true||true||0||true||N
InpHybridTimeDecayCheckpoint=30||30||1||300||N
InpHybridTimeDecayMaxUnrealizedR=-0.45||-0.45||0.01||2.0||N
InpHybridTimeDecayMaxMfeR=0.15||0.15||0.01||2.0||N
InpHybridReverseExitTriageEnabled=true||true||0||true||N
InpHybridReverseExitMinMfeR=0.1||0.1||0.01||2.0||N
InpShortQualityGateEnabled=true||true||0||true||N
InpShortQualityGateLenBars=24960||24960||100||50000||N
InpTimeRiskFilterEnabled=true||true||0||true||N
InpBlockedUtcHoursCsv=13,15,21
InpBlockedPythonWeekdaysCsv=6
InpBrokerUtcOffsetHours=$BrokerUtcOffsetHours||$BrokerUtcOffsetHours||-12||12||N
InpRiskPct=$risk||$risk||0.001||0.05||N
InpMaxLeverage=$maxLev||$maxLev||0.1||5.0||N
InpMagicNumber=$MagicNumber||$MagicNumber||1||99999999||N
InpSlippagePoints=20||20||1||200||N
InpDebugLogging=true||true||0||true||N
"@

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $content, $utf8NoBom)
}

function New-TesterConfigFile {
    param(
        [string]$Path,
        [string]$ExpertName,
        [string]$SetFile,
        [string]$Symbol,
        [string]$Timeframe,
        [string]$FromDate,
        [string]$ToDate,
        [string]$ReportStem,
        [int]$Deposit,
        [string]$Currency,
        [string]$Leverage,
        [bool]$ShutdownTerminal
    )

    $content = @"
[Tester]
Expert=$ExpertName
ExpertParameters=$SetFile
Symbol=$Symbol
Period=$Timeframe
Model=4
ExecutionMode=0
Optimization=0
OptimizationCriterion=6
FromDate=$FromDate
ToDate=$ToDate
ForwardMode=0
Deposit=$Deposit
Currency=$Currency
Leverage=$Leverage
Report=$ReportStem
ReplaceReport=1
ShutdownTerminal=$([int]$ShutdownTerminal)
Visual=0
"@

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $content, $utf8NoBom)
}

if (-not (Test-Path -LiteralPath $TerminalPath)) {
    throw "MT5 terminal not found at: $TerminalPath"
}

$reportsRoot = Join-Path $ProjectRoot "MT5\$Symbol\reports\$Timeframe"
if (-not [string]::IsNullOrWhiteSpace($ReportSubfolder)) {
    $reportsRoot = Join-Path $reportsRoot $ReportSubfolder
}
$automationRoot = Join-Path $ProjectRoot 'MT5\automation'
New-Item -ItemType Directory -Force -Path $reportsRoot, $automationRoot, $TerminalTesterProfileRoot | Out-Null

$periods = @(Get-TestPeriods -Window $Window -Count $Count)
if ($OnlyTag) {
    $periods = @($periods | Where-Object { $_.Tag -eq $OnlyTag })
    if (-not $periods) {
        throw "Requested tag '$OnlyTag' was not found for window '$Window'."
    }
}
if ($StartTag -or $EndTag) {
    $start = if ($StartTag) { [int]$StartTag.Substring(1) } else { 1 }
    $end = if ($EndTag) { [int]$EndTag.Substring(1) } else { 99 }
    if ($end -lt $start) {
        throw "EndTag '$EndTag' cannot be lower than StartTag '$StartTag'."
    }
    $periods = @($periods | Where-Object {
        $tagNumber = [int]$_.Tag.Substring(1)
        $tagNumber -ge $start -and $tagNumber -le $end
    })
    if (-not $periods) {
        throw "No runs matched the requested range StartTag='$StartTag' EndTag='$EndTag'."
    }
}

$runs = foreach ($period in $periods) {
    $fromFile = Convert-DateForFileName $period.From
    $toFile = Convert-DateForFileName $period.To
    $stem = "strategy_lab_$($Symbol.ToLower())_$($Timeframe.ToLower())_$Window`_${fromFile}_${toFile}_$($period.Tag)"
    $reportStem = Join-Path $reportsRoot $stem
    $setPath = Join-Path $automationRoot "$stem.set"
    $iniPath = Join-Path $automationRoot "$stem.ini"
    $uiIniPath = Join-Path $automationRoot "$($stem)_manual_ui.ini"
    $terminalSetPath = Join-Path $TerminalTesterProfileRoot "$stem.set"
    $terminalSetFileName = [System.IO.Path]::GetFileName($terminalSetPath)

    New-ExpertSetFile -Path $setPath -RiskPct $RiskPct -MaxLeverage $MaxLeverage -BrokerUtcOffsetHours $BrokerUtcOffsetHours -MagicNumber $MagicNumber
    Copy-Item -LiteralPath $setPath -Destination $terminalSetPath -Force
    New-TesterConfigFile -Path $iniPath -ExpertName $ExpertName -SetFile $terminalSetFileName -Symbol $Symbol -Timeframe $Timeframe -FromDate $period.From -ToDate $period.To -ReportStem $reportStem -Deposit $Deposit -Currency $Currency -Leverage $Leverage -ShutdownTerminal (-not $UiExport)
    New-TesterConfigFile -Path $uiIniPath -ExpertName $ExpertName -SetFile $terminalSetFileName -Symbol $Symbol -Timeframe $Timeframe -FromDate $period.From -ToDate $period.To -ReportStem $reportStem -Deposit $Deposit -Currency $Currency -Leverage $Leverage -ShutdownTerminal $false

    [PSCustomObject]@{
        Tag = $period.Tag
        From = $period.From
        To = $period.To
        ReportStem = $reportStem
        SetFile = $setPath
        TerminalSetFile = $terminalSetPath
        ConfigFile = $iniPath
        UiConfigFile = $uiIniPath
    }
}

$runs | Format-Table -AutoSize

if ($DryRun) {
    return
}

foreach ($run in $runs) {
    Write-Host "Running $($run.Tag): $($run.From) -> $($run.To)"

    if ($UiExport -and $UiPhase -eq 'export_only') {
        $match = Get-ExactTerminalProcesses -TerminalPath $TerminalPath |
            Sort-Object StartTime -Descending |
            Select-Object -First 1
        if (-not $match) {
            throw 'No active MT5 process found for export_only phase.'
        }

        $uiProcess = Get-Process -Id $match.Id -ErrorAction Stop
        Export-ReportViaUI -Process $uiProcess -SavePathWithoutExtension $run.ReportStem -BacktestTabX $BacktestTabX -BacktestTabY $BacktestTabY -MetricsPanelX $MetricsPanelX -MetricsPanelY $MetricsPanelY -MenuReportDownCount $MenuReportDownCount -MenuHtmlDownCount $MenuHtmlDownCount
        $expectedHtml = "$($run.ReportStem).html"
        if (-not (Wait-ForReportFile -FilePath $expectedHtml)) {
            throw "Expected exported report was not found: $expectedHtml"
        }
        Write-Host "Exported $expectedHtml" -ForegroundColor Green
        continue
    }

    Stop-ExactTerminalProcesses -TerminalPath $TerminalPath
    $configFile = if ($UiExport) { $run.UiConfigFile } else { $run.ConfigFile }
    $skipUpdateArg = if ([string]::IsNullOrWhiteSpace($SkipUpdateToken)) { '/skipupdate' } else { "/skipupdate:$SkipUpdateToken" }
    $process = Start-Process -FilePath $TerminalPath -ArgumentList "$skipUpdateArg /config:`"$configFile`"" -PassThru -Wait:(!$UiExport)

    if ($UiExport) {
        Start-Sleep -Seconds $PostLaunchDelaySeconds
        if (-not (Wait-ForTesterStart)) {
            throw "MT5 opened but tester did not start for $($run.Tag)"
        }

        if ($UiPhase -eq 'run_only') {
            Write-Host "Checkpoint reached for $($run.Tag). Test remains open for export." -ForegroundColor Yellow
            continue
        }

        if (-not (Wait-ForTesterCompletion -TimeoutSeconds $TesterTimeoutSeconds)) {
            throw "MT5 tester did not report successful completion within $TesterTimeoutSeconds seconds for $($run.Tag)"
        }

        Start-Sleep -Seconds $UiReadyDelaySeconds
        Export-ReportViaUI -Process $process -SavePathWithoutExtension $run.ReportStem -BacktestTabX $BacktestTabX -BacktestTabY $BacktestTabY -MetricsPanelX $MetricsPanelX -MetricsPanelY $MetricsPanelY -MenuReportDownCount $MenuReportDownCount -MenuHtmlDownCount $MenuHtmlDownCount
        $expectedHtml = "$($run.ReportStem).html"
        if (-not (Wait-ForReportFile -FilePath $expectedHtml)) {
            throw "Expected exported report was not found: $expectedHtml"
        }
        Write-Host "Exported $expectedHtml" -ForegroundColor Green
        continue
    }

    if ($process.ExitCode -ne 0) {
        throw "MT5 exited with code $($process.ExitCode) for $($run.Tag)"
    }
}
