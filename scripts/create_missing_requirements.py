#!/usr/bin/env python3
"""
Create missing requirements.txt files for products that don't have them.
"""

import os
import sys
from pathlib import Path

# Standard FastAPI backend requirements
STANDARD_REQUIREMENTS = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
redis==5.0.1
httpx==0.25.2
"""

PRODUCTS_MISSING_REQUIREMENTS = [
    "itechsmart-ai",
    "itechsmart-cloud",
    "itechsmart-compliance",
    "itechsmart-customer-success",
    "itechsmart-data-platform",
    "itechsmart-devops",
    "itechsmart-mobile",
    "itechsmart-sandbox",
    "itechsmart-thinktank",
]


def create_requirements_file(product_path: Path):
    """Create requirements.txt file for a product."""
    requirements_path = product_path / "backend" / "requirements.txt"
    
    if requirements_path.exists():
        print(f"  ⚠️  requirements.txt already exists for {product_path.name}")
        return False
    
    requirements_path.write_text(STANDARD_REQUIREMENTS.strip() + "\n")
    print(f"  ✅ Created requirements.txt for {product_path.name}")
    return True


def main():
    """Main function."""
    repo_root = Path(__file__).parent.parent
    
    print("📦 Creating missing requirements.txt files...\n")
    
    created_count = 0
    
    for product in PRODUCTS_MISSING_REQUIREMENTS:
        product_path = repo_root / product
        if not product_path.exists():
            print(f"  ⚠️  Product directory not found: {product}")
            continue
        
        if create_requirements_file(product_path):
            created_count += 1
    
    print(f"\n✅ Created {created_count} requirements.txt files")
    return 0


if __name__ == "__main__":
    sys.exit(main())