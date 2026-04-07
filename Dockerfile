FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/tmp/huggingface
ENV MODEL_ID=ivrit-ai/whisper-large-v3-ct2
ENV DEFAULT_LANGUAGE=he
ENV DEFAULT_BEAM_SIZE=5
ENV MODEL_DEVICE=cuda
ENV MODEL_COMPUTE_TYPE=float16

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY handler.py /app/handler.py

CMD ["python", "-u", "/app/handler.py"]
