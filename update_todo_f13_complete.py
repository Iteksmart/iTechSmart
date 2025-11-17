import re

# Read the current todo.md
with open("todo.md", "r") as f:
    content = f.read()

# Mark all Phase 9 tasks as complete
phase9_pattern = r"(## \[~\] Phase 9: Feature 13.*?)((?=## \[|\Z))"
phase9_match = re.search(phase9_pattern, content, re.DOTALL)

if phase9_match:
    phase9_content = phase9_match.group(1)
    # Replace all [ ] with [x] in Phase 9
    phase9_content = phase9_content.replace("[ ]", "[x]")
    # Change [~] to [x]
    phase9_content = phase9_content.replace("[~]", "[x]")

    content = content.replace(phase9_match.group(1), phase9_content)

# Write back
with open("todo.md", "w") as f:
    f.write(content)

print("✅ Phase 9 (Feature 13) marked as complete!")
print("📊 Project Status: 13/15 features complete (86.7%)")
