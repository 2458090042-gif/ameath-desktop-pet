# 在桌面创建快捷方式，指向当前目录的 启动桌宠.bat
$here = $PSScriptRoot
$desktop = [Environment]::GetFolderPath('Desktop')
$wshell = New-Object -ComObject WScript.Shell
$s = $wshell.CreateShortcut((Join-Path $desktop 'AmeathPet.lnk'))
$s.TargetPath = Join-Path $here '启动桌宠.bat'
$s.WorkingDirectory = $here
$s.Save()
Write-Output 'OK'
