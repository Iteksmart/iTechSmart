/**
 * Model Commands - AI Model Selection and Management
 * Implements SuperNinja-equivalent model browsing and selection
 */

import * as vscode from 'vscode';
import { NinjaAPIClient } from '../api/client';

export class ModelCommands {
    constructor(private client: NinjaAPIClient) {}

    /**
     * Show all available AI models
     */
    async showAllModels(): Promise<void> {
        try {
            const response = await this.client.get('/models/all');
            
            if (!response.success) {
                vscode.window.showErrorMessage('Failed to fetch models');
                return;
            }

            // Create webview to display models
            const panel = vscode.window.createWebviewPanel(
                'ninjaModels',
                'AI Models - iTechSmart Ninja',
                vscode.ViewColumn.One,
                { enableScripts: true }
            );

            panel.webview.html = this.getModelsWebviewContent(response.models);

        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error}`);
        }
    }

    /**
     * Select AI model for current session
     */
    async selectModel(): Promise<void> {
        try {
            const response = await this.client.get('/models/all');
            
            if (!response.success) {
                vscode.window.showErrorMessage('Failed to fetch models');
                return;
            }

            // Group models by provider
            const modelsByProvider: { [key: string]: any[] } = {};
            response.models.forEach((model: any) => {
                if (!modelsByProvider[model.provider]) {
                    modelsByProvider[model.provider] = [];
                }
                modelsByProvider[model.provider].push(model);
            });

            // Create quick pick items
            const items: vscode.QuickPickItem[] = [];
            
            for (const [provider, models] of Object.entries(modelsByProvider)) {
                items.push({
                    label: `$(folder) ${provider.toUpperCase()}`,
                    kind: vscode.QuickPickItemKind.Separator
                });

                models.forEach((model: any) => {
                    const costInfo = model.cost_per_1k_input === 0 
                        ? 'FREE (Local)' 
                        : `$${model.cost_per_1k_input.toFixed(4)}/1K in`;
                    
                    items.push({
                        label: `$(circuit-board) ${model.name}`,
                        description: `${model.tier} | ${costInfo}`,
                        detail: model.description,
                        picked: false
                    });
                });
            }

            const selected = await vscode.window.showQuickPick(items, {
                placeHolder: 'Select an AI model',
                matchOnDescription: true,
                matchOnDetail: true
            });

            if (selected) {
                // Find the actual model
                const modelName = selected.label.replace('$(circuit-board) ', '');
                const model = response.models.find((m: any) => m.name === modelName);
                
                if (model) {
                    // Store selected model in workspace state
                    await vscode.workspace.getConfiguration('ninja').update(
                        'selectedModel',
                        model.id,
                        vscode.ConfigurationTarget.Workspace
                    );

                    vscode.window.showInformationMessage(
                        `Selected model: ${model.name} (${model.provider})`
                    );
                }
            }

        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error}`);
        }
    }

    /**
     * Compare multiple models
     */
    async compareModels(): Promise<void> {
        try {
            const response = await this.client.get('/models/all');
            
            if (!response.success) {
                vscode.window.showErrorMessage('Failed to fetch models');
                return;
            }

            // Create quick pick for model selection
            const items = response.models.map((model: any) => ({
                label: model.name,
                description: `${model.provider} | ${model.tier}`,
                detail: model.description,
                picked: false
            }));

            const selected = await vscode.window.showQuickPick(items, {
                placeHolder: 'Select models to compare (multiple selection)',
                canPickMany: true
            });

            if (selected && selected.length >= 2) {
                const modelIds = selected.map(s => {
                    const model = response.models.find((m: any) => m.name === s.label);
                    return model?.id;
                }).filter(Boolean);

                // Request comparison
                const comparison = await this.client.post('/models/compare', {
                    model_ids: modelIds,
                    criteria: ['cost', 'context_window', 'speed']
                });

                if (comparison.success) {
                    // Show comparison in webview
                    const panel = vscode.window.createWebviewPanel(
                        'ninjaModelComparison',
                        'Model Comparison',
                        vscode.ViewColumn.One,
                        { enableScripts: true }
                    );

                    panel.webview.html = this.getComparisonWebviewContent(comparison.comparison);
                }
            }

        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error}`);
        }
    }

    /**
     * Get model recommendations
     */
    async getRecommendations(): Promise<void> {
        try {
            // Ask user for task type
            const taskType = await vscode.window.showQuickPick([
                { label: 'General', value: 'general' },
                { label: 'Coding', value: 'coding' },
                { label: 'Research', value: 'research' },
                { label: 'Creative Writing', value: 'creative' },
                { label: 'Fast Responses', value: 'fast' }
            ], {
                placeHolder: 'What type of task?'
            });

            if (!taskType) return;

            // Ask for budget
            const budget = await vscode.window.showQuickPick([
                { label: 'Low Budget', value: 'low' },
                { label: 'Medium Budget', value: 'medium' },
                { label: 'High Budget', value: 'high' },
                { label: 'Unlimited', value: 'unlimited' }
            ], {
                placeHolder: 'What is your budget?'
            });

            if (!budget) return;

            // Get recommendations
            const response = await this.client.get(
                `/models/recommendations?task_type=${taskType.value}&budget=${budget.value}`
            );

            if (response.success && response.recommendations.length > 0) {
                // Show recommendations
                const items = response.recommendations.map((model: any) => ({
                    label: `$(star) ${model.name}`,
                    description: `${model.provider} | $${model.cost_per_1k_input.toFixed(4)}/1K`,
                    detail: model.description
                }));

                const selected = await vscode.window.showQuickPick(items, {
                    placeHolder: `Recommended models for ${taskType.label} (${budget.label})`
                });

                if (selected) {
                    const modelName = selected.label.replace('$(star) ', '');
                    const model = response.recommendations.find((m: any) => m.name === modelName);
                    
                    if (model) {
                        await vscode.workspace.getConfiguration('ninja').update(
                            'selectedModel',
                            model.id,
                            vscode.ConfigurationTarget.Workspace
                        );

                        vscode.window.showInformationMessage(
                            `Selected recommended model: ${model.name}`
                        );
                    }
                }
            }

        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error}`);
        }
    }

    /**
     * Show model usage statistics
     */
    async showUsageStats(): Promise<void> {
        try {
            const response = await this.client.get('/models/usage/stats');
            
            if (!response.success) {
                vscode.window.showErrorMessage('Failed to fetch usage stats');
                return;
            }

            // Create webview to display stats
            const panel = vscode.window.createWebviewPanel(
                'ninjaUsageStats',
                'Model Usage Statistics',
                vscode.ViewColumn.One,
                { enableScripts: true }
            );

            panel.webview.html = this.getUsageStatsWebviewContent(response.stats);

        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error}`);
        }
    }

    /**
     * Check provider status
     */
    async checkProviderStatus(): Promise<void> {
        try {
            const response = await this.client.get('/models/providers/status');
            
            if (!response.success) {
                vscode.window.showErrorMessage('Failed to fetch provider status');
                return;
            }

            // Show status in output channel
            const output = vscode.window.createOutputChannel('Ninja Provider Status');
            output.clear();
            output.appendLine('=== AI Provider Status ===\n');

            for (const [provider, status] of Object.entries(response.providers)) {
                const statusIcon = (status as any).available ? '✓' : '✗';
                const statusText = (status as any).available ? 'Available' : 'Not Configured';
                
                output.appendLine(`${statusIcon} ${provider.toUpperCase()}: ${statusText}`);
                output.appendLine(`   Models: ${(status as any).total_models}`);
                output.appendLine(`   IDs: ${(status as any).models.join(', ')}`);
                output.appendLine('');
            }

            output.show();

        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error}`);
        }
    }

    /**
     * Generate HTML for models webview
     */
    private getModelsWebviewContent(models: any[]): string {
        // Group by provider
        const modelsByProvider: { [key: string]: any[] } = {};
        models.forEach(model => {
            if (!modelsByProvider[model.provider]) {
                modelsByProvider[model.provider] = [];
            }
            modelsByProvider[model.provider].push(model);
        });

        let html = `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 20px;
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                }
                h1 { color: var(--vscode-textLink-foreground); }
                h2 { 
                    color: var(--vscode-textLink-activeForeground);
                    border-bottom: 1px solid var(--vscode-panel-border);
                    padding-bottom: 5px;
                    margin-top: 30px;
                }
                .model-card {
                    background: var(--vscode-editor-inactiveSelectionBackground);
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 5px;
                    padding: 15px;
                    margin: 10px 0;
                }
                .model-name {
                    font-size: 18px;
                    font-weight: bold;
                    color: var(--vscode-textLink-foreground);
                }
                .model-tier {
                    display: inline-block;
                    padding: 2px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                    margin-left: 10px;
                }
                .tier-flagship { background: #ff6b6b; color: white; }
                .tier-advanced { background: #4ecdc4; color: white; }
                .tier-standard { background: #45b7d1; color: white; }
                .tier-fast { background: #96ceb4; color: white; }
                .tier-local { background: #ffeaa7; color: black; }
                .model-info {
                    margin-top: 10px;
                    font-size: 14px;
                }
                .info-row {
                    margin: 5px 0;
                }
                .label {
                    font-weight: bold;
                    color: var(--vscode-textLink-activeForeground);
                }
                .badge {
                    display: inline-block;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 11px;
                    margin-right: 5px;
                    background: var(--vscode-badge-background);
                    color: var(--vscode-badge-foreground);
                }
            </style>
        </head>
        <body>
            <h1>🤖 Available AI Models (${models.length} total)</h1>
        `;

        for (const [provider, providerModels] of Object.entries(modelsByProvider)) {
            html += `<h2>${provider.toUpperCase()} (${providerModels.length} models)</h2>`;

            providerModels.forEach(model => {
                const costText = model.cost_per_1k_input === 0 
                    ? 'FREE (Local)' 
                    : `$${model.cost_per_1k_input.toFixed(4)}/1K input, $${model.cost_per_1k_output.toFixed(4)}/1K output`;

                html += `
                <div class="model-card">
                    <div class="model-name">
                        ${model.name}
                        <span class="model-tier tier-${model.tier}">${model.tier.toUpperCase()}</span>
                    </div>
                    <div class="model-info">
                        <div class="info-row">
                            <span class="label">ID:</span> ${model.id}
                        </div>
                        <div class="info-row">
                            <span class="label">Description:</span> ${model.description}
                        </div>
                        <div class="info-row">
                            <span class="label">Context Window:</span> ${model.context_window.toLocaleString()} tokens
                        </div>
                        <div class="info-row">
                            <span class="label">Max Output:</span> ${model.max_output.toLocaleString()} tokens
                        </div>
                        <div class="info-row">
                            <span class="label">Cost:</span> ${costText}
                        </div>
                        <div class="info-row">
                            <span class="label">Capabilities:</span>
                            ${model.supports_vision ? '<span class="badge">Vision</span>' : ''}
                            ${model.supports_function_calling ? '<span class="badge">Function Calling</span>' : ''}
                            ${model.supports_streaming ? '<span class="badge">Streaming</span>' : ''}
                        </div>
                    </div>
                </div>
                `;
            });
        }

        html += `
        </body>
        </html>
        `;

        return html;
    }

    /**
     * Generate HTML for comparison webview
     */
    private getComparisonWebviewContent(comparison: any): string {
        const models = Object.values(comparison);

        let html = `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 20px;
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                }
                h1 { color: var(--vscode-textLink-foreground); }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid var(--vscode-panel-border);
                }
                th {
                    background: var(--vscode-editor-inactiveSelectionBackground);
                    font-weight: bold;
                    color: var(--vscode-textLink-activeForeground);
                }
                tr:hover {
                    background: var(--vscode-list-hoverBackground);
                }
                .best {
                    color: #4ecdc4;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <h1>📊 Model Comparison</h1>
            <table>
                <tr>
                    <th>Model</th>
                    <th>Provider</th>
                    <th>Tier</th>
                    <th>Cost (Input)</th>
                    <th>Cost (Output)</th>
                    <th>Context Window</th>
                    <th>Max Output</th>
                    <th>Vision</th>
                    <th>Functions</th>
                </tr>
        `;

        models.forEach((model: any) => {
            html += `
                <tr>
                    <td>${model.name}</td>
                    <td>${model.provider}</td>
                    <td>${model.tier}</td>
                    <td>$${model.cost_per_1k_input.toFixed(4)}</td>
                    <td>$${model.cost_per_1k_output.toFixed(4)}</td>
                    <td>${model.context_window.toLocaleString()}</td>
                    <td>${model.max_output.toLocaleString()}</td>
                    <td>${model.supports_vision ? '✓' : '✗'}</td>
                    <td>${model.supports_function_calling ? '✓' : '✗'}</td>
                </tr>
            `;
        });

        html += `
            </table>
        </body>
        </html>
        `;

        return html;
    }

    /**
     * Generate HTML for usage stats webview
     */
    private getUsageStatsWebviewContent(stats: any): string {
        let html = `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 20px;
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                }
                h1 { color: var(--vscode-textLink-foreground); }
                .stat-card {
                    background: var(--vscode-editor-inactiveSelectionBackground);
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 5px;
                    padding: 15px;
                    margin: 10px 0;
                }
                .stat-title {
                    font-size: 16px;
                    font-weight: bold;
                    color: var(--vscode-textLink-foreground);
                    margin-bottom: 10px;
                }
                .stat-value {
                    font-size: 24px;
                    color: var(--vscode-textLink-activeForeground);
                }
                .stat-label {
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                }
            </style>
        </head>
        <body>
            <h1>📈 Model Usage Statistics</h1>
        `;

        if (Object.keys(stats).length === 0) {
            html += '<p>No usage data yet. Start using models to see statistics!</p>';
        } else {
            for (const [modelId, modelStats] of Object.entries(stats)) {
                const s = modelStats as any;
                html += `
                <div class="stat-card">
                    <div class="stat-title">${modelId}</div>
                    <div>
                        <span class="stat-value">${s.total_requests}</span>
                        <span class="stat-label">requests</span>
                    </div>
                    <div>
                        <span class="stat-value">${s.total_tokens.toLocaleString()}</span>
                        <span class="stat-label">tokens</span>
                    </div>
                    <div>
                        <span class="stat-value">$${s.total_cost.toFixed(4)}</span>
                        <span class="stat-label">total cost</span>
                    </div>
                </div>
                `;
            }
        }

        html += `
        </body>
        </html>
        `;

        return html;
    }
}