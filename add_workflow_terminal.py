# Read the terminal panel file
with open("itechsmart-ninja/vscode-extension/src/terminal/panel.ts", "r") as f:
    content = f.read()

# Add workflow help command handler
workflow_help_handler = """
    private showWorkflowHelp() {
        const helpText = `
Workflow Commands:
══════════════════════════════════════════════════════════════

  workflow-create               Create new workflow
  create-workflow               (alias for workflow-create)
  workflow-edit                 Edit existing workflow
  edit-workflow                 (alias for workflow-edit)
  workflow-execute              Execute workflow
  execute-workflow              (alias for workflow-execute)
  workflow-list                 List all workflows
  list-workflows                (alias for workflow-list)
  workflow-history              View workflow history
  view-history                  (alias for workflow-history)
  workflow-templates            Browse templates
  browse-templates              (alias for workflow-templates)
  workflow-delete               Delete workflow
  delete-workflow               (alias for workflow-delete)
  workflow-share                Share workflow
  share-workflow                (alias for workflow-share)

Examples:
  workflow-create
  workflow-execute
  workflow-list
  workflow-templates

`;
        this.sendToTerminal({
            type: 'output',
            content: helpText,
            color: '#4ecdc4'
        });
    }

    private async createWorkflow() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n🔧 Creating workflow...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.createWorkflow');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async editWorkflow() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n✏️ Editing workflow...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.editWorkflow');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async executeWorkflow() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n▶️ Executing workflow...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.executeWorkflow');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async listWorkflows() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n📋 Listing workflows...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.listWorkflows');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async viewWorkflowHistory() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n📊 Viewing workflow history...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.viewWorkflowHistory');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async browseWorkflowTemplates() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n🎨 Browsing templates...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.browseTemplates');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async deleteWorkflow() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n🗑️ Deleting workflow...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.deleteWorkflow');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async shareWorkflow() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n🤝 Sharing workflow...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.shareWorkflow');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }
"""

# Find the last method and add workflow handlers
last_method_end = content.rfind("    }\n}")
if last_method_end != -1:
    content = (
        content[:last_method_end]
        + workflow_help_handler
        + "\n"
        + content[last_method_end:]
    )
    print("Added workflow command handlers")

# Add workflow command cases
workflow_cases = """
            case 'workflow-help':
                this.showWorkflowHelp();
                break;
            case 'workflow-create':
            case 'create-workflow':
                this.createWorkflow();
                break;
            case 'workflow-edit':
            case 'edit-workflow':
                this.editWorkflow();
                break;
            case 'workflow-execute':
            case 'execute-workflow':
                this.executeWorkflow();
                break;
            case 'workflow-list':
            case 'list-workflows':
                this.listWorkflows();
                break;
            case 'workflow-history':
            case 'view-history':
                this.viewWorkflowHistory();
                break;
            case 'workflow-templates':
            case 'browse-templates':
                this.browseWorkflowTemplates();
                break;
            case 'workflow-delete':
            case 'delete-workflow':
                this.deleteWorkflow();
                break;
            case 'workflow-share':
            case 'share-workflow':
                this.shareWorkflow();
                break;
"""

# Find debug-help case and add workflow cases after it
debug_help_marker = "            case 'debug-help':"
if debug_help_marker in content:
    pos = content.find(debug_help_marker)
    break_pos = content.find("break;", pos) + 6
    content = content[:break_pos] + "\n" + workflow_cases + content[break_pos:]
    print("Added workflow command cases")

# Write back
with open("itechsmart-ninja/vscode-extension/src/terminal/panel.ts", "w") as f:
    f.write(content)

print("Workflow terminal commands added successfully")
