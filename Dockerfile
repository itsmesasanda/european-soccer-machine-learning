FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY huggingface_app/requirements.txt /app/huggingface_app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/huggingface_app/requirements.txt

COPY huggingface_app /app/huggingface_app
COPY models/team_profiling /app/models/team_profiling

EXPOSE 7860

CMD ["uvicorn", "huggingface_app.app:app", "--host", "0.0.0.0", "--port", "7860"]
