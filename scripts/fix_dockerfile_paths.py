#!/usr/bin/env python3
"""
Fix Dockerfile paths after moving them from subdirectories to product root.
"""

import os
import sys
from pathlib import Path

def fix_backend_dockerfile(dockerfile_path: Path):
    """Fix backend Dockerfile to use correct paths."""
    content = dockerfile_path.read_text()
    
    # Update COPY commands to include backend/ prefix
    content = content.replace(
        "COPY requirements.txt .",
        "COPY backend/requirements.txt ."
    )
    content = content.replace(
        "COPY . .",
        "COPY backend/ ."
    )
    
    dockerfile_path.write_text(content)
    print(f"  ✅ Fixed {dockerfile_path}")


def fix_frontend_dockerfile(dockerfile_path: Path, framework: str):
    """Fix frontend Dockerfile to use correct paths."""
    content = dockerfile_path.read_text()
    
    # Update COPY commands to include frontend/ prefix
    if "COPY package*.json ./" in content:
        content = content.replace(
            "COPY package*.json ./",
            "COPY frontend/package*.json ./"
        )
    
    if framework in ["vite", "cra"]:
        # For Vite and CRA
        content = content.replace(
            "COPY . .",
            "COPY frontend/ ."
        )
        content = content.replace(
            "COPY nginx.conf /etc/nginx/conf.d/default.conf",
            "COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf"
        )
    elif framework == "nextjs":
        # For Next.js - need to copy specific files
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.strip().startswith("COPY . ."):
                new_lines.append("COPY frontend/ .")
            elif "COPY --from=builder /app/.next" in line:
                # Keep as is - already correct
                new_lines.append(line)
            elif "COPY --from=builder /app/public" in line:
                # Keep as is - already correct
                new_lines.append(line)
            elif "COPY --from=builder /app/next.config" in line:
                # Keep as is - already correct
                new_lines.append(line)
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
    
    dockerfile_path.write_text(content)
    print(f"  ✅ Fixed {dockerfile_path}")


def main():
    """Main function."""
    repo_root = Path(__file__).parent.parent
    
    print("🔧 Fixing Dockerfile paths...\n")
    
    # Framework mapping
    vite_products = [
        "itechsmart-ai", "itechsmart-citadel", "itechsmart-connect",
        "itechsmart-copilot", "itechsmart-dataflow", "itechsmart-forge",
        "itechsmart-ledger", "itechsmart-marketplace", "itechsmart-mdm-agent",
        "itechsmart-notify", "itechsmart-qaqc", "itechsmart-sandbox",
        "itechsmart-supreme-plus", "itechsmart-thinktank", "itechsmart-vault",
        "itechsmart-workflow", "legalai-pro"
    ]
    
    cra_products = [
        "itechsmart-analytics", "itechsmart-cloud", "itechsmart-compliance",
        "itechsmart-customer-success", "itechsmart-data-platform",
        "itechsmart-devops", "itechsmart-mobile", "itechsmart-observatory",
        "itechsmart-port-manager", "itechsmart-pulse", "itechsmart-shield"
    ]
    
    nextjs_products = [
        "itechsmart-enterprise", "itechsmart-hl7", "itechsmart-impactos",
        "itechsmart-ninja", "passport", "prooflink"
    ]
    
    # Fix all products
    all_products = vite_products + cra_products + nextjs_products
    
    for product in all_products:
        product_path = repo_root / product
        if not product_path.exists():
            continue
        
        print(f"{product}:")
        
        # Fix backend Dockerfile
        backend_dockerfile = product_path / "Dockerfile.backend"
        if backend_dockerfile.exists():
            fix_backend_dockerfile(backend_dockerfile)
        
        # Fix frontend Dockerfile
        frontend_dockerfile = product_path / "Dockerfile.frontend"
        if frontend_dockerfile.exists():
            if product in vite_products:
                fix_frontend_dockerfile(frontend_dockerfile, "vite")
            elif product in cra_products:
                fix_frontend_dockerfile(frontend_dockerfile, "cra")
            elif product in nextjs_products:
                fix_frontend_dockerfile(frontend_dockerfile, "nextjs")
    
    print("\n✅ All Dockerfile paths fixed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())