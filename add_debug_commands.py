import json

# Read package.json
with open("itechsmart-ninja/vscode-extension/package.json", "r") as f:
    package = json.load(f)

# Debug commands to add
debug_commands = [
    {
        "command": "itechsmart.analyzeError",
        "title": "iTechSmart: Analyze Error",
        "category": "Debug",
    },
    {
        "command": "itechsmart.setSmartBreakpoint",
        "title": "iTechSmart: Set Smart Breakpoint",
        "category": "Debug",
    },
    {
        "command": "itechsmart.listBreakpoints",
        "title": "iTechSmart: List Breakpoints",
        "category": "Debug",
    },
    {
        "command": "itechsmart.inspectVariable",
        "title": "iTechSmart: Inspect Variable",
        "category": "Debug",
    },
    {
        "command": "itechsmart.profileCode",
        "title": "iTechSmart: Profile Code",
        "category": "Debug",
    },
    {
        "command": "itechsmart.detectMemoryLeaks",
        "title": "iTechSmart: Detect Memory Leaks",
        "category": "Debug",
    },
    {
        "command": "itechsmart.viewCallStack",
        "title": "iTechSmart: View Call Stack",
        "category": "Debug",
    },
    {
        "command": "itechsmart.getCodeCoverage",
        "title": "iTechSmart: Get Code Coverage",
        "category": "Debug",
    },
]

# Add commands if they don't exist
existing_commands = {cmd["command"] for cmd in package["contributes"]["commands"]}
for cmd in debug_commands:
    if cmd["command"] not in existing_commands:
        package["contributes"]["commands"].append(cmd)
        print(f"Added command: {cmd['command']}")

# Write back
with open("itechsmart-ninja/vscode-extension/package.json", "w") as f:
    json.dump(package, f, indent=2)

print(f"\nTotal commands: {len(package['contributes']['commands'])}")
