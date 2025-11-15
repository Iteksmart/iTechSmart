"""
GitHub API - GitHub integration endpoints
Provides repository operations, PR management, issue tracking, and more
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User
from app.integrations.github_client import (
    GitHubClient,
    PullRequestState,
    IssueState,
    ReviewState
)

router = APIRouter(prefix="/api/v1/github", tags=["github"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GitHubTokenRequest(BaseModel):
    """Request to set GitHub token"""
    token: str = Field(..., description="GitHub personal access token")


class RepositoryRequest(BaseModel):
    """Request to create repository"""
    name: str = Field(..., description="Repository name")
    description: Optional[str] = Field(None, description="Repository description")
    private: bool = Field(False, description="Make repository private")
    auto_init: bool = Field(True, description="Initialize with README")


class BranchRequest(BaseModel):
    """Request to create branch"""
    name: str = Field(..., description="Branch name")
    from_branch: str = Field("main", description="Source branch")


class PullRequestRequest(BaseModel):
    """Request to create pull request"""
    title: str = Field(..., description="PR title")
    head: str = Field(..., description="Head branch")
    base: str = Field(..., description="Base branch")
    body: Optional[str] = Field(None, description="PR description")
    draft: bool = Field(False, description="Create as draft")


class ReviewRequest(BaseModel):
    """Request to create review"""
    body: str = Field(..., description="Review body")
    event: str = Field(..., description="Review event (APPROVE, REQUEST_CHANGES, COMMENT)")
    comments: List[Dict[str, Any]] = Field(default_factory=list, description="Review comments")


class IssueRequest(BaseModel):
    """Request to create issue"""
    title: str = Field(..., description="Issue title")
    body: Optional[str] = Field(None, description="Issue body")
    labels: List[str] = Field(default_factory=list, description="Issue labels")
    assignees: List[str] = Field(default_factory=list, description="Issue assignees")


class CommentRequest(BaseModel):
    """Request to add comment"""
    body: str = Field(..., description="Comment body")


class FileContentRequest(BaseModel):
    """Request to create/update file"""
    path: str = Field(..., description="File path")
    message: str = Field(..., description="Commit message")
    content: str = Field(..., description="File content")
    branch: Optional[str] = Field(None, description="Branch name")
    sha: Optional[str] = Field(None, description="File SHA (for updates)")


class WorkflowTriggerRequest(BaseModel):
    """Request to trigger workflow"""
    workflow_id: str = Field(..., description="Workflow ID or filename")
    ref: str = Field(..., description="Branch or tag")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Workflow inputs")


# ============================================================================
# GITHUB CLIENT MANAGEMENT
# ============================================================================

# Store GitHub clients per user (in production, use Redis or database)
github_clients: Dict[int, GitHubClient] = {}


def get_github_client(current_user: User = Depends(get_current_user)) -> GitHubClient:
    """Get GitHub client for current user"""
    if current_user.id not in github_clients:
        raise HTTPException(
            status_code=401,
            detail="GitHub token not configured. Please set your GitHub token first."
        )
    return github_clients[current_user.id]


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/token")
async def set_github_token(
    request: GitHubTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set GitHub personal access token
    
    This token will be used for all GitHub API operations.
    """
    try:
        # Create GitHub client
        client = GitHubClient(token=request.token)
        
        # Verify token by getting user info
        user_info = client.get_authenticated_user()
        
        # Store client
        github_clients[current_user.id] = client
        
        return {
            "success": True,
            "message": "GitHub token configured successfully",
            "github_user": user_info.get('login'),
            "name": user_info.get('name')
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid GitHub token: {str(e)}")


@router.delete("/token")
async def remove_github_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove GitHub token"""
    if current_user.id in github_clients:
        del github_clients[current_user.id]
    
    return {
        "success": True,
        "message": "GitHub token removed"
    }


@router.get("/user")
async def get_github_user(
    client: GitHubClient = Depends(get_github_client)
):
    """Get authenticated GitHub user information"""
    try:
        user_info = client.get_authenticated_user()
        return user_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# REPOSITORY ENDPOINTS
# ============================================================================

@router.get("/repos")
async def list_repositories(
    type: str = Query("all", description="Repository type (all, owner, member)"),
    sort: str = Query("updated", description="Sort by (created, updated, pushed, full_name)"),
    client: GitHubClient = Depends(get_github_client)
):
    """List user repositories"""
    try:
        repos = client.list_repositories(type=type, sort=sort)
        return {
            "repositories": repos,
            "total": len(repos)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repos/{owner}/{repo}")
async def get_repository(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_github_client)
):
    """Get repository information"""
    try:
        return client.get_repository(owner, repo)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/repos")
async def create_repository(
    request: RepositoryRequest,
    client: GitHubClient = Depends(get_github_client)
):
    """Create a new repository"""
    try:
        repo = client.create_repository(
            name=request.name,
            description=request.description,
            private=request.private,
            auto_init=request.auto_init
        )
        return repo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/repos/{owner}/{repo}/fork")
async def fork_repository(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_github_client)
):
    """Fork a repository"""
    try:
        forked_repo = client.fork_repository(owner, repo)
        return forked_repo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/repos/{owner}/{repo}")
async def delete_repository(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_github_client)
):
    """Delete a repository"""
    try:
        success = client.delete_repository(owner, repo)
        if success:
            return {"success": True, "message": "Repository deleted"}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete repository")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# BRANCH ENDPOINTS
# ============================================================================

@router.get("/repos/{owner}/{repo}/branches")
async def list_branches(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_github_client)
):
    """List repository branches"""
    try:
        branches = client.list_branches(owner, repo)
        return {
            "branches": branches,
            "total": len(branches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repos/{owner}/{repo}/branches/{branch}")
async def get_branch(
    owner: str,
    repo: str,
    branch: str,
    client: GitHubClient = Depends(get_github_client)
):
    """Get branch information"""
    try:
        return client.get_branch(owner, repo, branch)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/repos/{owner}/{repo}/branches")
async def create_branch(
    owner: str,
    repo: str,
    request: BranchRequest,
    client: GitHubClient = Depends(get_github_client)
):
    """Create a new branch"""
    try:
        branch = client.create_branch(owner, repo, request.name, request.from_branch)
        return branch
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/repos/{owner}/{repo}/branches/{branch}")
async def delete_branch(
    owner: str,
    repo: str,
    branch: str,
    client: GitHubClient = Depends(get_github_client)
):
    """Delete a branch"""
    try:
        success = client.delete_branch(owner, repo, branch)
        if success:
            return {"success": True, "message": "Branch deleted"}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete branch")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# PULL REQUEST ENDPOINTS
# ============================================================================

@router.get("/repos/{owner}/{repo}/pulls")
async def list_pull_requests(
    owner: str,
    repo: str,
    state: str = Query("open", description="PR state (open, closed, all)"),
    sort: str = Query("created", description="Sort by (created, updated, popularity)"),
    direction: str = Query("desc", description="Sort direction (asc, desc)"),
    client: GitHubClient = Depends(get_github_client)
):
    """List pull requests"""
    try:
        pr_state = PullRequestState(state)
        prs = client.list_pull_requests(owner, repo, pr_state, sort, direction)
        return {
            "pull_requests": prs,
            "total": len(prs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repos/{owner}/{repo}/pulls/{pr_number}")
async def get_pull_request(
    owner: str,
    repo: str,
    pr_number: int,
    client: GitHubClient = Depends(get_github_client)
):
    """Get pull request details"""
    try:
        return client.get_pull_request(owner, repo, pr_number)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/repos/{owner}/{repo}/pulls")
async def create_pull_request(
    owner: str,
    repo: str,
    request: PullRequestRequest,
    client: GitHubClient = Depends(get_github_client)
):
    """Create a pull request"""
    try:
        pr = client.create_pull_request(
            owner=owner,
            repo=repo,
            title=request.title,
            head=request.head,
            base=request.base,
            body=request.body,
            draft=request.draft
        )
        return pr
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/repos/{owner}/{repo}/pulls/{pr_number}/merge")
async def merge_pull_request(
    owner: str,
    repo: str,
    pr_number: int,
    merge_method: str = Query("merge", description="Merge method (merge, squash, rebase)"),
    client: GitHubClient = Depends(get_github_client)
):
    """Merge a pull request"""
    try:
        result = client.merge_pull_request(owner, repo, pr_number, merge_method=merge_method)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/repos/{owner}/{repo}/pulls/{pr_number}/reviews")
async def create_review(
    owner: str,
    repo: str,
    pr_number: int,
    request: ReviewRequest,
    client: GitHubClient = Depends(get_github_client)
):
    """Create a pull request review"""
    try:
        review_state = ReviewState(request.event)
        review = client.create_pull_request_review(
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            body=request.body,
            event=review_state,
            comments=request.comments
        )
        return review
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/repos/{owner}/{repo}/pulls/{pr_number}/files")
async def list_pull_request_files(
    owner: str,
    repo: str,
    pr_number: int,
    client: GitHubClient = Depends(get_github_client)
):
    """List files in a pull request"""
    try:
        files = client.list_pull_request_files(owner, repo, pr_number)
        return {
            "files": files,
            "total": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ISSUE ENDPOINTS
# ============================================================================

@router.get("/repos/{owner}/{repo}/issues")
async def list_issues(
    owner: str,
    repo: str,
    state: str = Query("open", description="Issue state (open, closed, all)"),
    labels: Optional[str] = Query(None, description="Comma-separated labels"),
    sort: str = Query("created", description="Sort by (created, updated, comments)"),
    direction: str = Query("desc", description="Sort direction (asc, desc)"),
    client: GitHubClient = Depends(get_github_client)
):
    """List issues"""
    try:
        issue_state = IssueState(state)
        label_list = labels.split(',') if labels else None
        issues = client.list_issues(owner, repo, issue_state, label_list, sort, direction)
        return {
            "issues": issues,
            "total": len(issues)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repos/{owner}/{repo}/issues/{issue_number}")
async def get_issue(
    owner: str,
    repo: str,
    issue_number: int,
    client: GitHubClient = Depends(get_github_client)
):
    """Get issue details"""
    try:
        return client.get_issue(owner, repo, issue_number)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/repos/{owner}/{repo}/issues")
async def create_issue(
    owner: str,
    repo: str,
    request: IssueRequest,
    client: GitHubClient = Depends(get_github_client)
):
    """Create an issue"""
    try:
        issue = client.create_issue(
            owner=owner,
            repo=repo,
            title=request.title,
            body=request.body,
            labels=request.labels,
            assignees=request.assignees
        )
        return issue
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/repos/{owner}/{repo}/issues/{issue_number}")
async def update_issue(
    owner: str,
    repo: str,
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    state: Optional[str] = None,
    client: GitHubClient = Depends(get_github_client)
):
    """Update an issue"""
    try:
        issue = client.update_issue(owner, repo, issue_number, title, body, state)
        return issue
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/repos/{owner}/{repo}/issues/{issue_number}/comments")
async def add_issue_comment(
    owner: str,
    repo: str,
    issue_number: int,
    request: CommentRequest,
    client: GitHubClient = Depends(get_github_client)
):
    """Add comment to issue"""
    try:
        comment = client.add_issue_comment(owner, repo, issue_number, request.body)
        return comment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# COMMIT ENDPOINTS
# ============================================================================

@router.get("/repos/{owner}/{repo}/commits")
async def list_commits(
    owner: str,
    repo: str,
    sha: Optional[str] = Query(None, description="Branch or commit SHA"),
    path: Optional[str] = Query(None, description="File path"),
    author: Optional[str] = Query(None, description="Author username"),
    client: GitHubClient = Depends(get_github_client)
):
    """List commits"""
    try:
        commits = client.list_commits(owner, repo, sha, path, author)
        return {
            "commits": commits,
            "total": len(commits)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repos/{owner}/{repo}/commits/{sha}")
async def get_commit(
    owner: str,
    repo: str,
    sha: str,
    client: GitHubClient = Depends(get_github_client)
):
    """Get commit details"""
    try:
        return client.get_commit(owner, repo, sha)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/repos/{owner}/{repo}/compare/{base}...{head}")
async def compare_commits(
    owner: str,
    repo: str,
    base: str,
    head: str,
    client: GitHubClient = Depends(get_github_client)
):
    """Compare two commits"""
    try:
        return client.compare_commits(owner, repo, base, head)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FILE ENDPOINTS
# ============================================================================

@router.get("/repos/{owner}/{repo}/contents/{path:path}")
async def get_file_content(
    owner: str,
    repo: str,
    path: str,
    ref: Optional[str] = Query(None, description="Branch or commit SHA"),
    client: GitHubClient = Depends(get_github_client)
):
    """Get file content"""
    try:
        content, sha = client.get_file_content(owner, repo, path, ref)
        return {
            "content": content,
            "sha": sha,
            "path": path
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/repos/{owner}/{repo}/contents")
async def create_or_update_file(
    owner: str,
    repo: str,
    request: FileContentRequest,
    client: GitHubClient = Depends(get_github_client)
):
    """Create or update a file"""
    try:
        result = client.create_or_update_file(
            owner=owner,
            repo=repo,
            path=request.path,
            message=request.message,
            content=request.content,
            branch=request.branch,
            sha=request.sha
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# GITHUB ACTIONS ENDPOINTS
# ============================================================================

@router.get("/repos/{owner}/{repo}/actions/workflows")
async def list_workflows(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_github_client)
):
    """List repository workflows"""
    try:
        workflows = client.list_workflows(owner, repo)
        return {
            "workflows": workflows,
            "total": len(workflows)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repos/{owner}/{repo}/actions/workflows/trigger")
async def trigger_workflow(
    owner: str,
    repo: str,
    request: WorkflowTriggerRequest,
    client: GitHubClient = Depends(get_github_client)
):
    """Trigger a workflow"""
    try:
        success = client.trigger_workflow(
            owner=owner,
            repo=repo,
            workflow_id=request.workflow_id,
            ref=request.ref,
            inputs=request.inputs
        )
        if success:
            return {"success": True, "message": "Workflow triggered"}
        else:
            raise HTTPException(status_code=400, detail="Failed to trigger workflow")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/repos/{owner}/{repo}/actions/runs")
async def list_workflow_runs(
    owner: str,
    repo: str,
    workflow_id: Optional[str] = Query(None, description="Filter by workflow"),
    status: Optional[str] = Query(None, description="Filter by status"),
    client: GitHubClient = Depends(get_github_client)
):
    """List workflow runs"""
    try:
        runs = client.list_workflow_runs(owner, repo, workflow_id, status)
        return {
            "workflow_runs": runs,
            "total": len(runs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@router.get("/search/repositories")
async def search_repositories(
    q: str = Query(..., description="Search query"),
    sort: Optional[str] = Query(None, description="Sort by (stars, forks, updated)"),
    order: str = Query("desc", description="Sort order (asc, desc)"),
    client: GitHubClient = Depends(get_github_client)
):
    """Search repositories"""
    try:
        repos = client.search_repositories(q, sort, order)
        return {
            "repositories": repos,
            "total": len(repos)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/code")
async def search_code(
    q: str = Query(..., description="Search query"),
    sort: Optional[str] = Query(None, description="Sort by (indexed)"),
    order: str = Query("desc", description="Sort order (asc, desc)"),
    client: GitHubClient = Depends(get_github_client)
):
    """Search code"""
    try:
        results = client.search_code(q, sort, order)
        return {
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/issues")
async def search_issues(
    q: str = Query(..., description="Search query"),
    sort: Optional[str] = Query(None, description="Sort by (comments, created, updated)"),
    order: str = Query("desc", description="Sort order (asc, desc)"),
    client: GitHubClient = Depends(get_github_client)
):
    """Search issues and pull requests"""
    try:
        issues = client.search_issues(q, sort, order)
        return {
            "issues": issues,
            "total": len(issues)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))