# Read the terminal panel file
with open("itechsmart-ninja/vscode-extension/src/terminal/panel.ts", "r") as f:
    content = f.read()

# Find the position to insert document commands (before chart commands)
insert_marker = "                    case 'chart':"

# New document command cases
doc_cases = """                    case 'doc':
                    case 'document':
                        await this.showDocumentHelp();
                        break;
                    case 'doc-upload':
                    case 'upload-document':
                        await this.uploadDocument(args);
                        break;
                    case 'doc-list':
                    case 'list-documents':
                        await this.listDocuments();
                        break;
                    case 'doc-extract':
                    case 'extract-text':
                        await this.extractDocumentText(args);
                        break;
                    case 'doc-tables':
                    case 'extract-tables':
                        await this.extractDocumentTables(args);
                        break;
                    case 'doc-ocr':
                    case 'ocr-document':
                        await this.ocrDocument(args);
                        break;
                    case 'doc-search':
                    case 'search-document':
                        await this.searchDocument(args);
                        break;
"""

# Insert the cases
if insert_marker in content:
    content = content.replace(insert_marker, doc_cases + insert_marker)
    print("✓ Added document command cases")
else:
    print("✗ Could not find insertion point")

# Write back
with open("itechsmart-ninja/vscode-extension/src/terminal/panel.ts", "w") as f:
    f.write(content)

print("✓ Terminal document commands added")
