/**
 * iTechSmart Ninja VS Code Extension
 * Main extension entry point
 */
import * as vscode from 'vscode';
import { ApiClient } from './api/client';
import { TerminalManager } from './terminal/manager';
import { TasksProvider } from './providers/tasksProvider';
import { AgentsProvider } from './providers/agentsProvider';
import { FilesProvider } from './providers/filesProvider';
import { AuthManager } from './auth/manager';
import { ModelCommands } from './commands/modelCommands';
import { ResearchCommands } from './commands/researchCommands';
import { registerEditorCommands } from './commands/editorCommands';
import { registerGitHubCommands } from './commands/githubCommands';
import { registerImageCommands } from './commands/imageCommands';
import { registerVisualizationCommands } from './commands/visualizationCommands';
import { registerDocumentCommands } from './commands/documentCommands';
import { registerVMCommands } from './commands/vmCommands';
import { registerSchedulerCommands } from './commands/schedulerCommands';
import { registerMCPCommands } from './commands/mcpCommands';
import { registerHistoryCommands } from './commands/historyCommands';
import { registerVideoCommands } from './commands/videoCommands';
import { registerDebugCommands } from './commands/debugCommands';
import { registerWorkflowCommands } from './commands/workflowCommands';
import { registerCollaborationCommands } from './commands/collaborationCommands';

let apiClient: ApiClient;
let terminalManager: TerminalManager;
let authManager: AuthManager;

export async function activate(context: vscode.ExtensionContext) {
    console.log('iTechSmart Ninja extension is now active!');

    // Initialize managers
    authManager = new AuthManager(context);
    apiClient = new ApiClient(authManager);
    terminalManager = new TerminalManager(apiClient, context);
    const modelCommands = new ModelCommands(apiClient);
    const researchCommands = new ResearchCommands(apiClient);
    
    // Register editor commands
    registerEditorCommands(context, apiClient);
    
    // Register GitHub commands
    registerGitHubCommands(context, apiClient);
    
    // Register image generation commands
    registerImageCommands(context, apiClient);
    
    // Register visualization commands
    registerVisualizationCommands(context, apiClient);
    
    // Register document processing commands
    registerDocumentCommands(context, apiClient);
    
    // Register VM management commands
    registerVMCommands(context, apiClient);
    
    // Register scheduler commands
    registerSchedulerCommands(context, apiClient);
    
    // Register MCP commands
    registerMCPCommands(context, apiClient);
    
    // Register history commands
    registerHistoryCommands(context, apiClient);
    
    // Register video generation commands
    registerVideoCommands(context, apiClient);
    
    // Register debugging commands
    registerDebugCommands(context, apiClient);
    
    // Register workflow commands
    registerWorkflowCommands(context, apiClient);
    
    // Register collaboration commands
    registerCollaborationCommands(context, apiClient);

    // Register tree data providers
    const tasksProvider = new TasksProvider(apiClient);
    const agentsProvider = new AgentsProvider(apiClient);
    const filesProvider = new FilesProvider(apiClient);

    vscode.window.registerTreeDataProvider('itechsmart.tasksView', tasksProvider);
    vscode.window.registerTreeDataProvider('itechsmart.agentsView', agentsProvider);
    vscode.window.registerTreeDataProvider('itechsmart.filesView', filesProvider);

    // Register commands
    context.subscriptions.push(
        // Terminal commands
        vscode.commands.registerCommand('itechsmart.openTerminal', () => {
            terminalManager.openTerminal();
        }),

        // Authentication commands
        vscode.commands.registerCommand('itechsmart.login', async () => {
            await authManager.login();
            tasksProvider.refresh();
            agentsProvider.refresh();
            filesProvider.refresh();
        }),

        vscode.commands.registerCommand('itechsmart.logout', async () => {
            await authManager.logout();
            tasksProvider.refresh();
            agentsProvider.refresh();
            filesProvider.refresh();
        }),

        // Code generation commands
        vscode.commands.registerCommand('itechsmart.generateCode', async () => {
            const description = await vscode.window.showInputBox({
                prompt: 'Describe what code you want to generate',
                placeHolder: 'e.g., Create a REST API endpoint for user authentication'
            });

            if (description) {
                await generateCode(description);
            }
        }),

        // Code explanation
        vscode.commands.registerCommand('itechsmart.explainCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }

            const selection = editor.document.getText(editor.selection);
            if (!selection) {
                vscode.window.showErrorMessage('No code selected');
                return;
            }

            await explainCode(selection);
        }),

        // Code refactoring
        vscode.commands.registerCommand('itechsmart.refactorCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }

            const selection = editor.document.getText(editor.selection);
            if (!selection) {
                vscode.window.showErrorMessage('No code selected');
                return;
            }

            await refactorCode(selection, editor);
        }),

        // Code debugging
        vscode.commands.registerCommand('itechsmart.debugCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }

            const selection = editor.document.getText(editor.selection);
            if (!selection) {
                vscode.window.showErrorMessage('No code selected');
                return;
            }

            await debugCode(selection);
        }),

        // Task management
        vscode.commands.registerCommand('itechsmart.createTask', async () => {
            await createTask();
            tasksProvider.refresh();
        }),

        vscode.commands.registerCommand('itechsmart.viewTasks', () => {
            vscode.commands.executeCommand('workbench.view.extension.itechsmart-sidebar');
        }),

        vscode.commands.registerCommand('itechsmart.refreshTasks', () => {
            tasksProvider.refresh();
        }),

        vscode.commands.registerCommand('itechsmart.cancelTask', async (taskId: number) => {
            await apiClient.cancelTask(taskId);
            tasksProvider.refresh();
        }),

        vscode.commands.registerCommand('itechsmart.viewTaskDetails', async (taskId: number) => {
            await viewTaskDetails(taskId);
        }),

        // Model commands
        vscode.commands.registerCommand('itechsmart.showModels', async () => {
            await modelCommands.showAllModels();
        }),

        vscode.commands.registerCommand('itechsmart.selectModel', async () => {
            await modelCommands.selectModel();
        }),

        vscode.commands.registerCommand('itechsmart.devpareModels', async () => {
            await modelCommands.compareModels();
        }),

        vscode.commands.registerCommand('itechsmart.getModelRecommendations', async () => {
            await modelCommands.getRecommendations();
        }),

        vscode.commands.registerCommand('itechsmart.showUsageStats', async () => {
            await modelCommands.showUsageStats();
        }),

        vscode.commands.registerCommand('itechsmart.checkProviderStatus', async () => {
            await modelCommands.checkProviderStatus();
        }),

        // Research commands
        vscode.commands.registerCommand('itechsmart.performDeepResearch', async () => {
            await researchCommands.performDeepResearch();
        }),

        vscode.commands.registerCommand('itechsmart.formatCitation', async () => {
            await researchCommands.formatCitation();
        }),

        vscode.commands.registerCommand('itechsmart.checkCredibility', async () => {
            await researchCommands.checkCredibility();
        }),

        vscode.commands.registerCommand('itechsmart.viewCitationStyles', async () => {
            await researchCommands.viewCitationStyles();
        })
    );

    // Show welcome message
    if (!authManager.isAuthenticated()) {
        const result = await vscode.window.showInformationMessage(
            'Welcome to iTechSmart Ninja! Please login to get started.',
            'Login',
            'Later'
        );

        if (result === 'Login') {
            await authManager.login();
        }
    } else {
        vscode.window.showInformationMessage('iTechSmart Ninja is ready!');
    }

    // Auto-refresh tasks every 30 seconds
    setInterval(() => {
        if (authManager.isAuthenticated()) {
            tasksProvider.refresh();
        }
    }, 30000);
}

async function generateCode(description: string) {
    const editor = vscode.window.activeTextEditor;
    const language = editor?.document.languageId || 'python';

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Generating code...',
        cancellable: false
    }, async (progress) => {
        try {
            const task = await apiClient.createTask({
                title: 'Code Generation',
                description: description,
                task_type: 'code',
                parameters: {
                    language: language,
                    description: description
                }
            });

            // Wait for task completion
            const result = await waitForTaskCompletion(task.id, progress);

            if (result && result.code) {
                // Insert code at cursor position
                if (editor) {
                    editor.edit(editBuilder => {
                        editBuilder.insert(editor.selection.active, result.code);
                    });
                    vscode.window.showInformationMessage('Code generated successfully!');
                } else {
                    // Create new file
                    const doc = await vscode.workspace.openTextDocument({
                        content: result.code,
                        language: language
                    });
                    await vscode.window.showTextDocument(doc);
                }
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`Code generation failed: ${error.message}`);
        }
    });
}

async function explainCode(code: string) {
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Analyzing code...',
        cancellable: false
    }, async (progress) => {
        try {
            const task = await apiClient.createTask({
                title: 'Code Explanation',
                description: 'Explain the following code',
                task_type: 'documentation',
                parameters: {
                    code: code,
                    doc_type: 'explanation'
                }
            });

            const result = await waitForTaskCompletion(task.id, progress);

            if (result && result.explanation) {
                // Show explanation in webview
                const panel = vscode.window.createWebviewPanel(
                    'codeExplanation',
                    'Code Explanation',
                    vscode.ViewColumn.Beside,
                    {}
                );

                panel.webview.html = getExplanationHtml(result.explanation);
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`Code explanation failed: ${error.message}`);
        }
    });
}

async function refactorCode(code: string, editor: vscode.TextEditor) {
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Refactoring code...',
        cancellable: false
    }, async (progress) => {
        try {
            const task = await apiClient.createTask({
                title: 'Code Refactoring',
                description: 'Refactor the following code',
                task_type: 'code',
                parameters: {
                    code: code,
                    action: 'refactor',
                    language: editor.document.languageId
                }
            });

            const result = await waitForTaskCompletion(task.id, progress);

            if (result && result.refactored_code) {
                // Replace selected code
                editor.edit(editBuilder => {
                    editBuilder.replace(editor.selection, result.refactored_code);
                });
                vscode.window.showInformationMessage('Code refactored successfully!');
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`Code refactoring failed: ${error.message}`);
        }
    });
}

async function debugCode(code: string) {
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Debugging code...',
        cancellable: false
    }, async (progress) => {
        try {
            const task = await apiClient.createTask({
                title: 'Code Debugging',
                description: 'Debug the following code',
                task_type: 'debug',
                parameters: {
                    code: code
                }
            });

            const result = await waitForTaskCompletion(task.id, progress);

            if (result) {
                // Show debug results in webview
                const panel = vscode.window.createWebviewPanel(
                    'debugResults',
                    'Debug Results',
                    vscode.ViewColumn.Beside,
                    {}
                );

                panel.webview.html = getDebugResultsHtml(result);
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`Code debugging failed: ${error.message}`);
        }
    });
}

async function createTask() {
    const taskType = await vscode.window.showQuickPick([
        { label: 'Research', value: 'research' },
        { label: 'Code Generation', value: 'code' },
        { label: 'Website Creation', value: 'website' },
        { label: 'Data Analysis', value: 'analysis' },
        { label: 'Debugging', value: 'debug' },
        { label: 'Documentation', value: 'documentation' }
    ], {
        placeHolder: 'Select task type'
    });

    if (!taskType) return;

    const title = await vscode.window.showInputBox({
        prompt: 'Enter task title',
        placeHolder: 'e.g., Research AI trends'
    });

    if (!title) return;

    const description = await vscode.window.showInputBox({
        prompt: 'Enter task description',
        placeHolder: 'Detailed description of what you want to accomplish'
    });

    if (!description) return;

    try {
        await apiClient.createTask({
            title: title,
            description: description,
            task_type: taskType.value,
            parameters: {}
        });

        vscode.window.showInformationMessage('Task created successfully!');
    } catch (error: any) {
        vscode.window.showErrorMessage(`Task creation failed: ${error.message}`);
    }
}

async function viewTaskDetails(taskId: number) {
    try {
        const task = await apiClient.getTask(taskId);
        const steps = await apiClient.getTaskSteps(taskId);

        const panel = vscode.window.createWebviewPanel(
            'taskDetails',
            `Task: ${task.title}`,
            vscode.ViewColumn.One,
            {}
        );

        panel.webview.html = getTaskDetailsHtml(task, steps);
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to load task details: ${error.message}`);
    }
}

async function waitForTaskCompletion(taskId: number, progress: vscode.Progress<any>): Promise<any> {
    return new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
            try {
                const task = await apiClient.getTask(taskId);
                
                progress.report({ message: `Progress: ${task.progress}%` });

                if (task.status === 'completed') {
                    clearInterval(interval);
                    resolve(task.result);
                } else if (task.status === 'failed') {
                    clearInterval(interval);
                    reject(new Error(task.error || 'Task failed'));
                }
            } catch (error) {
                clearInterval(interval);
                reject(error);
            }
        }, 2000);

        // Timeout after 5 minutes
        setTimeout(() => {
            clearInterval(interval);
            reject(new Error('Task timeout'));
        }, 300000);
    });
}

function getExplanationHtml(explanation: string): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    padding: 20px;
                    line-height: 1.6;
                }
                h1 { color: #007acc; }
                pre { 
                    background: #f4f4f4; 
                    padding: 10px; 
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <h1>Code Explanation</h1>
            <div>${explanation.replace(/\n/g, '<br>')}</div>
        </body>
        </html>
    `;
}

function getDebugResultsHtml(result: any): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    padding: 20px;
                }
                h1 { color: #007acc; }
                .error { color: #d32f2f; }
                .fix { color: #388e3c; }
                pre { 
                    background: #f4f4f4; 
                    padding: 10px; 
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <h1>Debug Results</h1>
            <h2 class="error">Error Analysis</h2>
            <pre>${JSON.stringify(result.error_analysis, null, 2)}</pre>
            <h2 class="fix">Suggested Fix</h2>
            <pre>${result.fix || 'No fix available'}</pre>
        </body>
        </html>
    `;
}

function getTaskDetailsHtml(task: any, steps: any[]): string {
    const stepsHtml = steps.map(step => `
        <div class="step">
            <h3>Step ${step.step_number}: ${step.agent_type}</h3>
            <p><strong>Status:</strong> ${step.status}</p>
            <p><strong>Description:</strong> ${step.description}</p>
            ${step.result ? `<pre>${JSON.stringify(step.result, null, 2)}</pre>` : ''}
        </div>
    `).join('');

    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    padding: 20px;
                }
                h1 { color: #007acc; }
                .step {
                    border: 1px solid #ddd;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                }
                pre { 
                    background: #f4f4f4; 
                    padding: 10px; 
                    border-radius: 5px;
                    overflow-x: auto;
                }
            </style>
        </head>
        <body>
            <h1>${task.title}</h1>
            <p><strong>Type:</strong> ${task.task_type}</p>
            <p><strong>Status:</strong> ${task.status}</p>
            <p><strong>Progress:</strong> ${task.progress}%</p>
            <p><strong>Description:</strong> ${task.description}</p>
            <h2>Steps</h2>
            ${stepsHtml}
            ${task.result ? `<h2>Result</h2><pre>${JSON.stringify(task.result, null, 2)}</pre>` : ''}
        </body>
        </html>
    `;
}

export function deactivate() {
    console.log('iTechSmart Ninja extension is now deactivated');
}