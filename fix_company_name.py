#!/usr/bin/env python3
import os
import re
from pathlib import Path


def replace_in_file(filepath, old_text, new_text):
    """Replace text in a file"""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if old_text in content:
            new_content = content.replace(old_text, new_text)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    # Define replacements
    replacements = [
        ("iTechSmart Inc.", "iTechSmart Inc."),
        ("Manufacturer: iTechSmart Inc.", "Manufacturer: iTechSmart Inc."),  # Keep this
        ("iTechSmart AI Platform", "iTechSmart AI Platform"),  # Keep product name
        ("iTechSmart Inc.", "iTechSmart Inc."),
        ("iTechSmart Inc.", "iTechSmart Inc."),
        ("by iTechSmart Inc.", "by iTechSmart Inc."),  # Keep this
        ("the iTechSmart Inc.", "iTechSmart Inc."),  # Fix grammar
    ]

    # File extensions to process
    extensions = [".md", ".py", ".tsx", ".jsx", ".html", ".json", ".txt"]

    # Directories to skip
    skip_dirs = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
    }

    files_updated = 0
    total_replacements = 0

    # Walk through all files
    for root, dirs, files in os.walk("."):
        # Remove skip directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)

                # First pass: Replace "iTechSmart Inc." with "iTechSmart Inc."
                # But preserve "iTechSmart AI Platform" as product name
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    original_content = content

                    # Replace "iTechSmart Inc." but not "iTechSmart AI Platform"
                    # Use regex to avoid replacing product name
                    content = re.sub(
                        r"iTechSmart Inc.(?! Platform)", "iTechSmart Inc.", content
                    )

                    # Fix specific patterns
                    content = content.replace("iTechSmart Inc.", "iTechSmart Inc.")
                    content = content.replace("iTechSmart Inc.", "iTechSmart Inc.")
                    content = content.replace(
                        "by iTechSmart Inc.", "by iTechSmart Inc."
                    )
                    content = content.replace("the iTechSmart Inc.", "iTechSmart Inc.")

                    if content != original_content:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)
                        files_updated += 1
                        count = original_content.count(
                            "iTechSmart Inc."
                        ) - content.count("iTechSmart Inc.")
                        total_replacements += count
                        print(f"Updated: {filepath} ({count} replacements)")

                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    print(f"\n✅ Complete!")
    print(f"Files updated: {files_updated}")
    print(f"Total replacements: {total_replacements}")


if __name__ == "__main__":
    main()
