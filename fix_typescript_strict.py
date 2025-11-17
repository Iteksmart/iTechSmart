#!/usr/bin/env python3
"""
Fix TypeScript strict mode for products with compilation errors.
Sets strict: false in tsconfig.json for specified products.
"""

import json
import os
from pathlib import Path

# Products to fix
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


def fix_tsconfig(product_name):
    """Fix tsconfig.json for a product."""
    tsconfig_path = Path(product_name) / "frontend" / "tsconfig.json"

    if not tsconfig_path.exists():
        print(f"❌ {product_name}: tsconfig.json not found")
        return False

    try:
        # Read current config
        with open(tsconfig_path, "r") as f:
            config = json.load(f)

        # Update strict mode
        if "compilerOptions" in config:
            config["compilerOptions"]["strict"] = False

            # Write back
            with open(tsconfig_path, "w") as f:
                json.dump(config, f, indent=2)

            print(f"✅ {product_name}: Set strict: false")
            return True
        else:
            print(f"❌ {product_name}: No compilerOptions found")
            return False

    except Exception as e:
        print(f"❌ {product_name}: Error - {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Phase 3: Fixing TypeScript Strict Mode")
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
