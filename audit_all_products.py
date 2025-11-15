#!/usr/bin/env python3
"""
iTechSmart Suite - Comprehensive Product Audit Script
Checks all 32 products for completeness
"""

import os
import json
from pathlib import Path

# Product definitions
PRODUCTS = [
    # Foundation Products (9)
    {"name": "iTechSmart Enterprise", "dir": "itechsmart-enterprise", "port": 8001},
    {"name": "iTechSmart Ninja", "dir": "itechsmart-ninja", "port": 8002},
    {"name": "iTechSmart Analytics", "dir": "itechsmart-analytics", "port": 8003},
    {"name": "iTechSmart Supreme", "dir": "itechsmart_supreme", "port": 8004},
    {"name": "iTechSmart HL7", "dir": "itechsmart-hl7", "port": 8005},
    {"name": "ProofLink.AI", "dir": "prooflink", "port": 8006},
    {"name": "PassPort", "dir": "passport", "port": 8007},
    {"name": "ImpactOS", "dir": "itechsmart-impactos", "port": 8008},
    {"name": "LegalAI Pro", "dir": "legalai-pro", "port": 8009},
    
    # Strategic Products (10)
    {"name": "iTechSmart DataFlow", "dir": "itechsmart-dataflow", "port": 8010},
    {"name": "iTechSmart Pulse", "dir": "itechsmart-pulse", "port": 8011},
    {"name": "iTechSmart Connect", "dir": "itechsmart-connect", "port": 8012},
    {"name": "iTechSmart Vault", "dir": "itechsmart-vault", "port": 8013},
    {"name": "iTechSmart Notify", "dir": "itechsmart-notify", "port": 8014},
    {"name": "iTechSmart Ledger", "dir": "itechsmart-ledger", "port": 8015},
    {"name": "iTechSmart Copilot", "dir": "itechsmart-copilot", "port": 8016},
    {"name": "iTechSmart Shield", "dir": "itechsmart-shield", "port": 8017},
    {"name": "iTechSmart Workflow", "dir": "itechsmart-workflow", "port": 8018},
    {"name": "iTechSmart Marketplace", "dir": "itechsmart-marketplace", "port": 8019},
    
    # Business Products (7)
    {"name": "iTechSmart Cloud", "dir": "itechsmart-cloud", "port": 8020},
    {"name": "iTechSmart DevOps", "dir": "itechsmart-devops", "port": 8021},
    {"name": "iTechSmart Mobile", "dir": "itechsmart-mobile", "port": 8022},
    {"name": "iTechSmart Inc.", "dir": "itechsmart-ai", "port": 8023},
    {"name": "iTechSmart Compliance", "dir": "itechsmart-compliance", "port": 8024},
    {"name": "iTechSmart Data Platform", "dir": "itechsmart-data-platform", "port": 8025},
    {"name": "iTechSmart Customer Success", "dir": "itechsmart-customer-success", "port": 8026},
    
    # Infrastructure Products (3)
    {"name": "iTechSmart Port Manager", "dir": "itechsmart-port-manager", "port": 8100},
    {"name": "iTechSmart MDM Agent", "dir": "itechsmart-mdm-agent", "port": 8200},
    {"name": "iTechSmart QA/QC", "dir": "itechsmart-qaqc", "port": 8300},
    
    # Internal Products (1)
    {"name": "iTechSmart Think-Tank", "dir": "itechsmart-thinktank", "port": 8030},
    
    # Latest Products (2)
    {"name": "iTechSmart Sentinel", "dir": "itechsmart-sentinel", "port": 8031},
    {"name": "iTechSmart Forge", "dir": "itechsmart-forge", "port": 8032},
]

def check_file_exists(base_path, file_path):
    """Check if a file exists"""
    full_path = base_path / file_path
    return full_path.exists()

def check_directory_exists(base_path, dir_path):
    """Check if a directory exists"""
    full_path = base_path / dir_path
    return full_path.exists() and full_path.is_dir()

def audit_product(product):
    """Audit a single product"""
    base_path = Path("/workspace") / product["dir"]
    
    if not base_path.exists():
        return {
            "name": product["name"],
            "status": "MISSING",
            "exists": False,
            "components": {}
        }
    
    # Check components
    components = {
        # Backend
        "backend_dir": check_directory_exists(base_path, "backend"),
        "backend_main": check_file_exists(base_path, "backend/main.py"),
        "backend_models": check_file_exists(base_path, "backend/app/models"),
        "backend_api": check_directory_exists(base_path, "backend/app/api"),
        "backend_core": check_directory_exists(base_path, "backend/app/core"),
        
        # Frontend
        "frontend_dir": check_directory_exists(base_path, "frontend"),
        "frontend_src": check_directory_exists(base_path, "frontend/src"),
        "frontend_app": check_file_exists(base_path, "frontend/src/App.tsx"),
        "frontend_package": check_file_exists(base_path, "frontend/package.json"),
        
        # Docker
        "docker_compose": check_file_exists(base_path, "docker-compose.yml"),
        "dockerfile_backend": check_file_exists(base_path, "backend/Dockerfile"),
        "dockerfile_frontend": check_file_exists(base_path, "frontend/Dockerfile"),
        
        # Integration
        "integration_module": check_file_exists(base_path, "backend/app/integrations/integration.py"),
        
        # Documentation
        "readme": check_file_exists(base_path, "README.md"),
        "docs_dir": check_directory_exists(base_path, "docs"),
    }
    
    # Calculate completeness
    total = len(components)
    complete = sum(1 for v in components.values() if v)
    percentage = (complete / total) * 100
    
    # Determine status
    if percentage == 100:
        status = "COMPLETE"
    elif percentage >= 75:
        status = "MOSTLY_COMPLETE"
    elif percentage >= 50:
        status = "PARTIAL"
    elif percentage >= 25:
        status = "MINIMAL"
    else:
        status = "INCOMPLETE"
    
    return {
        "name": product["name"],
        "dir": product["dir"],
        "port": product["port"],
        "status": status,
        "exists": True,
        "completeness": f"{percentage:.1f}%",
        "components": components,
        "missing": [k for k, v in components.items() if not v]
    }

def main():
    """Run audit on all products"""
    print("=" * 80)
    print("iTechSmart Suite - Comprehensive Product Audit")
    print("=" * 80)
    print()
    
    results = []
    
    for i, product in enumerate(PRODUCTS, 1):
        print(f"[{i}/32] Auditing {product['name']}...", end=" ")
        result = audit_product(product)
        results.append(result)
        print(f"{result['status']} ({result.get('completeness', 'N/A')})")
    
    print()
    print("=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    
    # Count by status
    status_counts = {}
    for result in results:
        status = result["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\nTotal Products: {len(results)}")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    
    # Products needing work
    print("\n" + "=" * 80)
    print("PRODUCTS NEEDING ATTENTION")
    print("=" * 80)
    
    needs_work = [r for r in results if r["status"] not in ["COMPLETE", "MOSTLY_COMPLETE"]]
    
    if needs_work:
        for result in needs_work:
            print(f"\n{result['name']} ({result['status']} - {result.get('completeness', 'N/A')})")
            if result.get("missing"):
                print("  Missing components:")
                for component in result["missing"]:
                    print(f"    - {component}")
    else:
        print("\n✅ All products are complete or mostly complete!")
    
    # Save detailed results
    output_file = "/workspace/AUDIT_RESULTS.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\n📄 Detailed results saved to: {output_file}")
    print()

if __name__ == "__main__":
    main()
