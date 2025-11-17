#!/usr/bin/env python3
"""
iTechSmart Suite - Automated Documentation Generator
Generates comprehensive documentation for all products
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

# Product list
PRODUCTS = [
    "itechsmart-ai",
    "itechsmart-analytics",
    "itechsmart-citadel",
    "itechsmart-cloud",
    "itechsmart-compliance",
    "itechsmart-connect",
    "itechsmart-copilot",
    "itechsmart-customer-success",
    "itechsmart-data-platform",
    "itechsmart-dataflow",
    "itechsmart-devops",
    "itechsmart-enterprise",
    "itechsmart-forge",
    "itechsmart-hl7",
    "itechsmart-impactos",
    "itechsmart-ledger",
    "itechsmart-marketplace",
    "itechsmart-mdm-agent",
    "itechsmart-mobile",
    "itechsmart-notify",
    "itechsmart-observatory",
    "itechsmart-port-manager",
    "itechsmart-pulse",
    "itechsmart-qaqc",
    "itechsmart-sandbox",
    "itechsmart-sentinel",
    "itechsmart-shield",
    "itechsmart-supreme-plus",
    "itechsmart-thinktank",
    "itechsmart-vault",
    "itechsmart-workflow",
    "itechsmart_supreme",
    "passport",
    "prooflink",
    "legalai-pro",
    "license-server",
    "desktop-launcher"
]

def extract_info_from_readme(readme_path):
    """Extract key information from README file"""
    if not os.path.exists(readme_path):
        return None
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    info = {
        'description': '',
        'features': [],
        'tech_stack': [],
        'ports': [],
        'env_vars': []
    }
    
    # Extract description (first paragraph after title)
    desc_match = re.search(r'#[^\n]+\n\n([^\n]+)', content)
    if desc_match:
        info['description'] = desc_match.group(1).strip()
    
    # Extract features
    features_section = re.search(r'## Features(.*?)(?=##|\Z)', content, re.DOTALL)
    if features_section:
        features = re.findall(r'[-*]\s+\*\*([^*]+)\*\*', features_section.group(1))
        info['features'] = features[:10]  # Limit to 10 features
    
    # Extract ports
    ports = re.findall(r':(\d{4,5})', content)
    info['ports'] = list(set(ports))[:3]  # Unique ports, limit to 3
    
    # Extract tech stack
    tech_keywords = ['Python', 'Node.js', 'React', 'FastAPI', 'PostgreSQL', 'Redis', 'Docker']
    for tech in tech_keywords:
        if tech in content:
            info['tech_stack'].append(tech)
    
    return info

def generate_user_guide(product_name, product_dir, info):
    """Generate USER_GUIDE.md for a product"""
    
    # Read template
    with open('templates/USER_GUIDE_TEMPLATE.md', 'r') as f:
        template = f.read()
    
    # Format product name
    display_name = product_name.replace('-', ' ').replace('_', ' ').title()
    
    # Determine product type
    if 'security' in product_name.lower() or 'shield' in product_name.lower() or 'sentinel' in product_name.lower():
        product_type = 'Security Platform'
    elif 'data' in product_name.lower() or 'analytics' in product_name.lower():
        product_type = 'Data Platform'
    elif 'dev' in product_name.lower() or 'forge' in product_name.lower():
        product_type = 'Development Platform'
    else:
        product_type = 'Enterprise Platform'
    
    # Build features list
    features_text = ""
    if info and info['features']:
        for i, feature in enumerate(info['features'], 1):
            features_text += f"### {i}. {feature}\n\n"
            features_text += f"**Description**: {feature} functionality\n\n"
            features_text += "**How to Use**:\n```bash\n# Example usage\n```\n\n"
    else:
        features_text = "### Core Functionality\n\nSee README.md for detailed feature list.\n\n"
    
    # Build env variables
    env_vars = """# Core Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0

# Application
NODE_ENV=production
PORT=8000
SECRET_KEY=your-secret-key

# API Keys (if needed)
API_KEY=your-api-key
"""
    
    # Default URL
    default_port = info['ports'][0] if info and info['ports'] else '8000'
    default_url = f"http://localhost:{default_port}"
    
    # Replace placeholders
    content = template.replace('{PRODUCT_NAME}', display_name)
    content = content.replace('{PRODUCT_TYPE}', product_type)
    content = content.replace('{PRODUCT_DESCRIPTION}', info['description'] if info else f"{display_name} is an enterprise-grade platform.")
    content = content.replace('{KEY_BENEFITS}', "- Scalable\n- Secure\n- Easy to use\n- Production-ready")
    content = content.replace('{PRODUCT_DIR}', product_dir)
    content = content.replace('{DEFAULT_URL}', default_url)
    content = content.replace('{FIRST_LOGIN_INSTRUCTIONS}', "1. Navigate to the application URL\n2. Use default credentials or create an account\n3. Complete initial setup")
    content = content.replace('{FEATURES_LIST}', features_text)
    content = content.replace('{ENV_VARIABLES}', env_vars)
    content = content.replace('{DOCKER_CONFIG}', "See docker-compose.yml for configuration")
    content = content.replace('{EXAMPLE_1_TITLE}', "Basic Usage")
    content = content.replace('{EXAMPLE_1_CODE}', "# See README.md for examples")
    content = content.replace('{EXAMPLE_2_TITLE}', "Advanced Usage")
    content = content.replace('{EXAMPLE_2_CODE}', "# See README.md for examples")
    content = content.replace('{API_ENDPOINTS}', "See API_DOCUMENTATION.md for complete API reference")
    
    return content

def generate_api_docs(product_name, product_dir, info):
    """Generate API_DOCUMENTATION.md for a product"""
    
    with open('templates/API_DOCUMENTATION_TEMPLATE.md', 'r') as f:
        template = f.read()
    
    display_name = product_name.replace('-', ' ').replace('_', ' ').title()
    default_port = info['ports'][0] if info and info['ports'] else '8000'
    base_url = f"http://localhost:{default_port}"
    
    content = template.replace('{PRODUCT_NAME}', display_name)
    content = content.replace('{BASE_URL}', base_url)
    content = content.replace('{ENDPOINT_CATEGORY_1}', "Resources")
    content = content.replace('{ENDPOINT_1_NAME}', "List Resources")
    content = content.replace('{METHOD}', "GET")
    content = content.replace('{ENDPOINT_1_PATH}', "/api/resources")
    content = content.replace('{ProductClient}', product_name.replace('-', '_').title() + 'Client')
    content = content.replace('{product}', product_name)
    
    return content

def generate_deployment_guide(product_name, product_dir, info):
    """Generate DEPLOYMENT_GUIDE.md for a product"""
    
    with open('templates/DEPLOYMENT_GUIDE_TEMPLATE.md', 'r') as f:
        template = f.read()
    
    display_name = product_name.replace('-', ' ').replace('_', ' ').title()
    default_port = info['ports'][0] if info and info['ports'] else '8000'
    
    # Determine dependencies and runtime
    if info and 'Python' in info['tech_stack']:
        dependencies = "python3 python3-pip postgresql-client"
        runtime_install = "pip install -r requirements.txt"
        install_deps = "pip install -r requirements.txt"
        build_commands = "# No build needed for Python"
        start_command = f"/usr/bin/python3 /opt/{product_name}/main.py"
    elif info and 'Node.js' in info['tech_stack']:
        dependencies = "nodejs npm postgresql-client"
        runtime_install = "npm install"
        install_deps = "npm install"
        build_commands = "npm run build"
        start_command = f"/usr/bin/node /opt/{product_name}/dist/index.js"
    else:
        dependencies = "build-essential"
        runtime_install = "# Install runtime"
        install_deps = "# Install dependencies"
        build_commands = "# Build application"
        start_command = f"/opt/{product_name}/start.sh"
    
    content = template.replace('{PRODUCT_NAME}', display_name)
    content = content.replace('{PRODUCT_DIR}', product_dir)
    content = content.replace('{PORT}', default_port)
    content = content.replace('{SERVICE_NAME}', product_name)
    content = content.replace('{PRODUCT_NAMESPACE}', product_name)
    content = content.replace('{PRODUCT_DOMAIN}', f"{product_name}.itechsmart.com")
    content = content.replace('{DEPENDENCIES}', dependencies)
    content = content.replace('{RUNTIME_INSTALL_COMMANDS}', runtime_install)
    content = content.replace('{INSTALL_DEPENDENCIES}', install_deps)
    content = content.replace('{BUILD_COMMANDS}', build_commands)
    content = content.replace('{SERVICE_USER}', product_name)
    content = content.replace('{START_COMMAND}', start_command)
    content = content.replace('{API_KEYS}', "# Add API keys if needed")
    content = content.replace('{POSTGRES_CONTAINER}', f"{product_name}-postgres")
    content = content.replace('{DB_USER}', "postgres")
    content = content.replace('{DB_NAME}', product_name.replace('-', '_'))
    content = content.replace('{NETWORK_NAME}', f"{product_name}-network")
    
    return content

def main():
    """Main function to generate all documentation"""
    print("=" * 60)
    print("iTechSmart Suite - Documentation Generator")
    print("=" * 60)
    print()
    
    total = len(PRODUCTS)
    completed = 0
    
    for product in PRODUCTS:
        print(f"Processing: {product}")
        
        # Check if product directory exists
        if not os.path.exists(product):
            print(f"  ⚠️  Directory not found, skipping...")
            continue
        
        # Create docs directory
        docs_dir = os.path.join(product, 'docs')
        os.makedirs(docs_dir, exist_ok=True)
        
        # Extract info from README
        readme_path = os.path.join(product, 'README.md')
        info = extract_info_from_readme(readme_path)
        
        # Generate USER_GUIDE.md
        user_guide_path = os.path.join(docs_dir, 'USER_GUIDE.md')
        if not os.path.exists(user_guide_path):
            user_guide = generate_user_guide(product, product, info)
            with open(user_guide_path, 'w', encoding='utf-8') as f:
                f.write(user_guide)
            print(f"  ✅ Created USER_GUIDE.md")
        else:
            print(f"  ⏭️  USER_GUIDE.md already exists")
        
        # Generate API_DOCUMENTATION.md
        api_docs_path = os.path.join(docs_dir, 'API_DOCUMENTATION.md')
        if not os.path.exists(api_docs_path):
            api_docs = generate_api_docs(product, product, info)
            with open(api_docs_path, 'w', encoding='utf-8') as f:
                f.write(api_docs)
            print(f"  ✅ Created API_DOCUMENTATION.md")
        else:
            print(f"  ⏭️  API_DOCUMENTATION.md already exists")
        
        # Generate DEPLOYMENT_GUIDE.md
        deployment_path = os.path.join(docs_dir, 'DEPLOYMENT_GUIDE.md')
        if not os.path.exists(deployment_path):
            deployment = generate_deployment_guide(product, product, info)
            with open(deployment_path, 'w', encoding='utf-8') as f:
                f.write(deployment)
            print(f"  ✅ Created DEPLOYMENT_GUIDE.md")
        else:
            print(f"  ⏭️  DEPLOYMENT_GUIDE.md already exists")
        
        completed += 1
        print()
    
    print("=" * 60)
    print(f"✅ Documentation Generation Complete!")
    print("=" * 60)
    print()
    print(f"Processed: {completed} / {total} products")
    print()
    print("Generated files:")
    print("  - USER_GUIDE.md (for each product)")
    print("  - API_DOCUMENTATION.md (for each product)")
    print("  - DEPLOYMENT_GUIDE.md (for each product)")
    print()
    print("Next steps:")
    print("  1. Review generated documentation")
    print("  2. Customize as needed")
    print("  3. Commit and push to GitHub")
    print()

if __name__ == '__main__':
    main()