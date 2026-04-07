# Runpod Ivrit Worker

Custom Runpod Serverless worker that mirrors the local transcription setup:

- model: `ivrit-ai/whisper-large-v3-ct2`
- engine: `faster-whisper`
- language: `he`
- `beam_size=5`
- `vad_filter=True`

## Files

- `handler.py` - Runpod handler
- `Dockerfile` - container image
- `requirements.txt` - Python dependencies
- `test_input.json` - local test payload

## Request body

```json
{
  "input": {
    "audio_url": "https://your-file-url.mp3",
    "language": "he",
    "beam_size": 5,
    "vad_filter": true
  }
}
```

`audio` is also accepted as an alias for `audio_url`.

## Response shape

```json
{
  "audio": "file.mp3",
  "language": "he",
  "language_probability": 0.99,
  "duration": 123.4,
  "duration_after_vad": 120.1,
  "text": "Full transcript...",
  "segments": [
    {
      "start": 0.0,
      "end": 2.7,
      "text": "..."
    }
  ],
  "model": "ivrit-ai/whisper-large-v3-ct2",
  "compute_type": "float16",
  "device": "cuda"
}
```

## Deploy flow

1. Create a GitHub repo and push this folder.
2. In Runpod, create a new custom Serverless endpoint from that repo or image.
3. Keep the endpoint on Flex with `Active workers = 0`.
4. Use a 24GB or larger GPU.
5. Send requests from Pabbly to:

```text
POST https://api.runpod.ai/v2/<ENDPOINT_ID>/run
```

Headers:

```text
Authorization: Bearer <RUNPOD_API_KEY>
Content-Type: application/json
```

Body:

```json
{
  "input": {
    "audio_url": "{{res2.webContentLink}}",
    "language": "he",
    "beam_size": 5,
    "vad_filter": true
  }
}
```

Then poll:

```text
GET https://api.runpod.ai/v2/<ENDPOINT_ID>/status/<JOB_ID>
```

## Notes

- Google Drive links may fail if they are not directly downloadable. If needed, let Pabbly download the file first and upload it to a storage URL with direct access.
- This worker does transcription only. Speaker labels and real names should be added in a second step after transcript retrieval.
