# Feature 4: GitHub Integration - Quick Start Guide

## 🚀 Getting Started

This guide will help you quickly start using GitHub integration in iTechSmart Ninja.

---

## 📋 Prerequisites

1. iTechSmart Ninja backend running
2. VS Code extension installed
3. GitHub Personal Access Token
4. Authenticated user session

---

## 🔑 Step 1: Get GitHub Token

### Create Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "iTechSmart Ninja")
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `read:org` (Read org and team membership)
   - ✅ `user` (Update user data)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

---

## 🔧 Step 2: Configure Token

### Method 1: Command Palette

1. Press `Ctrl+Shift+P`
2. Type "GitHub Token"
3. Select "iTechSmart: Set GitHub Token"
4. Paste your token
5. Press Enter

### Method 2: API

```bash
POST /api/v1/github/token
{
  "token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "GitHub token configured successfully",
  "github_user": "your-username",
  "name": "Your Name"
}
```

---

## 🎯 Quick Access Methods

### Method 1: Command Palette (Ctrl+Shift+P)

```
iTechSmart: List GitHub Repositories
iTechSmart: Create GitHub Repository
iTechSmart: Fork GitHub Repository
iTechSmart: List Pull Requests
iTechSmart: Create Pull Request
iTechSmart: Review Pull Request
iTechSmart: List GitHub Issues
iTechSmart: Create GitHub Issue
iTechSmart: List GitHub Branches
iTechSmart: Create GitHub Branch
iTechSmart: List GitHub Workflows
iTechSmart: Trigger GitHub Workflow
```

### Method 2: Terminal Commands

Open iTechSmart terminal and use:
```bash
> gh-repos                    # List repositories
> gh-prs owner/repo          # List pull requests
> gh-issues owner/repo       # List issues
> gh-create-pr               # Create pull request
> gh-create-issue            # Create issue
```

### Method 3: REST API

```bash
GET    /api/v1/github/repos
POST   /api/v1/github/repos
GET    /api/v1/github/repos/{owner}/{repo}/pulls
POST   /api/v1/github/repos/{owner}/{repo}/pulls
GET    /api/v1/github/repos/{owner}/{repo}/issues
POST   /api/v1/github/repos/{owner}/{repo}/issues
```

---

## 📦 Repository Operations

### List Your Repositories

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "List GitHub"
3. Select "iTechSmart: List GitHub Repositories"
4. Choose type (All, Owner, Member)
5. Select a repository to view details

**Terminal:**
```bash
> gh-repos
```

**API:**
```bash
GET /api/v1/github/repos?type=all&sort=updated
```

### Create Repository

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "Create GitHub"
3. Select "iTechSmart: Create GitHub Repository"
4. Enter repository name
5. Enter description (optional)
6. Choose visibility (Public/Private)

**API:**
```bash
POST /api/v1/github/repos
{
  "name": "my-awesome-project",
  "description": "A brief description",
  "private": false,
  "auto_init": true
}
```

### Fork Repository

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "Fork"
3. Select "iTechSmart: Fork GitHub Repository"
4. Enter repository URL or owner/repo

**API:**
```bash
POST /api/v1/github/repos/owner/repo/fork
```

---

## 🔀 Pull Request Workflow

### List Pull Requests

**Terminal:**
```bash
> gh-prs owner/repo
```

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "List Pull"
3. Select "iTechSmart: List Pull Requests"
4. Enter repository (owner/repo)
5. Choose state (Open, Closed, All)

**API:**
```bash
GET /api/v1/github/repos/owner/repo/pulls?state=open
```

### Create Pull Request

**Terminal:**
```bash
> gh-create-pr
```

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "Create Pull"
3. Select "iTechSmart: Create Pull Request"
4. Enter repository (owner/repo)
5. Enter PR title
6. Enter head branch
7. Enter base branch (default: main)
8. Enter description (optional)

**API:**
```bash
POST /api/v1/github/repos/owner/repo/pulls
{
  "title": "Add new feature",
  "head": "feature-branch",
  "base": "main",
  "body": "This PR adds...",
  "draft": false
}
```

### Review Pull Request

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "Review Pull"
3. Select "iTechSmart: Review Pull Request"
4. Enter repository (owner/repo)
5. Enter PR number
6. Choose review type:
   - **Approve** - Approve the changes
   - **Request Changes** - Request modifications
   - **Comment** - Add comments without approval
7. Enter review comment

**API:**
```bash
POST /api/v1/github/repos/owner/repo/pulls/123/reviews
{
  "body": "Looks good to me!",
  "event": "APPROVED",
  "comments": []
}
```

### Merge Pull Request

**API:**
```bash
PUT /api/v1/github/repos/owner/repo/pulls/123/merge
{
  "merge_method": "squash"
}
```

**Merge Methods:**
- `merge` - Create a merge commit
- `squash` - Squash and merge
- `rebase` - Rebase and merge

---

## 🐛 Issue Tracking

### List Issues

**Terminal:**
```bash
> gh-issues owner/repo
```

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "List Issues"
3. Select "iTechSmart: List GitHub Issues"
4. Enter repository (owner/repo)
5. Choose state (Open, Closed, All)

**API:**
```bash
GET /api/v1/github/repos/owner/repo/issues?state=open
```

### Create Issue

**Terminal:**
```bash
> gh-create-issue
```

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "Create Issue"
3. Select "iTechSmart: Create GitHub Issue"
4. Enter repository (owner/repo)
5. Enter issue title
6. Enter description (optional)

**API:**
```bash
POST /api/v1/github/repos/owner/repo/issues
{
  "title": "Bug: Something is broken",
  "body": "Steps to reproduce...",
  "labels": ["bug"],
  "assignees": ["username"]
}
```

### Update Issue

**API:**
```bash
PATCH /api/v1/github/repos/owner/repo/issues/456
{
  "state": "closed",
  "labels": ["bug", "fixed"]
}
```

### Add Comment

**API:**
```bash
POST /api/v1/github/repos/owner/repo/issues/456/comments
{
  "body": "This has been fixed in PR #123"
}
```

---

## 🌿 Branch Management

### List Branches

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "List Branches"
3. Select "iTechSmart: List GitHub Branches"
4. Enter repository (owner/repo)

**API:**
```bash
GET /api/v1/github/repos/owner/repo/branches
```

### Create Branch

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "Create Branch"
3. Select "iTechSmart: Create GitHub Branch"
4. Enter repository (owner/repo)
5. Enter branch name
6. Enter source branch (default: main)

**API:**
```bash
POST /api/v1/github/repos/owner/repo/branches
{
  "name": "feature/new-feature",
  "from_branch": "main"
}
```

### Delete Branch

**API:**
```bash
DELETE /api/v1/github/repos/owner/repo/branches/feature-branch
```

---

## ⚙️ GitHub Actions

### List Workflows

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "List Workflows"
3. Select "iTechSmart: List GitHub Workflows"
4. Enter repository (owner/repo)

**API:**
```bash
GET /api/v1/github/repos/owner/repo/actions/workflows
```

### Trigger Workflow

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "Trigger Workflow"
3. Select "iTechSmart: Trigger GitHub Workflow"
4. Enter repository (owner/repo)
5. Enter workflow ID or filename (e.g., deploy.yml)
6. Enter branch or tag (default: main)

**API:**
```bash
POST /api/v1/github/repos/owner/repo/actions/workflows/trigger
{
  "workflow_id": "deploy.yml",
  "ref": "main",
  "inputs": {}
}
```

### List Workflow Runs

**API:**
```bash
GET /api/v1/github/repos/owner/repo/actions/runs?status=success
```

---

## 🔍 Search Operations

### Search Repositories

**API:**
```bash
GET /api/v1/github/search/repositories?q=machine+learning&sort=stars
```

### Search Code

**API:**
```bash
GET /api/v1/github/search/code?q=function+repo:owner/repo
```

### Search Issues

**API:**
```bash
GET /api/v1/github/search/issues?q=is:open+label:bug
```

---

## 💡 Common Workflows

### Workflow 1: Create Feature Branch and PR

```bash
# 1. Create branch
POST /api/v1/github/repos/owner/repo/branches
{
  "name": "feature/new-feature",
  "from_branch": "main"
}

# 2. Make changes and commit (use git)

# 3. Create pull request
POST /api/v1/github/repos/owner/repo/pulls
{
  "title": "Add new feature",
  "head": "feature/new-feature",
  "base": "main",
  "body": "This PR adds..."
}

# 4. Review and merge
PUT /api/v1/github/repos/owner/repo/pulls/123/merge
```

### Workflow 2: Bug Fix Process

```bash
# 1. Create issue
POST /api/v1/github/repos/owner/repo/issues
{
  "title": "Bug: Login not working",
  "body": "Steps to reproduce...",
  "labels": ["bug"]
}

# 2. Create branch
POST /api/v1/github/repos/owner/repo/branches
{
  "name": "fix/login-bug",
  "from_branch": "main"
}

# 3. Fix and create PR
POST /api/v1/github/repos/owner/repo/pulls
{
  "title": "Fix: Login bug",
  "head": "fix/login-bug",
  "base": "main",
  "body": "Fixes #456"
}

# 4. Close issue when merged
PATCH /api/v1/github/repos/owner/repo/issues/456
{
  "state": "closed"
}
```

### Workflow 3: Release Process

```bash
# 1. Create release branch
POST /api/v1/github/repos/owner/repo/branches
{
  "name": "release/v1.0.0",
  "from_branch": "develop"
}

# 2. Create PR to main
POST /api/v1/github/repos/owner/repo/pulls
{
  "title": "Release v1.0.0",
  "head": "release/v1.0.0",
  "base": "main"
}

# 3. Trigger deployment workflow
POST /api/v1/github/repos/owner/repo/actions/workflows/trigger
{
  "workflow_id": "deploy.yml",
  "ref": "main"
}
```

---

## 🐛 Troubleshooting

### Token Not Working
1. Check token has correct scopes
2. Verify token hasn't expired
3. Try regenerating token
4. Check token is set correctly:
   ```bash
   GET /api/v1/github/user
   ```

### Rate Limit Exceeded
1. Wait for rate limit reset
2. Check rate limit status:
   ```bash
   # Response headers include:
   X-RateLimit-Limit: 5000
   X-RateLimit-Remaining: 4999
   X-RateLimit-Reset: 1234567890
   ```
3. Use authenticated requests (higher limits)

### Repository Not Found
1. Check repository name is correct
2. Verify you have access to the repository
3. Check repository visibility (public/private)
4. Ensure token has `repo` scope for private repos

### Permission Denied
1. Check token has required scopes
2. Verify you're a collaborator on the repository
3. Check repository settings
4. Try with a new token with full permissions

---

## 📚 Additional Resources

- **Full Documentation:** See `FEATURE4_COMPLETE.md`
- **API Reference:** See `backend/app/api/github.py`
- **GitHub API Docs:** https://docs.github.com/en/rest
- **Token Scopes:** https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps

---

## 🎉 Quick Examples

### Example 1: List My Repositories
```bash
> gh-repos
# Select repository type: All
# View list of repositories
# Select a repository to see details
```

### Example 2: Create and Merge PR
```bash
# Create PR
> gh-create-pr
Repository: owner/repo
Title: Add new feature
Head: feature-branch
Base: main
Description: This adds...

# Review PR
Ctrl+Shift+P → iTechSmart: Review Pull Request
Repository: owner/repo
PR Number: 123
Review Type: Approve
Comment: LGTM!

# Merge PR (via API)
PUT /api/v1/github/repos/owner/repo/pulls/123/merge
```

### Example 3: Create Issue and Track
```bash
# Create issue
> gh-create-issue
Repository: owner/repo
Title: Bug: Login fails
Description: When I try to login...

# Add comment
POST /api/v1/github/repos/owner/repo/issues/456/comments
{
  "body": "I'm working on this"
}

# Close issue
PATCH /api/v1/github/repos/owner/repo/issues/456
{
  "state": "closed"
}
```

---

**Happy Coding! 🚀**