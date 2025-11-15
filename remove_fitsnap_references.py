#!/usr/bin/env python3
"""
Remove all FitSnap AI references from documentation
"""

import os
import re
from pathlib import Path

def remove_fitsnap_references(file_path):
    """Remove FitSnap references from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove lines mentioning FitSnap
        lines = content.split('\n')
        filtered_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            # Skip lines with FitSnap references
            if re.search(r'fitsnap|FitSnap', line, re.IGNORECASE):
                # Check if it's a list item or bullet point
                if re.match(r'^\s*[-*•]\s+', line):
                    continue  # Skip this line
                elif re.match(r'^\s*\d+\.\s+', line):
                    continue  # Skip numbered list item
                else:
                    # For other lines, just skip
                    continue
            else:
                filtered_lines.append(line)
        
        content = '\n'.join(filtered_lines)
        
        # Update product counts
        content = re.sub(r'\b36\+?\s+products?', '35 products', content, flags=re.IGNORECASE)
        content = re.sub(r'\b36\s+products?', '35 products', content, flags=re.IGNORECASE)
        content = re.sub(r'All\s+36\s+products?', 'All 35 products', content, flags=re.IGNORECASE)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function"""
    workspace = Path('.')
    updated_files = []
    
    # Find all markdown files
    md_files = list(workspace.glob('*.md'))
    
    print(f"Found {len(md_files)} markdown files to process...")
    
    for md_file in md_files:
        if md_file.name == 'FITSNAP_REMOVAL_PLAN.md':
            continue  # Skip the removal plan itself
            
        if remove_fitsnap_references(md_file):
            updated_files.append(md_file.name)
            print(f"✓ Updated: {md_file.name}")
    
    print(f"\n✅ Updated {len(updated_files)} files")
    
    if updated_files:
        print("\nUpdated files:")
        for f in updated_files:
            print(f"  - {f}")

if __name__ == "__main__":
    main()