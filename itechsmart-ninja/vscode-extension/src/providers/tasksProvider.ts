/**
 * Tasks Tree Data Provider
 * Shows tasks in VS Code sidebar
 */
import * as vscode from 'vscode';
import { ApiClient, Task } from '../api/client';

export class TasksProvider implements vscode.TreeDataProvider<TaskItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<TaskItem | undefined | null | void> = new vscode.EventEmitter<TaskItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<TaskItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private apiClient: ApiClient) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: TaskItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: TaskItem): Promise<TaskItem[]> {
        if (!element) {
            // Root level - show tasks
            try {
                const tasks = await this.apiClient.getTasks({ limit: 20 });
                return tasks.map(task => new TaskItem(task));
            } catch (error) {
                return [];
            }
        }
        return [];
    }
}

class TaskItem extends vscode.TreeItem {
    constructor(public readonly task: Task) {
        super(task.title, vscode.TreeItemCollapsibleState.None);

        this.description = `${task.status} (${task.progress}%)`;
        this.tooltip = `${task.description}\nType: ${task.task_type}\nCreated: ${new Date(task.created_at).toLocaleString()}`;

        // Set icon based on status
        if (task.status === 'completed') {
            this.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
        } else if (task.status === 'failed') {
            this.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed'));
        } else if (task.status === 'running') {
            this.iconPath = new vscode.ThemeIcon('sync~spin', new vscode.ThemeColor('testing.iconQueued'));
        } else {
            this.iconPath = new vscode.ThemeIcon('circle-outline');
        }

        // Add context menu
        this.contextValue = 'task';

        // Make clickable
        this.command = {
            command: 'itechsmart.viewTaskDetails',
            title: 'View Task Details',
            arguments: [task.id]
        };
    }
}