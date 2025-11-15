/**
 * Files Tree Data Provider
 * Shows uploaded files in VS Code sidebar
 */
import * as vscode from 'vscode';
import { ApiClient, FileInfo } from '../api/client';

export class FilesProvider implements vscode.TreeDataProvider<FileItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<FileItem | undefined | null | void> = new vscode.EventEmitter<FileItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<FileItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private apiClient: ApiClient) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: FileItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: FileItem): Promise<FileItem[]> {
        if (!element) {
            // Root level - show files
            try {
                const files = await this.apiClient.getFiles();
                return files.map(file => new FileItem(file));
            } catch (error) {
                return [];
            }
        }
        return [];
    }
}

class FileItem extends vscode.TreeItem {
    constructor(public readonly file: FileInfo) {
        super(file.filename, vscode.TreeItemCollapsibleState.None);

        const sizeMB = (file.size / 1024 / 1024).toFixed(2);
        this.description = `${sizeMB} MB`;
        this.tooltip = `${file.filename}\nSize: ${sizeMB} MB\nType: ${file.content_type}\nUploaded: ${new Date(file.uploaded_at).toLocaleString()}`;

        // Set icon based on file type
        this.iconPath = vscode.ThemeIcon.File;

        this.contextValue = 'file';
    }
}