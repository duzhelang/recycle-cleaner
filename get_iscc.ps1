$ErrorActionPreference = 'Stop'
$tools = Join-Path $PSScriptRoot 'tools'
$tmpDir = Join-Path $tools 'is_tmp'
$installDir = Join-Path $tools 'InnoSetup6'
$target = Join-Path $installDir 'ISCC.exe'

if (Test-Path $target) {
  Write-Host "FOUND|$target"
  exit 0
}

New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null
$url = 'https://github.com/jrsoftware/issrc/releases/download/is-6_7_3/innosetup-6.7.3.exe'
$installer = Join-Path $tmpDir 'innosetup.exe'

Write-Host "Downloading Inno Setup..."
curl.exe -L -o $installer $url

Write-Host "Installing Inno Setup silently..."
Start-Process -FilePath $installer -ArgumentList "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /DIR=`"$installDir`"" -Wait

if (Test-Path $target) {
  Write-Host "FOUND|$target"
} else {
  Write-Host "NOTFOUND"
  exit 1
}
