#!/usr/bin/env python3

import os
import json
import re

# List of frontend directories that need @heroicons/react
frontend_dirs = [
    "itechsmart-enterprise/frontend",
    "itechsmart-impactos/frontend",
    "itechsmart-ninja/frontend",  # Already fixed, but included for completeness
]


def fix_package_json(frontend_path):
    """Add @heroicons/react to package.json dependencies"""
    package_json_path = os.path.join(frontend_path, "package.json")

    if not os.path.exists(package_json_path):
        print(f"❌ package.json not found in {frontend_path}")
        return False

    try:
        with open(package_json_path, "r") as f:
            package_data = json.load(f)

        # Check if @heroicons/react is already in dependencies
        if (
            "dependencies" in package_data
            and "@heroicons/react" in package_data["dependencies"]
        ):
            print(f"✅ @heroicons/react already exists in {frontend_path}")
            return True

        # Add @heroicons/react to dependencies
        if "dependencies" not in package_data:
            package_data["dependencies"] = {}

        package_data["dependencies"]["@heroicons/react"] = "^2.0.18"

        # Write back to file
        with open(package_json_path, "w") as f:
            json.dump(package_data, f, indent=2)

        print(f"✅ Added @heroicons/react to {frontend_path}")
        return True

    except Exception as e:
        print(f"❌ Error fixing {frontend_path}: {str(e)}")
        return False


def main():
    print("🔧 Fixing @heroicons/react dependencies across iTechSmart suite...")

    success_count = 0
    total_count = len(frontend_dirs)

    for frontend_dir in frontend_dirs:
        if fix_package_json(frontend_dir):
            success_count += 1

    print(f"\n📊 Summary: {success_count}/{total_count} frontends fixed successfully")

    if success_count == total_count:
        print("🎉 All @heroicons/react dependencies have been fixed!")
    else:
        print("⚠️  Some frontends may need manual attention")


if __name__ == "__main__":
    main()
