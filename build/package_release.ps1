[CmdletBinding()]
param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe",
    [switch]$SmokeTestPassed
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pythonPath = if ([System.IO.Path]::IsPathRooted($PythonExe)) {
    (Resolve-Path $PythonExe).Path
} else {
    (Resolve-Path (Join-Path $repoRoot $PythonExe)).Path
}
$distribution = Join-Path $repoRoot "dist\ProbabilityOfUs"
if (-not (Test-Path (Join-Path $distribution "ProbabilityOfUs.exe"))) {
    throw "Build the one-folder application before staging the release."
}

$docs = Join-Path $distribution "docs"
$licenses = Join-Path $distribution "licenses"
$data = Join-Path $distribution "data"
New-Item -ItemType Directory -Force -Path $docs, $licenses, $data | Out-Null

Copy-Item -Force -LiteralPath (Join-Path $repoRoot "docs\distribution_readme.md") -Destination (Join-Path $distribution "README.md")
foreach ($name in @("user_guide.md", "mathematical_model.md", "data_sources.md", "data_dictionary.md", "privacy.md", "limitations.md")) {
    Copy-Item -Force -LiteralPath (Join-Path $repoRoot "docs\$name") -Destination (Join-Path $docs $name)
}
Copy-Item -Force -LiteralPath (Join-Path $repoRoot "data\README.md") -Destination (Join-Path $data "README.md")
Copy-Item -Force -LiteralPath (Join-Path $repoRoot "LICENSE") -Destination (Join-Path $licenses "LICENSE")
Copy-Item -Force -LiteralPath (Join-Path $repoRoot "THIRD-PARTY-NOTICES.md") -Destination (Join-Path $licenses "THIRD-PARTY-NOTICES.md")

$sitePackages = (& $pythonPath -c "import sysconfig; print(sysconfig.get_paths()['purelib'])" | Select-Object -Last 1).Trim()
$pythonBase = (& $pythonPath -c "import sys; print(sys.base_prefix)" | Select-Object -Last 1).Trim()
$licenseSources = @(
    @{ Source = Join-Path $sitePackages "numpy-2.3.4.dist-info\LICENSE.txt"; Target = "NumPy-LICENSE.txt" },
    @{ Source = Join-Path $sitePackages "pyinstaller-6.20.0.dist-info\licenses\COPYING.txt"; Target = "PyInstaller-COPYING.txt" }
)
foreach ($license in $licenseSources) {
    if (-not (Test-Path -LiteralPath $license.Source)) {
        throw "Pinned third-party license file is missing: $($license.Source)"
    }
    Copy-Item -Force -LiteralPath $license.Source -Destination (Join-Path $licenses $license.Target)
}
$pythonLicense = Join-Path $pythonBase "LICENSE.txt"
if (Test-Path -LiteralPath $pythonLicense) {
    Copy-Item -Force -LiteralPath $pythonLicense -Destination (Join-Path $licenses "Python-LICENSE.txt")
}

$exe = Join-Path $distribution "ProbabilityOfUs.exe"
$exeInfo = Get-Item -LiteralPath $exe
$exeHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $exe).Hash
$runtime = (& $pythonPath -c "import PyInstaller, PySide6, numpy; from PySide6.QtCore import qVersion; print(f'Python build runtime; PyInstaller {PyInstaller.__version__}; PySide6 {PySide6.__version__}; Qt {qVersion()}; NumPy {numpy.__version__}')" | Select-Object -Last 1).Trim()
$smokeStatus = if ($SmokeTestPassed) {
    "Passed on the build machine with Qt offscreen and isolated LOCALAPPDATA; clean-VM verification remains outstanding."
} else {
    "Not confirmed by this staging script; run the documented packaged smoke check before distribution."
}
@"
# Build manifest

- Product: Probability of Us
- Product version: $($exeInfo.VersionInfo.ProductVersion)
- Target: Windows x64, PyInstaller one-folder
- Runtime: $runtime
- Executable SHA-256: $exeHash
- ICU packaging: ICU-family DLLs are excluded to avoid collecting an unrelated build-host ICU library.
- Startup check: $smokeStatus
- Signing: unsigned
- Source state: current workspace snapshot; no release commit was created.
"@ | Set-Content -LiteralPath (Join-Path $distribution "BUILD-MANIFEST.md") -Encoding utf8

$distParent = Split-Path -Parent $distribution
$archive = Join-Path $distParent "ProbabilityOfUs-windows-x64.zip"
Compress-Archive -Path $distribution -DestinationPath $archive -CompressionLevel Optimal -Force
$archiveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash
@(
    "$exeHash  ProbabilityOfUs/ProbabilityOfUs.exe",
    "$archiveHash  ProbabilityOfUs-windows-x64.zip"
) | Set-Content -LiteralPath (Join-Path $distParent "SHA256SUMS.txt") -Encoding ascii

Get-Item -LiteralPath $archive, $exe | Select-Object FullName, Length
Get-Content -LiteralPath (Join-Path $distParent "SHA256SUMS.txt")
