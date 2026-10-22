# JOB 001 — STS HARVESTER (dispatched by Rocky via the bridge)

## EXECUTION CONTEXT — read first, these rules override the brief below where they differ
- You are running as a dispatched job under the RockyDispatch dispatcher. Your current work directory is your job folder; your writable locations are that folder and the repo clone at `C:\RockyDispatch\repo`. Root reads are permitted.
- Where the brief says "Desktop", build inside your job work folder instead: create `STS-Harvester\` there and work inside it.
- DELIVERABLES (required before you finish): (1) copy `REPORT.md` and every transcript `.txt` you produce into `C:\RockyDispatch\repo\dispatch\outbox\001-sts-harvester\`; (2) ALSO print the full text of `REPORT.md` in your final output. The dispatcher pushes the repo copy back to Rocky — files left only in the work folder do NOT reach him.
- Installs: if pip/ffmpeg/model downloads fail because the job sandbox has no network, do NOT fake results — write exactly what failed into REPORT.md and finish cleanly; Rocky will fall back to an interactive run.
- Chrome: the owner's Chrome profile is under `C:\Users\vitos\AppData\Local\Google\Chrome\User Data`. Attach via remote debugging; if Chrome is already running without the debug flag, relaunch it with the flag (tabs restore). If you cannot attach to the browser, report precisely why.
- Step 0 (power settings) from the brief still applies: attempt it, log the outcome, never fail the whole job over it.

---

# TASK FOR CODEX (running on Adam's Windows PC) — STS lesson harvester: capture, download, transcribe

## Mission
Build a small local tool on THIS PC that, given a list of Services That Scale (STS) course lesson URLs, automatically: (1) captures the video stream request each lesson's player makes, (2) downloads the audio, and (3) produces a text transcript per lesson. One proof run, then a report. Adam (the owner) is asleep; work autonomously inside the constraints below and leave everything in the project folder.

## Environment facts (verified 2026-10-22 by the owner's assistant)
- This PC: Windows 11. The owner is signed in to the course portal in Chrome: portal host `customer.servicesthatscale.com`, player is GoHighLevel's native HTML5 course player (menu = Quality + Speed only, NO captions anywhere, no download button).
- Video is HLS served from `content.apisystem.tech`. Two lesson kinds exist:
  - "medias" kind — stream URL path contains `/hls/medias/.../transcoded_videos/.../master.m3u8`. PROVEN downloadable: replaying the request with its FULL original headers works (it carries a Firebase ID token, ~1-hour expiry, plus `Referer: https://courses.servicesthatscale.com/`). From the master playlist, the 360p variant's audio playlist is `index-f1-v1-a1.m3u8`; ffmpeg with the same headers → audio MP3 → transcript. This route produced a verified transcript already (done manually).
  - "memberships" kind — paths `/hls/memberships/...` or `/hls/v2/memberships/...`. Verbatim request replay returned 401 from other machines AND from this PC's browser copy; in-page fetch failed too (401 / CORS). ONE unchecked lead remains: the player's own requests may carry an `authorization:` header that the manual copies missed. Test exactly this lead; do not brute-force variations.
- Transcription rig pattern that works: ffmpeg → 16 kHz mono WAV → faster-whisper (base model, CPU int8) fed the WAV decoded as a float32 array (PyAV decode inside faster-whisper is unreliable here; pre-decode with ffmpeg and pass samples). ~30 s per 5 minutes of audio on CPU.

## Step 0 — keep this PC awake (owner's direct instruction)
First: record the current power/sleep settings into `STS-Harvester/power-settings-backup.txt` (create the folder first), then set the PC to NEVER sleep while plugged in (AC standby timeout to never, e.g. `powercfg /change standby-timeout-ac 0`). Screen may still turn off; do NOT change battery settings, lid-close behavior, or hibernation. Confirm by reading the setting back (`powercfg /query`) and note the result in REPORT.md.

## Build (in a NEW folder `STS-Harvester` on the Desktop; touch nothing outside it)
1. `harvest.py` — for each lesson URL in `lessons.txt`:
   - Drive the owner's Chrome via the DevTools protocol (launch/attach with a remote-debugging port using his EXISTING profile so the login session is preserved; if Chrome must restart with the debug flag, that's fine — restore his tabs after).
   - Open the lesson, let the player start, capture every network request whose URL contains `master.m3u8`, saving the FULL request (URL + all headers, incl. any `authorization`) to `captures/<lesson-slug>.json`.
   - Classify the lesson kind (medias vs memberships) from the captured path.
2. `download.py` — for medias-kind captures: replay the master request with the captured headers via ffmpeg, pull the audio track, save `audio/<lesson-slug>.mp3`. For memberships-kind captures: attempt ONE replay with the complete captured header set (this is the authorization-header lead test) and log the exact HTTP result to `captures/memberships-test.log`.
3. `transcribe.py` — faster-whisper per the pattern above → `transcripts/<lesson-slug>.txt`.
4. `lessons.txt` — seed it with this one proven medias-kind lesson:
   https://customer.servicesthatscale.com/courses/products/e0e1094a-1b48-40c8-b971-a473532f3b78/modules/735f9174-51d2-494d-8c32-f4bf8fe40e3d/lessons/926633ca-e1b8-43c1-b412-1c237c63295f?template_id=Neue&lessonRouteName=post-overview-v2
5. Install what you need locally inside the folder (Python venv, ffmpeg if missing, faster-whisper). Keep downloads/installs inside the project folder or standard user locations.

## Run + report
- Execute the full pipeline on the seeded lesson. Success = a real transcript file whose opening lines are the lesson's actual spoken words.
- If any memberships-kind lesson URL is discoverable from the course pages you open, run the single header-replay test on ONE of them; otherwise state that no memberships URL was available to test.
- Write `REPORT.md` in the project folder: environment notes, what was built (files + how to re-run), the proof transcript path + its first 5 lines, the memberships lead-test result (exact status/error), every blocker hit, and anything you changed outside the folder (should be: nothing).

## Constraints
- Work ONLY inside `STS-Harvester` (plus standard tool installs). Don't modify browser settings, the course account, or any other files. Don't upload anything anywhere. Don't delete anything.
- One replay attempt per memberships lesson — no credential guessing, no header fuzzing beyond the captured set.
- The stream tokens expire in ~1 hour: capture and download in the same run.
- If the local-PC Codex environment cannot be used for this task (e.g., you are running in a cloud sandbox without access to this PC's Chrome/files), STOP and say so plainly as your first line — do not simulate the work.
