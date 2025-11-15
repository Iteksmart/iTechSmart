/**
 * Terminal Panel
 * Webview-based AI terminal interface
 */
import * as vscode from 'vscode';
import { ApiClient } from '../api/client';

export class TerminalPanel {
    public static currentPanel: TerminalPanel | undefined;
    private readonly panel: vscode.WebviewPanel;
    private readonly extensionUri: vscode.Uri;
    private readonly apiClient: ApiClient;
    private disposables: vscode.Disposable[] = [];
    private commandHistory: string[] = [];
    private historyIndex: number = -1;

    constructor(extensionUri: vscode.Uri, apiClient: ApiClient) {
        this.extensionUri = extensionUri;
        this.apiClient = apiClient;

        // Create webview panel
        this.panel = vscode.window.createWebviewPanel(
            'itechsmartTerminal',
            'iTechSmart AI Terminal',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [this.extensionUri]
            }
        );

        // Set HTML content
        this.panel.webview.html = this.getHtmlContent();

        // Handle messages from webview
        this.panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.type) {
                    case 'command':
                        await this.handleCommand(message.command);
                        break;
                    case 'clear':
                        this.sendToTerminal({ type: 'clear' });
                        break;
                    case 'history-up':
                        this.navigateHistory(-1);
                        break;
                    case 'history-down':
                        this.navigateHistory(1);
                        break;
                }
            },
            null,
            this.disposables
        );

        // Handle panel disposal
        this.panel.onDidDispose(() => this.dispose(), null, this.disposables);

        // Send welcome message
        this.sendWelcomeMessage();
    }

    private sendWelcomeMessage() {
        this.sendToTerminal({
            type: 'output',
            content: `
╔══════════════════════════════════════════════════════════════╗
║           iTechSmart Ninja AI Terminal v1.0.0                ║
║                                                              ║
║  AI-Powered Development Assistant                           ║
║  Type 'help' for available commands                         ║
╚══════════════════════════════════════════════════════════════╝

`,
            color: '#00ff00'
        });
    }

    private async handleCommand(command: string) {
        if (!command.trim()) {
            return;
        }

        // Add to history
        this.commandHistory.push(command);
        this.historyIndex = this.commandHistory.length;

        // Echo command
        this.sendToTerminal({
            type: 'output',
            content: `$ ${command}\n`,
            color: '#00aaff'
        });

        // Parse and execute command
        const parts = command.trim().split(/\s+/);
        const cmd = parts[0].toLowerCase();
        const args = parts.slice(1);

        try {
            switch (cmd) {
                case 'help':
                    await this.showHelp();
                    break;
                case 'clear':
                    this.sendToTerminal({ type: 'clear' });
                    break;
                case 'generate':
                    await this.generateCode(args.join(' '));
                    break;
                case 'research':
                    await this.research(args.join(' '));
                    break;
                case 'analyze':
                    await this.analyze(args.join(' '));
                    break;
                case 'debug':
                    await this.debug(args.join(' '));
                    break;
                case 'explain':
                    await this.explain(args.join(' '));
                    break;
                case 'tasks':
                    await this.listTasks();
                    break;
                case 'task':
                    await this.viewTask(parseInt(args[0]));
                    break;
                case 'agents':
                    await this.listAgents();
                    break;
                case 'files':
                    await this.listFiles();
                    break;
                case 'status':
                    await this.showStatus();
                    break;
                case 'whoami':
                    await this.showCurrentUser();
                    break;
                   case 'gh-repos':
                       await this.listGitHubRepos();
                       break;
                   case 'gh-prs':
                       await this.listGitHubPRs(args);
                       break;
                   case 'gh-issues':
                       await this.listGitHubIssues(args);
                       break;
                   case 'gh-create-pr':
                       await this.createGitHubPR(args);
                       break;
                   case 'gh-create-issue':
                       await this.createGitHubIssue(args);
                       break;
                default:
                      case 'doc':
                    case 'document':
                        await this.showDocumentHelp();
                        break;
                    case 'doc-upload':
                    case 'upload-document':
                        await this.uploadDocument(args);
                        break;
                    case 'doc-list':
                    case 'list-documents':
                        await this.listDocuments();
                        break;
                    case 'doc-extract':
                    case 'extract-text':
                        await this.extractDocumentText(args);
                        break;
                    case 'doc-tables':
                    case 'extract-tables':
                        await this.extractDocumentTables(args);
                        break;
                    case 'doc-ocr':
                    case 'ocr-document':
                        await this.ocrDocument(args);
                        break;
                    case 'doc-search':
                    case 'search-document':
                        await this.searchDocument(args);
                        break;
                    case 'chart':
                    case 'create-chart':
                        await this.createChart(args);
                        break;
                    case 'dashboard':
                    case 'create-dashboard':
                        await this.createDashboard(args);
                        break;
                    case 'list-charts':
                        await this.listCharts();
                        break;
                    case 'export-chart':
                        await this.exportChart(args);
                        break;
                    case 'analyze':
                    case 'analyze-data':
                        await this.analyzeDataFile(args);
                        break;
                    case 'img-generate':
                      case 'generate-image':
                          await this.generateImage(args);
                          break;
                      case 'img-transform':
                      case 'transform-image':
                          await this.transformImage(args);
                          break;
                      case 'img-upscale':
                      case 'upscale-image':
                          await this.upscaleImage(args);
                          break;
                      case 'img-remove-bg':
                      case 'remove-background':
                          await this.removeBackground(args);
                          break;
                      case 'img-providers':
                      case 'list-image-providers':
                          await this.listImageProviders();
                          break;
                    case 'mcp':
                    case 'mcp-help':
                        await this.showMCPHelp();
                        break;
                    case 'mcp-register':
                    case 'register-source':
                        await this.registerMCPSource(args);
                        break;
                    case 'mcp-list':
                    case 'list-sources':
                        await this.listMCPSources();
                        break;
                    case 'mcp-query':
                    case 'query-source':
                        await this.queryMCPSource(args);
                        break;
                    case 'mcp-test':
                    case 'test-source':
                        await this.testMCPSource(args);
                        break;
                    case 'mcp-schema':
                    case 'view-schema':
                        await this.viewMCPSchema(args);
                        break;
                    case 'history':
                    case 'history-help':
                        await this.showHistoryHelp();
                        break;
                    case 'undo':
                        await this.undoAction();
                        break;
                    case 'redo':
                        await this.redoAction();
                        break;
                    case 'history-view':
                    case 'view-history':
                        await this.viewHistory();
                        break;
                    case 'history-search':
                    case 'search-history':
                        await this.searchHistory();
                        break;
                    case 'history-stats':
                    case 'stats':
                        await this.viewHistoryStats();
                        break;
                    case 'video':
                    case 'video-help':
                        await this.showVideoHelp();
                        break;

            case 'debug-help':
                this.showDebugHelp();
                break;

            case 'workflow-help':
                this.showWorkflowHelp();
                break;

            case 'collab-help':
            case 'team-help':
                this.showCollabHelp();
                break;
            case 'team-create':
            case 'create-team':
                this.createTeam();
                break;
            case 'team-invite':
            case 'invite-member':
                this.inviteTeamMember();
                break;
            case 'team-list':
            case 'list-teams':
                this.listTeamsCmd();
                break;
            case 'workspace-create':
            case 'create-workspace':
                this.createWorkspaceCmd();
                break;
            case 'workspace-switch':
            case 'switch-workspace':
                this.switchWorkspaceCmd();
                break;
            case 'comment-add':
            case 'add-comment':
                this.addCommentCmd();
                break;
            case 'team-activity':
            case 'view-activity':
                this.viewTeamActivityCmd();
                break;
            case 'team-permissions':
            case 'manage-permissions':
                this.managePermissionsCmd();
                break;

            case 'workflow-create':
            case 'create-workflow':
                this.createWorkflow();
                break;
            case 'workflow-edit':
            case 'edit-workflow':
                this.editWorkflow();
                break;
            case 'workflow-execute':
            case 'execute-workflow':
                this.executeWorkflow();
                break;
            case 'workflow-list':
            case 'list-workflows':
                this.listWorkflows();
                break;
            case 'workflow-history':
            case 'view-history':
                this.viewWorkflowHistory();
                break;
            case 'workflow-templates':
            case 'browse-templates':
                this.browseWorkflowTemplates();
                break;
            case 'workflow-delete':
            case 'delete-workflow':
                this.deleteWorkflow();
                break;
            case 'workflow-share':
            case 'share-workflow':
                this.shareWorkflow();
                break;

            case 'debug-analyze':
            case 'analyze-error':
                this.analyzeError();
                break;
            case 'debug-breakpoint':
            case 'set-breakpoint':
                this.setBreakpoint();
                break;
            case 'debug-list':
            case 'list-breakpoints':
                this.listBreakpoints();
                break;
            case 'debug-inspect':
            case 'inspect-variable':
                this.inspectVariable();
                break;
            case 'debug-profile':
            case 'profile-code':
                this.profileCode();
                break;
            case 'debug-leaks':
            case 'detect-leaks':
                this.detectMemoryLeaks();
                break;
            case 'debug-stack':
            case 'view-stack':
                this.viewCallStack();
                break;
            case 'debug-coverage':
            case 'get-coverage':
                this.getCodeCoverage();
                break;

                    case 'video-generate':
                    case 'generate-video':
                        await this.generateVideo();
                        break;
                    case 'video-transform':
                    case 'transform-video':
                        await this.transformVideo();
                        break;
                    case 'video-upscale':
                    case 'upscale-video':
                        await this.upscaleVideo();
                        break;
                    case 'video-edit':
                    case 'edit-video':
                        await this.editVideo();
                        break;
                    case 'video-list':
                    case 'list-videos':
                        await this.listVideos();
                        break;
                    this.sendToTerminal({
                        type: 'output',
                        content: `Unknown command: ${cmd}\nType 'help' for available commands.\n`,
                        color: '#ff6b6b'
                    });
            }
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }

        this.sendToTerminal({ type: 'ready' });
    }

    private async showHelp() {
        const helpText = `
Available Commands:
═══════════════════════════════════════════════════════════════

AI Commands:
  generate <description>    Generate code from description
  research <query>          Research a topic
  analyze <data>            Analyze data
  debug <code>              Debug code
  explain <code>            Explain code

Image Generation:
  img-generate              Generate image from text
  generate-image            (alias for img-generate)
  img-transform             Transform an existing image
  transform-image           (alias for img-transform)
  img-upscale               Upscale image resolution
  upscale-image             (alias for img-upscale)
  img-remove-bg             Remove image background
  remove-background         (alias for img-remove-bg)
  img-providers             List available image providers
  list-image-providers      (alias for img-providers)

   MCP Data Sources:
     mcp-register              Register new data source
     register-source           (alias for mcp-register)
     mcp-list                  List all data sources
     list-sources              (alias for mcp-list)
     mcp-query                 Query a data source
     query-source              (alias for mcp-query)
     mcp-test                  Test data source connection
     test-source               (alias for mcp-test)
     mcp-schema                View data source schema
     view-schema               (alias for mcp-schema)

   Action History:
     undo                      Undo last action
     redo                      Redo last undone action
     history-view              View action history
     view-history              (alias for history-view)
     history-search            Search action history
     search-history            (alias for history-search)
     history-stats             View history statistics
     stats                     (alias for history-stats)

   Video Generation:
     video-generate            Generate video from text
     generate-video            (alias for video-generate)
     video-transform           Transform existing video
     transform-video           (alias for video-transform)
     video-upscale             Upscale video resolution
     upscale-video             (alias for video-upscale)
     video-edit                Edit video (trim, merge, effects)
     edit-video                (alias for video-edit)
     video-list                List video generations
     list-videos               (alias for video-list)

GitHub Commands:
  gh-repos                  List GitHub repositories
  gh-prs [repo]             List pull requests
  gh-issues [repo]          List issues
  gh-create-pr              Create a pull request
  gh-create-issue           Create an issue

Task Management:
  tasks                     List all tasks
  task <id>                 View task details
  
Information:
  agents                    List available AI agents
  files                     List uploaded files
  status                    Show system status
  whoami                    Show current user

Terminal:
  help                      Show this help message
  clear                     Clear terminal
  
Keyboard Shortcuts:
  ↑/↓                       Navigate command history
  Ctrl+C                    Cancel current operation
  Ctrl+L                    Clear terminal

Examples:
  generate Create a REST API endpoint for user login
  research Latest AI trends in 2024
  analyze sales_data.csv
  img-generate A sunset over mountains
  gh-repos

`;
        this.sendToTerminal({
            type: 'output',
            content: helpText,
            color: '#ffffff'
        });
    }

    private async generateCode(description: string) {
        if (!description) {
            this.sendToTerminal({
                type: 'output',
                content: 'Usage: generate <description>\n',
                color: '#ff6b6b'
            });
            return;
        }

        this.sendToTerminal({
            type: 'output',
            content: 'Generating code...\n',
            color: '#ffaa00'
        });

        const editor = vscode.window.activeTextEditor;
        const language = editor?.document.languageId || 'python';

        const task = await this.apiClient.createTask({
            title: 'Code Generation',
            description: description,
            task_type: 'code',
            parameters: {
                language: language,
                description: description
            }
        });

        this.sendToTerminal({
            type: 'output',
            content: `Task created (ID: ${task.id}). Waiting for completion...\n`,
            color: '#00ff00'
        });

        // Poll for completion
        await this.waitForTask(task.id);
    }

    private async research(query: string) {
        if (!query) {
            this.sendToTerminal({
                type: 'output',
                content: 'Usage: research <query>\n',
                color: '#ff6b6b'
            });
            return;
        }

        this.sendToTerminal({
            type: 'output',
            content: 'Researching...\n',
            color: '#ffaa00'
        });

        const task = await this.apiClient.createTask({
            title: 'Research',
            description: query,
            task_type: 'research',
            parameters: {
                query: query,
                num_sources: 5
            }
        });

        this.sendToTerminal({
            type: 'output',
            content: `Task created (ID: ${task.id}). Researching...\n`,
            color: '#00ff00'
        });

        await this.waitForTask(task.id);
    }

    private async analyze(data: string) {
        if (!data) {
            this.sendToTerminal({
                type: 'output',
                content: 'Usage: analyze <data>\n',
                color: '#ff6b6b'
            });
            return;
        }

        this.sendToTerminal({
            type: 'output',
            content: 'Analyzing data...\n',
            color: '#ffaa00'
        });

        const task = await this.apiClient.createTask({
            title: 'Data Analysis',
            description: `Analyze: ${data}`,
            task_type: 'analysis',
            parameters: {
                data: data,
                analysis_type: 'descriptive'
            }
        });

        await this.waitForTask(task.id);
    }

    private async debug(code: string) {
        if (!code) {
            this.sendToTerminal({
                type: 'output',
                content: 'Usage: debug <code>\n',
                color: '#ff6b6b'
            });
            return;
        }

        this.sendToTerminal({
            type: 'output',
            content: 'Debugging code...\n',
            color: '#ffaa00'
        });

        const task = await this.apiClient.createTask({
            title: 'Debug Code',
            description: 'Debug the provided code',
            task_type: 'debug',
            parameters: {
                code: code
            }
        });

        await this.waitForTask(task.id);
    }

    private async explain(code: string) {
        if (!code) {
            this.sendToTerminal({
                type: 'output',
                content: 'Usage: explain <code>\n',
                color: '#ff6b6b'
            });
            return;
        }

        this.sendToTerminal({
            type: 'output',
            content: 'Explaining code...\n',
            color: '#ffaa00'
        });

        const task = await this.apiClient.createTask({
            title: 'Explain Code',
            description: 'Explain the provided code',
            task_type: 'documentation',
            parameters: {
                code: code,
                doc_type: 'explanation'
            }
        });

        await this.waitForTask(task.id);
    }

    private async listTasks() {
        this.sendToTerminal({
            type: 'output',
            content: 'Fetching tasks...\n',
            color: '#ffaa00'
        });

        const tasks = await this.apiClient.getTasks({ limit: 10 });

        if (tasks.length === 0) {
            this.sendToTerminal({
                type: 'output',
                content: 'No tasks found.\n',
                color: '#888888'
            });
            return;
        }

        let output = '\nRecent Tasks:\n';
        output += '═══════════════════════════════════════════════════════════════\n';

        for (const task of tasks) {
            const statusColor = task.status === 'completed' ? '✓' : 
                               task.status === 'failed' ? '✗' : 
                               task.status === 'running' ? '⟳' : '○';
            
            output += `${statusColor} [${task.id}] ${task.title}\n`;
            output += `  Status: ${task.status} | Progress: ${task.progress}%\n`;
            output += `  Type: ${task.task_type} | Created: ${new Date(task.created_at).toLocaleString()}\n\n`;
        }

        this.sendToTerminal({
            type: 'output',
            content: output,
            color: '#ffffff'
        });
    }

    private async viewTask(taskId: number) {
        if (!taskId) {
            this.sendToTerminal({
                type: 'output',
                content: 'Usage: task <id>\n',
                color: '#ff6b6b'
            });
            return;
        }

        const task = await this.apiClient.getTask(taskId);
        const steps = await this.apiClient.getTaskSteps(taskId);

        let output = `\nTask #${task.id}: ${task.title}\n`;
        output += '═══════════════════════════════════════════════════════════════\n';
        output += `Status: ${task.status}\n`;
        output += `Progress: ${task.progress}%\n`;
        output += `Type: ${task.task_type}\n`;
        output += `Description: ${task.description}\n`;
        output += `Created: ${new Date(task.created_at).toLocaleString()}\n\n`;

        if (steps.length > 0) {
            output += 'Steps:\n';
            for (const step of steps) {
                output += `  ${step.step_number}. ${step.agent_type} - ${step.status}\n`;
                output += `     ${step.description}\n`;
            }
            output += '\n';
        }

        if (task.result) {
            output += 'Result:\n';
            output += JSON.stringify(task.result, null, 2) + '\n';
        }

        if (task.error) {
            output += `Error: ${task.error}\n`;
        }

        this.sendToTerminal({
            type: 'output',
            content: output,
            color: '#ffffff'
        });
    }

    private async listAgents() {
        const agents = await this.apiClient.getAgents();

        let output = '\nAvailable AI Agents:\n';
        output += '═══════════════════════════════════════════════════════════════\n';

        for (const agent of agents) {
            output += `\n${agent.name} (${agent.type})\n`;
            output += `  ${agent.description}\n`;
            output += `  Capabilities: ${agent.capabilities.join(', ')}\n`;
        }

        this.sendToTerminal({
            type: 'output',
            content: output + '\n',
            color: '#ffffff'
        });
    }

    private async listFiles() {
        const files = await this.apiClient.getFiles();

        if (files.length === 0) {
            this.sendToTerminal({
                type: 'output',
                content: 'No files found.\n',
                color: '#888888'
            });
            return;
        }

        let output = '\nUploaded Files:\n';
        output += '═══════════════════════════════════════════════════════════════\n';

        for (const file of files) {
            const sizeMB = (file.size / 1024 / 1024).toFixed(2);
            output += `📄 ${file.filename}\n`;
            output += `   Size: ${sizeMB} MB | Type: ${file.content_type}\n`;
            output += `   Uploaded: ${new Date(file.uploaded_at).toLocaleString()}\n\n`;
        }

        this.sendToTerminal({
            type: 'output',
            content: output,
            color: '#ffffff'
        });
    }

    private async showStatus() {
        try {
            const health = await this.apiClient.healthCheck();
            const stats = await this.apiClient.getTaskStats();

            let output = '\nSystem Status:\n';
            output += '═══════════════════════════════════════════════════════════════\n';
            output += `API Status: ${health.status}\n`;
            output += `Version: ${health.version}\n\n`;
            output += 'Task Statistics:\n';
            output += `  Total Tasks: ${stats.total_tasks}\n`;
            output += `  Completed: ${stats.completed_tasks}\n`;
            output += `  Failed: ${stats.failed_tasks}\n`;
            output += `  Running: ${stats.running_tasks}\n`;
            output += `  Success Rate: ${stats.success_rate}%\n`;

            this.sendToTerminal({
                type: 'output',
                content: output + '\n',
                color: '#00ff00'
            });
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Failed to fetch status: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async showCurrentUser() {
        try {
            const user = await this.apiClient.getCurrentUser();

            let output = '\nCurrent User:\n';
            output += '═══════════════════════════════════════════════════════════════\n';
            output += `Name: ${user.full_name}\n`;
            output += `Email: ${user.email}\n`;
            output += `Role: ${user.role}\n`;
            output += `Level: ${user.level}\n`;
            output += `Points: ${user.points}\n`;

            this.sendToTerminal({
                type: 'output',
                content: output + '\n',
                color: '#00aaff'
            });
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Failed to fetch user info: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async waitForTask(taskId: number) {
        const maxAttempts = 60; // 2 minutes
        let attempts = 0;

        const interval = setInterval(async () => {
            try {
                const task = await this.apiClient.getTask(taskId);

                if (task.status === 'completed') {
                    clearInterval(interval);
                    this.sendToTerminal({
                        type: 'output',
                        content: `\n✓ Task completed successfully!\n`,
                        color: '#00ff00'
                    });

                    if (task.result) {
                        this.sendToTerminal({
                            type: 'output',
                            content: `\nResult:\n${JSON.stringify(task.result, null, 2)}\n`,
                            color: '#ffffff'
                        });
                    }

                    this.sendToTerminal({ type: 'ready' });
                } else if (task.status === 'failed') {
                    clearInterval(interval);
                    this.sendToTerminal({
                        type: 'output',
                        content: `\n✗ Task failed: ${task.error}\n`,
                        color: '#ff0000'
                    });
                    this.sendToTerminal({ type: 'ready' });
                } else {
                    // Show progress
                    this.sendToTerminal({
                        type: 'progress',
                        progress: task.progress
                    });
                }

                attempts++;
                if (attempts >= maxAttempts) {
                    clearInterval(interval);
                    this.sendToTerminal({
                        type: 'output',
                        content: '\nTask timeout. Use "task <id>" to check status.\n',
                        color: '#ffaa00'
                    });
                    this.sendToTerminal({ type: 'ready' });
                }
            } catch (error: any) {
                clearInterval(interval);
                this.sendToTerminal({
                    type: 'output',
                    content: `\nError checking task: ${error.message}\n`,
                    color: '#ff0000'
                });
                this.sendToTerminal({ type: 'ready' });
            }
        }, 2000);
    }

    private navigateHistory(direction: number) {
        if (this.commandHistory.length === 0) {
            return;
        }

        this.historyIndex += direction;

        if (this.historyIndex < 0) {
            this.historyIndex = 0;
        } else if (this.historyIndex >= this.commandHistory.length) {
            this.historyIndex = this.commandHistory.length;
            this.sendToTerminal({ type: 'setInput', content: '' });
            return;
        }

        const command = this.commandHistory[this.historyIndex];
        this.sendToTerminal({ type: 'setInput', content: command });
    }

    private sendToTerminal(message: any) {
        this.panel.webview.postMessage(message);
    }

    public reveal() {
        this.panel.reveal();
    }

    public dispose() {
        TerminalPanel.currentPanel = undefined;
        this.panel.dispose();

        while (this.disposables.length) {
            const disposable = this.disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }

    private getHtmlContent(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>iTechSmart AI Terminal</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background-color: #1e1e1e;
            color: #d4d4d4;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        #terminal {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            font-size: 14px;
            line-height: 1.5;
        }

        #input-container {
            display: flex;
            align-items: center;
            padding: 10px 20px;
            background-color: #252526;
            border-top: 1px solid #3e3e42;
        }

        #prompt {
            color: #00aaff;
            margin-right: 10px;
            font-weight: bold;
        }

        #input {
            flex: 1;
            background: transparent;
            border: none;
            color: #d4d4d4;
            font-family: inherit;
            font-size: 14px;
            outline: none;
        }

        .output-line {
            margin: 2px 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #3e3e42;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00aaff, #00ff88);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }

        ::-webkit-scrollbar {
            width: 10px;
        }

        ::-webkit-scrollbar-track {
            background: #1e1e1e;
        }

        ::-webkit-scrollbar-thumb {
            background: #3e3e42;
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #4e4e52;
        }
    </style>
</head>
<body>
    <div id="terminal"></div>
    <div id="input-container">
        <span id="prompt">$</span>
        <input type="text" id="input" autofocus />
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        const terminal = document.getElementById('terminal');
        const input = document.getElementById('input');
        let progressBar = null;

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const command = input.value.trim();
                if (command) {
                    vscode.postMessage({ type: 'command', command });
                    input.value = '';
                    input.disabled = true;
                }
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                vscode.postMessage({ type: 'history-up' });
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                vscode.postMessage({ type: 'history-down' });
            } else if (e.key === 'l' && e.ctrlKey) {
                e.preventDefault();
                vscode.postMessage({ type: 'clear' });
            }
        });

        window.addEventListener('message', (event) => {
            const message = event.data;

            switch (message.type) {
                case 'output':
                    const line = document.createElement('div');
                    line.className = 'output-line';
                    line.textContent = message.content;
                    if (message.color) {
                        line.style.color = message.color;
                    }
                    terminal.appendChild(line);
                    terminal.scrollTop = terminal.scrollHeight;
                    break;

                case 'clear':
                    terminal.innerHTML = '';
                    progressBar = null;
                    break;

                case 'ready':
                    input.disabled = false;
                    input.focus();
                    if (progressBar) {
                        progressBar.remove();
                        progressBar = null;
                    }
                    break;

                case 'progress':
                    if (!progressBar) {
                        progressBar = document.createElement('div');
                        progressBar.className = 'progress-bar';
                        progressBar.innerHTML = '<div class="progress-fill"></div>';
                        terminal.appendChild(progressBar);
                    }
                    const fill = progressBar.querySelector('.progress-fill');
                    fill.style.width = message.progress + '%';
                    fill.textContent = message.progress + '%';
                    terminal.scrollTop = terminal.scrollHeight;
                    break;

                case 'setInput':
                    input.value = message.content;
                    break;
            }
        });

        // Focus input on load
        input.focus();
    </script>
</body>
</html>`;
    }
}
    // ==================== MODEL MANAGEMENT METHODS ====================

    private async listModels() {
        try {
            const response = await this.client.get('/models/all');
            
            if (!response.success) {
                this.sendToTerminal({
                    type: 'output',
                    content: 'Failed to fetch models\n',
                    color: '#ff6b6b'
                });
                return;
            }

            let output = '\n🤖 Available AI Models:\n';
            output += '═'.repeat(80) + '\n\n';

            // Group by provider
            const modelsByProvider: { [key: string]: any[] } = {};
            response.models.forEach((model: any) => {
                if (!modelsByProvider[model.provider]) {
                    modelsByProvider[model.provider] = [];
                }
                modelsByProvider[model.provider].push(model);
            });

            for (const [provider, models] of Object.entries(modelsByProvider)) {
                output += `\n📦 ${provider.toUpperCase()} (${models.length} models)\n`;
                output += '─'.repeat(80) + '\n';

                models.forEach((model: any) => {
                    const costText = model.cost_per_1k_input === 0 
                        ? 'FREE' 
                        : `$${model.cost_per_1k_input.toFixed(4)}/1K`;
                    
                    output += `  • ${model.name} [${model.tier}] - ${costText}\n`;
                    output += `    ${model.description}\n`;
                    output += `    Context: ${model.context_window.toLocaleString()} | Output: ${model.max_output.toLocaleString()}\n`;
                });
            }

            output += '\n' + '═'.repeat(80) + '\n';
            output += `Total: ${response.total_models} models\n\n`;

            this.sendToTerminal({
                type: 'output',
                content: output,
                color: '#4ecdc4'
            });

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async showCurrentModel() {
        const config = vscode.workspace.getConfiguration('ninja');
        const currentModel = config.get('selectedModel', 'gpt-4o-mini');

        try {
            const response = await this.client.get(`/models/${currentModel}`);
            
            if (!response.success) {
                this.sendToTerminal({
                    type: 'output',
                    content: `Current model: ${currentModel} (not found)\n`,
                    color: '#ff6b6b'
                });
                return;
            }

            const model = response.model;
            let output = '\n📌 Current Model:\n';
            output += '═'.repeat(80) + '\n';
            output += `Name: ${model.name}\n`;
            output += `Provider: ${model.provider}\n`;
            output += `Tier: ${model.tier}\n`;
            output += `Description: ${model.description}\n`;
            output += `Context Window: ${model.context_window.toLocaleString()} tokens\n`;
            output += `Max Output: ${model.max_output.toLocaleString()} tokens\n`;
            output += `Cost: $${model.cost_per_1k_input.toFixed(4)}/1K input, $${model.cost_per_1k_output.toFixed(4)}/1K output\n`;
            output += `Capabilities: `;
            if (model.supports_vision) output += '👁️ Vision ';
            if (model.supports_function_calling) output += '🔧 Functions ';
            if (model.supports_streaming) output += '⚡ Streaming';
            output += '\n';
            output += '═'.repeat(80) + '\n\n';

            this.sendToTerminal({
                type: 'output',
                content: output,
                color: '#4ecdc4'
            });

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async selectModel(modelName: string) {
        try {
            // Search for model by name
            const response = await this.client.get(`/models/search?query=${encodeURIComponent(modelName)}`);
            
            if (!response.success || response.results.length === 0) {
                this.sendToTerminal({
                    type: 'output',
                    content: `Model not found: ${modelName}\nUse 'models' to see available models.\n`,
                    color: '#ff6b6b'
                });
                return;
            }

            const model = response.results[0];
            
            // Update configuration
            await vscode.workspace.getConfiguration('ninja').update(
                'selectedModel',
                model.id,
                vscode.ConfigurationTarget.Workspace
            );

            this.sendToTerminal({
                type: 'output',
                content: `✅ Selected model: ${model.name} (${model.provider})\n`,
                color: '#4ecdc4'
            });

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async compareModels(modelNames: string[]) {
        try {
            // Search for each model
            const modelIds: string[] = [];
            
            for (const name of modelNames) {
                const response = await this.client.get(`/models/search?query=${encodeURIComponent(name)}`);
                if (response.success && response.results.length > 0) {
                    modelIds.push(response.results[0].id);
                }
            }

            if (modelIds.length < 2) {
                this.sendToTerminal({
                    type: 'output',
                    content: 'Need at least 2 valid models to compare\n',
                    color: '#ff6b6b'
                });
                return;
            }

            const comparison = await this.client.post('/models/compare', {
                model_ids: modelIds,
                criteria: ['cost', 'context_window', 'speed']
            });

            if (!comparison.success) {
                this.sendToTerminal({
                    type: 'output',
                    content: 'Failed to compare models\n',
                    color: '#ff6b6b'
                });
                return;
            }

            let output = '\n📊 Model Comparison:\n';
            output += '═'.repeat(80) + '\n\n';

            for (const [modelId, data] of Object.entries(comparison.comparison)) {
                const model = data as any;
                output += `${model.name} (${model.provider})\n`;
                output += `  Tier: ${model.tier}\n`;
                output += `  Cost: $${model.cost_per_1k_input.toFixed(4)} in / $${model.cost_per_1k_output.toFixed(4)} out\n`;
                output += `  Context: ${model.context_window.toLocaleString()} | Output: ${model.max_output.toLocaleString()}\n`;
                output += `  Vision: ${model.supports_vision ? '✓' : '✗'} | Functions: ${model.supports_function_calling ? '✓' : '✗'}\n\n`;
            }

            output += '═'.repeat(80) + '\n\n';

            this.sendToTerminal({
                type: 'output',
                content: output,
                color: '#4ecdc4'
            });

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async getModelRecommendations(query: string) {
        try {
            // Parse query for task type and budget
            let taskType = 'general';
            let budget = 'medium';

            const lowerQuery = query.toLowerCase();
            
            if (lowerQuery.includes('cod')) taskType = 'coding';
            else if (lowerQuery.includes('research')) taskType = 'research';
            else if (lowerQuery.includes('creat') || lowerQuery.includes('writ')) taskType = 'creative';
            else if (lowerQuery.includes('fast') || lowerQuery.includes('quick')) taskType = 'fast';

            if (lowerQuery.includes('cheap') || lowerQuery.includes('low')) budget = 'low';
            else if (lowerQuery.includes('expensive') || lowerQuery.includes('high') || lowerQuery.includes('best')) budget = 'high';

            const response = await this.client.get(
                `/models/recommendations?task_type=${taskType}&budget=${budget}`
            );

            if (!response.success) {
                this.sendToTerminal({
                    type: 'output',
                    content: 'Failed to get recommendations\n',
                    color: '#ff6b6b'
                });
                return;
            }

            let output = `\n⭐ Recommended Models for ${taskType} (${budget} budget):\n`;
            output += '═'.repeat(80) + '\n\n';

            response.recommendations.forEach((model: any, index: number) => {
                output += `${index + 1}. ${model.name} (${model.provider})\n`;
                output += `   ${model.description}\n`;
                output += `   Cost: $${model.cost_per_1k_input.toFixed(4)}/1K | Context: ${model.context_window.toLocaleString()}\n\n`;
            });

            output += '═'.repeat(80) + '\n';
            output += `Use 'model <name>' to select a model\n\n`;

            this.sendToTerminal({
                type: 'output',
                content: output,
                color: '#4ecdc4'
            });

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async checkProviders() {
        try {
            const response = await this.client.get('/models/providers/status');
            
            if (!response.success) {
                this.sendToTerminal({
                    type: 'output',
                    content: 'Failed to check providers\n',
                    color: '#ff6b6b'
                });
                return;
            }

            let output = '\n🔌 AI Provider Status:\n';
            output += '═'.repeat(80) + '\n\n';

            for (const [provider, status] of Object.entries(response.providers)) {
                const s = status as any;
                const statusIcon = s.available ? '✅' : '❌';
                const statusText = s.available ? 'Available' : 'Not Configured';
                
                output += `${statusIcon} ${provider.toUpperCase()}: ${statusText}\n`;
                output += `   Models: ${s.total_models}\n`;
                if (s.available && s.models.length > 0) {
                    output += `   Available: ${s.models.slice(0, 3).join(', ')}${s.models.length > 3 ? '...' : ''}\n`;
                }
                output += '\n';
            }

            output += '═'.repeat(80) + '\n\n';

            this.sendToTerminal({
                type: 'output',
                content: output,
                color: '#4ecdc4'
            });

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async showModelUsage() {
        try {
            const response = await this.client.get('/models/usage/stats');
            
            if (!response.success) {
                this.sendToTerminal({
                    type: 'output',
                    content: 'Failed to fetch usage stats\n',
                    color: '#ff6b6b'
                });
                return;
            }

            let output = '\n📈 Model Usage Statistics:\n';
            output += '═'.repeat(80) + '\n\n';

            if (Object.keys(response.stats).length === 0) {
                output += 'No usage data yet. Start using models to see statistics!\n\n';
            } else {
                for (const [modelId, stats] of Object.entries(response.stats)) {
                    const s = stats as any;
                    output += `${modelId}:\n`;
                    output += `  Requests: ${s.total_requests}\n`;
                    output += `  Tokens: ${s.total_tokens.toLocaleString()}\n`;
                    output += `  Cost: $${s.total_cost.toFixed(4)}\n\n`;
                }
            }

            output += '═'.repeat(80) + '\n\n';

            this.sendToTerminal({
                type: 'output',
                content: output,
                color: '#4ecdc4'
            });

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }
}

    // ==================== RESEARCH METHODS ====================

    private async performResearch(query: string) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: `\n🔍 Performing deep research on: "${query}"\n`,
                color: '#4ecdc4'
            });

            this.sendToTerminal({
                type: 'output',
                content: 'Gathering sources and analyzing credibility...\n\n',
                color: '#96ceb4'
            });

            const response = await this.client.post('/research/deep-research', {
                query: query,
                num_sources: 10,
                citation_style: 'apa',
                verify_facts: true,
                min_credibility: 50.0
            });

            if (!response.success) {
                this.sendToTerminal({
                    type: 'output',
                    content: 'Research failed\n',
                    color: '#ff6b6b'
                });
                return;
            }

            const results = response.results;
            let output = '\n📊 Research Results:\n';
            output += '═'.repeat(80) + '\n\n';

            // Summary
            output += `Query: ${results.query}\n`;
            output += `Sources: ${results.total_sources}\n`;
            output += `Average Credibility: ${results.average_credibility.toFixed(1)}/100\n`;
            output += `Citation Style: ${results.citation_style.toUpperCase()}\n\n`;

            // Top sources
            output += '📚 Top Sources:\n';
            output += '─'.repeat(80) + '\n';

            results.sources.slice(0, 5).forEach((source: any, index: number) => {
                output += `\n${index + 1}. ${source.title}\n`;
                output += `   URL: ${source.url}\n`;
                output += `   Credibility: ${source.credibility_score.toFixed(1)}/100 (${source.credibility_level})\n`;
                output += `   Type: ${source.source_type}\n`;
            });

            output += '\n' + '═'.repeat(80) + '\n';
            output += `\nUse 'save-research' to save the full report\n\n`;

            this.sendToTerminal({
                type: 'output',
                content: output,
                color: '#4ecdc4'
            });

            // Store results for saving
            (this as any).lastResearchResults = results;

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async formatCitation(args: string[]) {
        try {
            if (args.length < 2) {
                this.sendToTerminal({
                    type: 'output',
                    content: 'Usage: cite <url> <title> [author] [style]\n',
                    color: '#ff6b6b'
                });
                return;
            }

            const url = args[0];
            const title = args.slice(1).join(' ');
            const style = args[args.length - 1].toLowerCase();
            const validStyles = ['apa', 'mla', 'chicago', 'harvard', 'ieee'];
            const citationStyle = validStyles.includes(style) ? style : 'apa';

            const response = await this.client.post('/research/format-citation', {
                url: url,
                title: title,
                citation_style: citationStyle
            });

            if (response.success) {
                let output = '\n📖 Citation:\n';
                output += '═'.repeat(80) + '\n\n';
                output += `${response.citation}\n\n`;
                output += '═'.repeat(80) + '\n';
                output += `Style: ${citationStyle.toUpperCase()}\n\n`;

                this.sendToTerminal({
                    type: 'output',
                    content: output,
                    color: '#4ecdc4'
                });
            }

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async checkSourceCredibility(url: string) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: `\n🔍 Checking credibility of: ${url}\n\n`,
                color: '#4ecdc4'
            });

            const response = await this.client.post('/research/check-credibility', {
                url: url,
                title: 'Source',
                content: ''
            });

            if (response.success) {
                const score = response.credibility_score;
                const level = response.credibility_level.replace('_', ' ').toUpperCase();
                
                let output = '\n📊 Credibility Report:\n';
                output += '═'.repeat(80) + '\n\n';
                output += `Score: ${score.toFixed(1)}/100\n`;
                output += `Level: ${level}\n`;
                output += `Type: ${response.source_type}\n`;
                output += `Domain: ${response.domain}\n\n`;

                output += 'Analysis:\n';
                output += `  Has Author: ${response.analysis.has_author ? '✓' : '✗'}\n`;
                output += `  Has Publication Date: ${response.analysis.has_publication_date ? '✓' : '✗'}\n`;
                output += `  Has Publisher: ${response.analysis.has_publisher ? '✓' : '✗'}\n`;
                output += `  Domain Reputation: ${response.analysis.domain_reputation}\n\n`;

                output += '═'.repeat(80) + '\n\n';

                this.sendToTerminal({
                    type: 'output',
                    content: output,
                    color: '#4ecdc4'
                });
            }

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async listCitationStyles() {
        try {
            const response = await this.client.get('/research/citation-styles');

            if (response.success) {
                let output = '\n📖 Available Citation Styles:\n';
                output += '═'.repeat(80) + '\n\n';

                response.styles.forEach((style: any) => {
                    output += `${style.name}\n`;
                    output += `  ID: ${style.id}\n`;
                    output += `  ${style.description}\n\n`;
                });

                output += '═'.repeat(80) + '\n';
                output += 'Use: cite <url> <title> <style>\n\n';

                this.sendToTerminal({
                    type: 'output',
                    content: output,
                    color: '#4ecdc4'
                });
            }

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }
}

    // ============================================================================
    // EDITOR COMMANDS
    // ============================================================================

    private async openEditor(args: string[]) {
        try {
            if (args.length === 0) {
                this.sendToTerminal({
                    type: 'output',
                    content: 'Usage: edit <file_path>\n',
                    color: '#ffa500'
                });
                return;
            }

            const filePath = args.join(' ');
            
            this.sendToTerminal({
                type: 'output',
                content: `\n📝 Opening file in Monaco editor: ${filePath}\n\n`,
                color: '#4ecdc4'
            });

            // Trigger VS Code command
            vscode.commands.executeCommand('itechsmart.openFileInMonaco', vscode.Uri.file(filePath));

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async openMonacoEditor(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📝 Opening Monaco code editor...\n\n',
                color: '#4ecdc4'
            });

            // Trigger VS Code command
            vscode.commands.executeCommand('itechsmart.openMonacoEditor');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async openImageEditor(args: string[]) {
        try {
            if (args.length === 0) {
                this.sendToTerminal({
                    type: 'output',
                    content: '\n🎨 Opening image editor...\n\n',
                    color: '#4ecdc4'
                });
                vscode.commands.executeCommand('itechsmart.openImageEditor');
            } else {
                const imagePath = args.join(' ');
                this.sendToTerminal({
                    type: 'output',
                    content: `\n🎨 Opening image editor for: ${imagePath}\n\n`,
                    color: '#4ecdc4'
                });
                vscode.commands.executeCommand('itechsmart.editImage', vscode.Uri.file(imagePath));
            }

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async openWebsiteBuilder(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🌐 Opening website builder...\n\n',
                color: '#4ecdc4'
            });

            // Trigger VS Code command
            vscode.commands.executeCommand('itechsmart.openWebsiteBuilder');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async openMarkdownEditor(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📄 Opening markdown editor...\n\n',
                color: '#4ecdc4'
            });

            // Trigger VS Code command
            vscode.commands.executeCommand('itechsmart.openMarkdownEditor');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async openJSONEditor(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📋 Opening JSON editor...\n\n',
                color: '#4ecdc4'
            });

            // Trigger VS Code command
            vscode.commands.executeCommand('itechsmart.openJSONEditor');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async openYAMLEditor(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📋 Opening YAML editor...\n\n',
                color: '#4ecdc4'
            });

            // Trigger VS Code command
            vscode.commands.executeCommand('itechsmart.openYAMLEditor');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async listEditors() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📝 Active Editors:\n',
                color: '#4ecdc4'
            });

            const response = await this.client.get('/editors/list');

            if (response.total === 0) {
                this.sendToTerminal({
                    type: 'output',
                    content: '\nNo active editors\n\n',
                    color: '#888888'
                });
                return;
            }

            let output = '\n';
            output += '═'.repeat(80) + '\n\n';

            for (const editor of response.editors) {
                output += `📝 ${editor.editor_type.toUpperCase()}\n`;
                output += `   ID: ${editor.editor_id}\n`;
                output += `   File: ${editor.file_path || 'N/A'}\n`;
                output += `   Created: ${new Date(editor.created_at).toLocaleString()}\n`;
                output += `   Modified: ${editor.is_modified ? 'Yes' : 'No'}\n\n`;
            }

            output += '═'.repeat(80) + '\n';
            output += `Total: ${response.total} editor(s)\n\n`;

            this.sendToTerminal({
                type: 'output',
                content: output,
                color: '#4ecdc4'
            });

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }
}

    // ============================================================================
    // GITHUB COMMANDS
    // ============================================================================

    private async listGitHubRepos() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📦 GitHub Repositories:\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.listRepositories');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async listGitHubPRs(args: string[]) {
        try {
            if (args.length === 0) {
                this.sendToTerminal({
                    type: 'output',
                    content: 'Usage: gh-prs <owner/repo>\n',
                    color: '#ffa500'
                });
                return;
            }

            this.sendToTerminal({
                type: 'output',
                content: `\n🔀 Pull Requests for ${args[0]}:\n\n`,
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.listPullRequests');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async listGitHubIssues(args: string[]) {
        try {
            if (args.length === 0) {
                this.sendToTerminal({
                    type: 'output',
                    content: 'Usage: gh-issues <owner/repo>\n',
                    color: '#ffa500'
                });
                return;
            }

            this.sendToTerminal({
                type: 'output',
                content: `\n🐛 Issues for ${args[0]}:\n\n`,
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.listIssues');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async createGitHubPR(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔀 Creating pull request...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.createPullRequest');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async createGitHubIssue(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🐛 Creating issue...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.createIssue');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async generateImage(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🎨 Generating image...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.generateImage');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async transformImage(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔄 Transforming image...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.imageToImage');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async upscaleImage(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n⬆️ Upscaling image...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.upscaleImage');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async removeBackground(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n✂️ Removing background...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.removeBackground');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async listImageProviders() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📋 Listing image providers...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.listImageProviders');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async createChart(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📊 Creating chart...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.createChart');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async createDashboard(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📈 Creating dashboard...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.createDashboard');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async listCharts() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📋 Listing charts...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.listCharts');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async exportChart(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n💾 Exporting chart...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.exportChart');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async analyzeDataFile(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔍 Analyzing data...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.analyzeData');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }
}

    private async showDocumentHelp() {
        const helpText = `
Document Processing Commands:
════════════════════════════════════════════════════════════════

  doc-upload              Upload document for processing
  upload-document         (alias for doc-upload)
  
  doc-list                List all uploaded documents
  list-documents          (alias for doc-list)
  
  doc-extract             Extract text from document
  extract-text            (alias for doc-extract)
  
  doc-tables              Extract tables from document
  extract-tables          (alias for doc-tables)
  
  doc-ocr                 Perform OCR on document
  ocr-document            (alias for doc-ocr)
  
  doc-search              Search within document
  search-document         (alias for doc-search)

Examples:
  doc-upload              Upload a document
  doc-list                List all documents
  doc-extract             Extract text from document
  doc-tables              Extract tables from document

`;
        this.sendToTerminal({
            type: 'output',
            content: helpText,
            color: '#ffffff'
        });
    }

    private async uploadDocument(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📄 Uploading document...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.uploadDocument');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async listDocuments() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📋 Listing documents...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.listDocuments');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async extractDocumentText(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📝 Extracting text...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.extractText');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async extractDocumentTables(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📊 Extracting tables...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.extractTables');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async ocrDocument(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔍 Performing OCR...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.ocrDocument');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async searchDocument(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔎 Searching document...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.searchDocuments');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }
}

    // MCP Commands
    private async showMCPHelp() {
        const helpText = `
MCP Data Source Commands:
══════════════════════════════════════════════════════════════

  mcp-register <name> <type>    Register a new data source
  mcp-list                      List all data sources
  mcp-query <id> <query>        Query a data source
  mcp-test <id>                 Test connection to a source
  mcp-schema <id>               View data source schema

Supported Types:
  postgresql, mysql, mongodb, redis, rest_api, elasticsearch

Examples:
  mcp-register "Production DB" postgresql
  mcp-list
  mcp-query 1 "SELECT * FROM users LIMIT 10"
  mcp-test 1
  mcp-schema 1

`;
        this.sendToTerminal({
            type: 'output',
            content: helpText,
            color: '#4ecdc4'
        });
    }

    private async registerMCPSource(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔌 Registering MCP data source...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.registerMCPSource');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async listMCPSources() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📊 Listing MCP data sources...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.listMCPSources');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async queryMCPSource(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔍 Querying MCP data source...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.queryMCPSource');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async testMCPSource(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔧 Testing MCP connection...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.testMCPConnection');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async viewMCPSchema(args: string[]) {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📋 Loading MCP schema...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.viewMCPSchema');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }
}

    // History Commands
    private async showHistoryHelp() {
        const helpText = `
Action History Commands:
══════════════════════════════════════════════════════════════

  undo                          Undo last action
  redo                          Redo last undone action
  history-view                  View action history
  view-history                  (alias for history-view)
  history-search <query>        Search action history
  search-history                (alias for history-search)
  history-stats                 View history statistics
  stats                         (alias for history-stats)

Keyboard Shortcuts:
  Ctrl+Alt+Z                    Undo last action
  Ctrl+Alt+Y                    Redo last action

Examples:
  undo
  redo
  history-view
  history-search "file modification"
  history-stats

`;
        this.sendToTerminal({
            type: 'output',
            content: helpText,
            color: '#4ecdc4'
        });
    }

    private async undoAction() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n⏪ Undoing action...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.undoLastAction');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async redoAction() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n⏩ Redoing action...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.redoLastAction');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async viewHistory() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📜 Loading action history...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.viewActionHistory');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async searchHistory() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔍 Searching history...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.searchHistory');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async viewHistoryStats() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📊 Loading statistics...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.viewStatistics');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }
}

    // Video Commands
    private async showVideoHelp() {
        const helpText = `
Video Generation Commands:
══════════════════════════════════════════════════════════════

  video-generate                Generate video from text
  generate-video                (alias for video-generate)
  video-transform               Transform existing video
  transform-video               (alias for video-transform)
  video-upscale                 Upscale video resolution
  upscale-video                 (alias for video-upscale)
  video-edit                    Edit video (trim, merge, effects)
  edit-video                    (alias for video-edit)
  video-list                    List video generations
  list-videos                   (alias for video-list)

Examples:
  video-generate
  video-transform
  video-upscale
  video-list

`;
        this.sendToTerminal({
            type: 'output',
            content: helpText,
            color: '#4ecdc4'
        });
    }

    private async generateVideo() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🎬 Generating video...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.generateVideoFromText');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async transformVideo() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🎨 Transforming video...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.transformVideo');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async upscaleVideo() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📈 Upscaling video...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.upscaleVideo');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async editVideo() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n✂️ Editing video...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.editVideo');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async listVideos() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📹 Loading video generations...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.viewVideoGenerations');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }

    private showDebugHelp() {
        const helpText = `
Debug Commands:
══════════════════════════════════════════════════════════════

  debug-analyze                 Analyze error with AI
  analyze-error                 (alias for debug-analyze)
  debug-breakpoint              Set smart breakpoint
  set-breakpoint                (alias for debug-breakpoint)
  debug-list                    List all breakpoints
  list-breakpoints              (alias for debug-list)
  debug-inspect                 Inspect variable
  inspect-variable              (alias for debug-inspect)
  debug-profile                 Profile current code
  profile-code                  (alias for debug-profile)
  debug-leaks                   Detect memory leaks
  detect-leaks                  (alias for debug-leaks)
  debug-stack                   View call stack
  view-stack                    (alias for debug-stack)
  debug-coverage                Get code coverage
  get-coverage                  (alias for debug-coverage)

Examples:
  debug-analyze
  debug-breakpoint
  debug-profile
  debug-leaks

`;
        this.sendToTerminal({
            type: 'output',
            content: helpText,
            color: '#4ecdc4'
        });
    }

    private async analyzeError() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔍 Analyzing error...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.analyzeError');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async setBreakpoint() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔴 Setting breakpoint...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.setSmartBreakpoint');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async listBreakpoints() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📋 Listing breakpoints...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.listBreakpoints');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async inspectVariable() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔬 Inspecting variable...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.inspectVariable');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async profileCode() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n⚡ Profiling code...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.profileCode');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async detectMemoryLeaks() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n💧 Detecting memory leaks...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.detectMemoryLeaks');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async viewCallStack() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📚 Viewing call stack...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.viewCallStack');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async getCodeCoverage() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📊 Getting code coverage...\n\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.getCodeCoverage');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }


    private showWorkflowHelp() {
        const helpText = `
Workflow Commands:
══════════════════════════════════════════════════════════════

  workflow-create               Create new workflow
  create-workflow               (alias for workflow-create)
  workflow-edit                 Edit existing workflow
  edit-workflow                 (alias for workflow-edit)
  workflow-execute              Execute workflow
  execute-workflow              (alias for workflow-execute)
  workflow-list                 List all workflows
  list-workflows                (alias for workflow-list)
  workflow-history              View workflow history
  view-history                  (alias for workflow-history)
  workflow-templates            Browse templates
  browse-templates              (alias for workflow-templates)
  workflow-delete               Delete workflow
  delete-workflow               (alias for workflow-delete)
  workflow-share                Share workflow
  share-workflow                (alias for workflow-share)

Examples:
  workflow-create
  workflow-execute
  workflow-list
  workflow-templates

`;
        this.sendToTerminal({
            type: 'output',
            content: helpText,
            color: '#4ecdc4'
        });
    }

    private async createWorkflow() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔧 Creating workflow...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.createWorkflow');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async editWorkflow() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n✏️ Editing workflow...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.editWorkflow');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async executeWorkflow() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n▶️ Executing workflow...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.executeWorkflow');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async listWorkflows() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📋 Listing workflows...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.listWorkflows');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async viewWorkflowHistory() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📊 Viewing workflow history...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.viewWorkflowHistory');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async browseWorkflowTemplates() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🎨 Browsing templates...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.browseTemplates');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async deleteWorkflow() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🗑️ Deleting workflow...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.deleteWorkflow');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async shareWorkflow() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🤝 Sharing workflow...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.shareWorkflow');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }


    private showCollabHelp() {
        const helpText = `
Collaboration Commands:
══════════════════════════════════════════════════════════════

  team-create                   Create new team
  create-team                   (alias for team-create)
  team-invite                   Invite team member
  invite-member                 (alias for team-invite)
  team-list                     List all teams
  list-teams                    (alias for team-list)
  workspace-create              Create workspace
  create-workspace              (alias for workspace-create)
  workspace-switch              Switch workspace
  switch-workspace              (alias for workspace-switch)
  comment-add                   Add comment
  add-comment                   (alias for comment-add)
  team-activity                 View team activity
  view-activity                 (alias for team-activity)
  team-permissions              Manage permissions
  manage-permissions            (alias for team-permissions)

Examples:
  team-create
  team-invite
  workspace-create
  team-activity

`;
        this.sendToTerminal({
            type: 'output',
            content: helpText,
            color: '#4ecdc4'
        });
    }

    private async createTeam() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n👥 Creating team...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.createTeam');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async inviteTeamMember() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n✉️ Inviting team member...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.inviteTeamMember');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async listTeamsCmd() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📋 Listing teams...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.listTeams');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async createWorkspaceCmd() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🏢 Creating workspace...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.createWorkspace');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async switchWorkspaceCmd() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔄 Switching workspace...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.switchWorkspace');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async addCommentCmd() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n💬 Adding comment...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.addComment');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async viewTeamActivityCmd() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n📊 Viewing team activity...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.viewTeamActivity');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    private async managePermissionsCmd() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\n🔐 Managing permissions...\n\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.managePermissions');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\n`,
                color: '#ff0000'
            });
        }
    }

    }
}
