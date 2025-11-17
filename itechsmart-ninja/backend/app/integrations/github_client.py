"""
GitHub Client - Comprehensive GitHub API integration
Provides repository operations, PR management, issue tracking, and more
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import requests
import base64
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class GitHubAuthType(str, Enum):
    """GitHub authentication types"""

    PERSONAL_ACCESS_TOKEN = "pat"
    OAUTH = "oauth"
    APP = "app"


class PullRequestState(str, Enum):
    """Pull request states"""

    OPEN = "open"
    CLOSED = "closed"
    ALL = "all"


class IssueState(str, Enum):
    """Issue states"""

    OPEN = "open"
    CLOSED = "closed"
    ALL = "all"


class ReviewState(str, Enum):
    """Pull request review states"""

    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    COMMENTED = "COMMENTED"


class GitHubClient:
    """
    Comprehensive GitHub API client

    Features:
    - Repository operations (clone, pull, push, fork)
    - Pull request management (create, review, merge)
    - Issue tracking (create, update, close)
    - Branch management (create, delete, merge)
    - Commit history (view, search, analyze)
    - Code review automation
    - GitHub Actions integration
    - Webhook support
    """

    def __init__(
        self,
        token: str,
        auth_type: GitHubAuthType = GitHubAuthType.PERSONAL_ACCESS_TOKEN,
        base_url: str = "https://api.github.com",
    ):
        """
        Initialize GitHub client

        Args:
            token: GitHub authentication token
            auth_type: Type of authentication
            base_url: GitHub API base URL
        """
        self.token = token
        self.auth_type = auth_type
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "iTechSmart-Ninja",
            }
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make API request with error handling

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json: JSON body
            headers: Additional headers

        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method, url=url, params=params, json=json, headers=headers or {}
            )
            response.raise_for_status()

            # Handle rate limiting
            if response.status_code == 429:
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                logger.warning(f"Rate limit exceeded. Resets at {reset_time}")
                raise Exception(f"Rate limit exceeded. Try again after {reset_time}")

            return response.json() if response.content else {}

        except requests.exceptions.HTTPError as e:
            logger.error(f"GitHub API error: {e}")
            raise Exception(f"GitHub API error: {e}")
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

    def _paginate(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_pages: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Paginate through API results

        Args:
            endpoint: API endpoint
            params: Query parameters
            max_pages: Maximum pages to fetch

        Returns:
            List of all results
        """
        results = []
        page = 1
        params = params or {}
        params["per_page"] = 100

        while page <= max_pages:
            params["page"] = page
            data = self._request("GET", endpoint, params=params)

            if not data:
                break

            if isinstance(data, list):
                results.extend(data)
                if len(data) < 100:
                    break
            else:
                results.append(data)
                break

            page += 1

        return results

    # ========================================================================
    # REPOSITORY OPERATIONS
    # ========================================================================

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository information

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Repository data
        """
        return self._request("GET", f"/repos/{owner}/{repo}")

    def list_repositories(
        self,
        user: Optional[str] = None,
        org: Optional[str] = None,
        type: str = "all",
        sort: str = "updated",
    ) -> List[Dict[str, Any]]:
        """
        List repositories

        Args:
            user: Username (for user repos)
            org: Organization name (for org repos)
            type: Repository type (all, owner, member)
            sort: Sort by (created, updated, pushed, full_name)

        Returns:
            List of repositories
        """
        if org:
            endpoint = f"/orgs/{org}/repos"
        elif user:
            endpoint = f"/users/{user}/repos"
        else:
            endpoint = "/user/repos"

        params = {"type": type, "sort": sort}
        return self._paginate(endpoint, params=params)

    def create_repository(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = False,
        auto_init: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a new repository

        Args:
            name: Repository name
            description: Repository description
            private: Make repository private
            auto_init: Initialize with README

        Returns:
            Created repository data
        """
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init,
        }
        return self._request("POST", "/user/repos", json=data)

    def fork_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Fork a repository

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Forked repository data
        """
        return self._request("POST", f"/repos/{owner}/{repo}/forks")

    def delete_repository(self, owner: str, repo: str) -> bool:
        """
        Delete a repository

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Success status
        """
        try:
            self._request("DELETE", f"/repos/{owner}/{repo}")
            return True
        except Exception:
            return False

    # ========================================================================
    # BRANCH OPERATIONS
    # ========================================================================

    def list_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """
        List repository branches

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of branches
        """
        return self._paginate(f"/repos/{owner}/{repo}/branches")

    def get_branch(self, owner: str, repo: str, branch: str) -> Dict[str, Any]:
        """
        Get branch information

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name

        Returns:
            Branch data
        """
        return self._request("GET", f"/repos/{owner}/{repo}/branches/{branch}")

    def create_branch(
        self, owner: str, repo: str, branch: str, from_branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Create a new branch

        Args:
            owner: Repository owner
            repo: Repository name
            branch: New branch name
            from_branch: Source branch

        Returns:
            Created branch data
        """
        # Get source branch SHA
        source = self.get_branch(owner, repo, from_branch)
        sha = source["commit"]["sha"]

        # Create reference
        data = {"ref": f"refs/heads/{branch}", "sha": sha}
        return self._request("POST", f"/repos/{owner}/{repo}/git/refs", json=data)

    def delete_branch(self, owner: str, repo: str, branch: str) -> bool:
        """
        Delete a branch

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name

        Returns:
            Success status
        """
        try:
            self._request("DELETE", f"/repos/{owner}/{repo}/git/refs/heads/{branch}")
            return True
        except Exception:
            return False

    def merge_branches(
        self,
        owner: str,
        repo: str,
        base: str,
        head: str,
        commit_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Merge branches

        Args:
            owner: Repository owner
            repo: Repository name
            base: Base branch
            head: Head branch
            commit_message: Merge commit message

        Returns:
            Merge result
        """
        data = {
            "base": base,
            "head": head,
            "commit_message": commit_message or f"Merge {head} into {base}",
        }
        return self._request("POST", f"/repos/{owner}/{repo}/merges", json=data)

    # ========================================================================
    # PULL REQUEST OPERATIONS
    # ========================================================================

    def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: PullRequestState = PullRequestState.OPEN,
        sort: str = "created",
        direction: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        List pull requests

        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state (open, closed, all)
            sort: Sort by (created, updated, popularity)
            direction: Sort direction (asc, desc)

        Returns:
            List of pull requests
        """
        params = {"state": state.value, "sort": sort, "direction": direction}
        return self._paginate(f"/repos/{owner}/{repo}/pulls", params=params)

    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Get pull request details

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Pull request data
        """
        return self._request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}")

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: Optional[str] = None,
        draft: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a pull request

        Args:
            owner: Repository owner
            repo: Repository name
            title: PR title
            head: Head branch
            base: Base branch
            body: PR description
            draft: Create as draft

        Returns:
            Created pull request data
        """
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "draft": draft,
        }
        return self._request("POST", f"/repos/{owner}/{repo}/pulls", json=data)

    def update_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a pull request

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            title: New title
            body: New body
            state: New state (open, closed)

        Returns:
            Updated pull request data
        """
        data = {}
        if title:
            data["title"] = title
        if body:
            data["body"] = body
        if state:
            data["state"] = state

        return self._request(
            "PATCH", f"/repos/{owner}/{repo}/pulls/{pr_number}", json=data
        )

    def merge_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        commit_title: Optional[str] = None,
        commit_message: Optional[str] = None,
        merge_method: str = "merge",
    ) -> Dict[str, Any]:
        """
        Merge a pull request

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            commit_title: Merge commit title
            commit_message: Merge commit message
            merge_method: Merge method (merge, squash, rebase)

        Returns:
            Merge result
        """
        data = {
            "commit_title": commit_title,
            "commit_message": commit_message,
            "merge_method": merge_method,
        }
        return self._request(
            "PUT", f"/repos/{owner}/{repo}/pulls/{pr_number}/merge", json=data
        )

    def create_pull_request_review(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str,
        event: ReviewState,
        comments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Create a pull request review

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            body: Review body
            event: Review event (APPROVE, REQUEST_CHANGES, COMMENT)
            comments: Review comments

        Returns:
            Created review data
        """
        data = {"body": body, "event": event.value, "comments": comments or []}
        return self._request(
            "POST", f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews", json=data
        )

    def list_pull_request_files(
        self, owner: str, repo: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """
        List files in a pull request

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            List of files
        """
        return self._paginate(f"/repos/{owner}/{repo}/pulls/{pr_number}/files")

    # ========================================================================
    # ISSUE OPERATIONS
    # ========================================================================

    def list_issues(
        self,
        owner: str,
        repo: str,
        state: IssueState = IssueState.OPEN,
        labels: Optional[List[str]] = None,
        sort: str = "created",
        direction: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        List issues

        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            labels: Filter by labels
            sort: Sort by (created, updated, comments)
            direction: Sort direction (asc, desc)

        Returns:
            List of issues
        """
        params = {"state": state.value, "sort": sort, "direction": direction}
        if labels:
            params["labels"] = ",".join(labels)

        return self._paginate(f"/repos/{owner}/{repo}/issues", params=params)

    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """
        Get issue details

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number

        Returns:
            Issue data
        """
        return self._request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create an issue

        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue body
            labels: Issue labels
            assignees: Issue assignees

        Returns:
            Created issue data
        """
        data = {
            "title": title,
            "body": body,
            "labels": labels or [],
            "assignees": assignees or [],
        }
        return self._request("POST", f"/repos/{owner}/{repo}/issues", json=data)

    def update_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Update an issue

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            title: New title
            body: New body
            state: New state (open, closed)
            labels: New labels

        Returns:
            Updated issue data
        """
        data = {}
        if title:
            data["title"] = title
        if body:
            data["body"] = body
        if state:
            data["state"] = state
        if labels:
            data["labels"] = labels

        return self._request(
            "PATCH", f"/repos/{owner}/{repo}/issues/{issue_number}", json=data
        )

    def close_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """
        Close an issue

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number

        Returns:
            Closed issue data
        """
        return self.update_issue(owner, repo, issue_number, state="closed")

    def add_issue_comment(
        self, owner: str, repo: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """
        Add comment to issue

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            body: Comment body

        Returns:
            Created comment data
        """
        data = {"body": body}
        return self._request(
            "POST", f"/repos/{owner}/{repo}/issues/{issue_number}/comments", json=data
        )

    # ========================================================================
    # COMMIT OPERATIONS
    # ========================================================================

    def list_commits(
        self,
        owner: str,
        repo: str,
        sha: Optional[str] = None,
        path: Optional[str] = None,
        author: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        List commits

        Args:
            owner: Repository owner
            repo: Repository name
            sha: Branch or commit SHA
            path: File path
            author: Author username
            since: Start date
            until: End date

        Returns:
            List of commits
        """
        params = {}
        if sha:
            params["sha"] = sha
        if path:
            params["path"] = path
        if author:
            params["author"] = author
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()

        return self._paginate(f"/repos/{owner}/{repo}/commits", params=params)

    def get_commit(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """
        Get commit details

        Args:
            owner: Repository owner
            repo: Repository name
            sha: Commit SHA

        Returns:
            Commit data
        """
        return self._request("GET", f"/repos/{owner}/{repo}/commits/{sha}")

    def compare_commits(
        self, owner: str, repo: str, base: str, head: str
    ) -> Dict[str, Any]:
        """
        Compare two commits

        Args:
            owner: Repository owner
            repo: Repository name
            base: Base commit
            head: Head commit

        Returns:
            Comparison data
        """
        return self._request("GET", f"/repos/{owner}/{repo}/compare/{base}...{head}")

    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    def get_file_content(
        self, owner: str, repo: str, path: str, ref: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Get file content

        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            ref: Branch or commit SHA

        Returns:
            Tuple of (content, sha)
        """
        params = {"ref": ref} if ref else {}
        data = self._request(
            "GET", f"/repos/{owner}/{repo}/contents/{path}", params=params
        )

        content = base64.b64decode(data["content"]).decode("utf-8")
        return content, data["sha"]

    def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        message: str,
        content: str,
        branch: Optional[str] = None,
        sha: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create or update a file

        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            message: Commit message
            content: File content
            branch: Branch name
            sha: File SHA (required for updates)

        Returns:
            Commit data
        """
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        data = {"message": message, "content": encoded_content}
        if branch:
            data["branch"] = branch
        if sha:
            data["sha"] = sha

        return self._request("PUT", f"/repos/{owner}/{repo}/contents/{path}", json=data)

    def delete_file(
        self,
        owner: str,
        repo: str,
        path: str,
        message: str,
        sha: str,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Delete a file

        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            message: Commit message
            sha: File SHA
            branch: Branch name

        Returns:
            Commit data
        """
        data = {"message": message, "sha": sha}
        if branch:
            data["branch"] = branch

        return self._request(
            "DELETE", f"/repos/{owner}/{repo}/contents/{path}", json=data
        )

    # ========================================================================
    # GITHUB ACTIONS
    # ========================================================================

    def list_workflows(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """
        List repository workflows

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of workflows
        """
        data = self._request("GET", f"/repos/{owner}/{repo}/actions/workflows")
        return data.get("workflows", [])

    def trigger_workflow(
        self,
        owner: str,
        repo: str,
        workflow_id: str,
        ref: str,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Trigger a workflow

        Args:
            owner: Repository owner
            repo: Repository name
            workflow_id: Workflow ID or filename
            ref: Branch or tag
            inputs: Workflow inputs

        Returns:
            Success status
        """
        data = {"ref": ref, "inputs": inputs or {}}
        try:
            self._request(
                "POST",
                f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                json=data,
            )
            return True
        except Exception:
            return False

    def list_workflow_runs(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List workflow runs

        Args:
            owner: Repository owner
            repo: Repository name
            workflow_id: Filter by workflow
            status: Filter by status

        Returns:
            List of workflow runs
        """
        params = {}
        if status:
            params["status"] = status

        if workflow_id:
            endpoint = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            endpoint = f"/repos/{owner}/{repo}/actions/runs"

        data = self._request("GET", endpoint, params=params)
        return data.get("workflow_runs", [])

    # ========================================================================
    # USER OPERATIONS
    # ========================================================================

    def get_authenticated_user(self) -> Dict[str, Any]:
        """
        Get authenticated user information

        Returns:
            User data
        """
        return self._request("GET", "/user")

    def get_user(self, username: str) -> Dict[str, Any]:
        """
        Get user information

        Args:
            username: GitHub username

        Returns:
            User data
        """
        return self._request("GET", f"/users/{username}")

    # ========================================================================
    # SEARCH OPERATIONS
    # ========================================================================

    def search_repositories(
        self, query: str, sort: Optional[str] = None, order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Search repositories

        Args:
            query: Search query
            sort: Sort by (stars, forks, updated)
            order: Sort order (asc, desc)

        Returns:
            List of repositories
        """
        params = {"q": query, "order": order}
        if sort:
            params["sort"] = sort

        data = self._request("GET", "/search/repositories", params=params)
        return data.get("items", [])

    def search_code(
        self, query: str, sort: Optional[str] = None, order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Search code

        Args:
            query: Search query
            sort: Sort by (indexed)
            order: Sort order (asc, desc)

        Returns:
            List of code results
        """
        params = {"q": query, "order": order}
        if sort:
            params["sort"] = sort

        data = self._request("GET", "/search/code", params=params)
        return data.get("items", [])

    def search_issues(
        self, query: str, sort: Optional[str] = None, order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Search issues and pull requests

        Args:
            query: Search query
            sort: Sort by (comments, created, updated)
            order: Sort order (asc, desc)

        Returns:
            List of issues
        """
        params = {"q": query, "order": order}
        if sort:
            params["sort"] = sort

        data = self._request("GET", "/search/issues", params=params)
        return data.get("items", [])
