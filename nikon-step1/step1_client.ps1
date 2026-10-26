# Step 1, the outside half, by hand or as the fallback: step1_bridge.py starts step1_client.py
# with NIS's own python.exe, and uses this only when NIS has none.
# Windows PowerShell only, so no Python is needed on this computer. Start it with
# step1_client.cmd while step1.mac runs in NIS. The answers go to results\step1_client.txt.
#
# Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
#         thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
# Date: 2026-10-26
# License: MIT

$ErrorActionPreference = 'Stop'
$Port = 54471
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Out = Join-Path $Here 'results'
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$Report = Join-Path $Out 'step1_client.txt'
Set-Content -Path $Report -Value "step 1 client, $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), PowerShell $($PSVersionTable.PSVersion)" -Encoding UTF8

function Write-Line([string]$text) {
    Write-Host $text
    Add-Content -Path $Report -Value $text -Encoding UTF8
}

function Open-Bridge {
    $client = New-Object System.Net.Sockets.TcpClient
    $client.Connect('127.0.0.1', $Port)
    $client.ReceiveTimeout = 40000
    $stream = $client.GetStream()
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $writer = New-Object System.IO.StreamWriter($stream, $utf8)
    $writer.NewLine = "`n"
    $writer.AutoFlush = $true
    $reader = New-Object System.IO.StreamReader($stream, $utf8)
    return @{ Client = $client; Writer = $writer; Reader = $reader }
}

function Send-Line($bridge, [string]$line) {
    $bridge.Writer.WriteLine($line)
    return $bridge.Reader.ReadLine() | ConvertFrom-Json
}

function Check([string]$name, [string]$line, [bool]$wantOk) {
    $watch = [Diagnostics.Stopwatch]::StartNew()
    try {
        $reply = Send-Line $script:bridge $line
        $watch.Stop()
        $passed = ($reply.ok -eq $wantOk)
        if ($reply.ok) { $text = $reply.answer | ConvertTo-Json -Compress -Depth 5 } else { $text = $reply.error }
    } catch {
        $watch.Stop()
        $passed = $false
        $text = "no reply: $($_.Exception.Message)"
    }
    if ($text.Length -gt 200) { $text = $text.Substring(0, 200) + ' ...' }
    $state = if ($passed) { 'ok  ' } else { 'FAIL' }
    Write-Line ('{0} {1,-42} {2,8:N1} ms  {3}' -f $state, $name, $watch.Elapsed.TotalMilliseconds, $text)
}

try {
    $script:bridge = Open-Bridge
} catch {
    Write-Line "FAIL no bridge on port ${Port}: is step1.mac running in NIS? ($($_.Exception.Message))"
    exit 1
}
Write-Line "connected to 127.0.0.1:$Port"

# The same checks as the self-test inside NIS (CHECKS in step1_bridge.py).
Check 'ping' '{"op": "ping"}' $true
Check 'NIS version' '{"op": "call", "fn": "Get_InfoStr", "args": [1, {"ptr": "char"}]}' $true
Check 'Z position' '{"op": "call", "fn": "StgGetPosZ", "args": [{"ptr": "double"}, 0]}' $true
Check 'XY position (not there without hardware)' '{"op": "call", "fn": "StgGetPosXY", "args": [{"ptr": "double"}, {"ptr": "double"}]}' $true
Check 'optical configurations' '{"op": "call", "fn": "GetOptConfCount", "args": []}' $true
Check 'PFS status' '{"op": "call", "fn": "Stg_GetPFSStatus", "args": []}' $true
Check 'unknown function' '{"op": "call", "fn": "ThisFunctionDoesNotExist_Step1", "args": []}' $false
Check 'function not on the list (a move)' '{"op": "call", "fn": "StgMoveZ", "args": [0, 0]}' $false
Check 'Python error' '{"op": "raise"}' $false
Check 'unknown op' '{"op": "fly"}' $false
Check 'broken request' 'this is not json' $false

# Speed: 100 round trips.
$times = New-Object System.Collections.Generic.List[double]
for ($i = 0; $i -lt 100; $i++) {
    $watch = [Diagnostics.Stopwatch]::StartNew()
    $null = Send-Line $script:bridge '{"op": "call", "fn": "StgGetPosZ", "args": [{"ptr": "double"}, 0]}'
    $times.Add($watch.Elapsed.TotalMilliseconds)
}
$times.Sort()
Write-Line ('ok   100 x Z position, round trip: median {0:N1} ms, max {1:N1} ms' -f $times[50], $times[99])

# Two programs at once: a second connection next to the first.
try {
    $second = Open-Bridge
    $reply = Send-Line $second '{"op": "ping"}'
    $second.Client.Close()
    Write-Line ('{0} second connection at the same time' -f $(if ($reply.ok) { 'ok  ' } else { 'FAIL' }))
} catch { Write-Line "FAIL second connection at the same time: $($_.Exception.Message)" }

# A client that leaves before its reply: NIS must not mind.
try {
    $leaver = Open-Bridge
    $leaver.Writer.WriteLine('{"op": "hold", "seconds": 1}')
    $leaver.Client.Close()
    Start-Sleep -Milliseconds 1500
    Check 'ping after a client left mid-request' '{"op": "ping"}' $true
} catch { Write-Line "FAIL client leaving mid-request: $($_.Exception.Message)" }

# NIS busy for 3 s: try to move the NIS window or click a menu now.
Write-Host ''
Write-Host 'NIS will now be busy for 3 seconds: try moving the NIS window or opening a menu.'
Check 'NIS busy for 3 s (hold)' '{"op": "hold", "seconds": 3}' $true

# Last, because it hands NIS's own code a wrong value: if anything crashes NIS, it is this.
Check 'wrong arguments' '{"op": "call", "fn": "StgGetPosZ", "args": ["text"]}' $false
Check 'ping after wrong arguments' '{"op": "ping"}' $true

# Stop on request: the macro loop ends by itself.
Check 'shutdown' '{"op": "shutdown"}' $true
$script:bridge.Client.Close()
Start-Sleep -Seconds 3
try {
    $after = New-Object System.Net.Sockets.TcpClient
    $after.Connect('127.0.0.1', $Port)
    $after.Close()
    Write-Line 'FAIL the bridge still answers 3 s after shutdown'
} catch { Write-Line 'ok   the bridge is closed after shutdown' }

$fails = (Get-Content $Report | Where-Object { $_ -like 'FAIL*' }).Count
Write-Line "done: $fails FAIL; the macro in NIS should now say 'step 1: stopped'."
