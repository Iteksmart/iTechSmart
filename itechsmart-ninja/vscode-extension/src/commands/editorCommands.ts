/**
 * Editor Commands - VS Code commands for embedded editors
 * Provides Monaco Editor, Image Editor, Website Builder, etc.
 */

import * as vscode from 'vscode';
import { APIClient } from '../api/client';
import * as path from 'path';

/**
 * Register all editor commands
 */
export function registerEditorCommands(context: vscode.ExtensionContext, apiClient: APIClient) {
    // Monaco Editor commands
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.openMonacoEditor', () => openMonacoEditor(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.openFileInMonaco', (uri: vscode.Uri) => 
            openFileInMonaco(apiClient, uri))
    );
    
    // Image Editor commands
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.openImageEditor', () => openImageEditor(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.editImage', (uri: vscode.Uri) => 
            editImage(apiClient, uri))
    );
    
    // Website Builder commands
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.openWebsiteBuilder', () => 
            openWebsiteBuilder(apiClient))
    );
    
    // Markdown Editor commands
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.openMarkdownEditor', () => 
            openMarkdownEditor(apiClient))
    );
    
    // JSON/YAML Editor commands
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.openJSONEditor', () => 
            openJSONEditor(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.openYAMLEditor', () => 
            openYAMLEditor(apiClient))
    );
    
    // List editors command
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.listEditors', () => listEditors(apiClient))
    );
}

/**
 * Open Monaco code editor
 */
async function openMonacoEditor(apiClient: APIClient) {
    try {
        // Get language selection
        const languages = await apiClient.get('/api/v1/editors/monaco/languages');
        const languageItems = languages.languages.map((lang: any) => ({
            label: lang.name,
            description: lang.extensions.join(', '),
            id: lang.id
        }));
        
        const selectedLanguage = await vscode.window.showQuickPick(languageItems, {
            placeHolder: 'Select programming language'
        });
        
        if (!selectedLanguage) {
            return;
        }
        
        // Get theme selection
        const theme = await vscode.window.showQuickPick(
            [
                { label: 'Dark Theme', value: 'vs-dark' },
                { label: 'Light Theme', value: 'vs-light' }
            ],
            { placeHolder: 'Select editor theme' }
        );
        
        if (!theme) {
            return;
        }
        
        // Open editor
        const response = await apiClient.post('/api/v1/editors/monaco/open', {
            language: selectedLanguage.id,
            theme: theme.value,
            content: '// Start coding here...\n'
        });
        
        // Create webview panel
        const panel = vscode.window.createWebviewPanel(
            'monacoEditor',
            `Monaco Editor - ${selectedLanguage.label}`,
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );
        
        panel.webview.html = getMonacoEditorHTML(response, selectedLanguage.id, theme.value);
        
        // Handle messages from webview
        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'save':
                        await saveMonacoFile(apiClient, response.editor_id, message.content);
                        break;
                    case 'close':
                        await apiClient.delete(`/api/v1/editors/${response.editor_id}`);
                        panel.dispose();
                        break;
                }
            }
        );
        
        vscode.window.showInformationMessage(`Monaco Editor opened: ${response.editor_id}`);
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to open Monaco editor: ${error.message}`);
    }
}

/**
 * Open file in Monaco editor
 */
async function openFileInMonaco(apiClient: APIClient, uri: vscode.Uri) {
    try {
        const filePath = uri.fsPath;
        const ext = path.extname(filePath);
        
        // Detect language from extension
        const languageMap: { [key: string]: string } = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php'
        };
        
        const language = languageMap[ext] || 'plaintext';
        
        // Open editor with file
        const response = await apiClient.post('/api/v1/editors/monaco/open', {
            file_path: filePath,
            language: language,
            theme: 'vs-dark'
        });
        
        // Create webview panel
        const panel = vscode.window.createWebviewPanel(
            'monacoEditor',
            `Monaco Editor - ${path.basename(filePath)}`,
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );
        
        panel.webview.html = getMonacoEditorHTML(response, language, 'vs-dark');
        
        // Handle messages
        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'save':
                        await saveMonacoFile(apiClient, response.editor_id, message.content, filePath);
                        vscode.window.showInformationMessage('File saved successfully');
                        break;
                    case 'close':
                        await apiClient.delete(`/api/v1/editors/${response.editor_id}`);
                        panel.dispose();
                        break;
                }
            }
        );
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to open file: ${error.message}`);
    }
}

/**
 * Save Monaco editor file
 */
async function saveMonacoFile(
    apiClient: APIClient,
    editorId: string,
    content: string,
    filePath?: string
) {
    try {
        if (!filePath) {
            // Ask for file path
            const uri = await vscode.window.showSaveDialog({
                filters: {
                    'All Files': ['*']
                }
            });
            
            if (!uri) {
                return;
            }
            
            filePath = uri.fsPath;
        }
        
        await apiClient.post('/api/v1/editors/monaco/save', {
            editor_id: editorId,
            file_path: filePath,
            content: content,
            create_backup: true
        });
        
        vscode.window.showInformationMessage('File saved successfully');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to save file: ${error.message}`);
    }
}

/**
 * Open image editor
 */
async function openImageEditor(apiClient: APIClient) {
    try {
        // Get canvas size
        const width = await vscode.window.showInputBox({
            prompt: 'Enter canvas width',
            value: '800',
            validateInput: (value) => {
                const num = parseInt(value);
                return isNaN(num) || num <= 0 ? 'Please enter a valid number' : null;
            }
        });
        
        if (!width) {
            return;
        }
        
        const height = await vscode.window.showInputBox({
            prompt: 'Enter canvas height',
            value: '600',
            validateInput: (value) => {
                const num = parseInt(value);
                return isNaN(num) || num <= 0 ? 'Please enter a valid number' : null;
            }
        });
        
        if (!height) {
            return;
        }
        
        // Open editor
        const response = await apiClient.post('/api/v1/editors/image/open', {
            width: parseInt(width),
            height: parseInt(height)
        });
        
        // Create webview panel
        const panel = vscode.window.createWebviewPanel(
            'imageEditor',
            'Image Editor',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );
        
        panel.webview.html = getImageEditorHTML(response);
        
        // Handle messages
        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'export':
                        await exportImage(apiClient, response.editor_id, message.format);
                        break;
                    case 'close':
                        await apiClient.delete(`/api/v1/editors/${response.editor_id}`);
                        panel.dispose();
                        break;
                }
            }
        );
        
        vscode.window.showInformationMessage('Image editor opened');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to open image editor: ${error.message}`);
    }
}

/**
 * Edit existing image
 */
async function editImage(apiClient: APIClient, uri: vscode.Uri) {
    try {
        const imagePath = uri.fsPath;
        
        // Open editor with image
        const response = await apiClient.post('/api/v1/editors/image/open', {
            image_path: imagePath,
            width: 800,
            height: 600
        });
        
        // Create webview panel
        const panel = vscode.window.createWebviewPanel(
            'imageEditor',
            `Image Editor - ${path.basename(imagePath)}`,
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );
        
        panel.webview.html = getImageEditorHTML(response);
        
        // Handle messages
        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'export':
                        await exportImage(apiClient, response.editor_id, message.format, imagePath);
                        break;
                    case 'close':
                        await apiClient.delete(`/api/v1/editors/${response.editor_id}`);
                        panel.dispose();
                        break;
                }
            }
        );
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to edit image: ${error.message}`);
    }
}

/**
 * Export image
 */
async function exportImage(
    apiClient: APIClient,
    editorId: string,
    format: string,
    filePath?: string
) {
    try {
        if (!filePath) {
            const uri = await vscode.window.showSaveDialog({
                filters: {
                    'PNG Images': ['png'],
                    'JPEG Images': ['jpg', 'jpeg'],
                    'SVG Images': ['svg']
                }
            });
            
            if (!uri) {
                return;
            }
            
            filePath = uri.fsPath;
        }
        
        await apiClient.post('/api/v1/editors/image/export', {
            editor_id: editorId,
            format: format,
            quality: 90
        });
        
        vscode.window.showInformationMessage('Image exported successfully');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to export image: ${error.message}`);
    }
}

/**
 * Open website builder
 */
async function openWebsiteBuilder(apiClient: APIClient) {
    try {
        // Get project name
        const projectName = await vscode.window.showInputBox({
            prompt: 'Enter project name',
            placeHolder: 'my-website'
        });
        
        if (!projectName) {
            return;
        }
        
        // Get template
        const templates = await apiClient.get('/api/v1/editors/website/templates');
        const templateItems = templates.templates.map((t: any) => ({
            label: t.name,
            description: t.description,
            id: t.id
        }));
        
        const selectedTemplate = await vscode.window.showQuickPick(templateItems, {
            placeHolder: 'Select a template'
        });
        
        if (!selectedTemplate) {
            return;
        }
        
        // Open builder
        const response = await apiClient.post('/api/v1/editors/website/open', {
            project_name: projectName,
            template: selectedTemplate.id
        });
        
        // Create webview panel
        const panel = vscode.window.createWebviewPanel(
            'websiteBuilder',
            `Website Builder - ${projectName}`,
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );
        
        panel.webview.html = getWebsiteBuilderHTML(response);
        
        // Handle messages
        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'export':
                        await exportWebsite(apiClient, response.editor_id, message.format);
                        break;
                    case 'close':
                        await apiClient.delete(`/api/v1/editors/${response.editor_id}`);
                        panel.dispose();
                        break;
                }
            }
        );
        
        vscode.window.showInformationMessage('Website builder opened');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to open website builder: ${error.message}`);
    }
}

/**
 * Export website
 */
async function exportWebsite(apiClient: APIClient, editorId: string, format: string) {
    try {
        const uri = await vscode.window.showSaveDialog({
            filters: {
                'HTML Files': ['html'],
                'ZIP Archives': ['zip']
            }
        });
        
        if (!uri) {
            return;
        }
        
        await apiClient.post('/api/v1/editors/website/export', {
            editor_id: editorId,
            format: format,
            include_assets: true
        });
        
        vscode.window.showInformationMessage('Website exported successfully');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to export website: ${error.message}`);
    }
}

/**
 * Open markdown editor
 */
async function openMarkdownEditor(apiClient: APIClient) {
    try {
        // Open editor
        const response = await apiClient.post('/api/v1/editors/markdown/open', {
            content: '# Markdown Editor\n\nStart writing...\n',
            enable_preview: true
        });
        
        // Create webview panel
        const panel = vscode.window.createWebviewPanel(
            'markdownEditor',
            'Markdown Editor',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );
        
        panel.webview.html = getMarkdownEditorHTML(response);
        
        // Handle messages
        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'save':
                        await saveMarkdownFile(apiClient, response.editor_id, message.content);
                        break;
                    case 'close':
                        await apiClient.delete(`/api/v1/editors/${response.editor_id}`);
                        panel.dispose();
                        break;
                }
            }
        );
        
        vscode.window.showInformationMessage('Markdown editor opened');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to open markdown editor: ${error.message}`);
    }
}

/**
 * Save markdown file
 */
async function saveMarkdownFile(apiClient: APIClient, editorId: string, content: string) {
    try {
        const uri = await vscode.window.showSaveDialog({
            filters: {
                'Markdown Files': ['md']
            }
        });
        
        if (!uri) {
            return;
        }
        
        await apiClient.post('/api/v1/editors/monaco/save', {
            editor_id: editorId,
            file_path: uri.fsPath,
            content: content
        });
        
        vscode.window.showInformationMessage('Markdown file saved');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to save markdown: ${error.message}`);
    }
}

/**
 * Open JSON editor
 */
async function openJSONEditor(apiClient: APIClient) {
    try {
        // Open editor
        const response = await apiClient.post('/api/v1/editors/json/open', {
            content: '{\n  "key": "value"\n}'
        });
        
        // Create webview panel
        const panel = vscode.window.createWebviewPanel(
            'jsonEditor',
            'JSON Editor',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );
        
        panel.webview.html = getJSONEditorHTML(response);
        
        // Handle messages
        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'validate':
                        // Re-validate JSON
                        break;
                    case 'save':
                        await saveJSONFile(apiClient, response.editor_id, message.content);
                        break;
                    case 'close':
                        await apiClient.delete(`/api/v1/editors/${response.editor_id}`);
                        panel.dispose();
                        break;
                }
            }
        );
        
        vscode.window.showInformationMessage('JSON editor opened');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to open JSON editor: ${error.message}`);
    }
}

/**
 * Save JSON file
 */
async function saveJSONFile(apiClient: APIClient, editorId: string, content: string) {
    try {
        const uri = await vscode.window.showSaveDialog({
            filters: {
                'JSON Files': ['json']
            }
        });
        
        if (!uri) {
            return;
        }
        
        await apiClient.post('/api/v1/editors/monaco/save', {
            editor_id: editorId,
            file_path: uri.fsPath,
            content: content
        });
        
        vscode.window.showInformationMessage('JSON file saved');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to save JSON: ${error.message}`);
    }
}

/**
 * Open YAML editor
 */
async function openYAMLEditor(apiClient: APIClient) {
    try {
        // Open editor
        const response = await apiClient.post('/api/v1/editors/yaml/open', {
            content: 'key: value\n'
        });
        
        // Create webview panel
        const panel = vscode.window.createWebviewPanel(
            'yamlEditor',
            'YAML Editor',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );
        
        panel.webview.html = getYAMLEditorHTML(response);
        
        // Handle messages
        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'validate':
                        // Re-validate YAML
                        break;
                    case 'save':
                        await saveYAMLFile(apiClient, response.editor_id, message.content);
                        break;
                    case 'close':
                        await apiClient.delete(`/api/v1/editors/${response.editor_id}`);
                        panel.dispose();
                        break;
                }
            }
        );
        
        vscode.window.showInformationMessage('YAML editor opened');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to open YAML editor: ${error.message}`);
    }
}

/**
 * Save YAML file
 */
async function saveYAMLFile(apiClient: APIClient, editorId: string, content: string) {
    try {
        const uri = await vscode.window.showSaveDialog({
            filters: {
                'YAML Files': ['yaml', 'yml']
            }
        });
        
        if (!uri) {
            return;
        }
        
        await apiClient.post('/api/v1/editors/monaco/save', {
            editor_id: editorId,
            file_path: uri.fsPath,
            content: content
        });
        
        vscode.window.showInformationMessage('YAML file saved');
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to save YAML: ${error.message}`);
    }
}

/**
 * List all active editors
 */
async function listEditors(apiClient: APIClient) {
    try {
        const response = await apiClient.get('/api/v1/editors/list');
        
        if (response.total === 0) {
            vscode.window.showInformationMessage('No active editors');
            return;
        }
        
        const items = response.editors.map((editor: any) => ({
            label: `${editor.editor_type} - ${editor.editor_id}`,
            description: editor.file_path || 'No file',
            detail: `Created: ${new Date(editor.created_at).toLocaleString()}`,
            editor: editor
        }));
        
        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select an editor to manage'
        });
        
        if (!selected) {
            return;
        }
        
        // Show editor actions
        const action = await vscode.window.showQuickPick(
            [
                { label: 'View Info', value: 'info' },
                { label: 'Close Editor', value: 'close' }
            ],
            { placeHolder: 'Select action' }
        );
        
        if (!action) {
            return;
        }
        
        if (action.value === 'info') {
            const info = await apiClient.get(`/api/v1/editors/${selected.editor.editor_id}`);
            vscode.window.showInformationMessage(
                `Editor: ${info.editor_type}\nCreated: ${new Date(info.created_at).toLocaleString()}\nModified: ${info.is_modified}`
            );
        } else if (action.value === 'close') {
            await apiClient.delete(`/api/v1/editors/${selected.editor.editor_id}`);
            vscode.window.showInformationMessage('Editor closed');
        }
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list editors: ${error.message}`);
    }
}

// ============================================================================
// HTML GENERATORS
// ============================================================================

function getMonacoEditorHTML(response: any, language: string, theme: string): string {
    return `<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Monaco Editor</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs/editor/editor.main.css">
        <style>
            body { margin: 0; padding: 0; overflow: hidden; }
            #container { width: 100vw; height: 100vh; }
            #toolbar {
                background: #1e1e1e;
                padding: 10px;
                display: flex;
                gap: 10px;
                border-bottom: 1px solid #333;
            }
            button {
                background: #0e639c;
                color: white;
                border: none;
                padding: 8px 16px;
                cursor: pointer;
                border-radius: 4px;
            }
            button:hover { background: #1177bb; }
            #editor { height: calc(100vh - 50px); }
        </style>
    </head>
    <body>
        <div id="container">
            <div id="toolbar">
                <button onclick="save()">Save</button>
                <button onclick="close()">Close</button>
                <span style="color: white; margin-left: auto; padding: 8px;">
                    Lines: ${response.line_count} | Characters: ${response.character_count}
                </span>
            </div>
            <div id="editor"></div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs/loader.js"></script>
        <script>
            const vscode = acquireVsCodeApi();
            let editor;
            
            require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs' }});
            
            require(['vs/editor/editor.main'], function() {
                editor = monaco.editor.create(document.getElementById('editor'), {
                    value: ${JSON.stringify(response.content)},
                    language: '${language}',
                    theme: '${theme}',
                    automaticLayout: true,
                    minimap: { enabled: true },
                    fontSize: 14,
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false
                });
            });
            
            function save() {
                vscode.postMessage({
                    command: 'save',
                    content: editor.getValue()
                });
            }
            
            function close() {
                vscode.postMessage({ command: 'close' });
            }
        </script>
    </body>
    </html>`;
}

function getImageEditorHTML(response: any): string {
    return `<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Image Editor</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.0/fabric.min.js"></script>
        <style>
            body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
            #toolbar {
                background: #2d2d2d;
                padding: 10px;
                display: flex;
                gap: 10px;
                border-bottom: 1px solid #444;
            }
            button {
                background: #0e639c;
                color: white;
                border: none;
                padding: 8px 16px;
                cursor: pointer;
                border-radius: 4px;
            }
            button:hover { background: #1177bb; }
            #canvas-container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: calc(100vh - 60px);
                background: #1e1e1e;
            }
        </style>
    </head>
    <body>
        <div id="toolbar">
            <button onclick="addRectangle()">Rectangle</button>
            <button onclick="addCircle()">Circle</button>
            <button onclick="addText()">Text</button>
            <button onclick="exportImage('png')">Export PNG</button>
            <button onclick="exportImage('jpg')">Export JPG</button>
            <button onclick="closeEditor()">Close</button>
        </div>
        <div id="canvas-container">
            <canvas id="canvas" width="${response.width}" height="${response.height}"></canvas>
        </div>
        
        <script>
            const vscode = acquireVsCodeApi();
            const canvas = new fabric.Canvas('canvas', {
                backgroundColor: '#ffffff'
            });
            
            function addRectangle() {
                const rect = new fabric.Rect({
                    left: 100,
                    top: 100,
                    fill: '#0e639c',
                    width: 100,
                    height: 100
                });
                canvas.add(rect);
            }
            
            function addCircle() {
                const circle = new fabric.Circle({
                    left: 150,
                    top: 150,
                    fill: '#1177bb',
                    radius: 50
                });
                canvas.add(circle);
            }
            
            function addText() {
                const text = new fabric.IText('Edit me', {
                    left: 200,
                    top: 200,
                    fontSize: 24,
                    fill: '#000000'
                });
                canvas.add(text);
            }
            
            function exportImage(format) {
                vscode.postMessage({
                    command: 'export',
                    format: format,
                    data: canvas.toDataURL('image/' + format)
                });
            }
            
            function closeEditor() {
                vscode.postMessage({ command: 'close' });
            }
        </script>
    </body>
    </html>`;
}

function getWebsiteBuilderHTML(response: any): string {
    return `<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Website Builder</title>
        <link rel="stylesheet" href="https://unpkg.com/grapesjs/dist/css/grapes.min.css">
        <script src="https://unpkg.com/grapesjs"></script>
        <style>
            body, html { margin: 0; padding: 0; height: 100%; }
            #gjs { height: 100vh; }
        </style>
    </head>
    <body>
        <div id="gjs"></div>
        
        <script>
            const vscode = acquireVsCodeApi();
            
            const editor = grapesjs.init({
                container: '#gjs',
                height: '100vh',
                storageManager: false,
                panels: { defaults: [] }
            });
            
            // Add custom export button
            editor.Panels.addButton('options', {
                id: 'export-html',
                className: 'fa fa-download',
                command: 'export-html',
                attributes: { title: 'Export HTML' }
            });
            
            editor.Commands.add('export-html', {
                run: function(editor) {
                    vscode.postMessage({
                        command: 'export',
                        format: 'html',
                        html: editor.getHtml(),
                        css: editor.getCss()
                    });
                }
            });
        </script>
    </body>
    </html>`;
}

function getMarkdownEditorHTML(response: any): string {
    return `<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Markdown Editor</title>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
            #toolbar {
                background: #2d2d2d;
                padding: 10px;
                display: flex;
                gap: 10px;
                border-bottom: 1px solid #444;
            }
            button {
                background: #0e639c;
                color: white;
                border: none;
                padding: 8px 16px;
                cursor: pointer;
                border-radius: 4px;
            }
            button:hover { background: #1177bb; }
            #container {
                display: flex;
                height: calc(100vh - 60px);
            }
            #editor, #preview {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
            }
            #editor {
                background: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Courier New', monospace;
                border: none;
                resize: none;
            }
            #preview {
                background: white;
                border-left: 1px solid #444;
            }
        </style>
    </head>
    <body>
        <div id="toolbar">
            <button onclick="save()">Save</button>
            <button onclick="closeEditor()">Close</button>
            <span style="color: white; margin-left: auto; padding: 8px;">
                Words: <span id="word-count">${response.word_count}</span>
            </span>
        </div>
        <div id="container">
            <textarea id="editor">${response.content}</textarea>
            <div id="preview"></div>
        </div>
        
        <script>
            const vscode = acquireVsCodeApi();
            const editor = document.getElementById('editor');
            const preview = document.getElementById('preview');
            const wordCount = document.getElementById('word-count');
            
            function updatePreview() {
                const markdown = editor.value;
                preview.innerHTML = marked.parse(markdown);
                wordCount.textContent = markdown.split(/\\s+/).length;
            }
            
            editor.addEventListener('input', updatePreview);
            updatePreview();
            
            function save() {
                vscode.postMessage({
                    command: 'save',
                    content: editor.value
                });
            }
            
            function closeEditor() {
                vscode.postMessage({ command: 'close' });
            }
        </script>
    </body>
    </html>`;
}

function getJSONEditorHTML(response: any): string {
    return `<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>JSON Editor</title>
        <style>
            body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
            #toolbar {
                background: #2d2d2d;
                padding: 10px;
                display: flex;
                gap: 10px;
                border-bottom: 1px solid #444;
            }
            button {
                background: #0e639c;
                color: white;
                border: none;
                padding: 8px 16px;
                cursor: pointer;
                border-radius: 4px;
            }
            button:hover { background: #1177bb; }
            #editor {
                width: 100%;
                height: calc(100vh - 60px);
                padding: 20px;
                background: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Courier New', monospace;
                border: none;
                resize: none;
            }
            .error {
                background: #f44336;
                color: white;
                padding: 10px;
                margin: 10px;
            }
        </style>
    </head>
    <body>
        <div id="toolbar">
            <button onclick="format()">Format</button>
            <button onclick="validate()">Validate</button>
            <button onclick="save()">Save</button>
            <button onclick="closeEditor()">Close</button>
            <span id="status" style="color: ${response.is_valid ? 'green' : 'red'}; margin-left: auto; padding: 8px;">
                ${response.is_valid ? '✓ Valid' : '✗ Invalid'}
            </span>
        </div>
        <textarea id="editor">${response.content}</textarea>
        
        <script>
            const vscode = acquireVsCodeApi();
            const editor = document.getElementById('editor');
            const status = document.getElementById('status');
            
            function format() {
                try {
                    const json = JSON.parse(editor.value);
                    editor.value = JSON.stringify(json, null, 2);
                    status.textContent = '✓ Valid';
                    status.style.color = 'green';
                } catch (e) {
                    status.textContent = '✗ Invalid: ' + e.message;
                    status.style.color = 'red';
                }
            }
            
            function validate() {
                try {
                    JSON.parse(editor.value);
                    status.textContent = '✓ Valid';
                    status.style.color = 'green';
                } catch (e) {
                    status.textContent = '✗ Invalid: ' + e.message;
                    status.style.color = 'red';
                }
            }
            
            function save() {
                vscode.postMessage({
                    command: 'save',
                    content: editor.value
                });
            }
            
            function closeEditor() {
                vscode.postMessage({ command: 'close' });
            }
            
            editor.addEventListener('input', validate);
        </script>
    </body>
    </html>`;
}

function getYAMLEditorHTML(response: any): string {
    return `<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>YAML Editor</title>
        <style>
            body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
            #toolbar {
                background: #2d2d2d;
                padding: 10px;
                display: flex;
                gap: 10px;
                border-bottom: 1px solid #444;
            }
            button {
                background: #0e639c;
                color: white;
                border: none;
                padding: 8px 16px;
                cursor: pointer;
                border-radius: 4px;
            }
            button:hover { background: #1177bb; }
            #container {
                display: flex;
                height: calc(100vh - 60px);
            }
            #editor, #json-preview {
                flex: 1;
                padding: 20px;
                background: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Courier New', monospace;
                border: none;
                resize: none;
                overflow-y: auto;
            }
            #json-preview {
                border-left: 1px solid #444;
            }
        </style>
    </head>
    <body>
        <div id="toolbar">
            <button onclick="save()">Save</button>
            <button onclick="closeEditor()">Close</button>
            <span id="status" style="color: ${response.is_valid ? 'green' : 'red'}; margin-left: auto; padding: 8px;">
                ${response.is_valid ? '✓ Valid' : '✗ Invalid'}
            </span>
        </div>
        <div id="container">
            <textarea id="editor">${response.content}</textarea>
            <textarea id="json-preview" readonly>${response.json_equivalent}</textarea>
        </div>
        
        <script>
            const vscode = acquireVsCodeApi();
            
            function save() {
                vscode.postMessage({
                    command: 'save',
                    content: document.getElementById('editor').value
                });
            }
            
            function closeEditor() {
                vscode.postMessage({ command: 'close' });
            }
        </script>
    </body>
    </html>`;
}