# Run the agent tier (tasks\agent.yaml) for several agent configs, one model at a time.
# Made for a long unattended run in your own terminal:
#   - resumable: finished runs are skipped, so run the same line again after any stop;
#   - repeat-major: every model gets repeat 1, then every model repeat 2, ... so an early stop
#     leaves all models with the same number of repeats;
#   - Windows is kept awake while the script runs (the request ends with the script);
#   - everything is also written to results\logs\agent-run-<time>.log;
#   - the report is rebuilt at the end.
# Why your own terminal: Claude Code stops its background jobs when Windows is briefly low on
# memory, which happens each time a 35B model loads (LOCAL_LLM_LAB.md 9.9, 9.11).
# Usage: powershell -ExecutionPolicy Bypass -File tools\run-agent.ps1 [-Repeats 5] [-Tasks "*"] [-Configs name1,name2]
#   -Configs: file names in configs\agent without .yaml (default: all of them)
param([int]$Repeats = 5, [string]$Tasks = '*', [string[]]$Configs)
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not $Configs) { $Configs = Get-ChildItem configs\agent -Filter *.yaml | ForEach-Object BaseName }
New-Item -ItemType Directory -Force results\logs | Out-Null
$log = "results\logs\agent-run-{0:yyyyMMdd-HHmmss}.log" -f (Get-Date)

# Ask Windows not to sleep while this script runs (ES_CONTINUOUS | ES_SYSTEM_REQUIRED).
Add-Type -Namespace Lab -Name Power -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint esFlags);'
[void][Lab.Power]::SetThreadExecutionState([uint32]2147483649)

function Say($text) { $line = "{0:HH:mm} {1}" -f (Get-Date), $text; $line; Add-Content -Path $log -Value $line -Encoding utf8 }
function Both { process { "$_"; Add-Content -Path $log -Value "$_" -Encoding utf8 } }   # screen + log, one encoding

Say "agent run: $($Configs.Count) configs x $Repeats repeats, tasks '$Tasks'; log file $log"
try {
  for ($r = 1; $r -le $Repeats; $r++) {
    foreach ($c in $Configs) {
      Say "== repeat $r of $Repeats : $c"
      uv run --no-sync lab agent "configs\agent\$c.yaml" --tasks $Tasks --repeats $r 2>&1 | Both
      if ($LASTEXITCODE -ne 0) { Say "!! $c ended with exit code $LASTEXITCODE; going on with the next one" }
      Get-Process llama-server -ErrorAction SilentlyContinue | Stop-Process -Force   # never leave a server behind
      Start-Sleep 5
    }
  }
  Say "all repeats done; building the report"
  uv run --no-sync lab report 2>&1 | Select-Object -Last 1 | Both
  Say "finished"
}
finally {
  [void][Lab.Power]::SetThreadExecutionState([uint32]2147483648)   # let Windows sleep again
}
