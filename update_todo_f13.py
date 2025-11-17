import re

# Read the current todo.md
with open("todo.md", "r") as f:
    content = f.read()

# Update Phase 9 to mark it as in progress
content = re.sub(
    r"## \[ \] Phase 9: Feature 13 - Advanced Debugging",
    "## [~] Phase 9: Feature 13 - Advanced Debugging (IN PROGRESS)",
    content,
)

# Mark the first subtask as complete
content = re.sub(
    r"(## \[~\] Phase 9: Feature 13.*?\n.*?- \[ \] Review FEATURE13_SPEC\.md specification)",
    r"\1".replace("[ ]", "[x]"),
    content,
    flags=re.DOTALL,
)

# Write back
with open("todo.md", "w") as f:
    f.write(content)

print("Updated todo.md - Phase 9 started")
