$tokens = $null
$errors = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile('D:\Github\markitdown\scripts\build-all.ps1', [ref]$tokens, [ref]$errors)
if (@($errors).Count) { $errors | ForEach-Object { Write-Output $_.Message } } else { Write-Output 'PARSE_OK' }
