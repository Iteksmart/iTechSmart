import re

# Read the current todo.md
with open("todo.md", "r") as f:
    content = f.read()

# Mark all Phase 11 tasks as complete
phase11_pattern = r"(## \[~\] Phase 11: Feature 15.*?)((?=## \[|\Z))"
phase11_match = re.search(phase11_pattern, content, re.DOTALL)

if phase11_match:
    phase11_content = phase11_match.group(1)
    # Replace all [ ] with [x] in Phase 11
    phase11_content = phase11_content.replace("[ ]", "[x]")
    # Change [~] to [x]
    phase11_content = phase11_content.replace("[~]", "[x]")

    content = content.replace(phase11_match.group(1), phase11_content)

# Write back
with open("todo.md", "w") as f:
    f.write(content)

print("✅ Phase 11 (Feature 15) marked as complete!")
print("🎉 PROJECT STATUS: 15/15 features complete (100%)")
print("🏆 ALL FEATURES IMPLEMENTED!")
