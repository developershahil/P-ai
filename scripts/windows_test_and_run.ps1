Param(
    [string]$VenvDir = ".venv",
    [switch]$SkipInstall,
    [switch]$StartCli,
    [switch]$StartDesktop
)

$ErrorActionPreference = "Stop"

Write-Host "[1/5] Creating/activating virtual environment..."
if (-not (Test-Path "$VenvDir\Scripts\python.exe")) {
    python -m venv $VenvDir
}

$pythonExe = "$VenvDir\Scripts\python.exe"
$pipExe = "$VenvDir\Scripts\pip.exe"

if (-not $SkipInstall) {
    Write-Host "[2/5] Installing dependencies..."
    & $pipExe install -r requirements.txt
    & $pipExe install -e .[dev,api]
}

Write-Host "[3/5] Running automated tests..."
& $pythonExe -m pytest -q

Write-Host "[4/5] Running Windows smoke script..."
& $pythonExe scripts/windows_smoke_test.py

Write-Host "[5/5] Running text/voice/security health checks..."
& $pythonExe -c @'
from importlib.util import find_spec
from personal_ai.core.assistant import handle_input
from personal_ai.security.permissions import BLOCKED_EXES

required_checks = []

text_result = handle_input("time")
text_reply = (text_result or {}).get("reply", "")
required_checks.append(bool(text_reply))
print(f"[TEXT] reply_ok={bool(text_reply)} reply={text_reply!r}")

chat_fallback = handle_input("hello")
chat_reply = (chat_fallback or {}).get("reply", "")
required_checks.append(bool(chat_reply))
print(f"[TEXT] chat_ok={bool(chat_reply)} reply={chat_reply!r}")

print(f"[SECURITY] blocked_exes={sorted(BLOCKED_EXES)}")
required_checks.append("powershell.exe" in BLOCKED_EXES and "pwsh.exe" in BLOCKED_EXES)

voice_in = find_spec("speech_recognition") is not None
voice_out = find_spec("pyttsx3") is not None
print(f"[VOICE] speech_recognition_installed={voice_in}")
print(f"[VOICE] pyttsx3_installed={voice_out}")
if not (voice_in and voice_out):
    print("[VOICE][WARN] Voice deps missing, text mode still works.")

if not all(required_checks):
    raise SystemExit(1)
'@

if ($StartCli) {
    Write-Host "Starting CLI assistant..."
    & $pythonExe -m personal_ai.main
}

if ($StartDesktop) {
    Write-Host "Starting desktop UI..."
    & $pythonExe ui-desktop/main_window.py
}

Write-Host "All checks completed. Use -StartCli or -StartDesktop to launch app."
