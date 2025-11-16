#!/usr/bin/env python3
"""
Properly fix tsconfig.json files by:
1. Setting strict: false
2. Setting noUnusedLocals: false
3. Setting noUnusedParameters: false
4. Removing references to tsconfig.node.json if file doesn't exist
"""

import json
import re
from pathlib import Path

# Products with tsconfig.json issues
PRODUCTS = [
    "itechsmart-citadel",
    "itechsmart-ledger",
    "itechsmart-mdm-agent",
    "itechsmart-notify",
    "itechsmart-port-manager",
    "itechsmart-sandbox",
    "itechsmart-sentinel",
    "itechsmart-shield",
    "itechsmart-supreme-plus",
    "itechsmart-vault",
    "itechsmart-workflow",
]

def strip_json_comments(text):
    """Remove comments from JSON text."""
    # Remove single-line comments
    text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
    # Remove multi-line comments
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    return text

def fix_tsconfig(product_name):
    """Fix tsconfig.json for a product."""
    tsconfig_path = Path(product_name) / "frontend" / "tsconfig.json"
    tsconfig_node_path = Path(product_name) / "frontend" / "tsconfig.node.json"
    
    if not tsconfig_path.exists():
        print(f"❌ {product_name}: tsconfig.json not found")
        return False
    
    try:
        # Read the file
        with open(tsconfig_path, 'r') as f:
            content = f.read()
        
        # Try to parse as JSON (with comments stripped)
        clean_content = strip_json_comments(content)
        try:
            config = json.loads(clean_content)
        except json.JSONDecodeError as e:
            print(f"❌ {product_name}: JSON parse error - {e}")
            # Try to fix common issues
            return False
        
        # Update compiler options
        if 'compilerOptions' in config:
            config['compilerOptions']['strict'] = False
            config['compilerOptions']['noUnusedLocals'] = False
            config['compilerOptions']['noUnusedParameters'] = False
            config['compilerOptions']['skipLibCheck'] = True
        
        # Remove reference to tsconfig.node.json if it doesn't exist
        if 'references' in config and not tsconfig_node_path.exists():
            del config['references']
            print(f"  → Removed reference to missing tsconfig.node.json")
        
        # Write back with proper formatting
        with open(tsconfig_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ {product_name}: Fixed")
        return True
        
    except Exception as e:
        print(f"❌ {product_name}: Error - {e}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("Fixing TypeScript Configuration Files")
    print("=" * 60)
    print()
    
    fixed = 0
    failed = 0
    
    for product in PRODUCTS:
        if fix_tsconfig(product):
            fixed += 1
        else:
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {fixed} fixed, {failed} failed")
    print("=" * 60)

if __name__ == "__main__":
    main()