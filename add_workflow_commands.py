import json

# Read package.json
with open('itechsmart-ninja/vscode-extension/package.json', 'r') as f:
    package = json.load(f)

# Workflow commands to add
workflow_commands = [
    {
        "command": "itechsmart.createWorkflow",
        "title": "iTechSmart: Create Workflow",
        "category": "Workflow"
    },
    {
        "command": "itechsmart.editWorkflow",
        "title": "iTechSmart: Edit Workflow",
        "category": "Workflow"
    },
    {
        "command": "itechsmart.executeWorkflow",
        "title": "iTechSmart: Execute Workflow",
        "category": "Workflow"
    },
    {
        "command": "itechsmart.viewWorkflowHistory",
        "title": "iTechSmart: View Workflow History",
        "category": "Workflow"
    },
    {
        "command": "itechsmart.browseTemplates",
        "title": "iTechSmart: Browse Workflow Templates",
        "category": "Workflow"
    },
    {
        "command": "itechsmart.listWorkflows",
        "title": "iTechSmart: List Workflows",
        "category": "Workflow"
    },
    {
        "command": "itechsmart.deleteWorkflow",
        "title": "iTechSmart: Delete Workflow",
        "category": "Workflow"
    },
    {
        "command": "itechsmart.shareWorkflow",
        "title": "iTechSmart: Share Workflow",
        "category": "Workflow"
    }
]

# Add commands if they don't exist
existing_commands = {cmd['command'] for cmd in package['contributes']['commands']}
for cmd in workflow_commands:
    if cmd['command'] not in existing_commands:
        package['contributes']['commands'].append(cmd)
        print(f"Added command: {cmd['command']}")

# Write back
with open('itechsmart-ninja/vscode-extension/package.json', 'w') as f:
    json.dump(package, f, indent=2)

print(f"\nTotal commands: {len(package['contributes']['commands'])}")