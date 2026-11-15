FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install fastapi uvicorn requests
WORKDIR /app
COPY app.py .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
