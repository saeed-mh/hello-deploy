import os
from datetime import UTC, datetime

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

APP_ENV = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "unknown")
BUILD_TIME = os.getenv("BUILD_TIME", "unknown")
FORCE_UNHEALTHY = os.getenv("FORCE_UNHEALTHY", "false").lower() == "true"

app = FastAPI(title="HelloDeploy", version=APP_VERSION)

REQUESTS = Counter(
    "hello_deploy_http_requests_total",
    "Total HTTP requests handled by HelloDeploy.",
    ["method", "path", "status"],
)
DEPLOYMENT_INFO = Gauge(
    "hello_deploy_info",
    "Information about the currently deployed release.",
    ["environment", "version", "build_time"],
)
DEPLOYMENT_INFO.labels(APP_ENV, APP_VERSION, BUILD_TIME).set(1)


@app.middleware("http")
async def count_requests(request: Request, call_next):
    response = await call_next(request)
    REQUESTS.labels(request.method, request.url.path, str(response.status_code)).inc()
    response.headers["X-App-Version"] = APP_VERSION
    return response


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    health_text = "Healthy" if not FORCE_UNHEALTHY else "Unhealthy (demo mode)"
    health_class = "healthy" if not FORCE_UNHEALTHY else "unhealthy"
    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>HelloDeploy</title>
        <style>
          body {{ font-family: system-ui, sans-serif; max-width: 760px; margin: 70px auto; padding: 24px; background: #f4f7fb; }}
          main {{ background: white; padding: 34px; border-radius: 18px; box-shadow: 0 8px 30px rgba(0,0,0,.08); }}
          .healthy {{ color: #0a7a31; font-weight: 700; }}
          .unhealthy {{ color: #b42318; font-weight: 700; }}
          code {{ background: #eef2f7; padding: 4px 8px; border-radius: 6px; word-break: break-all; }}
          a {{ color: #155eef; }}
        </style>
      </head>
      <body>
        <main>
          <h1>Hello World!</h1>
          <p>This application was deployed by a self-verifying CI/CD pipeline.</p>
          <p><strong>Environment:</strong> {APP_ENV}</p>
          <p><strong>Version:</strong> <code>{APP_VERSION}</code></p>
          <p><strong>Build time:</strong> {BUILD_TIME}</p>
          <p class="{health_class}">Status: {health_text}</p>
          <p><a href="/health">Health</a> · <a href="/ready">Readiness</a> · <a href="/version">Version proof</a> · <a href="/metrics">Metrics</a></p>
        </main>
      </body>
    </html>
    """


@app.get("/health")
def health(response: Response) -> dict[str, str]:
    if FORCE_UNHEALTHY:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy", "reason": "rollback demonstration enabled"}
    return {"status": "healthy"}


@app.get("/ready")
def ready(response: Response) -> dict[str, str]:
    if FORCE_UNHEALTHY:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not-ready"}
    return {"status": "ready"}


@app.get("/version")
def version() -> dict[str, str]:
    return {
        "environment": APP_ENV,
        "version": APP_VERSION,
        "build_time": BUILD_TIME,
        "current_time": datetime.now(UTC).isoformat(),
    }


@app.get("/metrics", response_class=PlainTextResponse)
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
