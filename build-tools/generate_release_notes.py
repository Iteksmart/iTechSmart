"""
Release Notes Generator
Generates comprehensive release notes from git history and product changes
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class ReleaseNotesGenerator:
    """Generate release notes for iTechSmart Suite"""

    def __init__(self, version: str):
        self.version = version
        self.workspace = Path.cwd()

    def get_git_commits(self, since_tag: str = None) -> List[Dict]:
        """Get git commits since last tag"""
        try:
            if since_tag:
                cmd = [
                    "git",
                    "log",
                    f"{since_tag}..HEAD",
                    "--pretty=format:%H|%an|%ae|%ad|%s",
                    "--date=short",
                ]
            else:
                cmd = [
                    "git",
                    "log",
                    "--pretty=format:%H|%an|%ae|%ad|%s",
                    "--date=short",
                    "-n",
                    "50",
                ]

            output = subprocess.check_output(cmd, text=True)

            commits = []
            for line in output.strip().split("\n"):
                if line:
                    parts = line.split("|")
                    if len(parts) == 5:
                        commits.append(
                            {
                                "hash": parts[0][:8],
                                "author": parts[1],
                                "email": parts[2],
                                "date": parts[3],
                                "message": parts[4],
                            }
                        )

            return commits

        except subprocess.CalledProcessError:
            return []

    def get_last_tag(self) -> str:
        """Get the last git tag"""
        try:
            output = subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"], text=True
            )
            return output.strip()
        except subprocess.CalledProcessError:
            return None

    def categorize_commits(self, commits: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize commits by type"""
        categories = {
            "features": [],
            "fixes": [],
            "improvements": [],
            "security": [],
            "documentation": [],
            "other": [],
        }

        for commit in commits:
            message = commit["message"].lower()

            if any(word in message for word in ["feat", "feature", "add", "new"]):
                categories["features"].append(commit)
            elif any(word in message for word in ["fix", "bug", "resolve", "patch"]):
                categories["fixes"].append(commit)
            elif any(
                word in message for word in ["improve", "enhance", "optimize", "update"]
            ):
                categories["improvements"].append(commit)
            elif any(word in message for word in ["security", "vulnerability", "cve"]):
                categories["security"].append(commit)
            elif any(word in message for word in ["doc", "readme", "documentation"]):
                categories["documentation"].append(commit)
            else:
                categories["other"].append(commit)

        return categories

    def get_product_list(self) -> List[str]:
        """Get list of products"""
        products = []
        for item in self.workspace.iterdir():
            if item.is_dir() and (
                item.name.startswith("itechsmart-")
                or item.name.endswith("-ai")
                or item.name in ["prooflink", "passport", "legalai-pro"]
            ):
                products.append(item.name)
        return sorted(products)

    def generate_markdown(self) -> str:
        """Generate release notes in Markdown format"""
        last_tag = self.get_last_tag()
        commits = self.get_git_commits(last_tag)
        categorized = self.categorize_commits(commits)
        products = self.get_product_list()

        notes = f"""# iTechSmart Suite v{self.version}

**Release Date:** {datetime.now().strftime('%B %d, %Y')}

## Overview

This release includes updates across the entire iTechSmart Suite with {len(commits)} commits since the last release.

## What's New

"""

        # Features
        if categorized["features"]:
            notes += "### ✨ New Features\n\n"
            for commit in categorized["features"][:10]:
                notes += f"- {commit['message']} ({commit['hash']})\n"
            notes += "\n"

        # Improvements
        if categorized["improvements"]:
            notes += "### 🚀 Improvements\n\n"
            for commit in categorized["improvements"][:10]:
                notes += f"- {commit['message']} ({commit['hash']})\n"
            notes += "\n"

        # Bug Fixes
        if categorized["fixes"]:
            notes += "### 🐛 Bug Fixes\n\n"
            for commit in categorized["fixes"][:10]:
                notes += f"- {commit['message']} ({commit['hash']})\n"
            notes += "\n"

        # Security
        if categorized["security"]:
            notes += "### 🔒 Security Updates\n\n"
            for commit in categorized["security"]:
                notes += f"- {commit['message']} ({commit['hash']})\n"
            notes += "\n"

        # Products
        notes += f"""## Included Products

This release includes {len(products)} products:

"""

        for product in products:
            product_name = product.replace("-", " ").title()
            notes += f"- **{product_name}**\n"

        notes += """

## Installation

### Windows
1. Download the Windows installer (.msi or .exe)
2. Run the installer as Administrator
3. Follow the installation wizard
4. Launch from Start Menu

### macOS
1. Download the macOS installer (.dmg)
2. Open the DMG file
3. Drag the application to Applications folder
4. Launch from Applications

### Linux
1. Download the appropriate package (.deb, .rpm, or .AppImage)
2. Install using your package manager or run the AppImage
3. Launch from application menu or terminal

## System Requirements

- **Windows:** Windows 10 or later (64-bit)
- **macOS:** macOS 10.13 or later
- **Linux:** Ubuntu 20.04+, Debian 11+, or compatible
- **RAM:** 8 GB minimum, 16 GB recommended
- **Disk Space:** 10 GB minimum
- **Internet:** Required for activation and updates

## Licensing

Each product requires a valid license key. Options include:

- **Trial:** 30-day free trial with limited features
- **Basic:** Individual user license
- **Professional:** Advanced features and priority support
- **Enterprise:** Unlimited users and dedicated support

Visit [https://itechsmart.com/pricing](https://itechsmart.com/pricing) for details.

## Demo Versions

Demo versions are available for all products with the following restrictions:
- 30-day trial period
- Maximum 5 users
- Maximum 10 projects
- Limited API calls
- Demo watermark on outputs

## Support

- **Documentation:** [https://itechsmart.com/docs](https://itechsmart.com/docs)
- **Support Portal:** [https://itechsmart.com/support](https://itechsmart.com/support)
- **Email:** support@itechsmart.com
- **Community:** [https://community.itechsmart.com](https://community.itechsmart.com)

## Known Issues

Please check our [issue tracker](https://github.com/Iteksmart/iTechSmart/issues) for known issues and workarounds.

## Upgrade Notes

If upgrading from a previous version:
1. Backup your data before upgrading
2. Uninstall the previous version (optional)
3. Install the new version
4. Your license and settings will be preserved

## Contributors

Thank you to all contributors who made this release possible!

"""

        # Add unique contributors
        contributors = set()
        for commit in commits:
            contributors.add(f"{commit['author']} <{commit['email']}>")

        for contributor in sorted(contributors):
            notes += f"- {contributor}\n"

        notes += f"""

---

**Full Changelog:** {last_tag}...v{self.version} if last_tag else f"Initial release v{self.version}"

© 2025 iTechSmart. All rights reserved.
"""

        return notes

    def run(self):
        """Generate and output release notes"""
        notes = self.generate_markdown()
        print(notes)
        return notes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_release_notes.py <version>")
        sys.exit(1)

    version = sys.argv[1]
    generator = ReleaseNotesGenerator(version)
    generator.run()
