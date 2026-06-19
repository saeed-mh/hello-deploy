# HelloDeploy beginner implementation guide

This guide assumes you use VS Code and a terminal. On Windows, use Git Bash for the commands unless a step says otherwise.

## Phase 1 - Install tools

Install Git, Docker Desktop, VS Code, and Python 3.12. Create a GitHub account. Verify:

```bash
git --version
docker --version
docker compose version
python --version
```

## Phase 2 - Open and understand the project

Extract the starter ZIP, rename the folder if desired, and open it in VS Code.

Important files:

- `app/main.py`: the web application and health/version/metrics endpoints.
- `tests/test_app.py`: automated tests.
- `Dockerfile`: builds the application image.
- `compose.yml`: runs the app behind Nginx.
- `deploy/deploy.sh`: deploys, checks health, and rolls back.
- `.github/workflows/pipeline.yml`: CI/CD workflow.

## Phase 3 - Run without Docker

Linux/macOS/Git Bash:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
ruff check app tests
pytest -v
uvicorn app.main:app --reload
```

On Windows PowerShell, activate using:

```powershell
.venv\Scripts\Activate.ps1
```

Open `http://127.0.0.1:8000`, then stop Uvicorn with Ctrl+C.

## Phase 4 - Run with Docker Compose

```bash
cp .env.example .env
docker compose -f compose.yml -f compose.local.yml config
docker compose -f compose.yml -f compose.local.yml up --build -d
docker compose -f compose.yml -f compose.local.yml ps
curl http://localhost:8080/health
curl http://localhost:8080/version
curl http://localhost:8080/metrics
```

Open `http://localhost:8080`. Stop it with:

```bash
docker compose -f compose.yml -f compose.local.yml down
```

## Phase 5 - Learn the minimum Git workflow

Inside the project folder:

```bash
git init
git branch -M main
git config user.name "YOUR NAME"
git config user.email "YOUR EMAIL"
git status
git add .
git commit -m "Initial HelloDeploy implementation"
```

Meaning:

- `git status`: shows changed/untracked files.
- `git add .`: stages the current changes.
- `git commit`: saves a named local snapshot.
- `git push`: uploads local commits to GitHub.
- `git pull`: downloads and combines remote changes.

For every future change, repeat:

```bash
git status
git add .
git commit -m "Describe the change"
git push
```

## Phase 6 - Create the GitHub repository

1. GitHub -> New repository.
2. Name it `hello-deploy`.
3. Prefer Public if your GitHub plan does not allow required reviewers on private repositories.
4. Do not add a README, `.gitignore`, or license because these files already exist.
5. Create the repository.
6. Copy the repository HTTPS URL.

Then run:

```bash
git remote add origin https://github.com/YOUR-USERNAME/hello-deploy.git
git remote -v
git push -u origin main
```

If GitHub asks for authentication, use the browser sign-in flow, GitHub CLI, or GitHub Desktop. Your normal GitHub password is not accepted as an HTTPS Git password.

## Phase 7 - Confirm CI works before deployment

Open GitHub -> Actions -> CI/CD Pipeline. The first three jobs should pass:

1. Lint, test, and validate.
2. Build and smoke-test container.
3. Publish immutable image.

The staging job will fail or wait because the VM and secrets do not exist yet. That is expected.

After publication, open the repository's Packages section. Make the container package public for the simplest student deployment. If it remains private, log the VM into GHCR using a read-only token.

## Phase 8 - Create an Ubuntu VM

Use an Ubuntu 24.04 LTS VM from your institution, Azure, AWS, Google Cloud, Oracle Cloud, or another provider. Record its public IP address.

Allow inbound TCP:

- 22 for SSH.
- 80 for production.
- 8080 for staging; restrict it to your IP where possible.

Connect using the provider's initial user:

```bash
ssh INITIAL_USER@VM_IP
```

Install Docker using Docker's current Ubuntu installation instructions. Verify:

```bash
sudo docker run hello-world
sudo docker compose version
```

Create the deployment user and folders:

```bash
sudo adduser deploy
sudo usermod -aG docker deploy
sudo mkdir -p /opt/hello-deploy/staging/deploy
sudo mkdir -p /opt/hello-deploy/production/deploy
sudo chown -R deploy:deploy /opt/hello-deploy
```

Log out and back in so the Docker group applies.

## Phase 9 - Create a dedicated deployment SSH key

On your own computer:

```bash
ssh-keygen -t ed25519 -C "hello-deploy-github-actions" -f ./hello_deploy_key
```

This creates:

- `hello_deploy_key`: private key; put it only in GitHub Secrets.
- `hello_deploy_key.pub`: public key; put it on the VM.

Copy the public key:

```bash
ssh-copy-id -i ./hello_deploy_key.pub deploy@VM_IP
```

If `ssh-copy-id` is unavailable, display the public key and paste it into `/home/deploy/.ssh/authorized_keys` on the VM.

Test before continuing:

```bash
ssh -i ./hello_deploy_key deploy@VM_IP
docker ps
exit
```

Capture the host key on your own computer:

```bash
ssh-keyscan -H VM_IP > ssh_known_hosts
cat ssh_known_hosts
```

## Phase 10 - Create GitHub environments

Repository -> Settings -> Environments.

Create `staging` with:

Secrets:

- `SSH_HOST`: VM public IP.
- `SSH_USER`: `deploy`.
- `SSH_PRIVATE_KEY`: complete contents of `hello_deploy_key`.
- `SSH_KNOWN_HOSTS`: complete contents of `ssh_known_hosts`.

Variables:

- `APPLICATION_URL`: `http://VM_IP:8080`.
- `FORCE_UNHEALTHY`: `false`.

Create `production` with the same four secrets and:

- `APPLICATION_URL`: `http://VM_IP`.

Configure a required reviewer for production. Enable Prevent self-review only when another reviewer is available.

## Phase 11 - Trigger the complete pipeline

Make a visible change in `app/main.py`, then:

```bash
git status
git add app/main.py
git commit -m "Trigger first automated deployment"
git push
```

Watch GitHub Actions. Expected sequence:

1. Quality checks pass.
2. Real container smoke test passes.
3. Commit-tagged image is pushed to GHCR.
4. Staging files are copied by SSH.
5. Staging becomes healthy.
6. `/version` is checked against the same commit SHA.
7. Production waits for approval.
8. After approval, production deploys and verifies.

Test from your computer:

```bash
curl http://VM_IP:8080/health
curl http://VM_IP:8080/version
curl http://VM_IP/health
curl http://VM_IP/version
```

## Phase 12 - Demonstrate automatic rollback safely

First complete at least one successful staging deployment.

In GitHub -> Settings -> Environments -> staging, change variable `FORCE_UNHEALTHY` to `true`.

Run Actions -> CI/CD Pipeline -> Run workflow. The candidate app becomes unhealthy. `deploy.sh` waits, detects failure, restores `.env.previous`, and starts the last healthy release. The staging deployment job is expected to fail because the new release was rejected, but the old release should still answer:

```bash
curl http://VM_IP:8080/health
curl http://VM_IP:8080/version
```

The version should be the previous successful SHA. Capture the workflow and terminal logs as evidence. Set `FORCE_UNHEALTHY` back to `false` afterward.

## Phase 13 - Useful troubleshooting commands

On the VM:

```bash
cd /opt/hello-deploy/staging
docker compose --project-name hello-staging ps
docker compose --project-name hello-staging logs --tail=100 app
docker compose --project-name hello-staging logs --tail=100 proxy
cat .env
docker inspect --format='{{json .State.Health}}' "$(docker compose --project-name hello-staging ps -q app)"
```

Common causes:

- SSH timeout: port 22/security group/firewall is wrong.
- Host verification failed: `SSH_KNOWN_HOSTS` is missing or stale.
- Docker permission denied: the deploy user needs a new login after joining the Docker group.
- GHCR pull denied: make the package public or authenticate the VM with a read-only package token.
- Nginx 502: inspect the app container and Compose network.
- Port already allocated: another service is using 80 or 8080.

## Phase 14 - Evidence to collect for the examiner

Capture screenshots of:

- Repository structure.
- Successful tests.
- Docker Compose containers and health.
- Full GitHub Actions pipeline.
- GHCR image tagged with the Git SHA.
- Production approval screen.
- Browser homepage.
- `/version` matching the GitHub commit.
- Rollback logs and the previous version still running.
- `/metrics` output and Docker log rotation settings.

## Git rescue commands

View recent commits:

```bash
git log --oneline --decorate -10
```

Discard an uncommitted change to one file:

```bash
git restore path/to/file
```

Unstage a file but keep its edit:

```bash
git restore --staged path/to/file
```

Download the newest GitHub commits before working:

```bash
git pull --rebase
```

Never commit `.env`, private keys, tokens, passwords, or VM credentials.
