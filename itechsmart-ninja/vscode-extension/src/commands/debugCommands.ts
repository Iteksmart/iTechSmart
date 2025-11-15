/**
 * Debug Commands - VS Code commands for advanced debugging
 */

import * as vscode from 'vscode';
import { APIClient } from '../api/client';

export function registerDebugCommands(context: vscode.ExtensionContext, apiClient: APIClient) {
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.analyzeError', () => analyzeError(apiClient)),
        vscode.commands.registerCommand('itechsmart.setSmartBreakpoint', () => setSmartBreakpoint(apiClient)),
        vscode.commands.registerCommand('itechsmart.listBreakpoints', () => listBreakpoints(apiClient)),
        vscode.commands.registerCommand('itechsmart.inspectVariable', () => inspectVariable(apiClient)),
        vscode.commands.registerCommand('itechsmart.profileCode', () => profileCode(apiClient)),
        vscode.commands.registerCommand('itechsmart.detectMemoryLeaks', () => detectMemoryLeaks(apiClient)),
        vscode.commands.registerCommand('itechsmart.viewCallStack', () => viewCallStack(apiClient)),
        vscode.commands.registerCommand('itechsmart.getCodeCoverage', () => getCodeCoverage(apiClient))
    );
}

async function analyzeError(apiClient: APIClient) {
    try {
        // Get error message from user
        const errorMessage = await vscode.window.showInputBox({
            prompt: 'Enter error message',
            placeHolder: 'TypeError: cannot read property...'
        });

        if (!errorMessage) {
            return;
        }

        // Get stack trace (optional)
        const includeStackTrace = await vscode.window.showQuickPick(['Yes', 'No'], {
            placeHolder: 'Include stack trace?'
        });

        let stackTrace: string | undefined;
        if (includeStackTrace === 'Yes') {
            stackTrace = await vscode.window.showInputBox({
                prompt: 'Paste stack trace',
                placeHolder: 'File "main.py", line 10...'
            });
        }

        // Get code context (optional)
        const editor = vscode.window.activeTextEditor;
        let code: string | undefined;
        if (editor) {
            const useCurrentFile = await vscode.window.showQuickPick(['Yes', 'No'], {
                placeHolder: 'Analyze current file?'
            });
            if (useCurrentFile === 'Yes') {
                code = editor.document.getText();
            }
        }

        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Analyzing error...',
            cancellable: false
        }, async () => {
            const response = await apiClient.post('/api/debug/analyze-error', {
                error_message: errorMessage,
                stack_trace: stackTrace,
                code: code,
                language: editor?.document.languageId || 'python'
            });

            if (response.success) {
                const analysis = response.analysis;
                
                // Show results in webview
                const panel = vscode.window.createWebviewPanel(
                    'errorAnalysis',
                    'Error Analysis',
                    vscode.ViewColumn.Two,
                    { enableScripts: true }
                );

                panel.webview.html = getErrorAnalysisHTML(analysis);
                
                // Also show quick summary
                vscode.window.showInformationMessage(
                    `Error Type: ${analysis.error_type} | Severity: ${analysis.severity}`
                );
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error analysis failed: ${error.message}`);
    }
}

async function setSmartBreakpoint(apiClient: APIClient) {
    try {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const filePath = editor.document.uri.fsPath;
        const lineNumber = editor.selection.active.line + 1;

        // Ask for condition (optional)
        const addCondition = await vscode.window.showQuickPick(['Yes', 'No'], {
            placeHolder: 'Add breakpoint condition?'
        });

        let condition: string | undefined;
        if (addCondition === 'Yes') {
            condition = await vscode.window.showInputBox({
                prompt: 'Enter breakpoint condition',
                placeHolder: 'x > 10'
            });
        }

        const response = await apiClient.post('/api/debug/set-breakpoint', {
            file_path: filePath,
            line_number: lineNumber,
            condition: condition
        });

        if (response.success) {
            vscode.window.showInformationMessage(
                `Breakpoint set at ${filePath}:${lineNumber}`
            );
            
            // Add decoration to show breakpoint
            const decoration = vscode.window.createTextEditorDecorationType({
                gutterIconPath: vscode.Uri.parse('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iOCIgY3k9IjgiIHI9IjYiIGZpbGw9IiNGRjAwMDAiLz4KPC9zdmc+'),
                gutterIconSize: 'contain'
            });
            
            const range = new vscode.Range(lineNumber - 1, 0, lineNumber - 1, 0);
            editor.setDecorations(decoration, [range]);
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to set breakpoint: ${error.message}`);
    }
}

async function listBreakpoints(apiClient: APIClient) {
    try {
        const response = await apiClient.get('/api/debug/breakpoints');

        if (response.success && response.breakpoints.length > 0) {
            const items = response.breakpoints.map((bp: any) => ({
                label: `${bp.file_path}:${bp.line_number}`,
                description: bp.condition || 'No condition',
                detail: `${bp.enabled ? '✓' : '✗'} Hit count: ${bp.hit_count}`,
                breakpoint: bp
            }));

            const selected = await vscode.window.showQuickPick(items, {
                placeHolder: 'Select breakpoint to manage'
            });

            if (selected) {
                const action = await vscode.window.showQuickPick(
                    ['Go to', 'Toggle', 'Remove'],
                    { placeHolder: 'Choose action' }
                );

                if (action === 'Go to') {
                    const doc = await vscode.workspace.openTextDocument(selected.breakpoint.file_path);
                    const editor = await vscode.window.showTextDocument(doc);
                    const position = new vscode.Position(selected.breakpoint.line_number - 1, 0);
                    editor.selection = new vscode.Selection(position, position);
                    editor.revealRange(new vscode.Range(position, position));
                } else if (action === 'Toggle') {
                    await apiClient.post(`/api/debug/breakpoints/${selected.breakpoint.id}/toggle`, {});
                    vscode.window.showInformationMessage('Breakpoint toggled');
                } else if (action === 'Remove') {
                    await apiClient.delete(`/api/debug/breakpoints/${selected.breakpoint.id}`);
                    vscode.window.showInformationMessage('Breakpoint removed');
                }
            }
        } else {
            vscode.window.showInformationMessage('No breakpoints set');
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list breakpoints: ${error.message}`);
    }
}

async function inspectVariable(apiClient: APIClient) {
    try {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        // Get variable name from selection or input
        let variableName = editor.document.getText(editor.selection);
        
        if (!variableName) {
            variableName = await vscode.window.showInputBox({
                prompt: 'Enter variable name to inspect',
                placeHolder: 'myVariable'
            }) || '';
        }

        if (!variableName) {
            return;
        }

        // For demo, use empty context - in real implementation, 
        // this would come from debugger state
        const response = await apiClient.post('/api/debug/inspect-variable', {
            variable_name: variableName,
            context: {}
        });

        if (response.success) {
            const variable = response.variable;
            
            const panel = vscode.window.createWebviewPanel(
                'variableInspection',
                `Variable: ${variableName}`,
                vscode.ViewColumn.Two,
                { enableScripts: true }
            );

            panel.webview.html = getVariableInspectionHTML(variable);
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Variable inspection failed: ${error.message}`);
    }
}

async function profileCode(apiClient: APIClient) {
    try {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const code = editor.document.getText();
        const language = editor.document.languageId;

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Profiling code...',
            cancellable: false
        }, async () => {
            const response = await apiClient.post('/api/debug/profile', {
                code: code,
                language: language
            });

            if (response.success) {
                const profile = response.profile;
                
                const panel = vscode.window.createWebviewPanel(
                    'codeProfile',
                    'Code Profile',
                    vscode.ViewColumn.Two,
                    { enableScripts: true }
                );

                panel.webview.html = getProfileHTML(profile);
                
                vscode.window.showInformationMessage(
                    `Execution time: ${profile.execution_time.toFixed(3)}s | Memory: ${profile.memory_usage.toFixed(2)}MB`
                );
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(`Code profiling failed: ${error.message}`);
    }
}

async function detectMemoryLeaks(apiClient: APIClient) {
    try {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const code = editor.document.getText();
        const language = editor.document.languageId;

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Detecting memory leaks...',
            cancellable: false
        }, async () => {
            const response = await apiClient.post('/api/debug/detect-memory-leaks', {
                code: code,
                language: language
            });

            if (response.success) {
                const leaks = response.leaks;
                
                if (leaks.length === 0) {
                    vscode.window.showInformationMessage('No memory leaks detected! ✓');
                } else {
                    const panel = vscode.window.createWebviewPanel(
                        'memoryLeaks',
                        'Memory Leak Detection',
                        vscode.ViewColumn.Two,
                        { enableScripts: true }
                    );

                    panel.webview.html = getMemoryLeaksHTML(leaks, response.severity_summary);
                    
                    vscode.window.showWarningMessage(
                        `Found ${leaks.length} potential memory leak(s)`
                    );
                }
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(`Memory leak detection failed: ${error.message}`);
    }
}

async function viewCallStack(apiClient: APIClient) {
    try {
        const executionId = await vscode.window.showInputBox({
            prompt: 'Enter execution ID',
            placeHolder: 'exec_123'
        });

        if (!executionId) {
            return;
        }

        const response = await apiClient.get(`/api/debug/call-stack/${executionId}`);

        if (response.success) {
            const callStack = response.call_stack;
            
            const panel = vscode.window.createWebviewPanel(
                'callStack',
                'Call Stack',
                vscode.ViewColumn.Two,
                { enableScripts: true }
            );

            panel.webview.html = getCallStackHTML(callStack);
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to get call stack: ${error.message}`);
    }
}

async function getCodeCoverage(apiClient: APIClient) {
    try {
        const projectId = await vscode.window.showInputBox({
            prompt: 'Enter project ID',
            placeHolder: 'my-project'
        });

        if (!projectId) {
            return;
        }

        const response = await apiClient.get(`/api/debug/coverage/${projectId}`);

        if (response.success) {
            const coverage = response.coverage;
            
            const panel = vscode.window.createWebviewPanel(
                'codeCoverage',
                'Code Coverage',
                vscode.ViewColumn.Two,
                { enableScripts: true }
            );

            panel.webview.html = getCoverageHTML(coverage);
            
            vscode.window.showInformationMessage(
                `Code coverage: ${coverage.percentage.toFixed(1)}%`
            );
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to get coverage: ${error.message}`);
    }
}

// HTML generators for webviews
function getErrorAnalysisHTML(analysis: any): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .header { background: #f44336; color: white; padding: 15px; border-radius: 5px; }
                .section { margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }
                .severity { display: inline-block; padding: 5px 10px; border-radius: 3px; color: white; }
                .severity.high { background: #f44336; }
                .severity.medium { background: #ff9800; }
                .severity.low { background: #4caf50; }
                .suggestion { margin: 10px 0; padding: 10px; background: white; border-left: 3px solid #2196f3; }
                pre { background: #263238; color: #aed581; padding: 15px; border-radius: 5px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Error Analysis</h2>
                <p>Type: ${analysis.error_type}</p>
                <span class="severity ${analysis.severity}">${analysis.severity.toUpperCase()}</span>
            </div>
            
            <div class="section">
                <h3>Root Cause</h3>
                <p>${analysis.root_cause}</p>
                ${analysis.line_number ? `<p>Line: ${analysis.line_number}</p>` : ''}
            </div>
            
            <div class="section">
                <h3>Fix Suggestions</h3>
                ${analysis.fix_suggestions.map((s: string) => `
                    <div class="suggestion">${s}</div>
                `).join('')}
            </div>
            
            ${analysis.code_analysis ? `
                <div class="section">
                    <h3>Code Context</h3>
                    <pre>${analysis.code_analysis.context_lines?.join('\n') || ''}</pre>
                </div>
            ` : ''}
        </body>
        </html>
    `;
}

function getVariableInspectionHTML(variable: any): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .info-grid { display: grid; grid-template-columns: 150px 1fr; gap: 10px; }
                .label { font-weight: bold; }
                .value { background: #f5f5f5; padding: 5px; border-radius: 3px; }
                pre { background: #263238; color: #aed581; padding: 15px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h2>Variable: ${variable.name}</h2>
            <div class="info-grid">
                <div class="label">Type:</div>
                <div class="value">${variable.type}</div>
                
                <div class="label">Size:</div>
                <div class="value">${variable.size} bytes</div>
                
                <div class="label">Memory Address:</div>
                <div class="value">${variable.memory_address}</div>
                
                <div class="label">Mutable:</div>
                <div class="value">${variable.is_mutable ? 'Yes' : 'No'}</div>
            </div>
            
            <h3>Value</h3>
            <pre>${variable.value}</pre>
        </body>
        </html>
    `;
}

function getProfileHTML(profile: any): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .metric { display: inline-block; margin: 10px; padding: 15px; background: #2196f3; color: white; border-radius: 5px; }
                .hotspot { margin: 10px 0; padding: 10px; background: #fff3e0; border-left: 3px solid #ff9800; }
            </style>
        </head>
        <body>
            <h2>Performance Profile</h2>
            <div>
                <div class="metric">
                    <div>Execution Time</div>
                    <div style="font-size: 24px;">${profile.execution_time.toFixed(3)}s</div>
                </div>
                <div class="metric">
                    <div>Memory Usage</div>
                    <div style="font-size: 24px;">${profile.memory_usage.toFixed(2)} MB</div>
                </div>
                <div class="metric">
                    <div>CPU Usage</div>
                    <div style="font-size: 24px;">${profile.cpu_usage.toFixed(1)}%</div>
                </div>
            </div>
            
            <h3>Performance Hotspots</h3>
            ${profile.hotspots.map((h: any) => `
                <div class="hotspot">
                    <strong>Line ${h.line}</strong>: ${h.description}
                    <br><small>Severity: ${h.severity}</small>
                </div>
            `).join('')}
        </body>
        </html>
    `;
}

function getMemoryLeaksHTML(leaks: any[], summary: any): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .summary { display: flex; gap: 10px; margin-bottom: 20px; }
                .summary-item { padding: 15px; border-radius: 5px; color: white; flex: 1; }
                .critical { background: #d32f2f; }
                .high { background: #f44336; }
                .medium { background: #ff9800; }
                .low { background: #4caf50; }
                .leak { margin: 10px 0; padding: 15px; background: #f5f5f5; border-left: 4px solid #f44336; }
            </style>
        </head>
        <body>
            <h2>Memory Leak Detection Results</h2>
            
            <div class="summary">
                <div class="summary-item critical">
                    <div>Critical</div>
                    <div style="font-size: 24px;">${summary.critical || 0}</div>
                </div>
                <div class="summary-item high">
                    <div>High</div>
                    <div style="font-size: 24px;">${summary.high || 0}</div>
                </div>
                <div class="summary-item medium">
                    <div>Medium</div>
                    <div style="font-size: 24px;">${summary.medium || 0}</div>
                </div>
                <div class="summary-item low">
                    <div>Low</div>
                    <div style="font-size: 24px;">${summary.low || 0}</div>
                </div>
            </div>
            
            <h3>Detected Leaks</h3>
            ${leaks.map(leak => `
                <div class="leak">
                    <strong>${leak.location}</strong> - ${leak.leak_type}
                    <br><span style="color: #666;">${leak.description}</span>
                    <br><strong>Suggestion:</strong> ${leak.suggestion}
                </div>
            `).join('')}
        </body>
        </html>
    `;
}

function getCallStackHTML(callStack: any[]): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .frame { margin: 10px 0; padding: 15px; background: #f5f5f5; border-left: 4px solid #2196f3; }
            </style>
        </head>
        <body>
            <h2>Call Stack</h2>
            ${callStack.map(frame => `
                <div class="frame">
                    <strong>Frame ${frame.frame}</strong>: ${frame.function}
                    <br>File: ${frame.file}, Line: ${frame.line}
                </div>
            `).join('')}
        </body>
        </html>
    `;
}

function getCoverageHTML(coverage: any): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .progress-bar { width: 100%; height: 30px; background: #e0e0e0; border-radius: 5px; overflow: hidden; }
                .progress-fill { height: 100%; background: #4caf50; display: flex; align-items: center; justify-content: center; color: white; }
                .file-coverage { margin: 10px 0; padding: 10px; background: #f5f5f5; }
            </style>
        </head>
        <body>
            <h2>Code Coverage</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${coverage.percentage}%">
                    ${coverage.percentage.toFixed(1)}%
                </div>
            </div>
            <p>${coverage.covered_lines} / ${coverage.total_lines} lines covered</p>
            
            <h3>Coverage by File</h3>
            ${Object.entries(coverage.coverage_by_file || {}).map(([file, pct]: [string, any]) => `
                <div class="file-coverage">
                    <strong>${file}</strong>: ${pct.toFixed(1)}%
                </div>
            `).join('')}
        </body>
        </html>
    `;
}