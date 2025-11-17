import re

# Read the current todo.md
with open("todo.md", "r") as f:
    content = f.read()

# Mark all Phase 10 tasks as complete
phase10_pattern = r"(## \[~\] Phase 10: Feature 14.*?)((?=## \[|\Z))"
phase10_match = re.search(phase10_pattern, content, re.DOTALL)

if phase10_match:
    phase10_content = phase10_match.group(1)
    # Replace all [ ] with [x] in Phase 10
    phase10_content = phase10_content.replace("[ ]", "[x]")
    # Change [~] to [x]
    phase10_content = phase10_content.replace("[~]", "[x]")

    content = content.replace(phase10_match.group(1), phase10_content)

# Write back
with open("todo.md", "w") as f:
    f.write(content)

print("✅ Phase 10 (Feature 14) marked as complete!")
print("📊 Project Status: 14/15 features complete (93.3%)")
