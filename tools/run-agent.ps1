# Run the agent tier (tasks\agent.yaml) for several agent configs, one model at a time.
# Resumable: finished runs are skipped, so run the same line again after any stop.
# Run it in your own terminal for a long job: Claude Code stops its background jobs when Windows is
# briefly low on memory, which happens each time a 35B model loads (LOCAL_LLM_LAB.md 9.9, 9.11).
# Usage: tools\run-agent.ps1 [-Repeats 3] [-Tasks "*"] [-Configs name1,name2,...]
#   -Configs: file names in configs\agent without .yaml (default: all of them)
param([int]$Repeats = 3, [string]$Tasks = '*', [string[]]$Configs)
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not $Configs) { $Configs = Get-ChildItem configs\agent -Filter *.yaml | ForEach-Object BaseName }
foreach ($c in $Configs) {
  for ($r = 1; $r -le $Repeats; $r++) {
    "{0:HH:mm} {1}: repeats up to {2}" -f (Get-Date), $c, $r
    uv run --no-sync lab agent "configs\agent\$c.yaml" --tasks $Tasks --repeats $r
  }
}
"{0:HH:mm} all done. Next: uv run --no-sync lab report" -f (Get-Date)
