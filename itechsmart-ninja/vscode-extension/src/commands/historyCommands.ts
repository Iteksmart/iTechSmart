/**
 * Action History Commands
 * Provides undo/redo capabilities for user actions
 */

import * as vscode from 'vscode';
import axios from 'axios';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

interface Action {
    action_id: string;
    action_type: string;
    description: string;
    previous_state?: any;
    new_state?: any;
    metadata?: any;
    undoable: boolean;
    undone: boolean;
    bookmarked: boolean;
    created_at: string;
}

interface HistoryStatistics {
    total_actions: number;
    active_actions: number;
    undone_actions: number;
    bookmarked_actions: number;
    current_index: number;
    can_undo: boolean;
    can_redo: boolean;
    action_type_counts: { [key: string]: number };
    max_history_size: number;
}

/**
 * Undo the last action
 */
export async function undoLastAction() {
    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Undoing action...',
            cancellable: false
        }, async () => {
            const response = await axios.post(`${API_BASE_URL}/api/history/undo`);

            if (response.data.success) {
                vscode.window.showInformationMessage(
                    `✅ ${response.data.message}`
                );
            }
        });

    } catch (error: any) {
        if (error.response?.status === 400) {
            vscode.window.showWarningMessage(
                error.response.data.detail || 'No actions to undo'
            );
        } else {
            vscode.window.showErrorMessage(
                `Failed to undo: ${error.response?.data?.detail || error.message}`
            );
        }
    }
}

/**
 * Redo the last undone action
 */
export async function redoLastAction() {
    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Redoing action...',
            cancellable: false
        }, async () => {
            const response = await axios.post(`${API_BASE_URL}/api/history/redo`);

            if (response.data.success) {
                vscode.window.showInformationMessage(
                    `✅ ${response.data.message}`
                );
            }
        });

    } catch (error: any) {
        if (error.response?.status === 400) {
            vscode.window.showWarningMessage(
                error.response.data.detail || 'No actions to redo'
            );
        } else {
            vscode.window.showErrorMessage(
                `Failed to redo: ${error.response?.data?.detail || error.message}`
            );
        }
    }
}

/**
 * View action history
 */
export async function viewActionHistory() {
    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Loading action history...',
            cancellable: false
        }, async () => {
            const response = await axios.get(`${API_BASE_URL}/api/history/actions`, {
                params: { limit: 100 }
            });

            if (response.data.success) {
                const actions: Action[] = response.data.actions;

                if (actions.length === 0) {
                    vscode.window.showInformationMessage('No actions in history yet.');
                    return;
                }

                // Create webview to display history
                const panel = vscode.window.createWebviewPanel(
                    'actionHistory',
                    'Action History',
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = generateHistoryHTML(actions);
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to load history: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Undo multiple actions
 */
export async function undoMultipleActions() {
    try {
        // Get statistics to show available actions
        const statsResponse = await axios.get(`${API_BASE_URL}/api/history/statistics`);
        const stats: HistoryStatistics = statsResponse.data.statistics;

        if (!stats.can_undo) {
            vscode.window.showWarningMessage('No actions to undo');
            return;
        }

        // Ask user how many actions to undo
        const count = await vscode.window.showInputBox({
            prompt: `How many actions to undo? (Available: ${stats.current_index + 1})`,
            placeHolder: '1',
            validateInput: (value) => {
                const num = parseInt(value);
                if (isNaN(num) || num <= 0) {
                    return 'Please enter a positive number';
                }
                if (num > stats.current_index + 1) {
                    return `Only ${stats.current_index + 1} actions available`;
                }
                return null;
            }
        });

        if (!count) return;

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Undoing ${count} actions...`,
            cancellable: false
        }, async () => {
            const response = await axios.post(`${API_BASE_URL}/api/history/undo-batch`, {
                count: parseInt(count)
            });

            if (response.data.success) {
                vscode.window.showInformationMessage(
                    `✅ Undone ${response.data.undone_count} actions`
                );
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to undo multiple actions: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Redo multiple actions
 */
export async function redoMultipleActions() {
    try {
        // Get statistics to show available actions
        const statsResponse = await axios.get(`${API_BASE_URL}/api/history/statistics`);
        const stats: HistoryStatistics = statsResponse.data.statistics;

        if (!stats.can_redo) {
            vscode.window.showWarningMessage('No actions to redo');
            return;
        }

        const availableRedos = stats.total_actions - stats.current_index - 1;

        // Ask user how many actions to redo
        const count = await vscode.window.showInputBox({
            prompt: `How many actions to redo? (Available: ${availableRedos})`,
            placeHolder: '1',
            validateInput: (value) => {
                const num = parseInt(value);
                if (isNaN(num) || num <= 0) {
                    return 'Please enter a positive number';
                }
                if (num > availableRedos) {
                    return `Only ${availableRedos} actions available`;
                }
                return null;
            }
        });

        if (!count) return;

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Redoing ${count} actions...`,
            cancellable: false
        }, async () => {
            const response = await axios.post(`${API_BASE_URL}/api/history/redo-batch`, {
                count: parseInt(count)
            });

            if (response.data.success) {
                vscode.window.showInformationMessage(
                    `✅ Redone ${response.data.redone_count} actions`
                );
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to redo multiple actions: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Search action history
 */
export async function searchHistory() {
    try {
        const query = await vscode.window.showInputBox({
            prompt: 'Search action history',
            placeHolder: 'Enter search query (e.g., "file modification", "image")'
        });

        if (!query) return;

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Searching history...',
            cancellable: false
        }, async () => {
            const response = await axios.post(`${API_BASE_URL}/api/history/search`, {
                query,
                limit: 50
            });

            if (response.data.success) {
                const results: Action[] = response.data.results;

                if (results.length === 0) {
                    vscode.window.showInformationMessage(`No results found for "${query}"`);
                    return;
                }

                // Create webview to display results
                const panel = vscode.window.createWebviewPanel(
                    'historySearch',
                    `Search Results: ${query}`,
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = generateSearchResultsHTML(query, results);
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Search failed: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * View bookmarked actions
 */
export async function viewBookmarks() {
    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Loading bookmarks...',
            cancellable: false
        }, async () => {
            const response = await axios.get(`${API_BASE_URL}/api/history/bookmarks`);

            if (response.data.success) {
                const bookmarks: Action[] = response.data.bookmarks;

                if (bookmarks.length === 0) {
                    vscode.window.showInformationMessage('No bookmarked actions yet.');
                    return;
                }

                // Create webview to display bookmarks
                const panel = vscode.window.createWebviewPanel(
                    'bookmarks',
                    'Bookmarked Actions',
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = generateBookmarksHTML(bookmarks);
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to load bookmarks: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * View history statistics
 */
export async function viewStatistics() {
    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Loading statistics...',
            cancellable: false
        }, async () => {
            const response = await axios.get(`${API_BASE_URL}/api/history/statistics`);

            if (response.data.success) {
                const stats: HistoryStatistics = response.data.statistics;

                // Create webview to display statistics
                const panel = vscode.window.createWebviewPanel(
                    'historyStats',
                    'Action History Statistics',
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = generateStatisticsHTML(stats);
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to load statistics: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Clear action history
 */
export async function clearHistory() {
    try {
        const choice = await vscode.window.showQuickPick(
            [
                { label: 'Clear all history', value: 'all' },
                { label: 'Clear history (keep bookmarks)', value: 'keep_bookmarks' }
            ],
            { placeHolder: 'Select clear option' }
        );

        if (!choice) return;

        const confirm = await vscode.window.showWarningMessage(
            'Are you sure you want to clear action history? This cannot be undone.',
            'Yes', 'No'
        );

        if (confirm !== 'Yes') return;

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Clearing history...',
            cancellable: false
        }, async () => {
            const response = await axios.delete(`${API_BASE_URL}/api/history/clear`, {
                params: { keep_bookmarked: choice.value === 'keep_bookmarks' }
            });

            if (response.data.success) {
                vscode.window.showInformationMessage(
                    `✅ ${response.data.message}`
                );
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to clear history: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Export action history
 */
export async function exportHistory() {
    try {
        const format = await vscode.window.showQuickPick(
            [
                { label: 'JSON', value: 'json' },
                { label: 'CSV', value: 'csv' }
            ],
            { placeHolder: 'Select export format' }
        );

        if (!format) return;

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Exporting history...',
            cancellable: false
        }, async () => {
            const response = await axios.get(`${API_BASE_URL}/api/history/export`, {
                params: { format: format.value },
                responseType: 'blob'
            });

            // Save file
            const uri = await vscode.window.showSaveDialog({
                defaultUri: vscode.Uri.file(`action_history.${format.value}`),
                filters: {
                    [format.label]: [format.value]
                }
            });

            if (uri) {
                const fs = require('fs');
                fs.writeFileSync(uri.fsPath, response.data);
                vscode.window.showInformationMessage(
                    `✅ History exported to ${uri.fsPath}`
                );
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to export history: ${error.response?.data?.detail || error.message}`
        );
    }
}

// Helper functions

function generateHistoryHTML(actions: Action[]): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #007acc; color: white; }
                .undone { opacity: 0.5; text-decoration: line-through; }
                .bookmarked { color: #ffa500; font-weight: bold; }
                .action-type { 
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    background-color: #e7f3ff;
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
            <h1>Action History</h1>
            <p>Total actions: ${actions.length}</p>
            <table>
                <tr>
                    <th>Time</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Status</th>
                </tr>
                ${actions.map(a => `
                    <tr class="${a.undone ? 'undone' : ''}">
                        <td>${new Date(a.created_at).toLocaleString()}</td>
                        <td><span class="action-type">${a.action_type}</span></td>
                        <td class="${a.bookmarked ? 'bookmarked' : ''}">
                            ${a.bookmarked ? '⭐ ' : ''}${a.description}
                        </td>
                        <td>${a.undone ? 'Undone' : 'Active'}</td>
                    </tr>
                `).join('')}
            </table>
        </body>
        </html>
    `;
}

function generateSearchResultsHTML(query: string, results: Action[]): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .query { background: #e7f3ff; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
                .result { 
                    border: 1px solid #ddd;
                    padding: 15px;
                    margin-bottom: 10px;
                    border-radius: 5px;
                }
                .result-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                }
                .action-type { 
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    background-color: #e7f3ff;
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
            <h1>Search Results</h1>
            <div class="query">
                <strong>Query:</strong> "${query}"<br>
                <strong>Results:</strong> ${results.length}
            </div>
            ${results.map(r => `
                <div class="result">
                    <div class="result-header">
                        <span class="action-type">${r.action_type}</span>
                        <span>${new Date(r.created_at).toLocaleString()}</span>
                    </div>
                    <div><strong>${r.description}</strong></div>
                    ${r.bookmarked ? '<div style="color: #ffa500;">⭐ Bookmarked</div>' : ''}
                </div>
            `).join('')}
        </body>
        </html>
    `;
}

function generateBookmarksHTML(bookmarks: Action[]): string {
    return generateHistoryHTML(bookmarks);
}

function generateStatisticsHTML(stats: HistoryStatistics): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .stat-card {
                    display: inline-block;
                    width: 200px;
                    padding: 20px;
                    margin: 10px;
                    border-radius: 8px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-align: center;
                }
                .stat-value { font-size: 36px; font-weight: bold; }
                .stat-label { font-size: 14px; margin-top: 10px; }
                .type-counts {
                    margin-top: 30px;
                    padding: 20px;
                    background: #f5f5f5;
                    border-radius: 8px;
                }
            </style>
        </head>
        <body>
            <h1>Action History Statistics</h1>
            
            <div class="stat-card">
                <div class="stat-value">${stats.total_actions}</div>
                <div class="stat-label">Total Actions</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">${stats.active_actions}</div>
                <div class="stat-label">Active Actions</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">${stats.undone_actions}</div>
                <div class="stat-label">Undone Actions</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">${stats.bookmarked_actions}</div>
                <div class="stat-label">Bookmarked</div>
            </div>
            
            <div class="type-counts">
                <h2>Actions by Type</h2>
                ${Object.entries(stats.action_type_counts).map(([type, count]) => `
                    <div style="margin: 10px 0;">
                        <strong>${type}:</strong> ${count}
                    </div>
                `).join('')}
            </div>
            
            <div style="margin-top: 30px;">
                <p><strong>Can Undo:</strong> ${stats.can_undo ? '✅ Yes' : '❌ No'}</p>
                <p><strong>Can Redo:</strong> ${stats.can_redo ? '✅ Yes' : '❌ No'}</p>
                <p><strong>Current Index:</strong> ${stats.current_index}</p>
                <p><strong>Max History Size:</strong> ${stats.max_history_size}</p>
            </div>
        </body>
        </html>
    `;
}

/**
 * Register all history commands
 */
export function registerHistoryCommands(context: vscode.ExtensionContext, apiClient: any) {
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.undoLastAction', undoLastAction),
        vscode.commands.registerCommand('itechsmart.redoLastAction', redoLastAction),
        vscode.commands.registerCommand('itechsmart.viewActionHistory', viewActionHistory),
        vscode.commands.registerCommand('itechsmart.undoMultipleActions', undoMultipleActions),
        vscode.commands.registerCommand('itechsmart.redoMultipleActions', redoMultipleActions),
        vscode.commands.registerCommand('itechsmart.searchHistory', searchHistory),
        vscode.commands.registerCommand('itechsmart.viewBookmarks', viewBookmarks),
        vscode.commands.registerCommand('itechsmart.viewStatistics', viewStatistics),
        vscode.commands.registerCommand('itechsmart.clearHistory', clearHistory),
        vscode.commands.registerCommand('itechsmart.exportHistory', exportHistory)
    );
}