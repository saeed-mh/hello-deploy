# HelloDeploy

## Team and Evaluation Guide

**Project:** Automated Deployment of a Hello World Application
**Module:** Digital Systems 2
**Document type:** Technical implementation, collaboration, operation, and evaluation guide
**Repository:** `https://github.com/akanksv/hello-deploy`

---

# 1. Document purpose

The document provides a formal overview of the HelloDeploy proof of concept.

* System architecture
* Repository structure
* Local development
* Docker configuration
* CI/CD stages
* Git collaboration
* Staging and production deployment
* Security controls
* Health verification
* Rollback behaviour
* Troubleshooting
* Evaluation evidence
* Known limitations

Personal workstation paths, personal credentials, private keys, passwords, and secret values are excluded.

---

# 2. Project objective

HelloDeploy demonstrates a complete automated deployment workflow for a simple FastAPI web application.

Application complexity remains intentionally low. Deployment quality represents the primary project focus.

Core objectives include:

* Source control through Git and GitHub
* Collaborative development through feature branches and pull requests
* Automated linting and testing
* Docker image creation
* Docker Compose service orchestration
* Immutable image publication
* SSH-based deployment
* Separate staging and production environments
* Application health verification
* Deployed commit verification
* Automatic rollback
* Basic monitoring and logging

---

# 3. Deployment architecture

The deployment environment consists of a student-provisioned Ubuntu virtual machine.

The virtual machine runs through Oracle VirtualBox on a Windows host.

The deployment architecture follows the sequence below:

```text
Developer workstation
        │
        ▼
GitHub repository
        │
        ▼
GitHub Actions
        ├── Source checkout
        ├── Dependency installation
        ├── Linting
        ├── Automated testing
        ├── Docker Compose validation
        ├── Container image build
        ├── Real-container smoke test
        └── Image publication to GHCR
                     │
                     ▼
Windows self-hosted GitHub Actions runner
                     │
                     ▼
                  SSH
                     │
                     ▼
Ubuntu VirtualBox VM
        ├── Staging environment
        └── Production environment
```

The GitHub-hosted runner performs quality checks, tests, image builds, and image publication.

The self-hosted Windows runner performs deployment jobs requiring access to the private VirtualBox network.

The Ubuntu virtual machine runs Docker and Docker Compose.

---

# 4. Environment separation

Two logical environments operate on the Ubuntu virtual machine.

| Environment | Purpose                   | Compose project    | Public port |
| ----------- | ------------------------- | ------------------ | ----------: |
| Staging     | Pre-production validation | `hello-staging`    |      `8080` |
| Production  | Final approved release    | `hello-production` |        `80` |

Separate deployment directories support environment isolation:

```text
/opt/hello-deploy/staging
/opt/hello-deploy/production
```

Separate GitHub environments provide independent secrets, variables, approval rules, and deployment records.

Physical infrastructure remains shared between staging and production.

---

# 5. Runtime-specific values

Machine-specific values remain outside the shared documentation.

Examples include:

* Windows repository location
* Windows runner installation directory
* VirtualBox machine name
* Ubuntu VM address
* SSH private-key location
* SSH host-key value
* GitHub secret values
* Administrator credentials

Runtime-specific values belong in:

* GitHub environment settings
* Restricted operations runbook
* Password manager
* Infrastructure inventory

Generic placeholders appear throughout the document:

| Placeholder                       | Meaning                           |
| --------------------------------- | --------------------------------- |
| `<REPOSITORY_URL>`                | Git repository URL                |
| `<VM_HOST>`                       | Ubuntu VM hostname or address     |
| `<DEPLOY_USER>`                   | Restricted SSH deployment account |
| `<SSH_KEY_PATH>`                  | Local private-key location        |
| `<STAGING_URL>`                   | Staging application URL           |
| `<PRODUCTION_URL>`                | Production application URL        |
| `<RUNNER_INSTALLATION_DIRECTORY>` | Self-hosted runner directory      |

---

# 6. Repository structure

```text
hello-deploy/
├── .github/
│   └── workflows/
│       └── pipeline.yml
├── app/
│   ├── __init__.py
│   └── main.py
├── deploy/
│   ├── deploy.sh
│   └── nginx.conf
├── tests/
├── .dockerignore
├── .env.example
├── Dockerfile
├── compose.yml
├── compose.local.yml
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── BEGINNER_GUIDE.md
```

## 6.1 File responsibilities

| File or directory                | Responsibility                               |
| -------------------------------- | -------------------------------------------- |
| `app/main.py`                    | FastAPI application and service endpoints    |
| `tests/`                         | Automated application tests                  |
| `Dockerfile`                     | Container image definition                   |
| `.dockerignore`                  | Docker build-context exclusions              |
| `compose.yml`                    | Staging and production services              |
| `compose.local.yml`              | Local development override                   |
| `deploy/nginx.conf`              | Nginx reverse-proxy configuration            |
| `deploy/deploy.sh`               | Deployment, verification, and rollback logic |
| `.github/workflows/pipeline.yml` | CI/CD workflow                               |
| `.env.example`                   | Example environment configuration            |
| `README.md`                      | Project summary                              |
| `BEGINNER_GUIDE.md`              | Team and evaluation documentation            |

---

# 7. Application endpoints

| Endpoint   | Purpose                                  |
| ---------- | ---------------------------------------- |
| `/`        | Hello World web page                     |
| `/health`  | Application health status                |
| `/ready`   | Application readiness status             |
| `/version` | Environment, Git SHA, and build metadata |
| `/metrics` | Basic monitoring metrics                 |

Expected health response:

```json
{
  "status": "healthy"
}
```

The `/version` endpoint provides proof of the deployed source revision.

Example response structure:

```json
{
  "environment": "production",
  "version": "<FULL_GIT_SHA>",
  "build_time": "<UTC_BUILD_TIME>",
  "current_time": "<UTC_CURRENT_TIME>"
}
```

---

# 8. Development prerequisites

Every development workstation requires:

* Git
* Python 3.12
* GitHub repository access
* Text editor or integrated development environment

Docker Desktop remains recommended for local container testing.

Infrastructure access remains unnecessary for normal application development.

Restricted infrastructure access includes:

* Ubuntu VM access
* SSH private key
* GitHub environment secrets
* Self-hosted runner administration
* Production environment administration

---

# 9. Repository setup

Clone the repository:

```bash
git clone <REPOSITORY_URL>
cd hello-deploy
```

Create local environment configuration:

```bash
cp .env.example .env
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the environment on Windows Git Bash:

```bash
source .venv/Scripts/activate
```

Activate the environment on Linux or macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
```

Run quality checks:

```bash
ruff check app tests
pytest --verbose
```

All commands operate from the repository root unless another location appears explicitly.

---

# 10. Local Docker development

Start the local application:

```bash
docker compose \
  -f compose.yml \
  -f compose.local.yml \
  up --build -d
```

Display service status:

```bash
docker compose \
  -f compose.yml \
  -f compose.local.yml \
  ps
```

Verify application health:

```bash
curl http://localhost:8080/health
```

Verify version information:

```bash
curl http://localhost:8080/version
```

Display logs:

```bash
docker compose \
  -f compose.yml \
  -f compose.local.yml \
  logs -f
```

Stop the local environment:

```bash
docker compose \
  -f compose.yml \
  -f compose.local.yml \
  down
```

Local Docker services remain separate from staging and production services.

---

# 11. Git collaboration model

Direct changes to `main` remain discouraged.

Every project change follows a feature-branch workflow.

## 11.1 Start a new change

```bash
git switch main
git pull origin main
git switch -c feature/descriptive-name
```

Example:

```bash
git switch -c feature/improve-health-endpoint
```

## 11.2 Validate a change

```bash
ruff check app tests
pytest --verbose
git diff --check
git status
```

## 11.3 Commit a change

```bash
git add .
git commit -m "Describe the implemented change"
```

## 11.4 Push a branch

```bash
git push -u origin feature/descriptive-name
```

---

# 12. Pull-request process

A pull request compares a feature branch against `main`.

Required branch direction:

```text
feature branch → main
```

GitHub navigation:

```text
Repository
→ Pull requests
→ New pull request
```

Required branch selection:

```text
base: main
compare: feature/descriptive-name
```

A pull request should contain:

* Clear title
* Change summary
* Technical details
* Testing evidence
* Relevant screenshots, when applicable

Required pull-request checks:

```text
Lint, test, and validate
Build and smoke-test container
```

Image publication and deployment remain disabled for pull-request events.

A second team member should review every pull request.

Review procedure:

```text
Files changed
→ Review changes
→ Approve
→ Submit review
```

---

# 13. CI/CD pipeline overview

The workflow file appears at:

```text
.github/workflows/pipeline.yml
```

Supported triggers include:

* Pull-request creation or update
* Push to `main`
* Manual workflow execution

Publishing and deployment remain restricted to `main`.

Manual execution from a feature branch performs validation only.

---

# 14. CI quality stage

The quality stage performs:

1. Repository checkout
2. Python 3.12 configuration
3. Dependency installation
4. Ruff linting
5. Pytest execution
6. Docker Compose validation

Relevant commands:

```bash
ruff check app tests
pytest --verbose
docker compose \
  -f compose.yml \
  -f compose.local.yml \
  config --quiet
```

A failed quality check prevents all later stages.

---

# 15. Container smoke-test stage

The container-test stage performs:

1. Docker image build
2. Container startup
3. Health-endpoint request
4. Version-endpoint request
5. Git SHA comparison
6. Failure-log output
7. Test-container cleanup

The test confirms operation of:

* Dockerfile
* Application startup command
* Published port
* Health endpoint
* Version metadata
* Embedded Git commit

A failed smoke test prevents image publication and deployment.

---

# 16. Image publication stage

Successful main-branch validation produces an immutable container image.

Image registry:

```text
GitHub Container Registry
```

Image naming format:

```text
ghcr.io/<repository-owner>/<repository-name>:<FULL_GIT_SHA>
```

The Git commit SHA functions as an immutable image tag.

The publication job receives package-write permission.

Other jobs receive read-only repository permission.

---

# 17. Staging deployment stage

The staging deployment job runs on the Windows self-hosted runner.

Required operations include:

1. Repository checkout
2. Temporary SSH configuration
3. SSH connectivity test
4. Deployment-file transfer
5. Remote deployment-script execution
6. Container health verification
7. Staging endpoint verification
8. Git SHA verification
9. Temporary SSH-file removal

Remote deployment directory:

```text
/opt/hello-deploy/staging
```

Compose project:

```text
hello-staging
```

Public port:

```text
8080
```

A failed staging deployment prevents production deployment.

---

# 18. Production deployment stage

The production deployment starts only after successful staging verification.

Remote deployment directory:

```text
/opt/hello-deploy/production
```

Compose project:

```text
hello-production
```

Public port:

```text
80
```

A protected GitHub production environment can require approval before production deployment.

Recommended protection settings:

* Required reviewer
* Prevention of self-review
* Main-branch deployment restriction
* Environment-specific secrets
* Environment-specific variables

---

# 19. GitHub environment configuration

## 19.1 Staging environment

Required secrets:

```text
SSH_HOST
SSH_USER
SSH_PRIVATE_KEY
SSH_KNOWN_HOSTS
```

Required variables:

```text
APPLICATION_URL=<STAGING_URL>
FORCE_UNHEALTHY=false
```

## 19.2 Production environment

Required secrets:

```text
SSH_HOST
SSH_USER
SSH_PRIVATE_KEY
SSH_KNOWN_HOSTS
```

Required variable:

```text
APPLICATION_URL=<PRODUCTION_URL>
```

Production deployment forces:

```text
FORCE_UNHEALTHY=false
```

Secret values must never appear in:

* Source files
* Workflow logs
* Screenshots
* Reports
* Presentation slides
* Chat messages

---

# 20. Deployment preparation

Before a merge into `main`, the following conditions must exist:

```text
[ ] Host computer running
[ ] Internet connection available
[ ] VirtualBox running
[ ] Ubuntu VM running
[ ] Docker service available
[ ] Self-hosted runner online
[ ] Self-hosted runner waiting for jobs
[ ] Staging failure simulation disabled
[ ] Pull-request checks successful
[ ] Production reviewer available
```

The self-hosted runner starts from the configured runner directory:

```powershell
Set-Location <RUNNER_INSTALLATION_DIRECTORY>
.\run.cmd
```

Expected runner status:

```text
Listening for Jobs
```

The runner terminal must remain open during deployment.

---

# 21. Deployment verification

## 21.1 Staging verification

```bash
curl <STAGING_URL>/health
curl <STAGING_URL>/version
```

## 21.2 Production verification

```bash
curl <PRODUCTION_URL>/health
curl <PRODUCTION_URL>/version
```

Required health result:

```json
{
  "status": "healthy"
}
```

Required version result:

```text
Returned Git SHA = GitHub Actions workflow Git SHA
```

The pipeline performs the same comparison automatically.

---

# 22. Ubuntu deployment inspection

Establish an SSH connection:

```bash
ssh -i <SSH_KEY_PATH> <DEPLOY_USER>@<VM_HOST>
```

Display running containers:

```bash
docker ps
```

Display staging services:

```bash
docker compose \
  -p hello-staging \
  -f /opt/hello-deploy/staging/compose.yml \
  ps
```

Display production services:

```bash
docker compose \
  -p hello-production \
  -f /opt/hello-deploy/production/compose.yml \
  ps
```

Display staging logs:

```bash
docker compose \
  -p hello-staging \
  -f /opt/hello-deploy/staging/compose.yml \
  logs --tail=100
```

Display production logs:

```bash
docker compose \
  -p hello-production \
  -f /opt/hello-deploy/production/compose.yml \
  logs --tail=100
```

---

# 23. Health-check strategy

Health validation occurs at several levels.

| Level                | Validation                           |
| -------------------- | ------------------------------------ |
| Application          | `/health` endpoint                   |
| Container            | Docker health check                  |
| Compose              | Health-based service dependency      |
| Deployment script    | Repeated container-health inspection |
| Pipeline             | External HTTP health request         |
| Release verification | `/version` Git SHA comparison        |

Multiple validation levels reduce false-positive deployment results.

A responding web server alone does not prove correct release deployment.

Commit verification confirms correct release identity.

---

# 24. Rollback strategy

The deployment script stores the previous deployment configuration before applying a new release.

Deployment sequence:

1. Previous configuration backup
2. New image pull
3. Service recreation
4. Container health polling
5. Success confirmation or failure detection
6. Previous configuration restoration after failure
7. Previous service recreation
8. Failed pipeline result

Rollback protects the last healthy deployment.

Production deployment remains blocked after staging failure.

---

# 25. Controlled rollback demonstration

A staging environment variable supports intentional health failure:

```text
FORCE_UNHEALTHY=true
```

Demonstration procedure:

1. Record the current staging version.
2. Enable the staging failure variable.
3. Start a manual workflow from `main`.
4. Observe successful build and publication.
5. Observe staging health failure.
6. Observe rollback messages.
7. Confirm production-stage cancellation.
8. Confirm previous staging version availability.
9. Restore `FORCE_UNHEALTHY=false`.
10. Run a normal workflow.

Production must never use the failure simulation.

---

# 26. Security controls

Implemented controls include:

* Dedicated deployment account
* SSH key authentication
* SSH host-key verification
* GitHub environment secrets
* Main-branch deployment restriction
* Pull-request validation without deployment
* Job-level package permissions
* Temporary SSH-file cleanup
* Deployment timeouts
* Immutable Git SHA image tags
* Non-root application container
* Read-only container filesystem
* Docker log rotation
* Staging-before-production validation
* Optional production approval
* Production concurrency protection

Sensitive infrastructure information remains restricted to designated maintainers.

---

# 27. Monitoring and logging

Basic monitoring includes:

* `/health`
* `/ready`
* `/metrics`
* Docker health status
* Application logs
* Nginx access logs
* Nginx error logs
* Docker log rotation
* GitHub Actions deployment logs

Common inspection commands:

```bash
docker ps
docker compose logs --tail=100
docker inspect <CONTAINER_ID>
```

Metrics remain suitable for proof-of-concept monitoring.

---

# 28. Team responsibility model

Common inspection commands:

````bash
docker ps
docker compose logs --tail=100
docker inspect <CONTAINER_ID

| Role | Main responsibility |
|---|---|
| Application owner | FastAPI application and endpoints |
| Test owner | Automated tests and linting |
| Container owner | Dockerfile and image configuration |
| Compose owner | Docker Compose, Nginx, and networking |
| CI owner | Quality, test, and publication jobs |
| Infrastructure owner | Ubuntu VM, SSH, and self-hosted runner |
| Reliability owner | Rollback, monitoring, documentation, and evidence |

Every team member should complete:

- At least one GitHub issue
- At least one feature branch
- At least one meaningful commit
- At least one pull request
- At least one review
- At least one presentation responsibility

Direct access to production infrastructure remains limited to designated maintainers.

---

# 29. Evaluation mapping

| Evaluation area | Project evidence |
|---|---|
| Architecture and deployment strategy | Architecture diagram, environment description, CI/CD flow |
| Dockerfile and Docker Compose | Multi-stage image, health check, Nginx, networks, Compose services |
| CI/CD build and test | Ruff, Pytest, Compose validation, real-container smoke test |
| Automated SSH deployment | Self-hosted runner, SCP, SSH, Compose deployment |
| Documentation and troubleshooting | Repository documentation, runbook, screenshots, issue history |
| Health-check bonus | Application, container, Compose, deployment, and pipeline health checks |
| Rollback bonus | Controlled unhealthy staging release and automatic restoration |
| Environment-variable bonus | GitHub environment variables and `.env` configuration |
| Monitoring/logging bonus | Metrics endpoint, Docker logs, Nginx logs, log rotation |
| Separate-environment bonus | Staging and production Compose projects and GitHub environments |

---

# 30. Demonstration sequence

Recommended demonstration order:

1. Architecture diagram
2. Repository structure
3. Pull-request workflow
4. Passing quality checks
5. Container smoke test
6. Immutable GHCR image
7. Self-hosted runner status
8. Staging deployment
9. Staging health response
10. Staging commit verification
11. Production approval
12. Production deployment
13. Production health response
14. Production commit verification
15. Rollback evidence
16. Security controls
17. Known limitations

Recorded evidence should remain available as a fallback for live-demo failure.

---

# 31. Required evaluation evidence

Recommended screenshots and records:

- Repository overview
- Architecture diagram
- Pull request with approval
- Passing quality job
- Passing container-test job
- Published GHCR image
- Full successful workflow
- Staging deployment job
- Production approval screen
- Production deployment job
- Running Docker containers
- Staging homepage
- Production homepage
- Staging `/health`
- Production `/health`
- `/version` response with matching Git SHA
- `/metrics` output
- Failed staging deployment
- Rollback log
- Previous healthy release after rollback

Secret values must remain hidden.

---

# 32. Troubleshooting

## 32.1 Pull request contains no differences

Possible causes:

- Identical feature and main branches
- Commit created on `main`
- Feature branch missing the intended commit

Diagnostic commands:

```bash
git branch --show-current
git status
git log --oneline --decorate --graph --all -10
````

---

## 32.2 Git opens a pager

Git may display long output through `less`.

Exit command:

```text
q
```

---

## 32.3 Deployment job remains queued

Possible causes:

* Offline self-hosted runner
* Runner-label mismatch
* Closed runner terminal
* Host computer without internet access

Required runner status:

```text
Listening for Jobs
```

---

## 32.4 SSH connection failure

Diagnostic command:

```bash
ssh -i <SSH_KEY_PATH> <DEPLOY_USER>@<VM_HOST>
```

Possible causes:

* Ubuntu VM offline
* Incorrect VM address
* SSH service unavailable
* Incorrect private key
* Incorrect GitHub secret
* Host-key mismatch

---

## 32.5 Docker permission failure

A deployment account requires Docker access.

Administrative correction:

```bash
sudo usermod -aG docker <DEPLOY_USER>
```

A new login session remains necessary after group modification.

---

## 32.6 Nginx 502 response

Possible causes:

* Application container stopped
* Application container unhealthy
* Incorrect Docker network
* Incorrect proxy destination

Diagnostic commands:

```bash
docker ps
docker compose logs app
docker compose logs proxy
```

---

## 32.7 Incorrect release version

Compare the deployed version against the workflow commit:

```bash
curl <PRODUCTION_URL>/version
```

A SHA mismatch indicates an incorrect image or stale deployment.

The pipeline should fail during commit verification.

---

# 33. Known limitations

The proof of concept contains the following limitations:

* Shared physical VM for staging and production
* Single physical host
* Private VirtualBox network
* Host-dependent deployment availability
* Self-hosted runner dependency
* Machine-specific runner configuration
* No high-availability deployment
* No external load balancer
* No public domain requirement
* No managed cloud infrastructure
* No automatic VM recovery

The limitations remain acceptable for a deployment proof of concept when documented clearly.

---

# 34. Final readiness checklist

```text
[ ] Repository accessible
[ ] Architecture diagram available
[ ] README complete
[ ] Team guide complete
[ ] Dockerfile validated
[ ] Compose configuration validated
[ ] Tests passing
[ ] Pull-request checks passing
[ ] GHCR image available
[ ] Ubuntu VM running
[ ] Docker running
[ ] Self-hosted runner online
[ ] Staging deployment healthy
[ ] Production deployment healthy
[ ] Git SHA verification successful
[ ] Production approval configured
[ ] Rollback evidence available
[ ] Metrics evidence available
[ ] Logs available
[ ] Secrets hidden
[ ] Presentation responsibilities assigned
[ ] Backup screenshots available
```

---

# 35. Conclusion

HelloDeploy demonstrates a complete modern deployment process for a simple web application.

The implementation combines:

* Git collaboration
* Automated quality checks
* Containerization
* Immutable image publication
* SSH deployment
* Environment separation
* Health verification
* Commit verification
* Controlled production promotion
* Automatic rollback
* Security-conscious secret handling

The resulting proof of concept exceeds a basic Hello World deployment by providing traceable, verifiable, and failure-aware release automation.
