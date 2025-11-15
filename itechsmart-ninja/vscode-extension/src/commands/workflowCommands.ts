/**
 * Workflow Commands - VS Code commands for workflow management
 */

import * as vscode from 'vscode';
import { APIClient } from '../api/client';

export function registerWorkflowCommands(context: vscode.ExtensionContext, apiClient: APIClient) {
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.createWorkflow', () => createWorkflow(apiClient)),
        vscode.commands.registerCommand('itechsmart.editWorkflow', () => editWorkflow(apiClient)),
        vscode.commands.registerCommand('itechsmart.executeWorkflow', () => executeWorkflow(apiClient)),
        vscode.commands.registerCommand('itechsmart.viewWorkflowHistory', () => viewWorkflowHistory(apiClient)),
        vscode.commands.registerCommand('itechsmart.browseTemplates', () => browseTemplates(apiClient)),
        vscode.commands.registerCommand('itechsmart.listWorkflows', () => listWorkflows(apiClient)),
        vscode.commands.registerCommand('itechsmart.deleteWorkflow', () => deleteWorkflow(apiClient)),
        vscode.commands.registerCommand('itechsmart.shareWorkflow', () => shareWorkflow(apiClient))
    );
}

async function createWorkflow(apiClient: APIClient) {
    try {
        const name = await vscode.window.showInputBox({
            prompt: 'Enter workflow name',
            placeHolder: 'My Workflow'
        });

        if (!name) {
            return;
        }

        const description = await vscode.window.showInputBox({
            prompt: 'Enter workflow description',
            placeHolder: 'Workflow description'
        });

        // Create basic workflow with start and end nodes
        const nodes = [
            {
                id: 'start',
                type: 'start',
                name: 'Start',
                config: {},
                position: { x: 100, y: 100 },
                next_nodes: ['end']
            },
            {
                id: 'end',
                type: 'end',
                name: 'End',
                config: {},
                position: { x: 300, y: 100 },
                next_nodes: []
            }
        ];

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Creating workflow...',
            cancellable: false
        }, async () => {
            const response = await apiClient.post('/api/workflows/create', {
                name: name,
                description: description || '',
                nodes: nodes,
                variables: {}
            });

            if (response.success) {
                const workflow = response.workflow;
                
                // Show workflow in webview
                const panel = vscode.window.createWebviewPanel(
                    'workflowEditor',
                    `Workflow: ${workflow.name}`,
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = getWorkflowEditorHTML(workflow);
                
                vscode.window.showInformationMessage(`Workflow "${name}" created successfully!`);
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to create workflow: ${error.message}`);
    }
}

async function editWorkflow(apiClient: APIClient) {
    try {
        // Get list of workflows
        const response = await apiClient.get('/api/workflows');

        if (!response.success || response.workflows.length === 0) {
            vscode.window.showInformationMessage('No workflows found. Create one first!');
            return;
        }

        // Show workflow picker
        const items = response.workflows.map((wf: any) => ({
            label: wf.name,
            description: wf.description,
            workflow: wf
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select workflow to edit'
        });

        if (!selected) {
            return;
        }

        // Show workflow editor
        const panel = vscode.window.createWebviewPanel(
            'workflowEditor',
            `Edit: ${selected.workflow.name}`,
            vscode.ViewColumn.One,
            { enableScripts: true }
        );

        panel.webview.html = getWorkflowEditorHTML(selected.workflow);

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to edit workflow: ${error.message}`);
    }
}

async function executeWorkflow(apiClient: APIClient) {
    try {
        // Get list of workflows
        const response = await apiClient.get('/api/workflows');

        if (!response.success || response.workflows.length === 0) {
            vscode.window.showInformationMessage('No workflows found. Create one first!');
            return;
        }

        // Show workflow picker
        const items = response.workflows.map((wf: any) => ({
            label: wf.name,
            description: wf.description,
            workflow: wf
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select workflow to execute'
        });

        if (!selected) {
            return;
        }

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Executing workflow: ${selected.workflow.name}...`,
            cancellable: false
        }, async () => {
            const execResponse = await apiClient.post(
                `/api/workflows/${selected.workflow.id}/execute`,
                { input_context: {} }
            );

            if (execResponse.success) {
                const execution = execResponse.execution;
                
                // Show execution results
                const panel = vscode.window.createWebviewPanel(
                    'workflowExecution',
                    `Execution: ${selected.workflow.name}`,
                    vscode.ViewColumn.Two,
                    { enableScripts: true }
                );

                panel.webview.html = getExecutionResultsHTML(execution);
                
                if (execution.status === 'completed') {
                    vscode.window.showInformationMessage('Workflow executed successfully!');
                } else if (execution.status === 'failed') {
                    vscode.window.showErrorMessage(`Workflow execution failed: ${execution.error}`);
                }
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to execute workflow: ${error.message}`);
    }
}

async function viewWorkflowHistory(apiClient: APIClient) {
    try {
        // Get list of workflows
        const response = await apiClient.get('/api/workflows');

        if (!response.success || response.workflows.length === 0) {
            vscode.window.showInformationMessage('No workflows found.');
            return;
        }

        // Show workflow picker
        const items = response.workflows.map((wf: any) => ({
            label: wf.name,
            description: wf.description,
            workflow: wf
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select workflow to view history'
        });

        if (!selected) {
            return;
        }

        // Get execution history
        const historyResponse = await apiClient.get(
            `/api/workflows/${selected.workflow.id}/history`
        );

        if (historyResponse.success) {
            const panel = vscode.window.createWebviewPanel(
                'workflowHistory',
                `History: ${selected.workflow.name}`,
                vscode.ViewColumn.Two,
                { enableScripts: true }
            );

            panel.webview.html = getHistoryHTML(historyResponse.executions, selected.workflow.name);
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to view history: ${error.message}`);
    }
}

async function browseTemplates(apiClient: APIClient) {
    try {
        const response = await apiClient.get('/api/workflows/templates/list');

        if (!response.success || response.templates.length === 0) {
            vscode.window.showInformationMessage('No templates available.');
            return;
        }

        // Show template picker
        const items = response.templates.map((tmpl: any) => ({
            label: tmpl.name,
            description: tmpl.description,
            template: tmpl
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select template to use'
        });

        if (!selected) {
            return;
        }

        // Ask for workflow name
        const name = await vscode.window.showInputBox({
            prompt: 'Enter name for new workflow',
            placeHolder: selected.template.name
        });

        if (!name) {
            return;
        }

        // Create from template
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Creating workflow from template...',
            cancellable: false
        }, async () => {
            const createResponse = await apiClient.post(
                '/api/workflows/templates/create-from',
                {
                    template_id: selected.template.id,
                    name: name,
                    variables: {}
                }
            );

            if (createResponse.success) {
                vscode.window.showInformationMessage(`Workflow "${name}" created from template!`);
                
                // Show workflow editor
                const panel = vscode.window.createWebviewPanel(
                    'workflowEditor',
                    `Workflow: ${name}`,
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = getWorkflowEditorHTML(createResponse.workflow);
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to browse templates: ${error.message}`);
    }
}

async function listWorkflows(apiClient: APIClient) {
    try {
        const response = await apiClient.get('/api/workflows');

        if (!response.success || response.workflows.length === 0) {
            vscode.window.showInformationMessage('No workflows found. Create one first!');
            return;
        }

        // Show workflows in webview
        const panel = vscode.window.createWebviewPanel(
            'workflowList',
            'My Workflows',
            vscode.ViewColumn.One,
            { enableScripts: true }
        );

        panel.webview.html = getWorkflowListHTML(response.workflows);

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list workflows: ${error.message}`);
    }
}

async function deleteWorkflow(apiClient: APIClient) {
    try {
        // Get list of workflows
        const response = await apiClient.get('/api/workflows');

        if (!response.success || response.workflows.length === 0) {
            vscode.window.showInformationMessage('No workflows found.');
            return;
        }

        // Show workflow picker
        const items = response.workflows.map((wf: any) => ({
            label: wf.name,
            description: wf.description,
            workflow: wf
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select workflow to delete'
        });

        if (!selected) {
            return;
        }

        // Confirm deletion
        const confirm = await vscode.window.showWarningMessage(
            `Are you sure you want to delete "${selected.workflow.name}"?`,
            'Yes', 'No'
        );

        if (confirm !== 'Yes') {
            return;
        }

        // Delete workflow
        const deleteResponse = await apiClient.delete(
            `/api/workflows/${selected.workflow.id}`
        );

        if (deleteResponse.success) {
            vscode.window.showInformationMessage(`Workflow "${selected.workflow.name}" deleted successfully!`);
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to delete workflow: ${error.message}`);
    }
}

async function shareWorkflow(apiClient: APIClient) {
    try {
        // Get list of workflows
        const response = await apiClient.get('/api/workflows');

        if (!response.success || response.workflows.length === 0) {
            vscode.window.showInformationMessage('No workflows found.');
            return;
        }

        // Show workflow picker
        const items = response.workflows.map((wf: any) => ({
            label: wf.name,
            description: wf.description,
            workflow: wf
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select workflow to share'
        });

        if (!selected) {
            return;
        }

        // Ask for user ID
        const userId = await vscode.window.showInputBox({
            prompt: 'Enter user ID to share with',
            placeHolder: '123'
        });

        if (!userId) {
            return;
        }

        // Share workflow
        const shareResponse = await apiClient.post(
            `/api/workflows/${selected.workflow.id}/share`,
            { share_with_user_id: parseInt(userId) }
        );

        if (shareResponse.success) {
            vscode.window.showInformationMessage(`Workflow shared successfully!`);
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to share workflow: ${error.message}`);
    }
}

// HTML generators for webviews
function getWorkflowEditorHTML(workflow: any): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
                .header { background: #2d2d30; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .canvas { background: #252526; border: 1px solid #3e3e42; border-radius: 5px; min-height: 400px; padding: 20px; }
                .node { background: #007acc; color: white; padding: 15px; border-radius: 5px; margin: 10px; display: inline-block; }
                .info { margin: 10px 0; }
                .label { font-weight: bold; color: #4ec9b0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>${workflow.name}</h2>
                <p>${workflow.description}</p>
                <div class="info">
                    <span class="label">Version:</span> ${workflow.version}
                    <span class="label" style="margin-left: 20px;">Nodes:</span> ${workflow.nodes.length}
                </div>
            </div>
            
            <h3>Workflow Canvas</h3>
            <div class="canvas">
                ${workflow.nodes.map((node: any) => `
                    <div class="node">
                        <strong>${node.name}</strong>
                        <br><small>${node.type}</small>
                    </div>
                `).join('')}
            </div>
            
            <p style="margin-top: 20px; color: #858585;">
                💡 Tip: Use the visual workflow builder to add more nodes and connections.
            </p>
        </body>
        </html>
    `;
}

function getExecutionResultsHTML(execution: any): string {
    const statusColor = execution.status === 'completed' ? '#4caf50' : 
                       execution.status === 'failed' ? '#f44336' : '#ff9800';
    
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
                .status { background: ${statusColor}; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                .log { background: #252526; padding: 10px; margin: 5px 0; border-left: 3px solid #007acc; }
                .error { background: #5a1d1d; border-left-color: #f44336; }
                .info { margin: 10px 0; }
                .label { font-weight: bold; color: #4ec9b0; }
            </style>
        </head>
        <body>
            <div class="status">
                <h2>Execution Status: ${execution.status.toUpperCase()}</h2>
                <div class="info">
                    <span class="label">ID:</span> ${execution.id}
                    <br><span class="label">Started:</span> ${new Date(execution.start_time).toLocaleString()}
                    ${execution.end_time ? `<br><span class="label">Ended:</span> ${new Date(execution.end_time).toLocaleString()}` : ''}
                </div>
            </div>
            
            ${execution.error ? `
                <div class="log error">
                    <strong>Error:</strong> ${execution.error}
                </div>
            ` : ''}
            
            <h3>Execution Logs</h3>
            ${execution.logs.map((log: any) => `
                <div class="log">
                    <strong>${log.node_name}</strong> - ${log.status}
                    <br><small>${new Date(log.timestamp).toLocaleString()}</small>
                </div>
            `).join('')}
        </body>
        </html>
    `;
}

function getHistoryHTML(executions: any[], workflowName: string): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
                h2 { color: #4ec9b0; }
                .execution { background: #252526; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007acc; }
                .status { display: inline-block; padding: 5px 10px; border-radius: 3px; color: white; font-size: 12px; }
                .completed { background: #4caf50; }
                .failed { background: #f44336; }
                .running { background: #ff9800; }
            </style>
        </head>
        <body>
            <h2>Execution History: ${workflowName}</h2>
            <p>Total executions: ${executions.length}</p>
            
            ${executions.map(exec => `
                <div class="execution">
                    <span class="status ${exec.status}">${exec.status.toUpperCase()}</span>
                    <br><strong>ID:</strong> ${exec.id}
                    <br><strong>Started:</strong> ${new Date(exec.start_time).toLocaleString()}
                    ${exec.end_time ? `<br><strong>Ended:</strong> ${new Date(exec.end_time).toLocaleString()}` : ''}
                    ${exec.error ? `<br><strong>Error:</strong> ${exec.error}` : ''}
                </div>
            `).join('')}
        </body>
        </html>
    `;
}

function getWorkflowListHTML(workflows: any[]): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
                h2 { color: #4ec9b0; }
                .workflow { background: #252526; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007acc; }
                .workflow:hover { background: #2d2d30; cursor: pointer; }
                .badge { display: inline-block; padding: 3px 8px; background: #007acc; border-radius: 3px; font-size: 12px; margin-left: 10px; }
            </style>
        </head>
        <body>
            <h2>My Workflows</h2>
            <p>Total workflows: ${workflows.length}</p>
            
            ${workflows.map(wf => `
                <div class="workflow">
                    <h3>${wf.name} <span class="badge">v${wf.version}</span></h3>
                    <p>${wf.description}</p>
                    <small>Nodes: ${wf.nodes.length} | Created: ${new Date(wf.created_at).toLocaleDateString()}</small>
                </div>
            `).join('')}
        </body>
        </html>
    `;
}