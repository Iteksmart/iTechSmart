#!/usr/bin/env python3

import os
import json
import re


class VersionUpdater:
    def __init__(self):
        self.base_path = "/workspace/iTechSmart"
        self.version_target = "1.5.0"
        self.updated_files = []
        self.errors = []

    def update_package_json_version(self, file_path):
        """Update version in package.json to 1.5.0"""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            old_version = data.get("version", "")
            if old_version != self.version_target:
                data["version"] = self.version_target

                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)

                self.updated_files.append(
                    {
                        "file": file_path,
                        "old_version": old_version,
                        "new_version": self.version_target,
                    }
                )
                return True, f"Updated {old_version} -> {self.version_target}"
            else:
                return True, "Already at target version"

        except Exception as e:
            self.errors.append(f"Error updating {file_path}: {str(e)}")
            return False, str(e)

    def find_package_json_files(self):
        """Find all package.json files in the iTechSmart suite"""
        package_json_files = []

        for root, dirs, files in os.walk(self.base_path):
            # Skip node_modules directories to avoid conflicts
            if "node_modules" in root:
                continue

            if "package.json" in files:
                package_json_files.append(os.path.join(root, "package.json"))

        return package_json_files

    def update_all_versions(self):
        """Update all package.json versions to 1.5.0"""
        print(f"🔄 Updating all package.json versions to {self.version_target}...")

        package_files = self.find_package_json_files()
        total_files = len(package_files)

        print(f"📁 Found {total_files} package.json files")

        for i, file_path in enumerate(package_files, 1):
            print(
                f"🔧 [{i}/{total_files}] Processing {os.path.relpath(file_path, self.base_path)}..."
            )

            success, message = self.update_package_json_version(file_path)
            status = "✅" if success else "❌"
            print(f"   {status} {message}")

        self.print_summary()

    def print_summary(self):
        """Print update summary"""
        print("\n" + "=" * 60)
        print("📊 VERSION UPDATE SUMMARY")
        print("=" * 60)

        print(f"✅ Successfully updated: {len(self.updated_files)} files")
        print(f"❌ Errors encountered: {len(self.errors)} files")

        if self.updated_files:
            print("\n📋 Updated Files:")
            for update in self.updated_files:
                rel_path = os.path.relpath(update["file"], self.base_path)
                print(
                    f"   📄 {rel_path}: {update['old_version']} → {update['new_version']}"
                )

        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"   ⚠️  {error}")

        if len(self.errors) == 0:
            print(
                f"\n🎉 All package.json files successfully updated to v{self.version_target}!"
            )
        else:
            print(f"\n⚠️  Some files could not be updated. Please review errors above.")


def main():
    print("🚀 iTechSmart Suite v1.5.0 - Version Update Tool")
    print("=" * 60)

    updater = VersionUpdater()
    updater.update_all_versions()


if __name__ == "__main__":
    main()
