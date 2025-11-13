# Branch Protection Implementation Guide

**Generated:** 2025-11-12
**Purpose:** Ready-to-apply branch protection settings for both Gun Del Sol repositories

---

## Backend Repository: solscan_hotkey

### Required Status Check Names (verified from workflows)

From [ci.yml](ci.yml):
- `Backend Linting`
- `Backend Tests`

From [backend-ci.yml](backend-ci.yml):
- `Lint Python Code`
- `Run Tests`
- `Test Python 3.10`
- `Test Python 3.11`
- `Test Python 3.12`

From [codeql-analysis.yml](codeql-analysis.yml):
- `Analyze Python Code`

From [docker-build.yml](docker-build.yml):
- `Build Docker Image`

From [openapi-schema.yml](openapi-schema.yml):
- `Export OpenAPI Schema`

### Recommended Configuration

Navigate to: **Repository Settings → Branches → Add rule**

#### Basic Settings
```
Branch name pattern: main
☑ Require a pull request before merging
  └─ Required approving review count: 1
  └─ ☑ Dismiss stale pull request approvals when new commits are pushed
☑ Require status checks to pass before merging
  └─ ☑ Require branches to be up to date before merging
☑ Require conversation resolution before merging
☑ Do not allow bypassing the above settings
☑ Do not allow force pushes
☑ Do not allow deletions
```

#### Required Status Checks (select these from dropdown)
**Core Checks (always required):**
- `Backend Linting`
- `Backend Tests`
- `Lint Python Code`
- `Run Tests`
- `Analyze Python Code`
- `Build Docker Image`

**Optional but Recommended:**
- `Test Python 3.10`
- `Test Python 3.11`
- `Test Python 3.12`
- `Export OpenAPI Schema`

### GitHub CLI Command (Backend)

```bash
# Authenticate first
gh auth login

# Apply to gun_del_sol
gh api repos/88simon/gun_del_sol/branches/main/protection \
  --method PUT \
  --field required_status_checks='{
    "strict": true,
    "contexts": [
      "Backend Linting",
      "Backend Tests",
      "Lint Python Code",
      "Run Tests",
      "Analyze Python Code",
      "Build Docker Image",
      "Export OpenAPI Schema"
    ]
  }' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  }' \
  --field restrictions=null
```

---

## Frontend Repository: gun-del-sol-web

### Required Status Check Names (verified from workflows)

From CI workflow:
- `Lint & Format`
- `TypeScript`
- `Build`

From CodeQL workflow:
- `Analyze JavaScript/TypeScript Code`

From Docker workflow:
- `Build Docker Image` (optional)

### Recommended Configuration

Navigate to: **Repository Settings → Branches → Add rule**

#### Basic Settings
```
Branch name pattern: main
☑ Require a pull request before merging
  └─ Required approving review count: 1
  └─ ☑ Dismiss stale pull request approvals when new commits are pushed
☑ Require status checks to pass before merging
  └─ ☑ Require branches to be up to date before merging
☑ Require conversation resolution before merging
☑ Do not allow bypassing the above settings
☑ Do not allow force pushes
☑ Do not allow deletions
```

#### Required Status Checks (select these from dropdown)
**Core Checks (always required):**
- `Lint & Format`
- `TypeScript`
- `Build`
- `Analyze JavaScript/TypeScript Code`

**Optional:**
- `Build Docker Image`

### GitHub CLI Command (Frontend)

```bash
# Apply to gun-del-sol-web (replace OWNER with your GitHub username/org)
gh api repos/OWNER/gun-del-sol-web/branches/main/protection \
  --method PUT \
  --field required_status_checks='{
    "strict": true,
    "contexts": [
      "Lint & Format",
      "TypeScript",
      "Build",
      "Analyze JavaScript/TypeScript Code",
      "Build Docker Image"
    ]
  }' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  }' \
  --field restrictions=null
```

---

## Testing Branch Protection

### 1. Test Direct Push Prevention

```bash
cd /path/to/repo
git checkout main
git commit --allow-empty -m "test: branch protection"
git push  # Should fail with "protected branch" error
```

Expected output:
```
remote: error: GH006: Protected branch update failed
```

### 2. Test PR Workflow

```bash
# Create test branch
git checkout -b test/branch-protection
git commit --allow-empty -m "test: verify PR workflow"
git push -u origin test/branch-protection

# Create PR (requires gh CLI or use GitHub web UI)
gh pr create --base main --head test/branch-protection \
  --title "Test: Branch Protection" \
  --body "Verifying branch protection rules work correctly"
```

### 3. Verify Required Checks

1. Go to the PR on GitHub
2. Check that "Merge" button shows:
   - "X checks pending"
   - "Merging is blocked"
3. Wait for all checks to complete
4. Verify "Merge" button becomes available only after all checks pass

### 4. Test Stale Review Dismissal

1. Get PR approved by a reviewer
2. Push a new commit to the PR branch
3. Verify that the approval is dismissed
4. Request re-review

---

## Current Status

### Backend (solscan_hotkey)
- ❓ **Branch protection rules:** Not verified (check in Settings → Branches)
- ✅ **Workflows:** All workflows active and functional
- ✅ **Status check names:** Verified and documented above
- ⚠️ **Codecov token:** Needs verification (see separate section)

### Frontend (gun-del-sol-web)
- ❓ **Branch protection rules:** Not verified (check in Settings → Branches)
- ✅ **Workflows:** All workflows active and functional
- ✅ **Status check names:** Verified and documented above
- ✅ **Lint checks:** Currently passing (as of 2025-11-12)

---

## Implementation Steps

### Manual Setup (Web UI)

1. **Backend Repository:**
   1. Go to: https://github.com/OWNER/solscan_hotkey/settings/branches
   2. Click "Add rule" or edit existing rule for `main`
   3. Apply settings from "Recommended Configuration" above
   4. Select status checks from dropdown (they appear after first workflow run)
   5. Save changes

2. **Frontend Repository:**
   1. Go to: https://github.com/OWNER/gun-del-sol-web/settings/branches
   2. Click "Add rule" or edit existing rule for `main`
   3. Apply settings from "Recommended Configuration" above
   4. Select status checks from dropdown
   5. Save changes

3. **Test Protection:**
   - Follow "Testing Branch Protection" steps above
   - Verify direct pushes are blocked
   - Verify PR workflow enforces checks

### Automated Setup (GitHub CLI)

**Prerequisites:**
```bash
# Install GitHub CLI (if not installed)
# Windows: winget install GitHub.cli
# Mac: brew install gh

# Authenticate
gh auth login
```

**Apply Protection:**
```bash
# Backend
gh api repos/OWNER/solscan_hotkey/branches/main/protection \
  --method PUT \
  -F required_status_checks='{"strict":true,"contexts":["Backend Linting","Backend Tests","Lint Python Code","Run Tests","Analyze Python Code","Build Docker Image","Export OpenAPI Schema"]}' \
  -F enforce_admins=true \
  -F required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  -F restrictions=null

# Frontend
gh api repos/OWNER/gun-del-sol-web/branches/main/protection \
  --method PUT \
  -F required_status_checks='{"strict":true,"contexts":["Lint & Format","TypeScript","Build","Analyze JavaScript/TypeScript Code","Build Docker Image"]}' \
  -F enforce_admins=true \
  -F required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  -F restrictions=null
```

---

## Troubleshooting

### Status Check Not Appearing in Dropdown

**Problem:** A workflow job doesn't appear in the "Required status checks" dropdown.

**Solutions:**
1. Ensure the workflow has run at least once on the `main` branch
2. Check workflow file for correct `on:` triggers (must include `pull_request`)
3. Verify job name exactly matches (case-sensitive)
4. Wait 5-10 minutes and refresh the page

### Unable to Merge Despite Passing Checks

**Problem:** All checks pass but merge button still disabled.

**Solutions:**
1. Check if "Require branches to be up to date" is enabled
   - If yes, click "Update branch" button
2. Verify all conversations are resolved
3. Check if required review is still pending
4. Ensure you have push access to the target branch

### Accidentally Locked Out of Main Branch

**Problem:** Protection rules prevent necessary emergency fixes.

**Solutions:**
1. Temporarily disable "Include administrators" setting
2. Make critical fix
3. Re-enable protection immediately after
4. **Better approach:** Use the "Allow specified actors to bypass" option for emergencies

### GitHub CLI Commands Fail

**Problem:** `gh api` commands return authentication or permission errors.

**Solutions:**
1. Re-authenticate: `gh auth login`
2. Check you have admin access to the repository
3. Verify correct OWNER/repo name
4. Try using the web UI as fallback

---

## Maintenance Checklist

Run quarterly or when CI/CD changes:

- [ ] Review list of required status checks
- [ ] Verify all checks are still active and necessary
- [ ] Remove deprecated/renamed workflow checks
- [ ] Test PR workflow with sample branch
- [ ] Update this documentation if changes made
- [ ] Verify Codecov uploads still working
- [ ] Check Dependabot is creating PRs successfully

---

## Related Documentation

- [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) - Detailed recommendations
- [CI_CD_IMPLEMENTATION_COMPLETE.md](CI_CD_IMPLEMENTATION_COMPLETE.md) - CI/CD architecture
- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)

---

**Next Steps:**
1. ✅ Verify workflow job names (COMPLETED)
2. ⏭️ Check current protection status via web UI
3. ⏭️ Apply protection rules via web UI or CLI
4. ⏭️ Test with sample PR
5. ⏭️ Document applied settings date