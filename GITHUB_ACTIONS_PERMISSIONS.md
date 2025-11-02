# GitHub Actions Permissions - Auto-Commit Explained

## How Auto-Commit Works

The GitHub Actions workflow can automatically commit attendance results back to your repository **without requiring any additional credentials**.

## Built-in Authentication

GitHub Actions provides a special `GITHUB_TOKEN` automatically:

- ✅ **Automatically created** for each workflow run
- ✅ **No setup required** - works out of the box
- ✅ **Secure** - token expires after the workflow completes
- ✅ **Limited permissions** - only has access to your repository

## Permissions Configuration

The workflow declares the permissions it needs:

```yaml
permissions:
  contents: write  # Allows pushing commits
  actions: read    # Allows reading workflow status
```

### What This Means:

1. **`contents: write`** - Allows the workflow to:
   - Push commits to the repository
   - Create/update files
   - Commit changes

2. **`actions: read`** - Allows the workflow to:
   - Read its own workflow status
   - Access workflow artifacts

## How the Commit Step Works

```yaml
- name: Commit results to repository (optional)
  if: success() && github.event_name == 'schedule'
  run: |
    git config --local user.email "github-actions[bot]@users.noreply.github.com"
    git config --local user.name "github-actions[bot]"

    if [ -f output/attendance.json ]; then
      git add output/attendance.json
      git commit -m "chore: update attendance data [skip ci]"
      git push
    fi
```

### Step-by-Step:

1. **Only runs on scheduled runs** - `if: github.event_name == 'schedule'`
   - Won't commit on manual runs or pushes
   - Only commits when running automatically (daily)

2. **Sets git identity** - Uses `github-actions[bot]` as the committer
   - Appears as a bot in commit history
   - Clearly shows automation

3. **Commits attendance.json** - Adds only the results file
   - NOT auth_data (sensitive)
   - NOT config (may be private)
   - ONLY the attendance results

4. **Uses `[skip ci]`** - Prevents infinite loop
   - Commit won't trigger another workflow run
   - Important to avoid endless automation

5. **Automatic push** - Uses the built-in `GITHUB_TOKEN`
   - No password needed
   - No SSH keys needed
   - Just works™

## Repository Settings

**You don't need to change any settings!** The permissions in the workflow file are sufficient.

However, if you want to be extra cautious or if your organization has restricted settings:

### Check Workflow Permissions (Optional):

1. Go to repository **Settings**
2. Click **Actions** → **General**
3. Scroll to **Workflow permissions**
4. Ensure one of these is selected:
   - ✅ **Read and write permissions** (recommended)
   - ⚠️ **Read repository contents and packages permissions** (won't allow commits)

**Default for new repos:** Read and write permissions (works automatically)

## Disabling Auto-Commit

If you don't want the workflow to commit back to the repository:

### Option 1: Comment Out the Step

```yaml
# - name: Commit results to repository (optional)
#   if: success() && github.event_name == 'schedule'
#   run: |
#     ...
```

### Option 2: Change Permissions

Remove `contents: write` from the workflow:

```yaml
permissions:
  actions: read    # Only read access
```

### Option 3: Change the Condition

Never commit by changing the condition to always false:

```yaml
if: false  # Never runs
```

## Security Considerations

### ✅ Safe:
- GitHub-managed authentication (no passwords in repo)
- Token expires after workflow completes
- Limited scope (only your repository)
- Bot commits clearly visible in history

### ⚠️ Consider:
- Anyone with write access to `.github/workflows/` can modify the workflow
- The workflow has write access to your repository
- Commits are made automatically without review

### 🔒 Best Practice:

1. **Use branch protection** (optional):
   - Protect `main` branch
   - Require pull request reviews
   - Allow bypass for `github-actions[bot]`

2. **Monitor commits**:
   - Check commit history periodically
   - Verify only `attendance.json` is committed
   - Ensure `[skip ci]` is present

3. **Review workflow changes**:
   - Be cautious when updating the workflow file
   - Review PRs that modify `.github/workflows/`

## Troubleshooting

### Push Fails with "Permission denied"

**Solution:** Check repository workflow permissions:
1. Settings → Actions → General → Workflow permissions
2. Select "Read and write permissions"
3. Save and re-run workflow

### Commits Not Appearing

**Possible causes:**
1. Workflow only commits on scheduled runs (not manual runs)
2. No changes to commit (attendance.json unchanged)
3. Workflow failed before reaching commit step

**Check:**
- Run logs for "Commit results to repository" step
- Verify `if: success() && github.event_name == 'schedule'` condition

### Infinite Loop (Workflow Keeps Triggering)

**Solution:** Ensure `[skip ci]` is in commit message:
```bash
git commit -m "chore: update attendance data [skip ci]"
```

This tells GitHub Actions not to trigger workflows for this commit.

## Summary

**No additional credentials needed!** The workflow uses GitHub's built-in authentication:

- ✅ `GITHUB_TOKEN` automatically provided
- ✅ `permissions: contents: write` declared in workflow
- ✅ Commits as `github-actions[bot]`
- ✅ Only commits `attendance.json` on scheduled runs
- ✅ Uses `[skip ci]` to prevent loops

**You can safely push this workflow and it will work immediately.**
