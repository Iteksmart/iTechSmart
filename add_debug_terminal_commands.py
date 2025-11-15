# Read the terminal panel file
with open('itechsmart-ninja/vscode-extension/src/terminal/panel.ts', 'r') as f:
    content = f.read()

# Terminal commands to add
terminal_commands = '''
    // Debug commands
    debug-analyze <error>          - Analyze error with AI
    debug-breakpoint <file:line>   - Set smart breakpoint
    debug-list                     - List all breakpoints
    debug-inspect <variable>       - Inspect variable
    debug-profile                  - Profile current code
    debug-leaks                    - Detect memory leaks
    debug-stack <id>               - View call stack
    debug-coverage <project>       - Get code coverage'''

# Find the help text section and add debug commands
help_marker = "    // Video commands"
if help_marker in content:
    content = content.replace(
        help_marker,
        terminal_commands + '\n\n' + help_marker
    )
    print("Added debug terminal commands to help text")
else:
    print("Warning: Could not find help marker")

# Write back
with open('itechsmart-ninja/vscode-extension/src/terminal/panel.ts', 'w') as f:
    f.write(content)

print("Terminal commands added successfully")