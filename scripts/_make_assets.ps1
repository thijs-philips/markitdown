Add-Type -AssemblyName System.Drawing

$png    = 'D:\Github\markitdown\references\MarkdownConverter\Assets\markdown_converter.png'
$icoSrc = 'D:\Github\markitdown\references\MarkdownConverter\MarkdownConverter.ico'
$appDir = 'D:\Github\markitdown\windows-context-menu'
$instDir = Join-Path $appDir 'Installer'

# 1. Context-menu / app icon (embedded in the exe via <ApplicationIcon>)
Copy-Item $icoSrc (Join-Path $appDir 'MarkdownConverter.ico') -Force
Write-Output 'Copied MarkdownConverter.ico'

# Helper: draw a source image scaled to fit (preserve aspect), centered on a
# white canvas of the given size, and save as a 24-bit BMP.
function Save-Bmp([string]$srcPath, [int]$w, [int]$h, [string]$outPath) {
    $src = [System.Drawing.Image]::FromFile($srcPath)
    try {
        $bmp = New-Object System.Drawing.Bitmap $w, $h, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        try {
            $g.Clear([System.Drawing.Color]::White)
            $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $g.PixelOffsetMode   = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality

            $pad   = [int]([math]::Round([math]::Min($w, $h) * 0.06))
            $availW = $w - 2 * $pad
            $availH = $h - 2 * $pad
            $scale = [math]::Min($availW / $src.Width, $availH / $src.Height)
            $dw = [int]([math]::Round($src.Width  * $scale))
            $dh = [int]([math]::Round($src.Height * $scale))
            $dx = [int](($w - $dw) / 2)
            $dy = [int](($h - $dh) / 2)

            $g.DrawImage($src, $dx, $dy, $dw, $dh)
        } finally { $g.Dispose() }
        $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Bmp)
        $bmp.Dispose()
        Write-Output ("Wrote {0} ({1}x{2})" -f (Split-Path $outPath -Leaf), $w, $h)
    } finally { $src.Dispose() }
}

# 2. Installer wizard images (BMP, aspect matched to Inno's image areas).
#    Large welcome image ~164:314; small header image square.
Save-Bmp $png 328 628 (Join-Path $instDir 'WizardImage.bmp')
Save-Bmp $png 138 138 (Join-Path $instDir 'WizardSmallImage.bmp')
