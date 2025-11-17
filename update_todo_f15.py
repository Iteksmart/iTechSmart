import re

# Read the current todo.md
with open("todo.md", "r") as f:
    content = f.read()

# Update Phase 11 to mark it as in progress
content = re.sub(
    r"## \[ \] Phase 11: Feature 15 - Team Collaboration",
    "## [~] Phase 11: Feature 15 - Team Collaboration (IN PROGRESS - FINAL FEATURE!)",
    content,
)

# Mark the first subtask as complete
content = re.sub(
    r"(## \[~\] Phase 11: Feature 15.*?\n.*?- \[ \] Review FEATURE15_SPEC\.md specification)",
    r"\1".replace("[ ]", "[x]"),
    content,
    flags=re.DOTALL,
)

# Write back
with open("todo.md", "w") as f:
    f.write(content)

print("Updated todo.md - Phase 11 started (FINAL FEATURE!)")
