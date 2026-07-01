$b='D:\Github\markitdown\build_nuitka\output\entry.build'
$obj = (Get-ChildItem $b -Recurse -Filter *.obj -EA SilentlyContinue).Count
$c   = (Get-ChildItem $b -Recurse -Filter *.c -EA SilentlyContinue).Count
Write-Output ("C source files:  {0}" -f $c)
Write-Output ("OBJ compiled:    {0}" -f $obj)
if($c -gt 0){ Write-Output ("Approx C-compile progress: {0}%" -f [math]::Round(100*$obj/$c,1)) }
$log = Get-Item 'D:\Github\markitdown\scripts\_nuitka.log'
Write-Output ("Log created:  {0}" -f $log.CreationTime)
Write-Output ("Log updated:  {0}" -f $log.LastWriteTime)
Write-Output ("Elapsed:      {0:hh\:mm\:ss}" -f ((Get-Date) - $log.CreationTime))
Write-Output ("Active cl.exe: {0}" -f (Get-Process cl -EA SilentlyContinue).Count)
