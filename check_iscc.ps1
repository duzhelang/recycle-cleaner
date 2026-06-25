$ErrorActionPreference = 'SilentlyContinue'
$candidates = @(
  'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
  'C:\Program Files\Inno Setup 6\ISCC.exe',
  'C:\Program Files (x86)\Inno Setup 5\ISCC.exe',
  'C:\Program Files\Inno Setup 5\ISCC.exe'
)
$found = $null
foreach ($p in $candidates) { if (Test-Path $p) { $found = $p; break } }
if (-not $found) { $found = (Get-Command ISCC.exe -ErrorAction SilentlyContinue | Select-Object -First 1).Source }
if ($found) { Write-Host "FOUND|$found" } else { Write-Host "NOTFOUND" }
