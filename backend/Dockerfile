FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Non-root and stateless: all state lives in Postgres. Numeric UID so Kubernetes can verify it.
RUN useradd --system --no-create-home --uid 10001 appuser
USER 10001

EXPOSE 8000

# WEB_CONCURRENCY (read by uvicorn) sets the worker count; see README "Scaling".
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
