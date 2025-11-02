# Docker Hub Registry Setup Guide

## Overview

This project uses Docker Hub as a container registry to store pre-built Docker images. This approach:
- **Faster workflows** - No need to rebuild the image on every run (saves 5-10 minutes per run)
- **Multi-architecture support** - Single build produces AMD64 and ARM64 images
- **Better caching** - Build cache stored in registry for faster rebuilds
- **Separation of concerns** - Build workflow separate from run workflow

## Architecture

### Two GitHub Actions Workflows

1. **Build and Push Workflow** (`.github/workflows/docker-build-push.yml`)
   - Triggers when Docker-related files change (src/, Dockerfile, entrypoint.sh, etc.)
   - Builds multi-architecture image (AMD64 + ARM64)
   - Pushes to Docker Hub registry
   - Tags: `latest`, `main-{sha}`, version tags (if release)

2. **Run Workflow** (`.github/workflows/myki-tracker-docker.yml`)
   - Triggers on schedule (daily 9 AM UTC) or manually
   - Pulls pre-built image from Docker Hub
   - Runs the Myki tracker
   - Uploads results and commits to repository

## Prerequisites

### 1. Docker Hub Account

If you don't have one:
1. Go to https://hub.docker.com/
2. Sign up for a free account
3. Verify your email

### 2. Create Docker Hub Access Token

**IMPORTANT:** Use an access token, not your password!

1. Log in to Docker Hub
2. Go to **Account Settings** → **Security** → **Access Tokens**
3. Click **New Access Token**
4. Configure:
   - **Description**: GitHub Actions - Myki Tracker
   - **Access permissions**: Read & Write
5. Click **Generate**
6. **Copy the token immediately** (you won't see it again!)

## GitHub Secrets Configuration

Add these secrets to your GitHub repository:

### Navigate to Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Add Required Secrets

Add the following three secrets:

#### 1. DOCKERHUB_USERNAME
- **Name**: `DOCKERHUB_USERNAME`
- **Value**: Your Docker Hub username (e.g., `yourusername`)

#### 2. DOCKERHUB_TOKEN
- **Name**: `DOCKERHUB_TOKEN`
- **Value**: The access token you generated (not your password!)

#### 3. MYKI_PASSWORD_KOUSTUBH25
- **Name**: `MYKI_PASSWORD_KOUSTUBH25`
- **Value**: Your Myki password (already set from previous setup)

### Verify Secrets

After adding, you should see:
```
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
MYKI_PASSWORD_KOUSTUBH25
```

## Initial Image Build

### Option 1: Trigger Build Workflow Manually

1. Go to **Actions** tab in your repository
2. Select **Build and Push Docker Image** workflow
3. Click **Run workflow**
4. Select branch: `main`
5. Click **Run workflow**

This will:
- Build the Docker image for AMD64 and ARM64
- Push to Docker Hub as `{username}/mykitracker:latest`
- Take approximately 5-10 minutes

### Option 2: Push Code to Trigger Automatic Build

If you push changes to any of these files, the build will trigger automatically:
- `src/**`
- `Dockerfile`
- `entrypoint.sh`
- `requirements.txt`
- `.github/workflows/docker-build-push.yml`

Example:
```bash
git add .
git commit -m "chore: trigger Docker build"
git push
```

## Verify Docker Hub Image

After the build completes:

1. Go to https://hub.docker.com/
2. Navigate to **Repositories**
3. You should see: `{username}/mykitracker`
4. Click on the repository
5. Verify:
   - **Tags**: `latest`, `main-{sha}`
   - **Architectures**: `linux/amd64`, `linux/arm64`
   - **Last pushed**: Recent timestamp

## Run the Myki Tracker

### Manual Trigger

1. Go to **Actions** tab
2. Select **Myki Tracker - Docker Deployment**
3. Click **Run workflow**
4. Select branch: `main`
5. Click **Run workflow**

This will:
- Pull the image from Docker Hub (fast - typically < 1 minute)
- Run the Myki tracker
- Upload results

### Automatic Schedule

The workflow runs automatically:
- **Daily at 9 AM UTC** (8 PM AEDT in Melbourne)
- Cron expression: `0 9 * * *`

No manual intervention needed!

## Workflow Behavior

### Build Workflow Triggers

The build workflow (`docker-build-push.yml`) runs when:

1. **Manual trigger** - Run workflow button in GitHub Actions
2. **Code changes** - Push to `main` branch with changes to:
   - Source code (`src/**`)
   - Dockerfile
   - Entrypoint script
   - Requirements
3. **Release** - When you publish a new release (optional)

### Run Workflow Triggers

The run workflow (`myki-tracker-docker.yml`) runs when:

1. **Manual trigger** - Run workflow button
2. **Daily schedule** - 9 AM UTC every day
3. **Config changes** - Push to `main` with changes to:
   - `config/myki_config.json` (be careful - this file should NOT be in git!)
   - Workflow file itself

## Image Tagging Strategy

Each build produces multiple tags:

### 1. `latest`
- Points to the most recent build from `main` branch
- Used by the run workflow by default
- Always up-to-date

### 2. `main-{git-sha}`
- Tagged with the Git commit SHA
- Example: `main-abc1234`
- Useful for debugging specific versions

### 3. Version tags (if using releases)
- Example: `v1.0.0`, `1.0`, `1`
- Created when you publish a GitHub release
- Semantic versioning

## Troubleshooting

### Error: "denied: requested access to the resource is denied"

**Cause:** Invalid Docker Hub credentials

**Fix:**
1. Verify `DOCKERHUB_USERNAME` is your actual Docker Hub username
2. Regenerate access token in Docker Hub
3. Update `DOCKERHUB_TOKEN` in GitHub secrets
4. Re-run the workflow

### Error: "repository does not exist"

**Cause:** Docker Hub repository not created yet

**Fix:** The repository is created automatically on first push. If this error persists:
1. Manually create the repository on Docker Hub:
   - Go to Docker Hub
   - Click **Create Repository**
   - Name: `myki-tracker`
   - Visibility: Private (recommended) or Public
2. Re-run the build workflow

### Build Workflow Fails with "buildx" Error

**Cause:** Docker Buildx not available

**Fix:** This should not happen on GitHub Actions runners, but if it does:
- Check the workflow uses `docker/setup-buildx-action@v3`
- Verify the workflow file is correct

### Run Workflow Can't Pull Image

**Cause:** Image not available in Docker Hub or authentication failed

**Fix:**
1. Check the build workflow completed successfully
2. Verify image exists on Docker Hub
3. Check `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets
4. Re-run the build workflow if needed

### Image Pull is Slow

**Cause:** Large image size (2.5GB+)

**Expected:** First pull takes 2-5 minutes depending on network speed

**Improvement:** Consider multi-stage builds or smaller base images (future optimization)

## Cost Considerations

### Docker Hub Free Tier

- **Free tier includes:**
  - Unlimited public repositories
  - 1 private repository
  - Unlimited pulls (with some rate limits)
  - 5 GB storage

- **This project uses:** ~2.5 GB for one multi-arch image

**Recommendation:** Use a private repository for this project (uses your 1 free private repo).

### GitHub Actions

- **Free tier:** 2,000 minutes/month for private repositories
- **Build workflow:** ~5-10 minutes per build
- **Run workflow:** ~2-3 minutes per run (much faster with pre-built image!)

**Monthly usage estimate:**
- Daily runs: 30 runs × 3 minutes = 90 minutes
- Builds (when code changes): ~5 builds × 10 minutes = 50 minutes
- **Total:** ~140 minutes/month (well within free tier)

## Security Best Practices

### 1. Use Access Tokens, Not Passwords
- ✅ Use `DOCKERHUB_TOKEN` (access token)
- ❌ Never use your Docker Hub password in GitHub secrets

### 2. Private Repository Recommended
- Contains your application code
- Set repository visibility to **Private** on Docker Hub

### 3. Limit Token Permissions
- Use **Read & Write** permissions (not Admin)
- Create separate tokens for different purposes

### 4. Rotate Tokens Regularly
- Regenerate access tokens every 6-12 months
- Update GitHub secrets after rotation

### 5. Never Commit Secrets
- Docker Hub credentials stay in GitHub secrets only
- Never add to `.env` or code

## Advanced Configuration

### Change Image Name

If you want to use a different image name:

1. **Update `docker-build-push.yml`:**
```yaml
images: ${{ secrets.DOCKERHUB_USERNAME }}/my-custom-name
```

2. **Update `myki-tracker-docker.yml`:**
```yaml
docker pull ${{ secrets.DOCKERHUB_USERNAME }}/my-custom-name:latest
docker tag ${{ secrets.DOCKERHUB_USERNAME }}/my-custom-name:latest myki-tracker:latest
```

### Use Specific Version Tags

To use a specific version instead of `latest`:

**In `myki-tracker-docker.yml`:**
```yaml
docker pull ${{ secrets.DOCKERHUB_USERNAME }}/myki-tracker:v1.0.0
docker tag ${{ secrets.DOCKERHUB_USERNAME }}/myki-tracker:v1.0.0 myki-tracker:latest
```

### Build on Release Only

To build only when you create a release:

**In `docker-build-push.yml`:**
```yaml
on:
  release:
    types: [published]
```

Then create releases:
```bash
git tag v1.0.0
git push origin v1.0.0
```

Or use GitHub UI to create releases.

## Monitoring

### Check Build Status

1. Go to **Actions** → **Build and Push Docker Image**
2. View recent runs
3. Check for failures

### Check Image Tags

1. Go to Docker Hub repository
2. Click **Tags** tab
3. Verify `latest` tag updated recently

### Check Pull Statistics

1. Docker Hub repository → **Insights**
2. View pull statistics
3. Monitor usage

## Migration from Local Builds

If you were previously building images locally in the workflow:

### What Changed

**Before:**
- Every run built the Docker image (~5-10 minutes)
- Build happened in the run workflow
- No image caching

**After:**
- Build happens once when code changes
- Run workflow just pulls pre-built image (~1 minute)
- Build cache stored in registry

### Benefits

- **Faster runs:** 2-3 minutes instead of 10-15 minutes
- **Lower GitHub Actions usage:** Save ~70% of workflow minutes
- **Better reliability:** Separate build failures from run failures
- **Multi-architecture:** Single build works on both AMD64 and ARM64

## Next Steps

After setup:

1. **Initial build:** Trigger the build workflow manually
2. **Verify image:** Check Docker Hub for the image
3. **Test run:** Trigger the run workflow manually
4. **Monitor:** Check first scheduled run the next day
5. **Iterate:** Push code changes and watch automatic rebuilds

## Support

If you encounter issues:

1. Check GitHub Actions logs for detailed error messages
2. Verify all secrets are set correctly
3. Check Docker Hub for image availability
4. Review this guide for troubleshooting steps

## Summary

**Setup steps:**
1. Create Docker Hub account and access token
2. Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` to GitHub secrets
3. Trigger initial build workflow
4. Verify image on Docker Hub
5. Run the tracker workflow

**Ongoing:**
- Code changes automatically trigger rebuilds
- Daily runs pull the latest image and execute
- No manual intervention needed

**Cost:** Free tier sufficient for this project

You're all set! The Myki tracker will now run autonomously using pre-built Docker images from Docker Hub.
