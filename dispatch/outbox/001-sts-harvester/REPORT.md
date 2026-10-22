# STS Harvester — Job 001 report

Date: 2026-10-22

## Environment and power settings

- Work folder: C:\RockyDispatch\work\001-sts-harvester\STS-Harvester
- Chrome executable exists at C:\Program Files\Google\Chrome\Application\chrome.exe; the requested profile directory exists at C:\Users\vitos\AppData\Local\Google\Chrome\User Data.
- No Chrome process was returned by Get-Process chrome, DevTools at http://127.0.0.1:9222/json/version refused the connection, and Computer Use inventory returned apps: [], browsers: [].
- Attempted the supported Computer Use launch call. It failed exactly with: Cannot read properties of undefined (reading 'launch_app'). This session cannot control or attach to the owner's Chrome.
- Initial powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE was saved to power-settings-backup.txt. It showed AC sleep timeout 600 seconds (0x258) and DC timeout 300 seconds (0x12c).
- Attempted powercfg /change standby-timeout-ac 0; Windows returned: You do not have the permissions required to perform this action. Exit code was 1. Read-back still showed AC 0x258 and DC 0x12c. No power setting was changed.

## Built

- lessons.txt: seeded with the requested proven medias lesson.
- harvest.py: uses Chrome DevTools Protocol to navigate lessons and save URL, full observed request headers, response details, and medias/memberships classification in captures/<slug>.json.
- download.py: invokes ffmpeg for medias captures; for memberships captures, makes one GET with the captured header set, does not follow redirects, and appends the exact HTTP result or request error to captures/memberships-test.log.
- transcribe.py: converts MP3 to 16 kHz mono WAV with ffmpeg, decodes float32 samples with ffmpeg, and transcribes with faster-whisper base on CPU int8.
- requirements.txt and README.txt: Python package list and runtime note.

## Run instructions

From the STS-Harvester directory in a normal local Windows session with access to the owner's Chrome profile:

1. Install Python and ffmpeg if needed. Make sure ffmpeg is on PATH.
2. Create a venv and install dependencies:
   py -m venv .venv
   .\.venv\Scripts\python -m pip install -r requirements.txt
3. Run .\.venv\Scripts\python harvest.py, then .\.venv\Scripts\python download.py, then .\.venv\Scripts\python transcribe.py.
4. Find request captures under captures\, audio under audio\, transcripts under transcripts\, and the memberships probe log at captures\memberships-test.log.

The default Chrome executable and profile paths are defined in harvest.py; override them with STS_CHROME and STS_CHROME_PROFILE if necessary.

## Proof run

Not completed. No transcript was produced, so there is no proof transcript path or first-five-line excerpt to report. The browser automation could not access the owner's Chrome session, and this session could not start the local pipeline:

- python --version failed because C:\Users\vitos\AppData\Local\Microsoft\WindowsApps\python.exe could not be accessed.
- py --version failed because py is not recognized.
- ffmpeg -version failed because C:\Users\vitos\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe was denied access.

Pip installation and faster-whisper model download were not attempted because no usable Python runtime was available. No network-download failure was observed or inferred.

## Memberships lead test

No memberships lesson URL was available to test. Chrome could not be opened or inspected, and lessons.txt contains only the supplied medias lesson. No memberships replay was made.

## Blockers and changes outside the project

- Windows denied the requested AC sleep setting change; the original values remain in effect.
- This dispatched session has no available Chrome browser/app session and its Computer Use launcher is unavailable.
- Python and ffmpeg launchers are inaccessible in this session; consequently no capture, download, or transcription proof run could happen.
- The required report and project source files were staged in C:\RockyDispatch\repo\dispatch\outbox\001-sts-harvester\. No capture JSON, access token, audio, or transcript was staged. No browser/account data or files outside the project and required outbox were changed.
