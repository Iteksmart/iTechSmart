/**
 * Collaboration Commands - VS Code commands for team collaboration
 */

import * as vscode from 'vscode';
import { APIClient } from '../api/client';

export function registerCollaborationCommands(context: vscode.ExtensionContext, apiClient: APIClient) {
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.createTeam', () => createTeam(apiClient)),
        vscode.commands.registerCommand('itechsmart.inviteTeamMember', () => inviteTeamMember(apiClient)),
        vscode.commands.registerCommand('itechsmart.switchWorkspace', () => switchWorkspace(apiClient)),
        vscode.commands.registerCommand('itechsmart.addComment', () => addComment(apiClient)),
        vscode.commands.registerCommand('itechsmart.viewTeamActivity', () => viewTeamActivity(apiClient)),
        vscode.commands.registerCommand('itechsmart.managePermissions', () => managePermissions(apiClient)),
        vscode.commands.registerCommand('itechsmart.listTeams', () => listTeams(apiClient)),
        vscode.commands.registerCommand('itechsmart.createWorkspace', () => createWorkspace(apiClient))
    );
}

async function createTeam(apiClient: APIClient) {
    try {
        const name = await vscode.window.showInputBox({
            prompt: 'Enter team name',
            placeHolder: 'My Team'
        });

        if (!name) return;

        const description = await vscode.window.showInputBox({
            prompt: 'Enter team description (optional)',
            placeHolder: 'Team description'
        });

        const plan = await vscode.window.showQuickPick(
            ['free', 'pro', 'enterprise'],
            { placeHolder: 'Select plan' }
        );

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Creating team...',
            cancellable: false
        }, async () => {
            const response = await apiClient.post('/api/teams/create', {
                name,
                description: description || '',
                plan: plan || 'free'
            });

            if (response.success) {
                vscode.window.showInformationMessage(`Team "${name}" created successfully!`);
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to create team: ${error.message}`);
    }
}

async function inviteTeamMember(apiClient: APIClient) {
    try {
        // Get teams
        const teamsResponse = await apiClient.get('/api/teams');
        if (!teamsResponse.success || teamsResponse.teams.length === 0) {
            vscode.window.showInformationMessage('No teams found. Create a team first!');
            return;
        }

        // Select team
        const teamItems = teamsResponse.teams.map((team: any) => ({
            label: team.name,
            description: team.description,
            team
        }));

        const selectedTeam = await vscode.window.showQuickPick(teamItems, {
            placeHolder: 'Select team'
        });

        if (!selectedTeam) return;

        // Get email
        const email = await vscode.window.showInputBox({
            prompt: 'Enter member email',
            placeHolder: 'member@example.com'
        });

        if (!email) return;

        // Select role
        const role = await vscode.window.showQuickPick(
            ['member', 'admin', 'viewer'],
            { placeHolder: 'Select role' }
        );

        if (!role) return;

        // Send invitation
        const response = await apiClient.post(
            `/api/teams/${selectedTeam.team.id}/invite`,
            { email, role }
        );

        if (response.success) {
            vscode.window.showInformationMessage(`Invitation sent to ${email}!`);
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to invite member: ${error.message}`);
    }
}

async function switchWorkspace(apiClient: APIClient) {
    try {
        // Get teams
        const teamsResponse = await apiClient.get('/api/teams');
        if (!teamsResponse.success || teamsResponse.teams.length === 0) {
            vscode.window.showInformationMessage('No teams found.');
            return;
        }

        // Select team
        const teamItems = teamsResponse.teams.map((team: any) => ({
            label: team.name,
            team
        }));

        const selectedTeam = await vscode.window.showQuickPick(teamItems, {
            placeHolder: 'Select team'
        });

        if (!selectedTeam) return;

        // Get workspaces
        const workspacesResponse = await apiClient.get(
            `/api/teams/${selectedTeam.team.id}/workspaces`
        );

        if (!workspacesResponse.success || workspacesResponse.workspaces.length === 0) {
            vscode.window.showInformationMessage('No workspaces found. Create one first!');
            return;
        }

        // Select workspace
        const workspaceItems = workspacesResponse.workspaces.map((ws: any) => ({
            label: ws.name,
            description: ws.description,
            workspace: ws
        }));

        const selectedWorkspace = await vscode.window.showQuickPick(workspaceItems, {
            placeHolder: 'Select workspace'
        });

        if (!selectedWorkspace) return;

        vscode.window.showInformationMessage(
            `Switched to workspace: ${selectedWorkspace.workspace.name}`
        );

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to switch workspace: ${error.message}`);
    }
}

async function addComment(apiClient: APIClient) {
    try {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const content = await vscode.window.showInputBox({
            prompt: 'Enter comment',
            placeHolder: 'Your comment here...'
        });

        if (!content) return;

        const response = await apiClient.post('/api/comments/create', {
            resource_type: 'code',
            resource_id: 1, // Would be actual file/resource ID
            content
        });

        if (response.success) {
            vscode.window.showInformationMessage('Comment added successfully!');
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to add comment: ${error.message}`);
    }
}

async function viewTeamActivity(apiClient: APIClient) {
    try {
        // Get teams
        const teamsResponse = await apiClient.get('/api/teams');
        if (!teamsResponse.success || teamsResponse.teams.length === 0) {
            vscode.window.showInformationMessage('No teams found.');
            return;
        }

        // Select team
        const teamItems = teamsResponse.teams.map((team: any) => ({
            label: team.name,
            team
        }));

        const selectedTeam = await vscode.window.showQuickPick(teamItems, {
            placeHolder: 'Select team'
        });

        if (!selectedTeam) return;

        // Get activity
        const activityResponse = await apiClient.get(
            `/api/teams/${selectedTeam.team.id}/activity`
        );

        if (activityResponse.success) {
            const panel = vscode.window.createWebviewPanel(
                'teamActivity',
                `Activity: ${selectedTeam.team.name}`,
                vscode.ViewColumn.Two,
                { enableScripts: true }
            );

            panel.webview.html = getActivityHTML(
                activityResponse.activities,
                selectedTeam.team.name
            );
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to view activity: ${error.message}`);
    }
}

async function managePermissions(apiClient: APIClient) {
    try {
        // Get teams
        const teamsResponse = await apiClient.get('/api/teams');
        if (!teamsResponse.success || teamsResponse.teams.length === 0) {
            vscode.window.showInformationMessage('No teams found.');
            return;
        }

        // Select team
        const teamItems = teamsResponse.teams.map((team: any) => ({
            label: team.name,
            team
        }));

        const selectedTeam = await vscode.window.showQuickPick(teamItems, {
            placeHolder: 'Select team'
        });

        if (!selectedTeam) return;

        // Get members
        const membersResponse = await apiClient.get(
            `/api/teams/${selectedTeam.team.id}/members`
        );

        if (!membersResponse.success || membersResponse.members.length === 0) {
            vscode.window.showInformationMessage('No members found.');
            return;
        }

        // Show members panel
        const panel = vscode.window.createWebviewPanel(
            'teamPermissions',
            `Permissions: ${selectedTeam.team.name}`,
            vscode.ViewColumn.Two,
            { enableScripts: true }
        );

        panel.webview.html = getPermissionsHTML(
            membersResponse.members,
            selectedTeam.team.name
        );

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to manage permissions: ${error.message}`);
    }
}

async function listTeams(apiClient: APIClient) {
    try {
        const response = await apiClient.get('/api/teams');

        if (!response.success || response.teams.length === 0) {
            vscode.window.showInformationMessage('No teams found. Create one first!');
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'teamList',
            'My Teams',
            vscode.ViewColumn.One,
            { enableScripts: true }
        );

        panel.webview.html = getTeamsHTML(response.teams);

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list teams: ${error.message}`);
    }
}

async function createWorkspace(apiClient: APIClient) {
    try {
        // Get teams
        const teamsResponse = await apiClient.get('/api/teams');
        if (!teamsResponse.success || teamsResponse.teams.length === 0) {
            vscode.window.showInformationMessage('No teams found. Create a team first!');
            return;
        }

        // Select team
        const teamItems = teamsResponse.teams.map((team: any) => ({
            label: team.name,
            team
        }));

        const selectedTeam = await vscode.window.showQuickPick(teamItems, {
            placeHolder: 'Select team'
        });

        if (!selectedTeam) return;

        const name = await vscode.window.showInputBox({
            prompt: 'Enter workspace name',
            placeHolder: 'My Workspace'
        });

        if (!name) return;

        const description = await vscode.window.showInputBox({
            prompt: 'Enter workspace description (optional)',
            placeHolder: 'Workspace description'
        });

        const response = await apiClient.post(
            `/api/teams/${selectedTeam.team.id}/workspaces`,
            { name, description: description || '' }
        );

        if (response.success) {
            vscode.window.showInformationMessage(`Workspace "${name}" created successfully!`);
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to create workspace: ${error.message}`);
    }
}

// HTML generators
function getActivityHTML(activities: any[], teamName: string): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
                h2 { color: #4ec9b0; }
                .activity { background: #252526; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007acc; }
                .timestamp { color: #858585; font-size: 12px; }
            </style>
        </head>
        <body>
            <h2>Team Activity: ${teamName}</h2>
            <p>Total activities: ${activities.length}</p>
            ${activities.map(activity => `
                <div class="activity">
                    <strong>${activity.action.replace('_', ' ')}</strong>
                    <br><span class="timestamp">${new Date(activity.timestamp).toLocaleString()}</span>
                    ${activity.details ? `<br><small>${JSON.stringify(activity.details)}</small>` : ''}
                </div>
            `).join('')}
        </body>
        </html>
    `;
}

function getPermissionsHTML(members: any[], teamName: string): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
                h2 { color: #4ec9b0; }
                .member { background: #252526; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .role { display: inline-block; padding: 5px 10px; background: #007acc; border-radius: 3px; color: white; }
            </style>
        </head>
        <body>
            <h2>Team Members: ${teamName}</h2>
            <p>Total members: ${members.length}</p>
            ${members.map(member => `
                <div class="member">
                    <strong>User ID: ${member.user_id}</strong>
                    <span class="role">${member.role}</span>
                    <br><small>Joined: ${new Date(member.joined_at).toLocaleDateString()}</small>
                </div>
            `).join('')}
        </body>
        </html>
    `;
}

function getTeamsHTML(teams: any[]): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
                h2 { color: #4ec9b0; }
                .team { background: #252526; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007acc; }
                .plan { display: inline-block; padding: 3px 8px; background: #4caf50; border-radius: 3px; font-size: 12px; }
            </style>
        </head>
        <body>
            <h2>My Teams</h2>
            <p>Total teams: ${teams.length}</p>
            ${teams.map(team => `
                <div class="team">
                    <h3>${team.name} <span class="plan">${team.plan}</span></h3>
                    <p>${team.description || 'No description'}</p>
                    <small>Members: ${team.member_count} | Workspaces: ${team.workspace_count}</small>
                </div>
            `).join('')}
        </body>
        </html>
    `;
}