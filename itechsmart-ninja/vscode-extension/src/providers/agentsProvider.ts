/**
 * Agents Tree Data Provider
 * Shows available AI agents in VS Code sidebar
 */
import * as vscode from 'vscode';
import { ApiClient, Agent } from '../api/client';

export class AgentsProvider implements vscode.TreeDataProvider<AgentItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<AgentItem | undefined | null | void> = new vscode.EventEmitter<AgentItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<AgentItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private apiClient: ApiClient) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: AgentItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: AgentItem): Promise<AgentItem[]> {
        if (!element) {
            // Root level - show agents
            try {
                const agents = await this.apiClient.getAgents();
                return agents.map(agent => new AgentItem(agent));
            } catch (error) {
                return [];
            }
        }
        return [];
    }
}

class AgentItem extends vscode.TreeItem {
    constructor(public readonly agent: Agent) {
        super(agent.name, vscode.TreeItemCollapsibleState.None);

        this.description = agent.type;
        this.tooltip = `${agent.description}\n\nCapabilities:\n${agent.capabilities.join('\n')}`;

        // Set icon based on agent type
        const iconMap: { [key: string]: string } = {
            'researcher': 'search',
            'coder': 'code',
            'writer': 'edit',
            'analyst': 'graph',
            'debugger': 'bug'
        };

        this.iconPath = new vscode.ThemeIcon(iconMap[agent.type] || 'robot');

        this.contextValue = 'agent';
    }
}