/**
 * GitHub Commands - VS Code commands for GitHub integration
 * Provides repository operations, PR management, issue tracking, and more
 */

import * as vscode from 'vscode';
import { APIClient } from '../api/client';

/**
 * Register all GitHub commands
 */
export function registerGitHubCommands(context: vscode.ExtensionContext, apiClient: APIClient) {
    // Authentication
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.setGitHubToken', () => setGitHubToken(apiClient))
    );
    
    // Repository operations
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.listRepositories', () => listRepositories(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.createRepository', () => createRepository(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.forkRepository', () => forkRepository(apiClient))
    );
    
    // Pull request operations
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.listPullRequests', () => listPullRequests(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.createPullRequest', () => createPullRequest(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.reviewPullRequest', () => reviewPullRequest(apiClient))
    );
    
    // Issue operations
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.listIssues', () => listIssues(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.createIssue', () => createIssue(apiClient))
    );
    
    // Branch operations
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.listBranches', () => listBranches(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.createBranch', () => createBranch(apiClient))
    );
    
    // Workflow operations
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.listWorkflows', () => listWorkflows(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.triggerWorkflow', () => triggerWorkflow(apiClient))
    );
}

/**
 * Set GitHub personal access token
 */
async function setGitHubToken(apiClient: APIClient) {
    try {
        const token = await vscode.window.showInputBox({
            prompt: 'Enter your GitHub Personal Access Token',
            password: true,
            placeHolder: 'ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        });
        
        if (!token) {
            return;
        }
        
        const response = await apiClient.post('/github/token', { token });
        
        vscode.window.showInformationMessage(
            `GitHub token configured for ${response.github_user}`
        );
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to set GitHub token: ${error.message}`);
    }
}

/**
 * List repositories
 */
async function listRepositories(apiClient: APIClient) {
    try {
        const type = await vscode.window.showQuickPick(
            [
                { label: 'All', value: 'all' },
                { label: 'Owner', value: 'owner' },
                { label: 'Member', value: 'member' }
            ],
            { placeHolder: 'Select repository type' }
        );
        
        if (!type) {
            return;
        }
        
        const response = await apiClient.get(`/github/repos?type=${type.value}`);
        
        if (response.total === 0) {
            vscode.window.showInformationMessage('No repositories found');
            return;
        }
        
        const items = response.repositories.map((repo: any) => ({
            label: repo.full_name,
            description: repo.description || 'No description',
            detail: `⭐ ${repo.stargazers_count} | 🍴 ${repo.forks_count} | ${repo.private ? '🔒 Private' : '🌐 Public'}`,
            repo: repo
        }));
        
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a repository'
        });
        
        if (!selected) {
            return;
        }
        
        // Show repository actions
        const action = await vscode.window.showQuickPick(
            [
                { label: 'View Details', value: 'details' },
                { label: 'Open in Browser', value: 'browser' },
                { label: 'List Branches', value: 'branches' },
                { label: 'List Pull Requests', value: 'prs' },
                { label: 'List Issues', value: 'issues' }
            ],
            { placeHolder: 'Select action' }
        );
        
        if (!action) {
            return;
        }
        
        switch (action.value) {
            case 'browser':
                vscode.env.openExternal(vscode.Uri.parse(selected.repo.html_url));
                break;
            case 'details':
                showRepositoryDetails(selected.repo);
                break;
            // Other actions would call respective functions
        }
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list repositories: ${error.message}`);
    }
}

/**
 * Show repository details
 */
function showRepositoryDetails(repo: any) {
    const panel = vscode.window.createWebviewPanel(
        'repoDetails',
        `Repository: ${repo.full_name}`,
        vscode.ViewColumn.One,
        { enableScripts: true }
    );
    
    panel.webview.html = getRepositoryDetailsHTML(repo);
}

/**
 * Create repository
 */
async function createRepository(apiClient: APIClient) {
    try {
        const name = await vscode.window.showInputBox({
            prompt: 'Enter repository name',
            placeHolder: 'my-awesome-project'
        });
        
        if (!name) {
            return;
        }
        
        const description = await vscode.window.showInputBox({
            prompt: 'Enter repository description (optional)',
            placeHolder: 'A brief description of your project'
        });
        
        const isPrivate = await vscode.window.showQuickPick(
            [
                { label: 'Public', value: false },
                { label: 'Private', value: true }
            ],
            { placeHolder: 'Select repository visibility' }
        );
        
        if (!isPrivate) {
            return;
        }
        
        const repo = await apiClient.post('/github/repos', {
            name,
            description,
            private: isPrivate.value,
            auto_init: true
        });
        
        vscode.window.showInformationMessage(
            `Repository created: ${repo.full_name}`,
            'Open in Browser'
        ).then(selection => {
            if (selection === 'Open in Browser') {
                vscode.env.openExternal(vscode.Uri.parse(repo.html_url));
            }
        });
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to create repository: ${error.message}`);
    }
}

/**
 * Fork repository
 */
async function forkRepository(apiClient: APIClient) {
    try {
        const repoUrl = await vscode.window.showInputBox({
            prompt: 'Enter repository URL or owner/repo',
            placeHolder: 'owner/repo or https://github.com/owner/repo'
        });
        
        if (!repoUrl) {
            return;
        }
        
        // Parse owner and repo from URL
        const match = repoUrl.match(/(?:https?:\/\/github\.com\/)?([^\/]+)\/([^\/]+)/);
        if (!match) {
            vscode.window.showErrorMessage('Invalid repository URL');
            return;
        }
        
        const [, owner, repo] = match;
        
        const forkedRepo = await apiClient.post(`/github/repos/${owner}/${repo}/fork`);
        
        vscode.window.showInformationMessage(
            `Repository forked: ${forkedRepo.full_name}`,
            'Open in Browser'
        ).then(selection => {
            if (selection === 'Open in Browser') {
                vscode.env.openExternal(vscode.Uri.parse(forkedRepo.html_url));
            }
        });
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to fork repository: ${error.message}`);
    }
}

/**
 * List pull requests
 */
async function listPullRequests(apiClient: APIClient) {
    try {
        const repoInput = await vscode.window.showInputBox({
            prompt: 'Enter repository (owner/repo)',
            placeHolder: 'owner/repo'
        });
        
        if (!repoInput) {
            return;
        }
        
        const [owner, repo] = repoInput.split('/');
        
        const state = await vscode.window.showQuickPick(
            [
                { label: 'Open', value: 'open' },
                { label: 'Closed', value: 'closed' },
                { label: 'All', value: 'all' }
            ],
            { placeHolder: 'Select PR state' }
        );
        
        if (!state) {
            return;
        }
        
        const response = await apiClient.get(`/github/repos/${owner}/${repo}/pulls?state=${state.value}`);
        
        if (response.total === 0) {
            vscode.window.showInformationMessage('No pull requests found');
            return;
        }
        
        const items = response.pull_requests.map((pr: any) => ({
            label: `#${pr.number} ${pr.title}`,
            description: pr.user.login,
            detail: `${pr.state} | ${pr.head.ref} → ${pr.base.ref}`,
            pr: pr
        }));
        
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a pull request'
        });
        
        if (!selected) {
            return;
        }
        
        // Show PR details
        showPullRequestDetails(selected.pr);
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list pull requests: ${error.message}`);
    }
}

/**
 * Create pull request
 */
async function createPullRequest(apiClient: APIClient) {
    try {
        const repoInput = await vscode.window.showInputBox({
            prompt: 'Enter repository (owner/repo)',
            placeHolder: 'owner/repo'
        });
        
        if (!repoInput) {
            return;
        }
        
        const [owner, repo] = repoInput.split('/');
        
        const title = await vscode.window.showInputBox({
            prompt: 'Enter PR title',
            placeHolder: 'Add new feature'
        });
        
        if (!title) {
            return;
        }
        
        const head = await vscode.window.showInputBox({
            prompt: 'Enter head branch',
            placeHolder: 'feature-branch'
        });
        
        if (!head) {
            return;
        }
        
        const base = await vscode.window.showInputBox({
            prompt: 'Enter base branch',
            value: 'main',
            placeHolder: 'main'
        });
        
        if (!base) {
            return;
        }
        
        const body = await vscode.window.showInputBox({
            prompt: 'Enter PR description (optional)',
            placeHolder: 'Describe your changes...'
        });
        
        const pr = await apiClient.post(`/github/repos/${owner}/${repo}/pulls`, {
            title,
            head,
            base,
            body,
            draft: false
        });
        
        vscode.window.showInformationMessage(
            `Pull request created: #${pr.number}`,
            'Open in Browser'
        ).then(selection => {
            if (selection === 'Open in Browser') {
                vscode.env.openExternal(vscode.Uri.parse(pr.html_url));
            }
        });
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to create pull request: ${error.message}`);
    }
}

/**
 * Review pull request
 */
async function reviewPullRequest(apiClient: APIClient) {
    try {
        const repoInput = await vscode.window.showInputBox({
            prompt: 'Enter repository (owner/repo)',
            placeHolder: 'owner/repo'
        });
        
        if (!repoInput) {
            return;
        }
        
        const [owner, repo] = repoInput.split('/');
        
        const prNumber = await vscode.window.showInputBox({
            prompt: 'Enter PR number',
            placeHolder: '123'
        });
        
        if (!prNumber) {
            return;
        }
        
        const reviewType = await vscode.window.showQuickPick(
            [
                { label: 'Approve', value: 'APPROVED' },
                { label: 'Request Changes', value: 'CHANGES_REQUESTED' },
                { label: 'Comment', value: 'COMMENTED' }
            ],
            { placeHolder: 'Select review type' }
        );
        
        if (!reviewType) {
            return;
        }
        
        const body = await vscode.window.showInputBox({
            prompt: 'Enter review comment',
            placeHolder: 'Looks good to me!'
        });
        
        if (!body) {
            return;
        }
        
        await apiClient.post(`/github/repos/${owner}/${repo}/pulls/${prNumber}/reviews`, {
            body,
            event: reviewType.value,
            comments: []
        });
        
        vscode.window.showInformationMessage('Review submitted successfully');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to submit review: ${error.message}`);
    }
}

/**
 * List issues
 */
async function listIssues(apiClient: APIClient) {
    try {
        const repoInput = await vscode.window.showInputBox({
            prompt: 'Enter repository (owner/repo)',
            placeHolder: 'owner/repo'
        });
        
        if (!repoInput) {
            return;
        }
        
        const [owner, repo] = repoInput.split('/');
        
        const state = await vscode.window.showQuickPick(
            [
                { label: 'Open', value: 'open' },
                { label: 'Closed', value: 'closed' },
                { label: 'All', value: 'all' }
            ],
            { placeHolder: 'Select issue state' }
        );
        
        if (!state) {
            return;
        }
        
        const response = await apiClient.get(`/github/repos/${owner}/${repo}/issues?state=${state.value}`);
        
        if (response.total === 0) {
            vscode.window.showInformationMessage('No issues found');
            return;
        }
        
        const items = response.issues.map((issue: any) => ({
            label: `#${issue.number} ${issue.title}`,
            description: issue.user.login,
            detail: `${issue.state} | 💬 ${issue.comments}`,
            issue: issue
        }));
        
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select an issue'
        });
        
        if (!selected) {
            return;
        }
        
        // Show issue details
        showIssueDetails(selected.issue);
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list issues: ${error.message}`);
    }
}

/**
 * Create issue
 */
async function createIssue(apiClient: APIClient) {
    try {
        const repoInput = await vscode.window.showInputBox({
            prompt: 'Enter repository (owner/repo)',
            placeHolder: 'owner/repo'
        });
        
        if (!repoInput) {
            return;
        }
        
        const [owner, repo] = repoInput.split('/');
        
        const title = await vscode.window.showInputBox({
            prompt: 'Enter issue title',
            placeHolder: 'Bug: Something is broken'
        });
        
        if (!title) {
            return;
        }
        
        const body = await vscode.window.showInputBox({
            prompt: 'Enter issue description (optional)',
            placeHolder: 'Describe the issue...'
        });
        
        const issue = await apiClient.post(`/github/repos/${owner}/${repo}/issues`, {
            title,
            body,
            labels: [],
            assignees: []
        });
        
        vscode.window.showInformationMessage(
            `Issue created: #${issue.number}`,
            'Open in Browser'
        ).then(selection => {
            if (selection === 'Open in Browser') {
                vscode.env.openExternal(vscode.Uri.parse(issue.html_url));
            }
        });
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to create issue: ${error.message}`);
    }
}

/**
 * List branches
 */
async function listBranches(apiClient: APIClient) {
    try {
        const repoInput = await vscode.window.showInputBox({
            prompt: 'Enter repository (owner/repo)',
            placeHolder: 'owner/repo'
        });
        
        if (!repoInput) {
            return;
        }
        
        const [owner, repo] = repoInput.split('/');
        
        const response = await apiClient.get(`/github/repos/${owner}/${repo}/branches`);
        
        if (response.total === 0) {
            vscode.window.showInformationMessage('No branches found');
            return;
        }
        
        const items = response.branches.map((branch: any) => ({
            label: branch.name,
            description: branch.commit.sha.substring(0, 7),
            detail: branch.protected ? '🔒 Protected' : '',
            branch: branch
        }));
        
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a branch'
        });
        
        if (selected) {
            vscode.window.showInformationMessage(`Branch: ${selected.label}`);
        }
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list branches: ${error.message}`);
    }
}

/**
 * Create branch
 */
async function createBranch(apiClient: APIClient) {
    try {
        const repoInput = await vscode.window.showInputBox({
            prompt: 'Enter repository (owner/repo)',
            placeHolder: 'owner/repo'
        });
        
        if (!repoInput) {
            return;
        }
        
        const [owner, repo] = repoInput.split('/');
        
        const name = await vscode.window.showInputBox({
            prompt: 'Enter branch name',
            placeHolder: 'feature/new-feature'
        });
        
        if (!name) {
            return;
        }
        
        const fromBranch = await vscode.window.showInputBox({
            prompt: 'Enter source branch',
            value: 'main',
            placeHolder: 'main'
        });
        
        if (!fromBranch) {
            return;
        }
        
        await apiClient.post(`/github/repos/${owner}/${repo}/branches`, {
            name,
            from_branch: fromBranch
        });
        
        vscode.window.showInformationMessage(`Branch created: ${name}`);
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to create branch: ${error.message}`);
    }
}

/**
 * List workflows
 */
async function listWorkflows(apiClient: APIClient) {
    try {
        const repoInput = await vscode.window.showInputBox({
            prompt: 'Enter repository (owner/repo)',
            placeHolder: 'owner/repo'
        });
        
        if (!repoInput) {
            return;
        }
        
        const [owner, repo] = repoInput.split('/');
        
        const response = await apiClient.get(`/github/repos/${owner}/${repo}/actions/workflows`);
        
        if (response.total === 0) {
            vscode.window.showInformationMessage('No workflows found');
            return;
        }
        
        const items = response.workflows.map((workflow: any) => ({
            label: workflow.name,
            description: workflow.path,
            detail: workflow.state,
            workflow: workflow
        }));
        
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a workflow'
        });
        
        if (selected) {
            vscode.window.showInformationMessage(`Workflow: ${selected.label}`);
        }
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list workflows: ${error.message}`);
    }
}

/**
 * Trigger workflow
 */
async function triggerWorkflow(apiClient: APIClient) {
    try {
        const repoInput = await vscode.window.showInputBox({
            prompt: 'Enter repository (owner/repo)',
            placeHolder: 'owner/repo'
        });
        
        if (!repoInput) {
            return;
        }
        
        const [owner, repo] = repoInput.split('/');
        
        const workflowId = await vscode.window.showInputBox({
            prompt: 'Enter workflow ID or filename',
            placeHolder: 'deploy.yml'
        });
        
        if (!workflowId) {
            return;
        }
        
        const ref = await vscode.window.showInputBox({
            prompt: 'Enter branch or tag',
            value: 'main',
            placeHolder: 'main'
        });
        
        if (!ref) {
            return;
        }
        
        await apiClient.post(`/github/repos/${owner}/${repo}/actions/workflows/trigger`, {
            workflow_id: workflowId,
            ref,
            inputs: {}
        });
        
        vscode.window.showInformationMessage('Workflow triggered successfully');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to trigger workflow: ${error.message}`);
    }
}

// ============================================================================
// HTML GENERATORS
// ============================================================================

function getRepositoryDetailsHTML(repo: any): string {
    return `<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Repository Details</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 20px;
                background: #1e1e1e;
                color: #d4d4d4;
            }
            h1 { color: #4ec9b0; }
            .stat {
                display: inline-block;
                margin-right: 20px;
                padding: 10px;
                background: #2d2d2d;
                border-radius: 4px;
            }
            .label {
                display: inline-block;
                padding: 4px 8px;
                margin: 2px;
                background: #0e639c;
                border-radius: 4px;
                font-size: 12px;
            }
            a { color: #4ec9b0; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>${repo.full_name}</h1>
        <p>${repo.description || 'No description'}</p>
        
        <div>
            <div class="stat">⭐ ${repo.stargazers_count} Stars</div>
            <div class="stat">🍴 ${repo.forks_count} Forks</div>
            <div class="stat">👁️ ${repo.watchers_count} Watchers</div>
            <div class="stat">${repo.private ? '🔒 Private' : '🌐 Public'}</div>
        </div>
        
        <h2>Details</h2>
        <p><strong>Language:</strong> ${repo.language || 'N/A'}</p>
        <p><strong>Default Branch:</strong> ${repo.default_branch}</p>
        <p><strong>Created:</strong> ${new Date(repo.created_at).toLocaleString()}</p>
        <p><strong>Updated:</strong> ${new Date(repo.updated_at).toLocaleString()}</p>
        <p><strong>Size:</strong> ${(repo.size / 1024).toFixed(2)} MB</p>
        
        ${repo.topics && repo.topics.length > 0 ? `
        <h2>Topics</h2>
        <div>
            ${repo.topics.map((topic: string) => `<span class="label">${topic}</span>`).join('')}
        </div>
        ` : ''}
        
        <h2>Links</h2>
        <p><a href="${repo.html_url}">View on GitHub</a></p>
        ${repo.homepage ? `<p><a href="${repo.homepage}">Homepage</a></p>` : ''}
    </body>
    </html>`;
}

function showPullRequestDetails(pr: any) {
    const panel = vscode.window.createWebviewPanel(
        'prDetails',
        `PR #${pr.number}: ${pr.title}`,
        vscode.ViewColumn.One,
        { enableScripts: true }
    );
    
    panel.webview.html = `<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 20px;
                background: #1e1e1e;
                color: #d4d4d4;
            }
            h1 { color: #4ec9b0; }
            .badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            .open { background: #28a745; color: white; }
            .closed { background: #cb2431; color: white; }
            .merged { background: #6f42c1; color: white; }
        </style>
    </head>
    <body>
        <h1>PR #${pr.number}: ${pr.title}</h1>
        <p><span class="badge ${pr.state}">${pr.state.toUpperCase()}</span></p>
        <p><strong>Author:</strong> ${pr.user.login}</p>
        <p><strong>Branch:</strong> ${pr.head.ref} → ${pr.base.ref}</p>
        <p><strong>Created:</strong> ${new Date(pr.created_at).toLocaleString()}</p>
        ${pr.body ? `<h2>Description</h2><p>${pr.body}</p>` : ''}
        <p><a href="${pr.html_url}">View on GitHub</a></p>
    </body>
    </html>`;
}

function showIssueDetails(issue: any) {
    const panel = vscode.window.createWebviewPanel(
        'issueDetails',
        `Issue #${issue.number}: ${issue.title}`,
        vscode.ViewColumn.One,
        { enableScripts: true }
    );
    
    panel.webview.html = `<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 20px;
                background: #1e1e1e;
                color: #d4d4d4;
            }
            h1 { color: #4ec9b0; }
            .badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            .open { background: #28a745; color: white; }
            .closed { background: #cb2431; color: white; }
            .label {
                display: inline-block;
                padding: 4px 8px;
                margin: 2px;
                background: #0e639c;
                border-radius: 4px;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <h1>Issue #${issue.number}: ${issue.title}</h1>
        <p><span class="badge ${issue.state}">${issue.state.toUpperCase()}</span></p>
        <p><strong>Author:</strong> ${issue.user.login}</p>
        <p><strong>Comments:</strong> ${issue.comments}</p>
        <p><strong>Created:</strong> ${new Date(issue.created_at).toLocaleString()}</p>
        ${issue.labels && issue.labels.length > 0 ? `
        <p><strong>Labels:</strong> ${issue.labels.map((label: any) => `<span class="label">${label.name}</span>`).join('')}</p>
        ` : ''}
        ${issue.body ? `<h2>Description</h2><p>${issue.body}</p>` : ''}
        <p><a href="${issue.html_url}">View on GitHub</a></p>
    </body>
    </html>`;
}