# Read the terminal panel file
with open('itechsmart-ninja/vscode-extension/src/terminal/panel.ts', 'r') as f:
    content = f.read()

# Find the position to insert visualization commands (before img-generate)
insert_marker = "                    case 'img-generate':"

# New visualization command cases
viz_cases = """                    case 'chart':
                    case 'create-chart':
                        await this.createChart(args);
                        break;
                    case 'dashboard':
                    case 'create-dashboard':
                        await this.createDashboard(args);
                        break;
                    case 'list-charts':
                        await this.listCharts();
                        break;
                    case 'export-chart':
                        await this.exportChart(args);
                        break;
                    case 'analyze':
                    case 'analyze-data':
                        await this.analyzeDataFile(args);
                        break;
"""

# Insert the cases
if insert_marker in content:
    content = content.replace(insert_marker, viz_cases + insert_marker)
    print("✓ Added visualization command cases")
else:
    print("✗ Could not find insertion point")

# Write back
with open('itechsmart-ninja/vscode-extension/src/terminal/panel.ts', 'w') as f:
    f.write(content)

print("✓ Terminal visualization commands added")