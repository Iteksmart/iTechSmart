import os
import re

def fix_urls_in_file(filepath):
    """Fix URLs in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace itechsmart.dev with itechsmart.dev
        original_content = content
        content = content.replace('itechsmart.dev', 'itechsmart.dev')
        content = content.replace('itechsmart.dev', 'itechsmart.dev')
        
        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Fix URLs in all relevant files"""
    extensions = ['.py', '.md', '.txt', '.nsi', '.spec']
    fixed_count = 0
    
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', '.updates']):
            continue
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                if fix_urls_in_file(filepath):
                    fixed_count += 1
                    print(f"Fixed: {filepath}")
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
