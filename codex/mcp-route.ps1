# Simplicio MCP route — advisory Map cache for Windows hosts.
# simplicio-hook-version: 4128-v1
#
# #6128: the Map-warming / mapper-only / native-file-tool-deny decision now
# lives once, in Rust, as `simplicio hooks pre-tool` (src/hooks_command.rs).
# This script is a thin, fail-soft wrapper: it reads the host's hook JSON on
# stdin, hands it to the Runtime binary unchanged, and forwards the binary's
# stdout and exit code back to the host verbatim.
# Native shell/terminal execution remains the host's optional tool surface;
# third-party MCP/apps remain available unchanged.
$ErrorActionPreference = 'Stop'

$overrideBin = [Environment]::GetEnvironmentVariable('SIMPLICIO_BIN')
$overrideBinDir = [Environment]::GetEnvironmentVariable('SIMPLICIO_BIN_DIR')
$UserHome = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
$SimplicioBin = if (-not [string]::IsNullOrWhiteSpace($overrideBin)) {
  $overrideBin
} elseif (-not [string]::IsNullOrWhiteSpace($overrideBinDir)) {
  Join-Path $overrideBinDir 'simplicio.exe'
} elseif ([string]::IsNullOrWhiteSpace($UserHome) -or -not [IO.Path]::IsPathRooted($UserHome)) {
  ''
} else {
  Join-Path (Join-Path $UserHome '.simplicio\bin') 'simplicio.exe'
}

$input_json = [Console]::In.ReadToEnd()
if ([string]::IsNullOrEmpty($input_json)) {
  exit 0
}

$resolved = $null
if (-not [string]::IsNullOrWhiteSpace($SimplicioBin)) {
  if (Test-Path -LiteralPath $SimplicioBin -PathType Leaf) {
    $resolved = $SimplicioBin
  } else {
    $found = Get-Command $SimplicioBin -ErrorAction SilentlyContinue
    if ($found) { $resolved = $found.Source }
  }
}

# Fail soft: no Runtime binary on this host means no opinion, not a block.
if (-not $resolved) {
  exit 0
}

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $resolved
$psi.Arguments = 'hooks pre-tool'
$psi.RedirectStandardInput = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$proc = [System.Diagnostics.Process]::Start($psi)
$proc.StandardInput.Write($input_json)
$proc.StandardInput.Close()
$stdout = $proc.StandardOutput.ReadToEnd()
$stderr = $proc.StandardError.ReadToEnd()
$proc.WaitForExit()
if ($stdout) { [Console]::Out.Write($stdout) }
if ($stderr) { [Console]::Error.Write($stderr) }
exit $proc.ExitCode
