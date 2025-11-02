# Spec Initialization: Docker Headed Mode Deployment for Myki Tracker

## Initial Description

**Context:**
The user has a working Myki transaction tracker that:
- Successfully bypasses Cloudflare locally using headed Chrome (headless=False)
- Uses a real Chrome profile with browsing history and cookies
- Runs via Playwright with human behavior simulation
- Takes ~2 minutes per run

**Goal:**
Replicate this working setup in Docker with headed mode (Xvfb virtual display) for deployment on GitHub Actions (free tier).

**Key constraints:**
- MUST use FREE solutions only (GitHub Actions free tier: 2000 min/month)
- User prefers GitHub Actions over Google Cloud
- Current headed Chrome solution is the ONLY thing that works with Cloudflare
- Must maintain the same success rate as local implementation

**Focus:**
Making Docker + headed mode work specifically, NOT alternative approaches like proxies or services.
