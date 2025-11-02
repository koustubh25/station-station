# GitHub Actions Deployment Guide

## Overview

This guide explains how to deploy the Myki Transaction Tracker using GitHub Actions with Docker.

**NEW:** This project now uses Docker Hub registry to store pre-built images, making workflows faster and more efficient!

## Architecture

The deployment uses **two separate workflows**:

1. **Build and Push Workflow** (`.github/workflows/docker-build-push.yml`)
   - Builds multi-architecture Docker image (AMD64 + ARM64)
   - Pushes to Docker Hub registry
   - Triggers when Docker-related files change
   - Takes 5-10 minutes

2. **Run Workflow** (`.github/workflows/myki-tracker-docker.yml`)
   - Pulls pre-built image from Docker Hub
   - Runs the Myki tracker
   - Uploads results and commits to repository
   - Takes 2-3 minutes (much faster!)

## What Gets Deployed

The run workflow (`.github/workflows/myki-tracker-docker.yml`) will:
1. Pull the pre-built Docker image from Docker Hub
2. Run the Myki tracker in a Docker container with Xvfb virtual display
3. Upload results (attendance.json) as artifacts
4. Optionally commit results back to the repository

## Prerequisites

### 1. Docker Hub Setup (Required)

**Before anything else, set up Docker Hub registry.**

See **[DOCKER_HUB_SETUP.md](DOCKER_HUB_SETUP.md)** for complete instructions.

Quick summary:
1. Create Docker Hub account (free)
2. Generate access token
3. Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` to GitHub secrets

### 2. Push Code to GitHub

First, push your code to a GitHub repository:

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Add Myki tracker with Docker deployment"

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 3. Configure GitHub Secrets

Add the following secrets to your repository:

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these three secrets:

**Docker Hub credentials:**
   - Name: `DOCKERHUB_USERNAME`
   - Value: Your Docker Hub username

   - Name: `DOCKERHUB_TOKEN`
   - Value: Your Docker Hub access token (not password!)

**Myki credentials:**
   - Name: `MYKI_PASSWORD_KOUSTUBH25`
   - Value: Your actual Myki password

**Important:**
- The password secret name must match the username pattern `MYKI_PASSWORD_{USERNAME_UPPERCASE}`
- For multiple users, add additional password secrets (e.g., `MYKI_PASSWORD_JOHN`)
- Never commit passwords to the repository!

### 4. Verify Configuration Files

Ensure these files exist in your repository:
- `config/myki_config.json` - User configuration (safe to commit - contains card numbers, not passwords)
- `config/myki_config.example.json` - Example configuration
- `Dockerfile` - Docker image definition
- `entrypoint.sh` - Container startup script
- `docker-run.sh` - Run script
- `docker-health-check.sh` - Validation script
- `.github/workflows/docker-build-push.yml` - Build workflow
- `.github/workflows/myki-tracker-docker.yml` - Run workflow

## Initial Setup: Build and Push Image

**IMPORTANT:** Before running the tracker, you must build and push the Docker image to Docker Hub.

### Trigger the Build Workflow

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Build and Push Docker Image** workflow
4. Click **Run workflow** button
5. Select branch: `main`
6. Click **Run workflow**

This will:
- Build multi-architecture image (AMD64 + ARM64)
- Push to Docker Hub as `{your-username}/mykitracker:latest`
- Take approximately 5-10 minutes

### Verify Image on Docker Hub

1. Go to https://hub.docker.com/
2. Navigate to **Repositories**
3. Find `{your-username}/mykitracker`
4. Verify tags: `latest`, `main-{sha}`
5. Verify architectures: `linux/amd64`, `linux/arm64`

## Running the Tracker

### Manual Trigger (Recommended for First Test)

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Myki Tracker - Docker Deployment** workflow
4. Click **Run workflow** button
5. Select branch (usually `main`)
6. Click **Run workflow**

### Automatic Triggers

The **run workflow** will automatically run:

**Daily Schedule:**
- Runs every day at 9 AM UTC (8 PM AEDT in Melbourne)
- Cron expression: `0 9 * * *`

**After Successful Build:**
- Automatically runs when the build workflow completes successfully
- Ensures the latest image is always tested after building

**Workflow:**
1. You push code changes (src/, Dockerfile, etc.)
2. Build workflow triggers and pushes image to Docker Hub
3. Run workflow triggers automatically after successful build
4. Run workflow pulls the new image and tests it

**Note:**
- The run workflow only triggers automatically after a **successful** build
- Failed builds won't trigger the run workflow

## Monitoring the Workflows

### View Build Workflow Logs

1. Go to **Actions** tab
2. Click on **Build and Push Docker Image** workflow
3. View recent runs
4. Check for successful image push

### View Run Workflow Logs

1. Go to **Actions** tab
2. Click on **Myki Tracker - Docker Deployment** workflow
3. Click on the workflow run
4. Click on the job name "Run Myki Tracker in Docker"
5. View logs for each step

### Check for Success

Look for these indicators in the **run workflow**:
- ✅ "Pull Docker image from Docker Hub" step completes successfully
- ✅ "Run Myki Tracker in Docker" step exits with code 0
- ✅ "Validate output" step passes health check
- ✅ Artifacts uploaded with attendance results

### Download Results

After a successful run:
1. Go to workflow run page
2. Scroll to **Artifacts** section
3. Download `attendance-results-{run-number}.zip`
4. Extract to view `attendance.json` and session files

### Debug Failed Runs

If the workflow fails:
1. Check the "Display container logs" step for errors
2. Download `debug-artifacts-{run-number}.zip`
3. Check screenshots for visual errors
4. Review output and auth_data directories

## Expected Behavior

### First Run

On the first run, the container will:
- Use an empty Chrome profile (no pre-warming)
- Attempt to authenticate with Myki
- May take longer due to Cloudflare verification
- **Cloudflare bypass success is NOT guaranteed** on first attempt

### Subsequent Runs

After successful authentication:
- Session files persist in artifacts
- Auth tokens may be reused (if not expired)
- Runs should be faster and more reliable

## Workflow Configuration

### Triggers

Edit `.github/workflows/myki-tracker-docker.yml` to change triggers:

```yaml
on:
  workflow_dispatch:  # Manual trigger

  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC

  push:
    branches: [main]
    paths: ['src/**', 'Dockerfile', ...]
```

### Scheduled Run Time

To change the schedule, edit the cron expression:
- `0 9 * * *` = 9 AM UTC daily
- `0 21 * * *` = 9 PM UTC daily (8 AM AEDT)
- `0 */6 * * *` = Every 6 hours

Use [crontab.guru](https://crontab.guru/) to generate cron expressions.

### Commit Results to Repository

The workflow can optionally commit results back to your repository.

Currently enabled for scheduled runs only:
```yaml
if: success() && github.event_name == 'schedule'
```

To enable for all runs, change to:
```yaml
if: success()
```

To disable completely, remove or comment out the commit step.

## Troubleshooting

### Issue: Workflow doesn't appear in Actions tab

**Solution:**
- Ensure `.github/workflows/myki-tracker-docker.yml` exists
- Check file is in `main` branch
- Verify YAML syntax is valid

### Issue: "Secret not found" error

**Solution:**
- Add `MYKI_PASSWORD_KOUSTUBH25` in repository secrets
- Check secret name matches exactly (case-sensitive)
- Ensure secret has a value (not empty)

### Issue: Docker build fails

**Solution:**
- Check Dockerfile syntax
- Verify all required files are in repository
- Check `docker-build.sh` script is executable
- Review build logs for specific errors

### Issue: Container exits with error code

**Solution:**
- Download debug artifacts
- Check screenshots for visual errors
- Review container logs in workflow
- Test Docker locally if possible (on AMD64 Linux)

### Issue: Cloudflare blocks authentication

**Solution:**
- This is expected on first runs without profile warming
- Consider pre-warming Chrome profile:
  1. Run container locally with manual Chrome session
  2. Visit Myki site, let Cloudflare build trust
  3. Save profile as GitHub artifact
  4. Download profile in workflow before running
- May require multiple attempts or different strategies
- **Important:** Cloudflare bypass in GitHub Actions is experimental

### Issue: No attendance data in output

**Solution:**
- Check workflow succeeded but no data found
- Verify `config/myki_config.json` has correct configuration
- Check date range in config (startDate, endDate)
- Review logs for API errors or authentication issues

## Cost Considerations

### GitHub Actions Free Tier

- Free tier: 2,000 minutes/month for private repositories
- Public repositories: Unlimited minutes
- Each run takes approximately 5-10 minutes
- Daily runs: ~30 runs/month = 150-300 minutes/month
- Well within free tier limits

### Storage

- Artifacts retained for 90 days (success) or 30 days (failure)
- Each artifact: <1 MB typically
- Free tier: 500 MB storage
- More than sufficient for this use case

## Advanced Configuration

### Add Multiple Users

To track multiple users:

1. Update `config/myki_config.json`:
```json
{
  "users": {
    "koustubh25": { ... },
    "john": { ... }
  }
}
```

2. Add secrets for each user:
   - `MYKI_PASSWORD_KOUSTUBH25`
   - `MYKI_PASSWORD_JOHN`

3. Update workflow to pass all passwords:
```yaml
- name: Prepare configuration
  run: |
    cat > .env << EOF
    MYKI_PASSWORD_KOUSTUBH25=${{ secrets.MYKI_PASSWORD_KOUSTUBH25 }}
    MYKI_PASSWORD_JOHN=${{ secrets.MYKI_PASSWORD_JOHN }}
    EOF
```

### Chrome Profile Warming (Advanced)

To pre-warm a Chrome profile for better Cloudflare bypass:

1. Run Docker locally with interactive shell
2. Manually browse to Myki site, authenticate
3. Save profile directory as artifact
4. Modify workflow to download profile before running

This is optional and may improve success rate.

## Next Steps

After successful deployment:

1. **Monitor first few runs** - Check success rate and errors
2. **Adjust schedule** - Change cron if needed
3. **Review artifacts** - Verify attendance data is correct
4. **Consider Cloud Run** - For even more reliable deployment (separate spec)

## Support

If you encounter issues:
1. Check workflow logs for errors
2. Download debug artifacts
3. Test Docker locally on AMD64 Linux if possible
4. Review Cloudflare bypass strategies in DOCKER_README.md
5. Consider consulting GitHub Actions documentation

## Files Reference

- **Workflow**: `.github/workflows/myki-tracker-docker.yml`
- **Configuration**: `config/myki_config.json`
- **Environment**: `.env` (created from secrets)
- **Docker Files**: `Dockerfile`, `entrypoint.sh`
- **Scripts**: `docker-build.sh`, `docker-run.sh`, `docker-health-check.sh`
- **Documentation**: `DOCKER_README.md`, `DOCKER_VOLUME_MOUNTS.md`

## Summary

GitHub Actions provides a free, automated way to run your Myki tracker in the cloud using Docker. While Cloudflare bypass success is not guaranteed, the implementation follows best practices and should work in most cases.

**First test is critical** - The workflow has not been tested on AMD64 Linux yet. Monitor the first run carefully and be prepared to iterate based on results.
