/**
 * Visualization Commands - VS Code commands for data visualization
 */

import * as vscode from 'vscode';
import { APIClient } from '../api/client';

export function registerVisualizationCommands(context: vscode.ExtensionContext, apiClient: APIClient) {
    // Create chart
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.createChart', () => createChart(apiClient))
    );
    
    // Create dashboard
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.createDashboard', () => createDashboard(apiClient))
    );
    
    // List charts
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.listCharts', () => listCharts(apiClient))
    );
    
    // View chart
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.viewChart', () => viewChart(apiClient))
    );
    
    // Export chart
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.exportChart', () => exportChart(apiClient))
    );
    
    // Analyze data
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.analyzeData', () => analyzeData(apiClient))
    );
    
    // Get chart types
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.getChartTypes', () => getChartTypes(apiClient))
    );
}

async function createChart(apiClient: APIClient) {
    try {
        // Get chart types from API
        const typesResponse = await apiClient.get('/api/visualization/chart-types');
        const chartTypes = typesResponse.data.chart_types.map((ct: any) => ({
            label: ct.name,
            description: ct.description,
            value: ct.type
        }));
        
        // Get chart type
        const chartTypeSelection = await vscode.window.showQuickPick(chartTypes, {
            placeHolder: 'Select chart type'
        });
        
        if (!chartTypeSelection) return;
        
        const chartType = chartTypeSelection.value;
        
        // Get title
        const title = await vscode.window.showInputBox({
            prompt: 'Enter chart title',
            placeHolder: 'My Chart',
            value: 'Untitled Chart'
        });
        
        if (!title) return;
        
        // Get data source
        const dataSource = await vscode.window.showQuickPick([
            { label: 'Manual Input', value: 'manual' },
            { label: 'From File', value: 'file' },
            { label: 'From Active Editor', value: 'editor' }
        ], { placeHolder: 'Select data source' });
        
        if (!dataSource) return;
        
        let data: any;
        
        if (dataSource.value === 'manual') {
            // Manual data input
            const dataInput = await vscode.window.showInputBox({
                prompt: 'Enter chart data (JSON format)',
                placeHolder: '{"labels": ["A", "B"], "datasets": [{"label": "Data", "data": [10, 20]}]}',
                validateInput: (value) => {
                    try {
                        JSON.parse(value);
                        return null;
                    } catch {
                        return 'Invalid JSON format';
                    }
                }
            });
            
            if (!dataInput) return;
            data = JSON.parse(dataInput);
            
        } else if (dataSource.value === 'file') {
            // From file
            const fileUri = await vscode.window.showOpenDialog({
                canSelectFiles: true,
                canSelectMany: false,
                filters: { 'JSON/CSV': ['json', 'csv'] }
            });
            
            if (!fileUri || fileUri.length === 0) return;
            
            const fileContent = await vscode.workspace.fs.readFile(fileUri[0]);
            const fileText = Buffer.from(fileContent).toString('utf8');
            
            if (fileUri[0].path.endsWith('.json')) {
                data = JSON.parse(fileText);
            } else {
                // Parse CSV
                data = parseCSVToChartData(fileText);
            }
            
        } else {
            // From active editor
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }
            
            const text = editor.document.getText();
            try {
                data = JSON.parse(text);
            } catch {
                vscode.window.showErrorMessage('Active editor does not contain valid JSON');
                return;
            }
        }
        
        // Get additional options
        const description = await vscode.window.showInputBox({
            prompt: 'Enter chart description (optional)',
            placeHolder: 'Chart description'
        });
        
        // Create chart
        vscode.window.showInformationMessage('Creating chart...');
        
        const result = await apiClient.post('/api/visualization/charts/create', {
            chart_type: chartType,
            data: data,
            options: {
                title: title,
                description: description || '',
                theme: 'light',
                width: 800,
                height: 600
            }
        });
        
        if (result.data.success) {
            const action = await vscode.window.showInformationMessage(
                `Chart "${title}" created successfully!`,
                'View Chart',
                'Export Chart'
            );
            
            if (action === 'View Chart') {
                showChartPreview(result.data.chart);
            } else if (action === 'Export Chart') {
                exportChartById(apiClient, result.data.chart.chart_id);
            }
        }
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error creating chart: ${error.message}`);
    }
}

async function createDashboard(apiClient: APIClient) {
    try {
        // Get title
        const title = await vscode.window.showInputBox({
            prompt: 'Enter dashboard title',
            placeHolder: 'My Dashboard'
        });
        
        if (!title) return;
        
        // Get charts
        const chartsResponse = await apiClient.get('/api/visualization/charts');
        const charts = chartsResponse.data.charts;
        
        if (charts.length === 0) {
            vscode.window.showWarningMessage('No charts available. Create charts first.');
            return;
        }
        
        // Select charts
        const selectedCharts = await vscode.window.showQuickPick(
            charts.map((c: any) => ({
                label: c.title,
                description: c.chart_type,
                value: c.chart_id,
                picked: false
            })),
            {
                placeHolder: 'Select charts to add to dashboard',
                canPickMany: true
            }
        );
        
        if (!selectedCharts || selectedCharts.length === 0) return;
        
        const chartIds = selectedCharts.map(c => c.value);
        
        // Get layout
        const columns = await vscode.window.showInputBox({
            prompt: 'Number of columns',
            placeHolder: '2',
            value: '2',
            validateInput: (value) => {
                const num = parseInt(value);
                return (isNaN(num) || num < 1 || num > 4) ? 'Enter a number between 1 and 4' : null;
            }
        });
        
        if (!columns) return;
        
        // Create dashboard
        vscode.window.showInformationMessage('Creating dashboard...');
        
        const result = await apiClient.post('/api/visualization/dashboards/create', {
            title: title,
            charts: chartIds,
            layout: {
                columns: parseInt(columns),
                spacing: 20,
                responsive: true
            }
        });
        
        if (result.data.success) {
            vscode.window.showInformationMessage(
                `Dashboard "${title}" created with ${chartIds.length} charts!`
            );
        }
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error creating dashboard: ${error.message}`);
    }
}

async function listCharts(apiClient: APIClient) {
    try {
        const response = await apiClient.get('/api/visualization/charts');
        const charts = response.data.charts;
        
        if (charts.length === 0) {
            vscode.window.showInformationMessage('No charts found. Create your first chart!');
            return;
        }
        
        const selected = await vscode.window.showQuickPick(
            charts.map((c: any) => ({
                label: c.title,
                description: `${c.chart_type} - Created: ${new Date(c.created_at).toLocaleDateString()}`,
                detail: c.description,
                value: c.chart_id
            })),
            { placeHolder: 'Select a chart to view' }
        );
        
        if (selected) {
            const chartResponse = await apiClient.get(`/api/visualization/charts/${selected.value}`);
            showChartPreview(chartResponse.data.chart);
        }
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error listing charts: ${error.message}`);
    }
}

async function viewChart(apiClient: APIClient) {
    try {
        const chartId = await vscode.window.showInputBox({
            prompt: 'Enter chart ID',
            placeHolder: 'chart_abc123'
        });
        
        if (!chartId) return;
        
        const response = await apiClient.get(`/api/visualization/charts/${chartId}`);
        
        if (response.data.success) {
            showChartPreview(response.data.chart);
        }
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error viewing chart: ${error.message}`);
    }
}

async function exportChart(apiClient: APIClient) {
    try {
        // Get charts
        const chartsResponse = await apiClient.get('/api/visualization/charts');
        const charts = chartsResponse.data.charts;
        
        if (charts.length === 0) {
            vscode.window.showWarningMessage('No charts available to export.');
            return;
        }
        
        // Select chart
        const selected = await vscode.window.showQuickPick(
            charts.map((c: any) => ({
                label: c.title,
                description: c.chart_type,
                value: c.chart_id
            })),
            { placeHolder: 'Select chart to export' }
        );
        
        if (!selected) return;
        
        await exportChartById(apiClient, selected.value);
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error exporting chart: ${error.message}`);
    }
}

async function exportChartById(apiClient: APIClient, chartId: string) {
    try {
        // Select format
        const format = await vscode.window.showQuickPick(
            [
                { label: 'PNG Image', value: 'png' },
                { label: 'SVG Vector', value: 'svg' },
                { label: 'PDF Document', value: 'pdf' },
                { label: 'HTML Page', value: 'html' },
                { label: 'JSON Data', value: 'json' }
            ],
            { placeHolder: 'Select export format' }
        );
        
        if (!format) return;
        
        // Export
        vscode.window.showInformationMessage('Exporting chart...');
        
        const result = await apiClient.post(`/api/visualization/charts/${chartId}/export`, {
            format: format.value
        });
        
        if (result.data.success) {
            // Save file
            const saveUri = await vscode.window.showSaveDialog({
                defaultUri: vscode.Uri.file(`chart.${format.value}`),
                filters: {
                    'Chart': [format.value]
                }
            });
            
            if (saveUri) {
                const exportData = result.data.export.data;
                let content: Uint8Array;
                
                if (format.value === 'png' || format.value === 'pdf') {
                    // Base64 encoded
                    content = Buffer.from(exportData, 'base64');
                } else {
                    // Text content
                    content = Buffer.from(exportData, 'utf8');
                }
                
                await vscode.workspace.fs.writeFile(saveUri, content);
                vscode.window.showInformationMessage(`Chart exported to ${saveUri.fsPath}`);
            }
        }
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error exporting chart: ${error.message}`);
    }
}

async function analyzeData(apiClient: APIClient) {
    try {
        // Get data source
        const dataSource = await vscode.window.showQuickPick([
            { label: 'From File', value: 'file' },
            { label: 'From Active Editor', value: 'editor' },
            { label: 'Manual Input', value: 'manual' }
        ], { placeHolder: 'Select data source' });
        
        if (!dataSource) return;
        
        let data: number[] = [];
        
        if (dataSource.value === 'file') {
            const fileUri = await vscode.window.showOpenDialog({
                canSelectFiles: true,
                canSelectMany: false,
                filters: { 'Data': ['json', 'csv', 'txt'] }
            });
            
            if (!fileUri || fileUri.length === 0) return;
            
            const fileContent = await vscode.workspace.fs.readFile(fileUri[0]);
            const fileText = Buffer.from(fileContent).toString('utf8');
            
            data = parseDataToNumbers(fileText);
            
        } else if (dataSource.value === 'editor') {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }
            
            const text = editor.document.getText();
            data = parseDataToNumbers(text);
            
        } else {
            const input = await vscode.window.showInputBox({
                prompt: 'Enter numbers separated by commas',
                placeHolder: '10, 20, 30, 40, 50'
            });
            
            if (!input) return;
            
            data = input.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
        }
        
        if (data.length === 0) {
            vscode.window.showErrorMessage('No valid numeric data found');
            return;
        }
        
        // Select analysis type
        const analysisType = await vscode.window.showQuickPick([
            { label: 'Basic Statistics', value: 'basic' },
            { label: 'Advanced Analysis', value: 'advanced' },
            { label: 'Statistical Analysis', value: 'statistical' }
        ], { placeHolder: 'Select analysis type' });
        
        if (!analysisType) return;
        
        // Analyze
        vscode.window.showInformationMessage('Analyzing data...');
        
        const result = await apiClient.post('/api/visualization/analyze', {
            data: data,
            analysis_type: analysisType.value
        });
        
        if (result.data.success) {
            showAnalysisResults(result.data.analysis, data.length);
        }
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error analyzing data: ${error.message}`);
    }
}

async function getChartTypes(apiClient: APIClient) {
    try {
        const response = await apiClient.get('/api/visualization/chart-types');
        const chartTypes = response.data.chart_types;
        
        const selected = await vscode.window.showQuickPick(
            chartTypes.map((ct: any) => ({
                label: ct.name,
                description: ct.type,
                detail: ct.description
            })),
            { placeHolder: 'Available chart types' }
        );
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error getting chart types: ${error.message}`);
    }
}

// Helper functions

function parseCSVToChartData(csv: string): any {
    const lines = csv.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    
    const labels: string[] = [];
    const datasets: any[] = [];
    
    for (let i = 1; i < headers.length; i++) {
        datasets.push({
            label: headers[i],
            data: []
        });
    }
    
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim());
        labels.push(values[0]);
        
        for (let j = 1; j < values.length; j++) {
            datasets[j - 1].data.push(parseFloat(values[j]));
        }
    }
    
    return { labels, datasets };
}

function parseDataToNumbers(text: string): number[] {
    // Try JSON first
    try {
        const parsed = JSON.parse(text);
        if (Array.isArray(parsed)) {
            return parsed.filter(n => typeof n === 'number');
        }
    } catch {}
    
    // Try comma/space separated
    const numbers = text.split(/[,\s\n]+/)
        .map(s => parseFloat(s.trim()))
        .filter(n => !isNaN(n));
    
    return numbers;
}

function showChartPreview(chart: any) {
    const panel = vscode.window.createWebviewPanel(
        'chartPreview',
        `Chart: ${chart.title}`,
        vscode.ViewColumn.One,
        { enableScripts: true }
    );
    
    panel.webview.html = getChartHTML(chart);
}

function showAnalysisResults(analysis: any, dataCount: number) {
    const panel = vscode.window.createWebviewPanel(
        'analysisResults',
        'Data Analysis Results',
        vscode.ViewColumn.One,
        {}
    );
    
    panel.webview.html = getAnalysisHTML(analysis, dataCount);
}

function getChartHTML(chart: any): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { 
                    padding: 20px; 
                    font-family: Arial, sans-serif;
                    background: #1e1e1e;
                    color: #d4d4d4;
                }
                .container { 
                    max-width: 900px; 
                    margin: 0 auto;
                }
                h1 { color: #4ec9b0; }
                .info { 
                    margin: 20px 0;
                    padding: 15px;
                    background: #252526;
                    border-radius: 5px;
                }
                canvas { 
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>${chart.title}</h1>
                ${chart.description ? `<p>${chart.description}</p>` : ''}
                <div class="info">
                    <strong>Type:</strong> ${chart.chart_type}<br>
                    <strong>Created:</strong> ${new Date(chart.created_at).toLocaleString()}
                </div>
                <canvas id="chart"></canvas>
            </div>
            <script>
                const ctx = document.getElementById('chart').getContext('2d');
                const chartData = ${JSON.stringify(chart.data)};
                new Chart(ctx, {
                    type: '${chart.chart_type}',
                    data: chartData,
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: true },
                            title: { display: false }
                        }
                    }
                });
            </script>
        </body>
        </html>
    `;
}

function getAnalysisHTML(analysis: any, dataCount: number): string {
    let percentiles = '';
    if (analysis.percentiles) {
        percentiles = `
            <tr><td>25th Percentile</td><td>${analysis.percentiles['25'].toFixed(2)}</td></tr>
            <tr><td>50th Percentile (Median)</td><td>${analysis.percentiles['50'].toFixed(2)}</td></tr>
            <tr><td>75th Percentile</td><td>${analysis.percentiles['75'].toFixed(2)}</td></tr>
        `;
    }
    
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { 
                    padding: 20px; 
                    font-family: Arial, sans-serif;
                    background: #1e1e1e;
                    color: #d4d4d4;
                }
                .container { 
                    max-width: 800px; 
                    margin: 0 auto;
                }
                h1 { color: #4ec9b0; }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: #252526;
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #3e3e42;
                }
                th {
                    background: #2d2d30;
                    color: #4ec9b0;
                }
                .highlight {
                    background: #264f78;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Data Analysis Results</h1>
                <p>Analysis of ${dataCount} data points</p>
                <table>
                    <tr><th>Statistic</th><th>Value</th></tr>
                    <tr class="highlight"><td>Count</td><td>${analysis.count}</td></tr>
                    <tr><td>Mean (Average)</td><td>${analysis.mean.toFixed(2)}</td></tr>
                    <tr><td>Median</td><td>${analysis.median.toFixed(2)}</td></tr>
                    ${analysis.mode !== null ? `<tr><td>Mode</td><td>${analysis.mode.toFixed(2)}</td></tr>` : ''}
                    <tr><td>Standard Deviation</td><td>${analysis.std_dev.toFixed(2)}</td></tr>
                    <tr><td>Variance</td><td>${analysis.variance.toFixed(2)}</td></tr>
                    <tr><td>Minimum</td><td>${analysis.min.toFixed(2)}</td></tr>
                    <tr><td>Maximum</td><td>${analysis.max.toFixed(2)}</td></tr>
                    <tr><td>Range</td><td>${analysis.range.toFixed(2)}</td></tr>
                    ${percentiles}
                </table>
            </div>
        </body>
        </html>
    `;
}