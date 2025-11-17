import os
import re

# Define all 15 features
features = {
    1: {
        "name": "Multi-AI Model Support",
        "description": "42 models across 11 providers",
        "file": "FEATURE1_COMPLETE.md",
    },
    2: {
        "name": "Deep Research with Citations",
        "description": "5 citation styles (APA, MLA, Chicago, Harvard, IEEE)",
        "file": "FEATURE2_COMPLETE.md",
    },
    3: {
        "name": "Embedded Code Editors",
        "description": "5 editors (Monaco, Image, Website, Markdown, JSON/YAML)",
        "file": "FEATURE3_COMPLETE.md",
    },
    4: {
        "name": "GitHub Integration",
        "description": "40+ operations for repos, PRs, issues, actions",
        "file": "FEATURE4_COMPLETE.md",
    },
    5: {
        "name": "Image Generation",
        "description": "4 providers (FLUX, DALL-E, Stable Diffusion, Imagen)",
        "file": "FEATURE5_COMPLETE.md",
    },
    6: {
        "name": "Advanced Data Visualization",
        "description": "12+ chart types with Chart.js integration",
        "file": "FEATURE6_COMPLETE_SUMMARY.md",
    },
    7: {
        "name": "Enhanced Document Processing",
        "description": "11+ formats (PDF, Word, Excel, PowerPoint, etc.)",
        "file": "FEATURE7_COMPLETE_SUMMARY.md",
    },
    8: {
        "name": "Concurrent VM Support",
        "description": "10 VMs per user, 8 programming languages",
        "file": "SESSION_COMPLETE_FEATURES_6_7_8.md",
    },
    9: {
        "name": "Scheduled Tasks",
        "description": "Cron expressions, interval scheduling, APScheduler",
        "file": "SESSION_COMPLETE_FEATURES_6_7_8.md",
    },
    10: {
        "name": "MCP Data Sources",
        "description": "Multiple data source integrations",
        "file": "FEATURE10_COMPLETE.md",
    },
    11: {
        "name": "Undo/Redo Actions",
        "description": "Unlimited history with bookmarks",
        "file": "FEATURE11_COMPLETE.md",
    },
    12: {
        "name": "Video Generation",
        "description": "3 providers (Runway, Stability AI, Pika)",
        "file": "FEATURE12_COMPLETE.md",
    },
    13: {
        "name": "Advanced Debugging",
        "description": "AI-powered error analysis, memory leak detection",
        "file": "FEATURE13_COMPLETE.md",
    },
    14: {
        "name": "Custom Workflows",
        "description": "8 node types, 7 action types, 5 templates",
        "file": "FEATURE14_COMPLETE.md",
    },
    15: {
        "name": "Team Collaboration",
        "description": "Real-time collaboration, workspaces, permissions",
        "file": "FEATURE15_COMPLETE.md",
    },
}

# Read feature details from files
base_path = "itechsmart-ninja"

print("# iTechSmart Ninja - Feature Analysis\n")
print("## All 15 Features:\n")

for num, feature in features.items():
    print(f"### Feature {num}: {feature['name']}")
    print(f"**Description:** {feature['description']}")

    file_path = os.path.join(base_path, feature["file"])
    if os.path.exists(file_path):
        print(f"**Status:** ✅ Complete")
        print(f"**Documentation:** {feature['file']}")
    else:
        print(f"**Status:** ⚠️ Documentation not found")
    print()

# Count code statistics
print("\n## Code Statistics:\n")

# Backend
backend_path = os.path.join(base_path, "backend")
if os.path.exists(backend_path):
    py_files = []
    for root, dirs, files in os.walk(backend_path):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))

    total_lines = 0
    for file in py_files:
        try:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                total_lines += len(f.readlines())
        except:
            pass

    print(f"**Backend Python Files:** {len(py_files)}")
    print(f"**Backend Lines of Code:** {total_lines:,}")

# VS Code Extension
vscode_path = os.path.join(base_path, "vscode-extension", "src")
if os.path.exists(vscode_path):
    ts_files = []
    for root, dirs, files in os.walk(vscode_path):
        for file in files:
            if file.endswith(".ts"):
                ts_files.append(os.path.join(root, file))

    total_lines = 0
    for file in ts_files:
        try:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                total_lines += len(f.readlines())
        except:
            pass

    print(f"**VS Code TypeScript Files:** {len(ts_files)}")
    print(f"**VS Code Lines of Code:** {total_lines:,}")

print("\n✅ Analysis complete!")
