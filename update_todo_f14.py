import re

# Read the current todo.md
with open("todo.md", "r") as f:
    content = f.read()

# Update Phase 10 to mark it as in progress
content = re.sub(
    r"## \[ \] Phase 10: Feature 14 - Custom Workflows",
    "## [~] Phase 10: Feature 14 - Custom Workflows (IN PROGRESS)",
    content,
)

# Mark the first subtask as complete
content = re.sub(
    r"(## \[~\] Phase 10: Feature 14.*?\n.*?- \[ \] Review FEATURE14_SPEC\.md specification)",
    r"\1".replace("[ ]", "[x]"),
    content,
    flags=re.DOTALL,
)

# Write back
with open("todo.md", "w") as f:
    f.write(content)

print("Updated todo.md - Phase 10 started")
