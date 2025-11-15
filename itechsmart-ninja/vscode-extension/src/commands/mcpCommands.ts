/**
 * MCP (Model Context Protocol) Commands
 * Provides data source integration capabilities
 */

import * as vscode from 'vscode';
import axios from 'axios';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

interface MCPDataSource {
    id: number;
    name: string;
    type: string;
    enabled: boolean;
    last_used?: string;
    created_at: string;
}

interface QueryResult {
    success: boolean;
    data?: any;
    cached?: boolean;
    execution_time?: number;
    error?: string;
}

/**
 * Register a new MCP data source
 */
export async function registerMCPSource() {
    try {
        // Get source type
        const sourceType = await vscode.window.showQuickPick(
            [
                { label: 'PostgreSQL', value: 'postgresql' },
                { label: 'MySQL', value: 'mysql' },
                { label: 'MongoDB', value: 'mongodb' },
                { label: 'Redis', value: 'redis' },
                { label: 'REST API', value: 'rest_api' },
                { label: 'Elasticsearch', value: 'elasticsearch' }
            ],
            { placeHolder: 'Select data source type' }
        );

        if (!sourceType) return;

        // Get source name
        const name = await vscode.window.showInputBox({
            prompt: 'Enter data source name',
            placeHolder: 'e.g., Production DB'
        });

        if (!name) return;

        // Get connection details based on type
        let connectionString: string | undefined;
        let connectionConfig: any = {};

        if (sourceType.value === 'postgresql' || sourceType.value === 'mysql') {
            connectionString = await vscode.window.showInputBox({
                prompt: `Enter ${sourceType.label} connection string`,
                placeHolder: 'e.g., postgresql://user:pass@host:5432/dbname',
                password: true
            });
        } else if (sourceType.value === 'mongodb') {
            connectionString = await vscode.window.showInputBox({
                prompt: 'Enter MongoDB connection string',
                placeHolder: 'e.g., mongodb://user:pass@host:27017/dbname',
                password: true
            });
        } else if (sourceType.value === 'redis') {
            const host = await vscode.window.showInputBox({
                prompt: 'Enter Redis host',
                placeHolder: 'localhost'
            });
            const port = await vscode.window.showInputBox({
                prompt: 'Enter Redis port',
                placeHolder: '6379'
            });
            const password = await vscode.window.showInputBox({
                prompt: 'Enter Redis password (optional)',
                password: true
            });
            
            connectionConfig = {
                host: host || 'localhost',
                port: parseInt(port || '6379'),
                password: password || undefined
            };
        } else if (sourceType.value === 'rest_api') {
            const baseUrl = await vscode.window.showInputBox({
                prompt: 'Enter API base URL',
                placeHolder: 'https://api.example.com'
            });
            
            connectionConfig = {
                base_url: baseUrl
            };
        } else if (sourceType.value === 'elasticsearch') {
            const host = await vscode.window.showInputBox({
                prompt: 'Enter Elasticsearch host',
                placeHolder: 'localhost:9200'
            });
            
            connectionConfig = {
                host: host || 'localhost:9200'
            };
        }

        // Register source
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Registering MCP data source...',
            cancellable: false
        }, async () => {
            const response = await axios.post(`${API_BASE_URL}/api/mcp/sources/register`, {
                name,
                type: sourceType.value,
                connection_string: connectionString,
                connection_config: connectionConfig
            });

            if (response.data.success) {
                vscode.window.showInformationMessage(
                    `✅ Data source "${name}" registered successfully!`
                );
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to register data source: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * List all MCP data sources
 */
export async function listMCPSources() {
    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Loading MCP data sources...',
            cancellable: false
        }, async () => {
            const response = await axios.get(`${API_BASE_URL}/api/mcp/sources`);

            if (response.data.success) {
                const sources: MCPDataSource[] = response.data.sources;

                if (sources.length === 0) {
                    vscode.window.showInformationMessage('No data sources registered yet.');
                    return;
                }

                // Create webview to display sources
                const panel = vscode.window.createWebviewPanel(
                    'mcpSources',
                    'MCP Data Sources',
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = generateSourcesHTML(sources);
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to list data sources: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Query an MCP data source
 */
export async function queryMCPSource() {
    try {
        // Get list of sources
        const sourcesResponse = await axios.get(`${API_BASE_URL}/api/mcp/sources`);
        const sources: MCPDataSource[] = sourcesResponse.data.sources;

        if (sources.length === 0) {
            vscode.window.showInformationMessage('No data sources available. Register one first.');
            return;
        }

        // Select source
        const selectedSource = await vscode.window.showQuickPick(
            sources.map(s => ({
                label: s.name,
                description: s.type,
                detail: `Last used: ${s.last_used || 'Never'}`,
                source: s
            })),
            { placeHolder: 'Select data source to query' }
        );

        if (!selectedSource) return;

        // Get query
        const query = await vscode.window.showInputBox({
            prompt: `Enter ${selectedSource.source.type} query`,
            placeHolder: getQueryPlaceholder(selectedSource.source.type),
            multiline: true
        });

        if (!query) return;

        // Execute query
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Executing query...',
            cancellable: false
        }, async () => {
            const response = await axios.post(
                `${API_BASE_URL}/api/mcp/sources/${selectedSource.source.id}/query`,
                { query, use_cache: true }
            );

            if (response.data.success) {
                // Display results
                const panel = vscode.window.createWebviewPanel(
                    'mcpQueryResults',
                    `Query Results - ${selectedSource.source.name}`,
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = generateResultsHTML(
                    response.data.data,
                    response.data.cached,
                    response.data.execution_time
                );

                vscode.window.showInformationMessage(
                    `✅ Query executed in ${response.data.execution_time.toFixed(3)}s ${response.data.cached ? '(cached)' : ''}`
                );
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Query failed: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Test MCP connection
 */
export async function testMCPConnection() {
    try {
        // Get list of sources
        const sourcesResponse = await axios.get(`${API_BASE_URL}/api/mcp/sources`);
        const sources: MCPDataSource[] = sourcesResponse.data.sources;

        if (sources.length === 0) {
            vscode.window.showInformationMessage('No data sources available.');
            return;
        }

        // Select source
        const selectedSource = await vscode.window.showQuickPick(
            sources.map(s => ({
                label: s.name,
                description: s.type,
                source: s
            })),
            { placeHolder: 'Select data source to test' }
        );

        if (!selectedSource) return;

        // Test connection
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Testing connection...',
            cancellable: false
        }, async () => {
            const response = await axios.post(
                `${API_BASE_URL}/api/mcp/sources/${selectedSource.source.id}/test`
            );

            if (response.data.success) {
                vscode.window.showInformationMessage(
                    `✅ Connection successful! ${response.data.message}`
                );
            } else {
                vscode.window.showErrorMessage(
                    `❌ Connection failed: ${response.data.message}`
                );
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Connection test failed: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * View MCP schema
 */
export async function viewMCPSchema() {
    try {
        // Get list of sources
        const sourcesResponse = await axios.get(`${API_BASE_URL}/api/mcp/sources`);
        const sources: MCPDataSource[] = sourcesResponse.data.sources;

        if (sources.length === 0) {
            vscode.window.showInformationMessage('No data sources available.');
            return;
        }

        // Select source
        const selectedSource = await vscode.window.showQuickPick(
            sources.map(s => ({
                label: s.name,
                description: s.type,
                source: s
            })),
            { placeHolder: 'Select data source to view schema' }
        );

        if (!selectedSource) return;

        // Get schema
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Loading schema...',
            cancellable: false
        }, async () => {
            const response = await axios.get(
                `${API_BASE_URL}/api/mcp/sources/${selectedSource.source.id}/schema`
            );

            if (response.data.success) {
                // Display schema
                const panel = vscode.window.createWebviewPanel(
                    'mcpSchema',
                    `Schema - ${selectedSource.source.name}`,
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = generateSchemaHTML(
                    response.data.schema,
                    selectedSource.source.type
                );
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to load schema: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Delete MCP data source
 */
export async function deleteMCPSource() {
    try {
        // Get list of sources
        const sourcesResponse = await axios.get(`${API_BASE_URL}/api/mcp/sources`);
        const sources: MCPDataSource[] = sourcesResponse.data.sources;

        if (sources.length === 0) {
            vscode.window.showInformationMessage('No data sources available.');
            return;
        }

        // Select source
        const selectedSource = await vscode.window.showQuickPick(
            sources.map(s => ({
                label: s.name,
                description: s.type,
                source: s
            })),
            { placeHolder: 'Select data source to delete' }
        );

        if (!selectedSource) return;

        // Confirm deletion
        const confirm = await vscode.window.showWarningMessage(
            `Are you sure you want to delete "${selectedSource.source.name}"?`,
            'Yes', 'No'
        );

        if (confirm !== 'Yes') return;

        // Delete source
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Deleting data source...',
            cancellable: false
        }, async () => {
            await axios.delete(
                `${API_BASE_URL}/api/mcp/sources/${selectedSource.source.id}`
            );

            vscode.window.showInformationMessage(
                `✅ Data source "${selectedSource.source.name}" deleted successfully!`
            );
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to delete data source: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Clear MCP cache
 */
export async function clearMCPCache() {
    try {
        const choice = await vscode.window.showQuickPick(
            [
                { label: 'Clear all cache', value: 'all' },
                { label: 'Clear cache for specific source', value: 'source' }
            ],
            { placeHolder: 'Select cache clear option' }
        );

        if (!choice) return;

        let sourceId: number | undefined;

        if (choice.value === 'source') {
            // Get list of sources
            const sourcesResponse = await axios.get(`${API_BASE_URL}/api/mcp/sources`);
            const sources: MCPDataSource[] = sourcesResponse.data.sources;

            if (sources.length === 0) {
                vscode.window.showInformationMessage('No data sources available.');
                return;
            }

            // Select source
            const selectedSource = await vscode.window.showQuickPick(
                sources.map(s => ({
                    label: s.name,
                    description: s.type,
                    source: s
                })),
                { placeHolder: 'Select data source' }
            );

            if (!selectedSource) return;
            sourceId = selectedSource.source.id;
        }

        // Clear cache
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Clearing cache...',
            cancellable: false
        }, async () => {
            const response = await axios.post(
                `${API_BASE_URL}/api/mcp/cache/clear`,
                null,
                { params: sourceId ? { source_id: sourceId } : {} }
            );

            vscode.window.showInformationMessage(
                `✅ ${response.data.message}`
            );
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to clear cache: ${error.response?.data?.detail || error.message}`
        );
    }
}

// Helper functions

function getQueryPlaceholder(type: string): string {
    const placeholders: { [key: string]: string } = {
        'postgresql': 'SELECT * FROM users LIMIT 10',
        'mysql': 'SELECT * FROM users LIMIT 10',
        'mongodb': '{"database": "mydb", "collection": "users", "operation": "find", "args": {}}',
        'redis': '{"command": "GET", "args": ["mykey"]}',
        'rest_api': '{"method": "GET", "endpoint": "/users"}',
        'elasticsearch': '{"index": "logs", "body": {"query": {"match_all": {}}}}'
    };
    return placeholders[type] || 'Enter query';
}

function generateSourcesHTML(sources: MCPDataSource[]): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #007acc; color: white; }
                .enabled { color: green; }
                .disabled { color: red; }
            </style>
        </head>
        <body>
            <h1>MCP Data Sources</h1>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Last Used</th>
                    <th>Created</th>
                </tr>
                ${sources.map(s => `
                    <tr>
                        <td>${s.name}</td>
                        <td>${s.type}</td>
                        <td class="${s.enabled ? 'enabled' : 'disabled'}">
                            ${s.enabled ? '✓ Enabled' : '✗ Disabled'}
                        </td>
                        <td>${s.last_used || 'Never'}</td>
                        <td>${new Date(s.created_at).toLocaleString()}</td>
                    </tr>
                `).join('')}
            </table>
        </body>
        </html>
    `;
}

function generateResultsHTML(data: any, cached: boolean, executionTime: number): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .info { background: #e7f3ff; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
                pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <h1>Query Results</h1>
            <div class="info">
                <strong>Execution Time:</strong> ${executionTime.toFixed(3)}s
                ${cached ? ' <span style="color: orange;">(Cached)</span>' : ''}
            </div>
            <pre>${JSON.stringify(data, null, 2)}</pre>
        </body>
        </html>
    `;
}

function generateSchemaHTML(schema: any, type: string): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .schema-type { color: #007acc; font-weight: bold; margin-bottom: 10px; }
                pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <h1>Data Source Schema</h1>
            <div class="schema-type">Type: ${type}</div>
            <pre>${JSON.stringify(schema, null, 2)}</pre>
        </body>
        </html>
    `;
}
/**
 * Register all MCP commands
 */
export function registerMCPCommands(context: vscode.ExtensionContext, apiClient: any) {
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.registerMCPSource', registerMCPSource),
        vscode.commands.registerCommand('itechsmart.listMCPSources', listMCPSources),
        vscode.commands.registerCommand('itechsmart.queryMCPSource', queryMCPSource),
        vscode.commands.registerCommand('itechsmart.testMCPConnection', testMCPConnection),
        vscode.commands.registerCommand('itechsmart.viewMCPSchema', viewMCPSchema),
        vscode.commands.registerCommand('itechsmart.deleteMCPSource', deleteMCPSource),
        vscode.commands.registerCommand('itechsmart.clearMCPCache', clearMCPCache)
    );
}
