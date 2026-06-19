# HelloDeploy

A self-verifying, rollback-safe Hello World deployment for Digital Systems 2.

## What makes it different

- The container image is tagged with the exact Git commit SHA.
- `/version` proves which commit is running.
- The deployment script waits for Docker health status.
- A failed release automatically restores the previous `.env` and image tag.
- Staging deploys automatically; production uses a protected GitHub environment.
- `/metrics` supplies basic Prometheus-format monitoring data.
- `FORCE_UNHEALTHY=true` provides a controlled rollback demonstration after one successful deployment.

## Endpoints

| Endpoint | Purpose |
|---|---|
| `/` | Deployment dashboard |
| `/health` | Liveness check |
| `/ready` | Readiness check |
| `/version` | Environment, Git SHA, and build time |
| `/metrics` | Prometheus-format metrics |

## Local quick start

```bash
cp .env.example .env
docker compose -f compose.yml -f compose.local.yml up --build -d
curl http://localhost:8080/health
curl http://localhost:8080/version
docker compose -f compose.yml -f compose.local.yml down
```

Read `BEGINNER_GUIDE.md` for the complete implementation sequence.
