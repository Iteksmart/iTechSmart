import json

# Read package.json
with open('itechsmart-ninja/vscode-extension/package.json', 'r') as f:
    package = json.load(f)

# New document commands
doc_commands = [
    {
        "command": "itechsmart.uploadDocument",
        "title": "iTechSmart: Upload Document"
    },
    {
        "command": "itechsmart.listDocuments",
        "title": "iTechSmart: List Documents"
    },
    {
        "command": "itechsmart.extractText",
        "title": "iTechSmart: Extract Text from Document"
    },
    {
        "command": "itechsmart.extractTables",
        "title": "iTechSmart: Extract Tables from Document"
    },
    {
        "command": "itechsmart.extractImages",
        "title": "iTechSmart: Extract Images from Document"
    },
    {
        "command": "itechsmart.extractMetadata",
        "title": "iTechSmart: Extract Document Metadata"
    },
    {
        "command": "itechsmart.ocrDocument",
        "title": "iTechSmart: OCR Document"
    },
    {
        "command": "itechsmart.convertDocument",
        "title": "iTechSmart: Convert Document Format"
    },
    {
        "command": "itechsmart.searchDocuments",
        "title": "iTechSmart: Search in Documents"
    },
    {
        "command": "itechsmart.devpareDocuments",
        "title": "iTechSmart: Compare Documents"
    }
]

# Add commands if they don't exist
existing_commands = [cmd['command'] for cmd in package['contributes']['commands']]
for cmd in doc_commands:
    if cmd['command'] not in existing_commands:
        package['contributes']['commands'].append(cmd)
        print(f"Added: {cmd['command']}")

# Write back
with open('itechsmart-ninja/vscode-extension/package.json', 'w') as f:
    json.dump(package, f, indent=2)

print("✓ Document commands added to package.json")