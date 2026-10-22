# STS Harvester — Job 001 report

Date: 2026-10-22

## Environment and power

- Python 3.12.14 was available in the existing Codex runtime; no separate Python installation was needed. Created `.venv` in this project and installed all packages from `requirements.txt` successfully (`faster-whisper 1.2.1`, `requests 2.34.2`, `websocket-client 1.9.2`, and dependencies).
- The Gyan FFmpeg 9.0.2 package was already registered by WinGet. Its WinGet link could not launch in the sandbox, but the package binary ran directly: `C:\Users\vitos\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe`.
- Before the power change, the current Balanced plan showed AC sleep after 600 seconds (`0x258`) and DC sleep after 300 seconds (`0x12c`). That query was saved in `power-settings-backup.txt` before changing anything.
- `powercfg /change standby-timeout-ac 0` succeeded (exit 0). Read-back shows AC sleep timeout `0` (never); DC remains 300 seconds (`0x12c`).

## Chrome and pipeline run

- `harvest.py` was run first. It launched Chrome 155 with the owner's real profile directory `C:\Users\vitos\AppData\Local\Google\Chrome\User Data` and `--remote-debugging-port=9222`. Chrome opened, but the DevTools endpoint at `127.0.0.1:9222` remained connection-refused; the script exited 1 after its 30-second startup wait. No lesson navigation or capture was completed.
- `download.py` was run second and exited 0. There was no capture JSON, so no audio was downloaded.
- `transcribe.py` was run third and exited 0. There was no MP3, so no transcript was produced. It initialized the base model but had no audio input to transcribe.
- `lessons.txt` contains only the seeded lesson. No memberships-kind request was observed and no memberships lesson was available to probe.
- No capture JSON, browser headers/cookies, audio, or transcript was copied to the repository outbox.

## Outbox and remaining blocker

- The updated report is copied to `C:\RockyDispatch\repo\dispatch\outbox\001-sts-harvester\REPORT.md` for commit and push.
- No transcript exists yet, so there is no first-five-line excerpt to provide. Chrome's real-profile DevTools endpoint must be made available for `harvest.py` to capture the seeded lesson before the remaining media and transcription results can exist.