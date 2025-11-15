/**
 * Research Commands - Deep Research with Citations
 * Implements SuperNinja-equivalent research capabilities
 */

import * as vscode from 'vscode';
import { NinjaAPIClient } from '../api/client';

export class ResearchCommands {
    constructor(private client: NinjaAPIClient) {}

    /**
     * Perform deep research
     */
    async performDeepResearch(): Promise<void> {
        try {
            // Get research query from user
            const query = await vscode.window.showInputBox({
                prompt: 'Enter your research query',
                placeHolder: 'e.g., Latest developments in quantum computing',
                validateInput: (value) => {
                    return value.length < 3 ? 'Query must be at least 3 characters' : null;
                }
            });

            if (!query) return;

            // Get number of sources
            const numSourcesStr = await vscode.window.showQuickPick(
                ['5 sources', '10 sources (recommended)', '15 sources', '20 sources'],
                { placeHolder: 'How many sources to consult?' }
            );

            if (!numSourcesStr) return;
            const numSources = parseInt(numSourcesStr.split(' ')[0]);

            // Get citation style
            const citationStyle = await vscode.window.showQuickPick([
                { label: 'APA (7th Edition)', value: 'apa' },
                { label: 'MLA (9th Edition)', value: 'mla' },
                { label: 'Chicago (17th Edition)', value: 'chicago' },
                { label: 'Harvard', value: 'harvard' },
                { label: 'IEEE', value: 'ieee' }
            ], {
                placeHolder: 'Select citation style'
            });

            if (!citationStyle) return;

            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Performing deep research...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0, message: 'Gathering sources...' });

                const response = await this.client.post('/research/deep-research', {
                    query: query,
                    num_sources: numSources,
                    citation_style: citationStyle.value,
                    verify_facts: true,
                    min_credibility: 50.0
                });

                progress.report({ increment: 100, message: 'Research complete!' });

                if (response.success) {
                    // Create webview to display results
                    const panel = vscode.window.createWebviewPanel(
                        'ninjaResearch',
                        `Research: ${query}`,
                        vscode.ViewColumn.One,
                        { enableScripts: true }
                    );

                    panel.webview.html = this.getResearchWebviewContent(response.results);

                    // Save report to file
                    const saveReport = await vscode.window.showInformationMessage(
                        'Research complete! Would you like to save the report?',
                        'Save Report',
                        'Close'
                    );

                    if (saveReport === 'Save Report') {
                        await this.saveResearchReport(query, response.results.report);
                    }
                }
            });

        } catch (error: any) {
            vscode.window.showErrorMessage(`Research failed: ${error.message}`);
        }
    }

    /**
     * Format citation
     */
    async formatCitation(): Promise<void> {
        try {
            // Get URL
            const url = await vscode.window.showInputBox({
                prompt: 'Enter source URL',
                placeHolder: 'https://example.com/article',
                validateInput: (value) => {
                    try {
                        new URL(value);
                        return null;
                    } catch {
                        return 'Please enter a valid URL';
                    }
                }
            });

            if (!url) return;

            // Get title
            const title = await vscode.window.showInputBox({
                prompt: 'Enter article/page title',
                placeHolder: 'Article Title'
            });

            if (!title) return;

            // Get optional fields
            const author = await vscode.window.showInputBox({
                prompt: 'Enter author name (optional)',
                placeHolder: 'John Doe'
            });

            const publisher = await vscode.window.showInputBox({
                prompt: 'Enter publisher (optional)',
                placeHolder: 'Publisher Name'
            });

            // Get citation style
            const citationStyle = await vscode.window.showQuickPick([
                { label: 'APA (7th Edition)', value: 'apa' },
                { label: 'MLA (9th Edition)', value: 'mla' },
                { label: 'Chicago (17th Edition)', value: 'chicago' },
                { label: 'Harvard', value: 'harvard' },
                { label: 'IEEE', value: 'ieee' }
            ], {
                placeHolder: 'Select citation style'
            });

            if (!citationStyle) return;

            // Format citation
            const response = await this.client.post('/research/format-citation', {
                url: url,
                title: title,
                author: author || null,
                publisher: publisher || null,
                citation_style: citationStyle.value
            });

            if (response.success) {
                // Show citation
                const action = await vscode.window.showInformationMessage(
                    `Citation (${citationStyle.label}):\n\n${response.citation}`,
                    'Copy to Clipboard',
                    'Insert at Cursor'
                );

                if (action === 'Copy to Clipboard') {
                    await vscode.env.clipboard.writeText(response.citation);
                    vscode.window.showInformationMessage('Citation copied to clipboard!');
                } else if (action === 'Insert at Cursor') {
                    const editor = vscode.window.activeTextEditor;
                    if (editor) {
                        editor.edit(editBuilder => {
                            editBuilder.insert(editor.selection.active, response.citation);
                        });
                    }
                }
            }

        } catch (error: any) {
            vscode.window.showErrorMessage(`Citation formatting failed: ${error.message}`);
        }
    }

    /**
     * Check source credibility
     */
    async checkCredibility(): Promise<void> {
        try {
            // Get URL
            const url = await vscode.window.showInputBox({
                prompt: 'Enter source URL to check',
                placeHolder: 'https://example.com/article',
                validateInput: (value) => {
                    try {
                        new URL(value);
                        return null;
                    } catch {
                        return 'Please enter a valid URL';
                    }
                }
            });

            if (!url) return;

            // Get title and content
            const title = await vscode.window.showInputBox({
                prompt: 'Enter article/page title',
                placeHolder: 'Article Title'
            });

            if (!title) return;

            const content = await vscode.window.showInputBox({
                prompt: 'Enter a sample of the content (optional)',
                placeHolder: 'First paragraph or excerpt...'
            });

            // Check credibility
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Checking source credibility...',
                cancellable: false
            }, async (progress) => {
                const response = await this.client.post('/research/check-credibility', {
                    url: url,
                    title: title,
                    content: content || ''
                });

                if (response.success) {
                    const score = response.credibility_score;
                    const level = response.credibility_level;
                    const type = response.source_type;

                    // Create webview to display results
                    const panel = vscode.window.createWebviewPanel(
                        'ninjaCredibility',
                        'Source Credibility Check',
                        vscode.ViewColumn.One,
                        { enableScripts: true }
                    );

                    panel.webview.html = this.getCredibilityWebviewContent(response);
                }
            });

        } catch (error: any) {
            vscode.window.showErrorMessage(`Credibility check failed: ${error.message}`);
        }
    }

    /**
     * View citation styles
     */
    async viewCitationStyles(): Promise<void> {
        try {
            const response = await this.client.get('/research/citation-styles');

            if (response.success) {
                const items = response.styles.map((style: any) => ({
                    label: `$(book) ${style.name}`,
                    description: style.description,
                    detail: `ID: ${style.id}`
                }));

                await vscode.window.showQuickPick(items, {
                    placeHolder: 'Available Citation Styles'
                });
            }

        } catch (error: any) {
            vscode.window.showErrorMessage(`Error: ${error.message}`);
        }
    }

    /**
     * Save research report to file
     */
    private async saveResearchReport(query: string, report: string): Promise<void> {
        const fileName = `research_${query.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${Date.now()}.md`;
        
        const uri = await vscode.window.showSaveDialog({
            defaultUri: vscode.Uri.file(fileName),
            filters: {
                'Markdown': ['md'],
                'All Files': ['*']
            }
        });

        if (uri) {
            const fs = require('fs').promises;
            await fs.writeFile(uri.fsPath, report, 'utf8');
            vscode.window.showInformationMessage(`Report saved to ${uri.fsPath}`);
            
            // Open the file
            const doc = await vscode.workspace.openTextDocument(uri);
            await vscode.window.showTextDocument(doc);
        }
    }

    /**
     * Generate HTML for research webview
     */
    private getResearchWebviewContent(results: any): string {
        const sources = results.sources || [];
        const avgCredibility = results.average_credibility || 0;

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
                .summary {
                    background: var(--vscode-editor-inactiveSelectionBackground);
                    border-left: 4px solid var(--vscode-textLink-foreground);
                    padding: 15px;
                    margin: 20px 0;
                }
                .source-card {
                    background: var(--vscode-editor-inactiveSelectionBackground);
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 5px;
                    padding: 15px;
                    margin: 10px 0;
                }
                .credibility-badge {
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                    font-weight: bold;
                }
                .very-high { background: #4caf50; color: white; }
                .high { background: #8bc34a; color: white; }
                .medium { background: #ffc107; color: black; }
                .low { background: #ff9800; color: white; }
                .very-low { background: #f44336; color: white; }
                .stat {
                    display: inline-block;
                    margin-right: 20px;
                    font-size: 14px;
                }
                .stat-value {
                    font-weight: bold;
                    color: var(--vscode-textLink-activeForeground);
                }
            </style>
        </head>
        <body>
            <h1>🔍 Research Results</h1>
            
            <div class="summary">
                <h3>Summary</h3>
                <div class="stat">
                    <span class="stat-value">${sources.length}</span> sources consulted
                </div>
                <div class="stat">
                    <span class="stat-value">${avgCredibility.toFixed(1)}/100</span> avg credibility
                </div>
                <div class="stat">
                    <span class="stat-value">${results.citation_style.toUpperCase()}</span> citation style
                </div>
            </div>

            <h2>📚 Sources</h2>
        `;

        sources.forEach((source: any, index: number) => {
            const credibilityClass = source.credibility_level.replace('_', '-');
            html += `
            <div class="source-card">
                <h3>${index + 1}. ${source.title}</h3>
                <p><strong>URL:</strong> <a href="${source.url}">${source.url}</a></p>
                <p>
                    <strong>Credibility:</strong> 
                    <span class="credibility-badge ${credibilityClass}">
                        ${source.credibility_score.toFixed(1)}/100 - ${source.credibility_level.replace('_', ' ').toUpperCase()}
                    </span>
                </p>
                <p><strong>Type:</strong> ${source.source_type}</p>
                ${source.author ? `<p><strong>Author:</strong> ${source.author}</p>` : ''}
                ${source.publisher ? `<p><strong>Publisher:</strong> ${source.publisher}</p>` : ''}
                <p><strong>Domain:</strong> ${source.domain}</p>
            </div>
            `;
        });

        if (results.verified_claims && results.verified_claims.length > 0) {
            html += `<h2>✓ Verified Claims</h2>`;
            results.verified_claims.forEach((claim: any) => {
                const verifiedIcon = claim.verified ? '✓' : '✗';
                const verifiedColor = claim.verified ? '#4caf50' : '#f44336';
                html += `
                <div class="source-card">
                    <p style="color: ${verifiedColor};">
                        <strong>${verifiedIcon} ${claim.claim}</strong>
                    </p>
                    <p>Confidence: ${claim.confidence.toFixed(1)}%</p>
                    <p>Supporting sources: ${claim.supporting_sources.length}</p>
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
     * Generate HTML for credibility webview
     */
    private getCredibilityWebviewContent(response: any): string {
        const score = response.credibility_score;
        const level = response.credibility_level.replace('_', ' ').toUpperCase();
        const credibilityClass = response.credibility_level.replace('_', '-');

        return `
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
                .score-display {
                    text-align: center;
                    padding: 40px;
                    background: var(--vscode-editor-inactiveSelectionBackground);
                    border-radius: 10px;
                    margin: 20px 0;
                }
                .score-value {
                    font-size: 72px;
                    font-weight: bold;
                    color: var(--vscode-textLink-activeForeground);
                }
                .score-label {
                    font-size: 24px;
                    margin-top: 10px;
                }
                .credibility-badge {
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 5px;
                    font-size: 18px;
                    font-weight: bold;
                    margin-top: 20px;
                }
                .very-high { background: #4caf50; color: white; }
                .high { background: #8bc34a; color: white; }
                .medium { background: #ffc107; color: black; }
                .low { background: #ff9800; color: white; }
                .very-low { background: #f44336; color: white; }
                .analysis {
                    margin-top: 30px;
                }
                .analysis-item {
                    padding: 10px;
                    margin: 10px 0;
                    background: var(--vscode-editor-inactiveSelectionBackground);
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <h1>🔍 Source Credibility Check</h1>
            
            <div class="score-display">
                <div class="score-value">${score.toFixed(1)}</div>
                <div class="score-label">out of 100</div>
                <div class="credibility-badge ${credibilityClass}">${level}</div>
            </div>

            <div class="analysis">
                <h2>Analysis</h2>
                <div class="analysis-item">
                    <strong>Source Type:</strong> ${response.source_type}
                </div>
                <div class="analysis-item">
                    <strong>Domain:</strong> ${response.domain}
                </div>
                <div class="analysis-item">
                    <strong>Has Author:</strong> ${response.analysis.has_author ? '✓ Yes' : '✗ No'}
                </div>
                <div class="analysis-item">
                    <strong>Has Publication Date:</strong> ${response.analysis.has_publication_date ? '✓ Yes' : '✗ No'}
                </div>
                <div class="analysis-item">
                    <strong>Has Publisher:</strong> ${response.analysis.has_publisher ? '✓ Yes' : '✗ No'}
                </div>
                <div class="analysis-item">
                    <strong>Content Length:</strong> ${response.analysis.content_length} characters
                </div>
                <div class="analysis-item">
                    <strong>Domain Reputation:</strong> ${response.analysis.domain_reputation}
                </div>
            </div>
        </body>
        </html>
        `;
    }
}