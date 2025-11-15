/**
 * Document Commands - VS Code commands for document processing
 */

import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { APIClient } from '../api/client';

export function registerDocumentCommands(context: vscode.ExtensionContext, apiClient: APIClient) {
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.uploadDocument', () => uploadDocument(apiClient)),
        vscode.commands.registerCommand('itechsmart.listDocuments', () => listDocuments(apiClient)),
        vscode.commands.registerCommand('itechsmart.extractText', () => extractText(apiClient)),
        vscode.commands.registerCommand('itechsmart.extractTables', () => extractTables(apiClient)),
        vscode.commands.registerCommand('itechsmart.extractImages', () => extractImages(apiClient)),
        vscode.commands.registerCommand('itechsmart.extractMetadata', () => extractMetadata(apiClient)),
        vscode.commands.registerCommand('itechsmart.ocrDocument', () => ocrDocument(apiClient)),
        vscode.commands.registerCommand('itechsmart.convertDocument', () => convertDocument(apiClient)),
        vscode.commands.registerCommand('itechsmart.searchDocuments', () => searchDocuments(apiClient)),
        vscode.commands.registerCommand('itechsmart.compareDocuments', () => compareDocuments(apiClient))
    );
}

async function uploadDocument(apiClient: APIClient) {
    try {
        // Select file to upload
        const fileUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectMany: false,
            filters: {
                'Documents': ['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'txt', 'md', 'csv'],
                'Images': ['jpg', 'jpeg', 'png', 'tiff', 'bmp'],
                'All Files': ['*']
            }
        });

        if (!fileUri || fileUri.length === 0) {
            return;
        }

        const filePath = fileUri[0].fsPath;
        const fileName = path.basename(filePath);

        vscode.window.showInformationMessage(`Uploading ${fileName}...`);

        // Read file
        const fileBuffer = fs.readFileSync(filePath);
        const blob = new Blob([fileBuffer]);
        
        // Create FormData
        const formData = new FormData();
        formData.append('file', blob, fileName);

        // Upload
        const response = await apiClient.post('/api/documents/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        if (response.data.success) {
            const action = await vscode.window.showInformationMessage(
                `Document "${fileName}" uploaded successfully!`,
                'Extract Text',
                'Extract Tables',
                'View Details'
            );

            if (action === 'Extract Text') {
                await extractTextById(apiClient, response.data.document_id);
            } else if (action === 'Extract Tables') {
                await extractTablesById(apiClient, response.data.document_id);
            }
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error uploading document: ${error.message}`);
    }
}

async function listDocuments(apiClient: APIClient) {
    try {
        const response = await apiClient.get('/api/documents');
        const documents = response.data.documents;

        if (documents.length === 0) {
            vscode.window.showInformationMessage('No documents found. Upload your first document!');
            return;
        }

        const selected = await vscode.window.showQuickPick(
            documents.map((doc: any) => ({
                label: doc.filename,
                description: `${doc.file_type.toUpperCase()} - ${formatFileSize(doc.file_size)}`,
                detail: `Uploaded: ${new Date(doc.created_at).toLocaleString()} | Processed: ${doc.is_processed ? 'Yes' : 'No'}`,
                value: doc.id
            })),
            { placeHolder: 'Select a document' }
        );

        if (selected) {
            await showDocumentActions(apiClient, selected.value);
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error listing documents: ${error.message}`);
    }
}

async function showDocumentActions(apiClient: APIClient, docId: number) {
    const action = await vscode.window.showQuickPick([
        { label: '📄 Extract Text', value: 'text' },
        { label: '📊 Extract Tables', value: 'tables' },
        { label: '🖼️ Extract Images', value: 'images' },
        { label: '📋 Extract Metadata', value: 'metadata' },
        { label: '🔍 OCR Document', value: 'ocr' },
        { label: '🔄 Convert Document', value: 'convert' },
        { label: '🔎 Search in Document', value: 'search' },
        { label: '🗑️ Delete Document', value: 'delete' }
    ], { placeHolder: 'Select an action' });

    if (!action) return;

    switch (action.value) {
        case 'text':
            await extractTextById(apiClient, docId);
            break;
        case 'tables':
            await extractTablesById(apiClient, docId);
            break;
        case 'images':
            await extractImagesById(apiClient, docId);
            break;
        case 'metadata':
            await extractMetadataById(apiClient, docId);
            break;
        case 'ocr':
            await ocrDocumentById(apiClient, docId);
            break;
        case 'convert':
            await convertDocumentById(apiClient, docId);
            break;
        case 'search':
            await searchDocumentById(apiClient, docId);
            break;
        case 'delete':
            await deleteDocument(apiClient, docId);
            break;
    }
}

async function extractText(apiClient: APIClient) {
    try {
        const documents = await getDocumentList(apiClient);
        if (documents.length === 0) return;

        const selected = await selectDocument(documents, 'Select document to extract text from');
        if (!selected) return;

        await extractTextById(apiClient, selected.value);

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function extractTextById(apiClient: APIClient, docId: number) {
    try {
        vscode.window.showInformationMessage('Extracting text...');

        const response = await apiClient.post(`/api/documents/${docId}/extract-text`);

        if (response.data.success) {
            const text = response.data.text;
            
            // Create new document with extracted text
            const doc = await vscode.workspace.openTextDocument({
                content: text,
                language: 'plaintext'
            });
            
            await vscode.window.showTextDocument(doc);
            
            vscode.window.showInformationMessage(
                `Text extracted successfully! (${response.data.length} characters)`
            );
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error extracting text: ${error.message}`);
    }
}

async function extractTables(apiClient: APIClient) {
    try {
        const documents = await getDocumentList(apiClient);
        if (documents.length === 0) return;

        const selected = await selectDocument(documents, 'Select document to extract tables from');
        if (!selected) return;

        await extractTablesById(apiClient, selected.value);

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function extractTablesById(apiClient: APIClient, docId: number) {
    try {
        vscode.window.showInformationMessage('Extracting tables...');

        const response = await apiClient.post(`/api/documents/${docId}/extract-tables`);

        if (response.data.success) {
            const tables = response.data.tables;
            
            if (tables.length === 0) {
                vscode.window.showInformationMessage('No tables found in document');
                return;
            }

            // Show tables in webview
            showTablesPreview(tables);
            
            vscode.window.showInformationMessage(
                `${tables.length} table(s) extracted successfully!`
            );
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error extracting tables: ${error.message}`);
    }
}

async function extractImages(apiClient: APIClient) {
    try {
        const documents = await getDocumentList(apiClient);
        if (documents.length === 0) return;

        const selected = await selectDocument(documents, 'Select document to extract images from');
        if (!selected) return;

        await extractImagesById(apiClient, selected.value);

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function extractImagesById(apiClient: APIClient, docId: number) {
    try {
        vscode.window.showInformationMessage('Extracting images...');

        const response = await apiClient.post(`/api/documents/${docId}/extract-images`);

        if (response.data.success) {
            const images = response.data.images;
            
            if (images.length === 0) {
                vscode.window.showInformationMessage('No images found in document');
                return;
            }

            vscode.window.showInformationMessage(
                `${images.length} image(s) extracted successfully!`
            );
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error extracting images: ${error.message}`);
    }
}

async function extractMetadata(apiClient: APIClient) {
    try {
        const documents = await getDocumentList(apiClient);
        if (documents.length === 0) return;

        const selected = await selectDocument(documents, 'Select document to extract metadata from');
        if (!selected) return;

        await extractMetadataById(apiClient, selected.value);

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function extractMetadataById(apiClient: APIClient, docId: number) {
    try {
        vscode.window.showInformationMessage('Extracting metadata...');

        const response = await apiClient.post(`/api/documents/${docId}/extract-metadata`);

        if (response.data.success) {
            const metadata = response.data.metadata;
            
            // Show metadata in webview
            showMetadataPreview(metadata);
            
            vscode.window.showInformationMessage('Metadata extracted successfully!');
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error extracting metadata: ${error.message}`);
    }
}

async function ocrDocument(apiClient: APIClient) {
    try {
        const documents = await getDocumentList(apiClient);
        if (documents.length === 0) return;

        const selected = await selectDocument(documents, 'Select document for OCR');
        if (!selected) return;

        await ocrDocumentById(apiClient, selected.value);

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function ocrDocumentById(apiClient: APIClient, docId: number) {
    try {
        // Select language
        const language = await vscode.window.showQuickPick([
            { label: 'English', value: 'eng' },
            { label: 'Spanish', value: 'spa' },
            { label: 'French', value: 'fra' },
            { label: 'German', value: 'deu' },
            { label: 'Chinese', value: 'chi_sim' }
        ], { placeHolder: 'Select OCR language' });

        if (!language) return;

        vscode.window.showInformationMessage('Performing OCR...');

        const response = await apiClient.post(`/api/documents/${docId}/ocr`, {
            language: language.value
        });

        if (response.data.success) {
            const text = response.data.text;
            
            // Create new document with OCR text
            const doc = await vscode.workspace.openTextDocument({
                content: text,
                language: 'plaintext'
            });
            
            await vscode.window.showTextDocument(doc);
            
            vscode.window.showInformationMessage(
                `OCR completed successfully! (${response.data.length} characters)`
            );
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error performing OCR: ${error.message}`);
    }
}

async function convertDocument(apiClient: APIClient) {
    try {
        const documents = await getDocumentList(apiClient);
        if (documents.length === 0) return;

        const selected = await selectDocument(documents, 'Select document to convert');
        if (!selected) return;

        await convertDocumentById(apiClient, selected.value);

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function convertDocumentById(apiClient: APIClient, docId: number) {
    try {
        // Select target format
        const format = await vscode.window.showQuickPick([
            { label: 'Text (.txt)', value: 'txt' },
            { label: 'Markdown (.md)', value: 'md' },
            { label: 'HTML (.html)', value: 'html' },
            { label: 'PDF (.pdf)', value: 'pdf' }
        ], { placeHolder: 'Select target format' });

        if (!format) return;

        vscode.window.showInformationMessage('Converting document...');

        const response = await apiClient.post(`/api/documents/${docId}/convert`, {
            target_format: format.value
        });

        if (response.data.success) {
            vscode.window.showInformationMessage(
                `Document converted to ${format.label} successfully!`
            );
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error converting document: ${error.message}`);
    }
}

async function searchDocuments(apiClient: APIClient) {
    try {
        const documents = await getDocumentList(apiClient);
        if (documents.length === 0) return;

        const selected = await selectDocument(documents, 'Select document to search');
        if (!selected) return;

        await searchDocumentById(apiClient, selected.value);

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function searchDocumentById(apiClient: APIClient, docId: number) {
    try {
        const query = await vscode.window.showInputBox({
            prompt: 'Enter search query',
            placeHolder: 'Search text...'
        });

        if (!query) return;

        vscode.window.showInformationMessage('Searching document...');

        const response = await apiClient.post(`/api/documents/${docId}/search`, {
            query: query
        });

        if (response.data.success) {
            const results = response.data.results;
            
            if (results.length === 0) {
                vscode.window.showInformationMessage('No matches found');
                return;
            }

            // Show search results
            showSearchResults(query, results);
            
            vscode.window.showInformationMessage(
                `Found ${results.length} match(es)`
            );
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error searching document: ${error.message}`);
    }
}

async function compareDocuments(apiClient: APIClient) {
    try {
        const documents = await getDocumentList(apiClient);
        if (documents.length < 2) {
            vscode.window.showWarningMessage('Need at least 2 documents to compare');
            return;
        }

        // Select first document
        const doc1 = await selectDocument(documents, 'Select first document');
        if (!doc1) return;

        // Select second document
        const doc2 = await selectDocument(
            documents.filter((d: any) => d.value !== doc1.value),
            'Select second document'
        );
        if (!doc2) return;

        vscode.window.showInformationMessage('Comparing documents...');

        const response = await apiClient.post('/api/documents/compare', {
            doc_id1: doc1.value,
            doc_id2: doc2.value
        });

        if (response.data.success) {
            const comparison = response.data.comparison;
            
            // Show comparison results
            showComparisonResults(comparison, doc1.label, doc2.label);
            
            vscode.window.showInformationMessage(
                `Similarity: ${(comparison.similarity * 100).toFixed(1)}%`
            );
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error comparing documents: ${error.message}`);
    }
}

async function deleteDocument(apiClient: APIClient, docId: number) {
    try {
        const confirm = await vscode.window.showWarningMessage(
            'Are you sure you want to delete this document?',
            'Yes', 'No'
        );

        if (confirm !== 'Yes') return;

        const response = await apiClient.delete(`/api/documents/${docId}`);

        if (response.data.success) {
            vscode.window.showInformationMessage('Document deleted successfully');
        }

    } catch (error: any) {
        vscode.window.showErrorMessage(`Error deleting document: ${error.message}`);
    }
}

// Helper functions

async function getDocumentList(apiClient: APIClient): Promise<any[]> {
    const response = await apiClient.get('/api/documents');
    const documents = response.data.documents;

    if (documents.length === 0) {
        vscode.window.showInformationMessage('No documents found. Upload a document first!');
    }

    return documents;
}

async function selectDocument(documents: any[], placeholder: string): Promise<any> {
    return await vscode.window.showQuickPick(
        documents.map((doc: any) => ({
            label: doc.filename,
            description: `${doc.file_type.toUpperCase()} - ${formatFileSize(doc.file_size)}`,
            value: doc.id
        })),
        { placeHolder: placeholder }
    );
}

function formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function showTablesPreview(tables: any[]) {
    const panel = vscode.window.createWebviewPanel(
        'tablesPreview',
        'Extracted Tables',
        vscode.ViewColumn.One,
        {}
    );

    let tablesHtml = '';
    for (const table of tables) {
        tablesHtml += `
            <h3>Table ${table.table_number || table.page || ''}</h3>
            <table>
                ${table.data.map((row: any[]) => `
                    <tr>
                        ${row.map(cell => `<td>${cell || ''}</td>`).join('')}
                    </tr>
                `).join('')}
            </table>
            <br>
        `;
    }

    panel.webview.html = getWebviewHtml('Extracted Tables', tablesHtml);
}

function showMetadataPreview(metadata: any) {
    const panel = vscode.window.createWebviewPanel(
        'metadataPreview',
        'Document Metadata',
        vscode.ViewColumn.One,
        {}
    );

    const metadataHtml = Object.entries(metadata)
        .map(([key, value]) => `
            <tr>
                <td><strong>${key}</strong></td>
                <td>${value}</td>
            </tr>
        `).join('');

    panel.webview.html = getWebviewHtml('Document Metadata', `
        <table>
            ${metadataHtml}
        </table>
    `);
}

function showSearchResults(query: string, results: any[]) {
    const panel = vscode.window.createWebviewPanel(
        'searchResults',
        `Search Results: "${query}"`,
        vscode.ViewColumn.One,
        {}
    );

    const resultsHtml = results.map((result, i) => `
        <div class="result">
            <h3>Match ${i + 1} (Line ${result.line_number})</h3>
            <p><strong>Match:</strong> ${result.match}</p>
            <pre>${result.context}</pre>
        </div>
    `).join('');

    panel.webview.html = getWebviewHtml(`Search Results: "${query}"`, resultsHtml);
}

function showComparisonResults(comparison: any, doc1: string, doc2: string) {
    const panel = vscode.window.createWebviewPanel(
        'comparisonResults',
        'Document Comparison',
        vscode.ViewColumn.One,
        {}
    );

    const comparisonHtml = `
        <h2>Comparison Results</h2>
        <p><strong>Document 1:</strong> ${doc1}</p>
        <p><strong>Document 2:</strong> ${doc2}</p>
        <p><strong>Similarity:</strong> ${(comparison.similarity * 100).toFixed(1)}%</p>
        <h3>Statistics</h3>
        <ul>
            <li>Added lines: ${comparison.added_count}</li>
            <li>Removed lines: ${comparison.removed_count}</li>
            <li>Total changes: ${comparison.total_changes}</li>
        </ul>
    `;

    panel.webview.html = getWebviewHtml('Document Comparison', comparisonHtml);
}

function getWebviewHtml(title: string, content: string): string {
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
                h1, h2, h3 { color: #4ec9b0; }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: #252526;
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #3e3e42;
                }
                th {
                    background: #2d2d30;
                    color: #4ec9b0;
                }
                .result {
                    margin: 20px 0;
                    padding: 15px;
                    background: #252526;
                    border-radius: 5px;
                }
                pre {
                    background: #1e1e1e;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }
            </style>
        </head>
        <body>
            <h1>${title}</h1>
            ${content}
        </body>
        </html>
    `;
}