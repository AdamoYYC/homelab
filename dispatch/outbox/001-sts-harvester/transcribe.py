"""Transcribe project MP3s via ffmpeg-predecoded 16 kHz mono samples."""
from __future__ import annotations
import os, subprocess, tempfile
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parent
AUDIO, TRANSCRIPTS = ROOT / "audio", ROOT / "transcripts"
FFMPEG = os.environ.get("STS_FFMPEG", "ffmpeg")

def samples_from_mp3(path):
    with tempfile.TemporaryDirectory(prefix="sts-whisper-") as td:
        wav = Path(td) / "audio.wav"
        subprocess.run([FFMPEG, "-y", "-i", str(path), "-ar", "16000", "-ac", "1",
                        "-c:a", "pcm_s16le", str(wav)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        raw = subprocess.run([FFMPEG, "-v", "error", "-i", str(wav), "-f", "f32le",
                              "-acodec", "pcm_f32le", "-ar", "16000", "-ac", "1", "pipe:1"],
                             check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        return np.frombuffer(raw, dtype=np.float32).copy()

def main():
    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    model = WhisperModel("base", device="cpu", compute_type="int8")
    for mp3 in sorted(AUDIO.glob("*.mp3")):
        samples = samples_from_mp3(mp3)
        segments, info = model.transcribe(samples, beam_size=5)
        text = "\n".join(s.text.strip() for s in segments).strip() + "\n"
        out = TRANSCRIPTS / f"{mp3.stem}.txt"
        out.write_text(text, encoding="utf-8")
        print(f"Wrote {out}; language={info.language}; duration={info.duration:.1f}s")

if __name__ == "__main__":
    main()
