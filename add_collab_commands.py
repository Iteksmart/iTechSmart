import json

# Read package.json
with open("itechsmart-ninja/vscode-extension/package.json", "r") as f:
    package = json.load(f)

# Collaboration commands to add
collab_commands = [
    {
        "command": "itechsmart.createTeam",
        "title": "iTechSmart: Create Team",
        "category": "Collaboration",
    },
    {
        "command": "itechsmart.inviteTeamMember",
        "title": "iTechSmart: Invite Team Member",
        "category": "Collaboration",
    },
    {
        "command": "itechsmart.switchWorkspace",
        "title": "iTechSmart: Switch Workspace",
        "category": "Collaboration",
    },
    {
        "command": "itechsmart.addComment",
        "title": "iTechSmart: Add Comment",
        "category": "Collaboration",
    },
    {
        "command": "itechsmart.viewTeamActivity",
        "title": "iTechSmart: View Team Activity",
        "category": "Collaboration",
    },
    {
        "command": "itechsmart.managePermissions",
        "title": "iTechSmart: Manage Permissions",
        "category": "Collaboration",
    },
    {
        "command": "itechsmart.listTeams",
        "title": "iTechSmart: List Teams",
        "category": "Collaboration",
    },
    {
        "command": "itechsmart.createWorkspace",
        "title": "iTechSmart: Create Workspace",
        "category": "Collaboration",
    },
]

# Add commands if they don't exist
existing_commands = {cmd["command"] for cmd in package["contributes"]["commands"]}
added = 0
for cmd in collab_commands:
    if cmd["command"] not in existing_commands:
        package["contributes"]["commands"].append(cmd)
        added += 1
        print(f"Added command: {cmd['command']}")

# Write back
with open("itechsmart-ninja/vscode-extension/package.json", "w") as f:
    json.dump(package, f, indent=2)

print(f"\nAdded {added} commands")
print(f"Total commands: {len(package['contributes']['commands'])}")
