# Read the terminal panel file
with open('itechsmart-ninja/vscode-extension/src/terminal/panel.ts', 'r') as f:
    content = f.read()

# Add debug help command handler after video help
debug_help_handler = '''
    private showDebugHelp() {
        const helpText = `
Debug Commands:
══════════════════════════════════════════════════════════════

  debug-analyze                 Analyze error with AI
  analyze-error                 (alias for debug-analyze)
  debug-breakpoint              Set smart breakpoint
  set-breakpoint                (alias for debug-breakpoint)
  debug-list                    List all breakpoints
  list-breakpoints              (alias for debug-list)
  debug-inspect                 Inspect variable
  inspect-variable              (alias for debug-inspect)
  debug-profile                 Profile current code
  profile-code                  (alias for debug-profile)
  debug-leaks                   Detect memory leaks
  detect-leaks                  (alias for debug-leaks)
  debug-stack                   View call stack
  view-stack                    (alias for debug-stack)
  debug-coverage                Get code coverage
  get-coverage                  (alias for debug-coverage)

Examples:
  debug-analyze
  debug-breakpoint
  debug-profile
  debug-leaks

`;
        this.sendToTerminal({
            type: 'output',
            content: helpText,
            color: '#4ecdc4'
        });
    }

    private async analyzeError() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n🔍 Analyzing error...\\n\\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.analyzeError');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async setBreakpoint() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n🔴 Setting breakpoint...\\n\\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.setSmartBreakpoint');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async listBreakpoints() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n📋 Listing breakpoints...\\n\\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.listBreakpoints');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async inspectVariable() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n🔬 Inspecting variable...\\n\\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.inspectVariable');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async profileCode() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n⚡ Profiling code...\\n\\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.profileCode');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async detectMemoryLeaks() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n💧 Detecting memory leaks...\\n\\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.detectMemoryLeaks');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async viewCallStack() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n📚 Viewing call stack...\\n\\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.viewCallStack');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }

    private async getCodeCoverage() {
        try {
            this.sendToTerminal({
                type: 'output',
                content: '\\n📊 Getting code coverage...\\n\\n',
                color: '#4ecdc4'
            });

            vscode.commands.executeCommand('itechsmart.getCodeCoverage');

        } catch (error: any) {
            this.sendToTerminal({
                type: 'output',
                content: `Error: ${error.message}\\n`,
                color: '#ff0000'
            });
        }
    }
'''

# Find the last method and add debug handlers before the closing brace
last_method_end = content.rfind('    }\n}')
if last_method_end != -1:
    content = content[:last_method_end] + debug_help_handler + '\n' + content[last_method_end:]
    print("Added debug command handlers")
else:
    print("Warning: Could not find insertion point")

# Add debug command cases to handleCommand method
debug_cases = '''
            case 'debug-help':
                this.showDebugHelp();
                break;
            case 'debug-analyze':
            case 'analyze-error':
                this.analyzeError();
                break;
            case 'debug-breakpoint':
            case 'set-breakpoint':
                this.setBreakpoint();
                break;
            case 'debug-list':
            case 'list-breakpoints':
                this.listBreakpoints();
                break;
            case 'debug-inspect':
            case 'inspect-variable':
                this.inspectVariable();
                break;
            case 'debug-profile':
            case 'profile-code':
                this.profileCode();
                break;
            case 'debug-leaks':
            case 'detect-leaks':
                this.detectMemoryLeaks();
                break;
            case 'debug-stack':
            case 'view-stack':
                this.viewCallStack();
                break;
            case 'debug-coverage':
            case 'get-coverage':
                this.getCodeCoverage();
                break;
'''

# Find video-help case and add debug cases after it
video_help_marker = "            case 'video-help':"
if video_help_marker in content:
    # Find the break after video-help
    pos = content.find(video_help_marker)
    break_pos = content.find('break;', pos) + 6
    content = content[:break_pos] + '\n' + debug_cases + content[break_pos:]
    print("Added debug command cases")
else:
    print("Warning: Could not find video-help marker")

# Write back
with open('itechsmart-ninja/vscode-extension/src/terminal/panel.ts', 'w') as f:
    f.write(content)

print("Debug terminal commands added successfully")