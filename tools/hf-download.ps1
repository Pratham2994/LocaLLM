# Resumable parallel download of one file from a public Hugging Face repo.
# The file is fetched as N byte ranges with curl. Every piece can continue after a stop, so a
# killed or timed-out job loses nothing. At the end the pieces are joined and the SHA-256 is
# compared with the value Hugging Face publishes for the file.
# Use it when `hf download` is too slow or keeps restarting (LOCAL_LLM_LAB.md 9.9, "Downloader").
# Usage: tools\hf-download.ps1 -Repo <repo> -File <file name> [-Dest <models folder>] [-Parts 32] [-MaxMinutes 105]
#   Run it again with the same arguments to continue a stopped download.
#   -MaxMinutes: the run stops cleanly after this time (Claude Code stops background jobs after 2 hours).
param([string]$Repo, [string]$File, [string]$Dest = 'D:\02_Code\Inference\models', [int]$Parts = 32, [int]$MaxMinutes = 105)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$dst = $Dest
$final = Join-Path $dst $File
if (Test-Path $final) { "OK      $File (already there)"; exit 0 }

$meta = $null
for ($i = 1; $i -le 6 -and -not $meta; $i++) {
  try { $meta = (Invoke-RestMethod "https://huggingface.co/api/models/$Repo/tree/main?recursive=1" -TimeoutSec 40) | Where-Object { $_.path -eq $File } }
  catch { Start-Sleep (3 * $i) }
}
if (-not $meta) { "MISSING $File (cannot read the repo file list)"; exit 1 }
$size = [int64]$meta.size
$sha = $meta.lfs.oid
$url = "https://huggingface.co/$Repo/resolve/main/$File"
$pdir = Join-Path $dst ".parts\$File"
New-Item -ItemType Directory -Force $pdir | Out-Null
# The piece layout must not change between runs: remember the piece count of the first run.
$layout = Join-Path $pdir 'layout.txt'
if (Test-Path $layout) { $Parts = [int](Get-Content $layout) } else { Set-Content $layout $Parts }
"$File : {0:N2} GB, sha256 {1}..." -f ($size / 1e9), $sha.Substring(0, 12)

function Add-Tmp($part, $tmp) {  # append a finished or interrupted chunk to its piece
  if ((Test-Path $tmp) -and (Get-Item $tmp).Length -gt 0) {
    $in = [IO.File]::OpenRead($tmp); $out = [IO.File]::Open($part, 'Append')
    try { $in.CopyTo($out, 4MB) } finally { $in.Close(); $out.Close() }
  }
  if (Test-Path $tmp) { Remove-Item $tmp -Force }
}

$step = [int64][math]::Ceiling($size / $Parts)
$pieces = for ($i = 0; $i -lt $Parts; $i++) {
  $s = $i * $step; $e = [math]::Min($size, $s + $step) - 1
  $p = Join-Path $pdir ('p{0:00}.bin' -f $i)
  if (-not (Test-Path $p)) { [IO.File]::Create($p).Close() }
  Add-Tmp $p "$p.tmp"
  [pscustomobject]@{ Start = [int64]$s; End = [int64]$e; Path = $p; Proc = $null }
}
function Open-Length($path) {  # real size of a file that curl still has open (the folder listing lags behind)
  if (-not (Test-Path $path)) { return 0 }
  $fs = [IO.File]::Open($path, 'Open', 'Read', 'ReadWrite'); try { return $fs.Length } finally { $fs.Close() }
}
function Done-Bytes { ($pieces | ForEach-Object { (Get-Item $_.Path).Length + (Open-Length "$($_.Path).tmp") } | Measure-Object -Sum).Sum }

$deadline = (Get-Date).AddMinutes($MaxMinutes)
$t0 = Get-Date; $b0 = Done-Bytes; $lastPrint = Get-Date
"starting at {0:N2} GB of {1:N2} GB" -f ($b0 / 1e9), ($size / 1e9)
while ($true) {
  $open = 0
  foreach ($pc in $pieces) {
    if ($pc.Proc -and -not $pc.Proc.HasExited) { $open++; continue }
    if ($pc.Proc) { Add-Tmp $pc.Path "$($pc.Path).tmp"; $pc.Proc = $null }
    $have = (Get-Item $pc.Path).Length
    $need = ($pc.End - $pc.Start + 1) - $have
    if ($need -le 0) { continue }
    if ((Get-Date) -lt $deadline) {
      $range = '{0}-{1}' -f ($pc.Start + $have), $pc.End
      $pc.Proc = Start-Process curl.exe -ArgumentList @('-L', '-sS', '--fail', '-y', '60', '-Y', '2000', '-r', $range, '-o', "`"$($pc.Path).tmp`"", "`"$url`"") -PassThru -NoNewWindow
      $open++
    }
  }
  if ($open -eq 0) { break }
  if ((Get-Date) -ge $deadline) { $pieces | Where-Object { $_.Proc -and -not $_.Proc.HasExited } | ForEach-Object { Stop-Process -Id $_.Proc.Id -Force -ErrorAction SilentlyContinue } ; Start-Sleep 2; continue }
  if (((Get-Date) - $lastPrint).TotalSeconds -ge 300) {
    $b = Done-Bytes; $lastPrint = Get-Date
    "{0:HH:mm}  {1:N2} / {2:N2} GB  ({3:N1} MB/s average)" -f (Get-Date), ($b / 1e9), ($size / 1e9), (($b - $b0) / 1e6 / ((Get-Date) - $t0).TotalSeconds)
  }
  Start-Sleep 5
}
$pieces | ForEach-Object { Add-Tmp $_.Path "$($_.Path).tmp" }
$b = Done-Bytes
if ($b -lt $size) { "INCOMPLETE $File : {0:N2} of {1:N2} GB (run again to continue)" -f ($b / 1e9), ($size / 1e9); exit 2 }

"joining pieces and checking SHA-256..."
$join = "$final.joining"
$out = [IO.File]::Create($join)
try { foreach ($pc in $pieces) { $in = [IO.File]::OpenRead($pc.Path); try { $in.CopyTo($out, 8MB) } finally { $in.Close() } } } finally { $out.Close() }
$got = (Get-FileHash $join -Algorithm SHA256).Hash.ToLower()
if ((Get-Item $join).Length -ne $size -or $got -ne $sha) { "BAD     $File : size or SHA-256 does not match (got $got)"; exit 3 }
Move-Item $join $final
Remove-Item $pdir -Recurse -Force
"OK      $File  {0:N2} GB, SHA-256 verified, {1:N0} min in this run" -f ($size / 1e9), ((Get-Date) - $t0).TotalMinutes
