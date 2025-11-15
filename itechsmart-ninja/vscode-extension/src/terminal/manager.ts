/**
 * Terminal Manager
 * Manages the integrated AI terminal
 */
import * as vscode from 'vscode';
import { ApiClient } from '../api/client';
import { TerminalPanel } from './panel';

export class TerminalManager {
    private apiClient: ApiClient;
    private context: vscode.ExtensionContext;
    private terminalPanel: TerminalPanel | undefined;

    constructor(apiClient: ApiClient, context: vscode.ExtensionContext) {
        this.apiClient = apiClient;
        this.context = context;
    }

    openTerminal() {
        if (this.terminalPanel) {
            this.terminalPanel.reveal();
        } else {
            this.terminalPanel = new TerminalPanel(
                this.context.extensionUri,
                this.apiClient
            );
        }
    }

    closeTerminal() {
        if (this.terminalPanel) {
            this.terminalPanel.dispose();
            this.terminalPanel = undefined;
        }
    }
}