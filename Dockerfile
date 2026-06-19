FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --requirement requirements.txt

FROM python:3.12-slim AS runtime

ARG GIT_SHA=development
ARG BUILD_TIME=unknown

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION="${GIT_SHA}" \
    BUILD_TIME="${BUILD_TIME}"

LABEL org.opencontainers.image.title="HelloDeploy" \
      org.opencontainers.image.description="Self-verifying rollback-safe deployment demonstration" \
      org.opencontainers.image.revision="${GIT_SHA}"

RUN groupadd --system appgroup \
    && useradd --system --gid appgroup --create-home appuser

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY app ./app

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
