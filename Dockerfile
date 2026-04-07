FROM nvidia/cuda:12.3.2-runtime-ubuntu22.04

ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/tmp/huggingface
ENV MODEL_ID=ivrit-ai/whisper-large-v3-ct2
ENV DEFAULT_LANGUAGE=he
ENV DEFAULT_BEAM_SIZE=5
ENV MODEL_DEVICE=cuda
ENV MODEL_COMPUTE_TYPE=float16

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN ln -sf /usr/bin/python3 /usr/bin/python \
    && python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

COPY handler.py /app/handler.py

CMD ["python", "-u", "/app/handler.py"]
