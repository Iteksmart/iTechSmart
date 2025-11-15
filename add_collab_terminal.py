# Read the terminal panel file
with open('itechsmart-ninja/vscode-extension/src/terminal/panel.ts', 'r') as f:
    content = f.read()

# Add collaboration help and handlers
collab_handlers = '''
    private showCollabHelp() {
        const helpText = `
Collaboration Commands:
══════════════════════════════════════════════════════════════

  team-create                   Create new team
  create-team                   (alias for team-create)
  team-invite                   Invite team member
  invite-member                 (alias for team-invite)
  team-list                     List all teams
  list-teams                    (alias for team-list)
  workspace-create              Create workspace
  create-workspace              (alias for workspace-create)
  workspace-switch              Switch workspace
  switch-workspace              (alias for workspace-switch)
  comment-add                   Add comment
  add-comment                   (alias for comment-add)
  team-activity                 View team activity
  view-activity                 (alias for team-activity)
  team-permissions              Manage permissions
  manage-permissions            (alias for team-permissions)

Examples:
  team-create
  team-invite
  workspace-create
  team-activity

`;
        this.sendToTerminal({
            type: 'output',
            content: helpText,
            color: '#4ecdc4'
        });
    }

    private async createTeam() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n👥 Creating team...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.createTeam');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async inviteTeamMember() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n✉️ Inviting team member...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.inviteTeamMember');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async listTeamsCmd() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n📋 Listing teams...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.listTeams');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async createWorkspaceCmd() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n🏢 Creating workspace...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.createWorkspace');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async switchWorkspaceCmd() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n🔄 Switching workspace...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.switchWorkspace');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async addCommentCmd() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n💬 Adding comment...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.addComment');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async viewTeamActivityCmd() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n📊 Viewing team activity...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.viewTeamActivity');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async managePermissionsCmd() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n🔐 Managing permissions...\\n\\n',
                color: '#4ecdc4'
            });
            vscode.commands.executeCommand('itechsmart.managePermissions');
        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }
'''

# Find the last method and add collab handlers
last_method_end = content.rfind('    }\n}')
if last_method_end != -1:
    content = content[:last_method_end] + collab_handlers + '\n' + content[last_method_end:]
    print("Added collaboration command handlers")

# Add collaboration command cases
collab_cases = '''
            case 'collab-help':
            case 'team-help':
                this.showCollabHelp();
                break;
            case 'team-create':
            case 'create-team':
                this.createTeam();
                break;
            case 'team-invite':
            case 'invite-member':
                this.inviteTeamMember();
                break;
            case 'team-list':
            case 'list-teams':
                this.listTeamsCmd();
                break;
            case 'workspace-create':
            case 'create-workspace':
                this.createWorkspaceCmd();
                break;
            case 'workspace-switch':
            case 'switch-workspace':
                this.switchWorkspaceCmd();
                break;
            case 'comment-add':
            case 'add-comment':
                this.addCommentCmd();
                break;
            case 'team-activity':
            case 'view-activity':
                this.viewTeamActivityCmd();
                break;
            case 'team-permissions':
            case 'manage-permissions':
                this.managePermissionsCmd();
                break;
'''

# Find workflow-help case and add collab cases after it
workflow_help_marker = "            case 'workflow-help':"
if workflow_help_marker in content:
    pos = content.find(workflow_help_marker)
    break_pos = content.find('break;', pos) + 6
    content = content[:break_pos] + '\n' + collab_cases + content[break_pos:]
    print("Added collaboration command cases")

# Write back
with open('itechsmart-ninja/vscode-extension/src/terminal/panel.ts', 'w') as f:
    f.write(content)

print("Collaboration terminal commands added successfully")