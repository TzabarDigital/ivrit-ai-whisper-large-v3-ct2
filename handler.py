import os
import tempfile
from pathlib import Path

import requests
import runpod
from faster_whisper import WhisperModel


MODEL_ID = os.getenv("MODEL_ID", "ivrit-ai/whisper-large-v3-ct2")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "he")
DEFAULT_BEAM_SIZE = int(os.getenv("DEFAULT_BEAM_SIZE", "5"))
DEFAULT_DEVICE = os.getenv("MODEL_DEVICE", "cuda")
DEFAULT_COMPUTE_TYPE = os.getenv("MODEL_COMPUTE_TYPE", "float16")

_MODEL = None


def parse_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = WhisperModel(
            MODEL_ID,
            device=DEFAULT_DEVICE,
            compute_type=DEFAULT_COMPUTE_TYPE,
        )
    return _MODEL


def download_file(audio_url: str) -> Path:
    response = requests.get(audio_url, stream=True, timeout=300)
    response.raise_for_status()

    suffix = Path(audio_url.split("?")[0]).suffix or ".audio"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                tmp_file.write(chunk)
        return Path(tmp_file.name)


def transcribe_audio(audio_path: Path, language: str, beam_size: int, vad_filter: bool):
    model = get_model()
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=beam_size,
        vad_filter=vad_filter,
    )

    segment_items = []
    full_text_parts = []

    for segment in segments:
        text = segment.text.strip()
        segment_items.append(
            {
                "start": segment.start,
                "end": segment.end,
                "text": text,
            }
        )
        if text:
            full_text_parts.append(text)

    return {
        "audio": str(audio_path.name),
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "duration_after_vad": getattr(info, "duration_after_vad", None),
        "text": " ".join(full_text_parts).strip(),
        "segments": segment_items,
        "model": MODEL_ID,
        "compute_type": DEFAULT_COMPUTE_TYPE,
        "device": DEFAULT_DEVICE,
    }


def handler(job):
    job_input = job.get("input", {})
    audio_url = job_input.get("audio_url") or job_input.get("audio")
    if not audio_url:
        return {"error": "Missing required field: audio_url"}

    language = job_input.get("language", DEFAULT_LANGUAGE)
    beam_size = int(job_input.get("beam_size", DEFAULT_BEAM_SIZE))
    vad_filter = parse_bool(job_input.get("vad_filter", True), default=True)

    runpod.serverless.progress_update(job, "Downloading audio")
    audio_path = download_file(audio_url)

    try:
        runpod.serverless.progress_update(job, "Transcribing audio")
        return transcribe_audio(
            audio_path=audio_path,
            language=language,
            beam_size=beam_size,
            vad_filter=vad_filter,
        )
    finally:
        try:
            audio_path.unlink(missing_ok=True)
        except OSError:
            pass


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
