FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY alembic ./alembic
EXPOSE 8080
CMD ["gunicorn", "app.app:app", "-b", "0.0.0.0:8080", "--workers", "3", "--worker-class", "gthread"]
