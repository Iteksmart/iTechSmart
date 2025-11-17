import json

# Read package.json
with open("itechsmart-ninja/vscode-extension/package.json", "r") as f:
    package = json.load(f)

# New visualization commands
viz_commands = [
    {"command": "itechsmart.createChart", "title": "iTechSmart: Create Chart"},
    {"command": "itechsmart.createDashboard", "title": "iTechSmart: Create Dashboard"},
    {"command": "itechsmart.listCharts", "title": "iTechSmart: List Charts"},
    {"command": "itechsmart.viewChart", "title": "iTechSmart: View Chart"},
    {"command": "itechsmart.exportChart", "title": "iTechSmart: Export Chart"},
    {"command": "itechsmart.analyzeData", "title": "iTechSmart: Analyze Data"},
    {"command": "itechsmart.getChartTypes", "title": "iTechSmart: Get Chart Types"},
]

# Add commands if they don't exist
existing_commands = [cmd["command"] for cmd in package["contributes"]["commands"]]
for cmd in viz_commands:
    if cmd["command"] not in existing_commands:
        package["contributes"]["commands"].append(cmd)
        print(f"Added: {cmd['command']}")

# Write back
with open("itechsmart-ninja/vscode-extension/package.json", "w") as f:
    json.dump(package, f, indent=2)

print("✓ Visualization commands added to package.json")
