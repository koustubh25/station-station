# Dev.to Integration Setup

This document explains how to set up automatic publishing of blog posts to Dev.to from this GitHub repository.

## Overview

The blog posts are automatically synchronized to Dev.to using GitHub Actions whenever changes are pushed to the `posts/` directory. This setup uses the [publish-devto](https://github.com/sinedied/publish-devto) GitHub Action.

## Prerequisites

1. A Dev.to account
2. A Dev.to API key
3. GitHub repository with Actions enabled

## Setup Steps

### 1. Get Your Dev.to API Key

1. Log in to [Dev.to](https://dev.to/)
2. Go to Settings → Extensions → DEV Community API Keys
3. Generate a new API key
4. Copy the API key (you won't be able to see it again)

### 2. Add API Key to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `DEVTO_TOKEN`
5. Value: Paste your Dev.to API key
6. Click "Add secret"

### 3. Verify Workflow Configuration

The workflow is already configured in `.github/workflows/publish-devto.yml`. It will:

- Trigger on pushes to `main` branch that modify files in `agent-os/specs/2025-11-03-technical-blog-sdd/posts/`
- Can also be triggered manually via "workflow_dispatch"
- Sync all markdown files in the `posts/` directory to Dev.to

## Blog Post Format

Each blog post must have Dev.to front matter at the top:

```markdown
---
title: "Your Post Title"
published: false
description: "A brief description of your post"
tags: tag1, tag2, tag3, tag4
series: "Series Name (if applicable)"
canonical_url:
---

Post content here...
```

### Front Matter Fields

- **title** (required): The post title - includes part number (e.g., "Part 1: Introduction...")
- **published** (required): `true` to publish, `false` to save as draft
- **description** (required): Brief description (max 158 characters recommended)
- **tags** (required): Up to 4 tags, comma-separated (use existing Dev.to tags for better discoverability)
- **series** (optional): Series name if this is part of a series
- **cover_image** (optional): URL to cover image (see Cover Images section below)
- **canonical_url** (optional): If you're cross-posting from another blog

### Cover Images

To add a cover image to your posts:

1. **Option 1: Host in GitHub repository**
   - Create an `images/` folder in your repository
   - Add your cover image (recommended size: 1000x420 pixels)
   - Commit and push
   - Use the raw GitHub URL: `https://raw.githubusercontent.com/username/repo/main/images/cover.jpg`

2. **Option 2: Use external hosting**
   - Upload to Unsplash, Imgur, or similar service
   - Copy the direct image URL
   - Add to `cover_image` field

3. **Option 3: Upload directly to Dev.to**
   - Leave `cover_image` field blank
   - After the post syncs, edit it on Dev.to
   - Upload cover image through Dev.to's editor
   - Subsequent syncs won't override the image

### Linking Posts in the Series

All posts include placeholder links at the bottom in the "About This Series" section. After publishing:

1. Publish all 5 posts to Dev.to (they'll start as drafts)
2. Note the URL for each post on Dev.to
3. Update the markdown files to replace `#` with actual Dev.to URLs:
   ```markdown
   - [**Part 1: Introduction to Spec-Driven Development**](https://dev.to/username/part-1-slug)
   ```
4. Commit and push - the action will update the posts with working links

## Publishing Workflow

### Publishing New Posts

1. Create or edit markdown files in `agent-os/specs/2025-11-03-technical-blog-sdd/posts/`
2. Ensure front matter is correct
3. Set `published: false` initially to create as draft
4. Commit and push to `main` branch
5. GitHub Actions will sync the post to Dev.to as a draft
6. Review the draft on Dev.to
7. When ready to publish:
   - Update `published: true` in the markdown file
   - Commit and push
   - The post will be published on Dev.to

### Updating Existing Posts

1. Edit the markdown file in the `posts/` directory
2. Commit and push to `main` branch
3. GitHub Actions will automatically update the post on Dev.to

**Note:** The action uses the post title to identify existing posts. If you change the title, it will create a new post instead of updating the existing one.

## Manual Trigger

You can manually trigger the sync workflow:

1. Go to Actions tab in your GitHub repository
2. Select "Publish to Dev.to" workflow
3. Click "Run workflow"
4. Select the branch (usually `main`)
5. Click "Run workflow"

## Troubleshooting

### Posts Not Syncing

1. Check GitHub Actions logs:
   - Go to Actions tab
   - Click on the failed workflow run
   - Review the logs for error messages

2. Common issues:
   - Missing or invalid `DEVTO_TOKEN` secret
   - Invalid front matter format
   - Missing required fields (title, published, description, tags)
   - Network issues connecting to Dev.to API

### Duplicate Posts

If you accidentally created duplicate posts by changing the title:
1. Delete the duplicate on Dev.to manually
2. Revert the title change in the markdown file
3. Push the corrected version

### Rate Limiting

Dev.to API has rate limits. If you're publishing many posts at once, you might hit these limits. The action will retry automatically.

## Current Blog Posts

This repository contains a 5-part series on Spec-Driven Development:

1. **Part 1**: Introduction to Spec-Driven Development
2. **Part 2**: The Station Station Project - A Real-World Case Study
3. **Part 3**: Agent-OS Workflow in Action
4. **Part 4**: Where SDD Helped (and Where It Didn't)
5. **Part 5**: Should You Use Spec-Driven Development?

All posts are in the `posts/` directory with proper Dev.to front matter.

## Additional Resources

- [Dev.to API Documentation](https://developers.forem.com/api)
- [publish-devto Action Documentation](https://github.com/sinedied/publish-devto)
- [Dev.to Markdown Editor Guide](https://dev.to/p/editor_guide)

## Notes

- The action preserves the original markdown files in your repository
- Changes made on Dev.to will NOT sync back to GitHub
- Always update the markdown files in the repository as the source of truth
- The action uses conventional commits to track which posts have been published
