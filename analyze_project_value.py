import os
import json
from pathlib import Path

def count_lines_of_code(directory):
    """Count lines of code in a directory"""
    extensions = {
        '.py': 'Python',
        '.ts': 'TypeScript',
        '.js': 'JavaScript',
        '.tsx': 'TypeScript React',
        '.jsx': 'JavaScript React',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.sql': 'SQL',
        '.sh': 'Shell',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.json': 'JSON',
        '.xml': 'XML',
        '.md': 'Markdown'
    }
    
    stats = {
        'total_lines': 0,
        'code_lines': 0,
        'comment_lines': 0,
        'blank_lines': 0,
        'files': 0,
        'by_language': {}
    }
    
    for root, dirs, files in os.walk(directory):
        # Skip common non-code directories
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build', '.next', 'coverage']]
        
        for file in files:
            ext = Path(file).suffix.lower()
            if ext in extensions:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        total = len(lines)
                        blank = sum(1 for line in lines if line.strip() == '')
                        comment = sum(1 for line in lines if line.strip().startswith(('#', '//', '/*', '*', '<!--')))
                        code = total - blank - comment
                        
                        stats['total_lines'] += total
                        stats['code_lines'] += code
                        stats['comment_lines'] += comment
                        stats['blank_lines'] += blank
                        stats['files'] += 1
                        
                        lang = extensions[ext]
                        if lang not in stats['by_language']:
                            stats['by_language'][lang] = {'files': 0, 'lines': 0}
                        stats['by_language'][lang]['files'] += 1
                        stats['by_language'][lang]['lines'] += code
                except Exception as e:
                    pass
    
    return stats

def count_features(directory):
    """Count implemented features"""
    features = 0
    feature_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if 'FEATURE' in file and 'COMPLETE' in file and file.endswith('.md'):
                features += 1
                feature_files.append(file)
    
    return features, feature_files

def count_api_endpoints(directory):
    """Count API endpoints"""
    endpoints = 0
    
    api_dirs = ['api', 'routes', 'controllers', 'endpoints']
    
    for root, dirs, files in os.walk(directory):
        if any(api_dir in root for api_dir in api_dirs):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # Count FastAPI decorators
                            endpoints += content.count('@router.get')
                            endpoints += content.count('@router.post')
                            endpoints += content.count('@router.put')
                            endpoints += content.count('@router.delete')
                            endpoints += content.count('@router.patch')
                            endpoints += content.count('@app.get')
                            endpoints += content.count('@app.post')
                            endpoints += content.count('@app.put')
                            endpoints += content.count('@app.delete')
                            endpoints += content.count('@app.patch')
                    except Exception as e:
                        pass
    
    return endpoints

def count_commands(directory):
    """Count VS Code commands and terminal commands"""
    vscode_commands = 0
    terminal_commands = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file == 'package.json':
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Count command registrations
                        vscode_commands += content.count('"command":')
                
                if 'terminal' in root.lower() or 'commands' in file.lower():
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Count terminal command definitions
                        terminal_commands += content.count('registerCommand')
                        terminal_commands += content.count('addCommand')
            except Exception as e:
                pass
    
    return vscode_commands, terminal_commands

def analyze_project(project_path, project_name):
    """Analyze a single project"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {project_name}")
    print(f"{'='*60}")
    
    if not os.path.exists(project_path):
        print(f"❌ Project not found: {project_path}")
        return None
    
    # Count lines of code
    stats = count_lines_of_code(project_path)
    
    # Count features
    features, feature_files = count_features(project_path)
    
    # Count API endpoints
    endpoints = count_api_endpoints(project_path)
    
    # Count commands
    vscode_cmds, terminal_cmds = count_commands(project_path)
    
    result = {
        'name': project_name,
        'path': project_path,
        'stats': stats,
        'features': features,
        'feature_files': feature_files,
        'api_endpoints': endpoints,
        'vscode_commands': vscode_cmds,
        'terminal_commands': terminal_cmds
    }
    
    print(f"\n📊 Code Statistics:")
    print(f"   Total Lines: {stats['total_lines']:,}")
    print(f"   Code Lines: {stats['code_lines']:,}")
    print(f"   Files: {stats['files']:,}")
    print(f"\n🎯 Features: {features}")
    print(f"🔌 API Endpoints: {endpoints}")
    print(f"⌨️  VS Code Commands: {vscode_cmds}")
    print(f"💻 Terminal Commands: {terminal_cmds}")
    
    if stats['by_language']:
        print(f"\n📝 Languages:")
        for lang, data in sorted(stats['by_language'].items(), key=lambda x: x[1]['lines'], reverse=True)[:5]:
            print(f"   {lang}: {data['lines']:,} lines ({data['files']} files)")
    
    return result

def calculate_market_value(project_data):
    """Calculate market value based on industry standards"""
    
    # Industry standard rates (conservative estimates)
    rates = {
        'per_line_of_code': 10,  # $10 per line of production code
        'per_feature': 5000,  # $5,000 per complete feature
        'per_api_endpoint': 500,  # $500 per API endpoint
        'per_command': 200,  # $200 per command
        'base_architecture': 10000,  # $10,000 for base architecture
        'documentation': 5000,  # $5,000 for documentation
        'testing': 3000  # $3,000 for testing infrastructure
    }
    
    # Calculate component values
    code_value = project_data['stats']['code_lines'] * rates['per_line_of_code']
    feature_value = project_data['features'] * rates['per_feature']
    api_value = project_data['api_endpoints'] * rates['per_api_endpoint']
    command_value = (project_data['vscode_commands'] + project_data['terminal_commands']) * rates['per_command']
    
    # Base components
    base_value = rates['base_architecture'] + rates['documentation'] + rates['testing']
    
    # Total value
    total_value = code_value + feature_value + api_value + command_value + base_value
    
    # Apply multipliers for complexity and integration
    if project_data['features'] > 10:
        total_value *= 1.2  # 20% premium for comprehensive feature set
    
    if project_data['api_endpoints'] > 50:
        total_value *= 1.15  # 15% premium for extensive API
    
    return {
        'code_value': code_value,
        'feature_value': feature_value,
        'api_value': api_value,
        'command_value': command_value,
        'base_value': base_value,
        'total_value': total_value,
        'breakdown': {
            'Code Development': f"${code_value:,.2f}",
            'Feature Implementation': f"${feature_value:,.2f}",
            'API Development': f"${api_value:,.2f}",
            'Command Integration': f"${command_value:,.2f}",
            'Base Infrastructure': f"${base_value:,.2f}",
            'Total Market Value': f"${total_value:,.2f}"
        }
    }

# Main execution
projects = [
    ('/workspace/itechsmart-ninja', 'iTechSmart Ninja'),
    ('/workspace/itechsmart_supreme', 'iTechSmart Supreme'),
    ('/workspace/itechsmart-enterprise', 'iTechSmart Enterprise')
]

all_results = []
total_portfolio_value = 0

print("\n" + "="*80)
print("💰 ITECHSMART PROJECT PORTFOLIO VALUATION")
print("="*80)

for project_path, project_name in projects:
    result = analyze_project(project_path, project_name)
    if result:
        value_analysis = calculate_market_value(result)
        result['value_analysis'] = value_analysis
        all_results.append(result)
        total_portfolio_value += value_analysis['total_value']
        
        print(f"\n💵 Market Value Breakdown:")
        for component, value in value_analysis['breakdown'].items():
            print(f"   {component}: {value}")

print("\n" + "="*80)
print("📈 PORTFOLIO SUMMARY")
print("="*80)

total_lines = sum(r['stats']['code_lines'] for r in all_results)
total_features = sum(r['features'] for r in all_results)
total_endpoints = sum(r['api_endpoints'] for r in all_results)
total_commands = sum(r['vscode_commands'] + r['terminal_commands'] for r in all_results)

print(f"\n📊 Combined Statistics:")
print(f"   Total Code Lines: {total_lines:,}")
print(f"   Total Features: {total_features}")
print(f"   Total API Endpoints: {total_endpoints}")
print(f"   Total Commands: {total_commands}")
print(f"   Total Projects: {len(all_results)}")

print(f"\n💰 TOTAL PORTFOLIO VALUE: ${total_portfolio_value:,.2f}")

# Save detailed report
report = {
    'projects': all_results,
    'portfolio_summary': {
        'total_lines': total_lines,
        'total_features': total_features,
        'total_endpoints': total_endpoints,
        'total_commands': total_commands,
        'total_value': total_portfolio_value
    }
}

with open('portfolio_valuation_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n✅ Detailed report saved to: portfolio_valuation_report.json")