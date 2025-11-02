# Raw Idea: Docker Headed Mode Deployment for Myki Tracker

## User Description

The user has a working Myki transaction tracker that successfully bypasses Cloudflare when running locally with:
- Headed Chrome browser (headless=False)
- Real Chrome profile with browsing history and cookies
- Playwright automation

The spec should explore running this exact setup in Docker with headed mode (using Xvfb virtual display) **locally first**.

## Goal

Prove that Docker + Xvfb + headed Chrome works locally before considering cloud deployment.

## Core Challenge

Replicating the working local headed Chrome setup in a Docker container while maintaining Cloudflare bypass success.

## Key Areas to Explore

- Xvfb (virtual display server) in Docker
- Chrome profile mounting from host system
- Docker configuration for headed Chrome
- Validating Cloudflare bypass still works

## Scope

- **IN SCOPE:** Local Docker deployment only
- **OUT OF SCOPE:** GitHub Actions, Cloud Run, or any cloud deployment (will be separate spec later)
