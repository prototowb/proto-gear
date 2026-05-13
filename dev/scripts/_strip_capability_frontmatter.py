"""One-shot: strip YAML frontmatter from capability content templates.

Used during PROTO-037 to make metadata.yaml the single source of truth.
Run once; result is committed.
"""
import re
from pathlib import Path

CAPS_ROOT = Path("core/proto_gear_pkg/capabilities")
TARGETS = ["SKILL.template.md", "WORKFLOW.template.md", "COMMAND.template.md"]

# Frontmatter: starts at line 1 with '---', ends at next '---' on its own line.
FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n+", re.DOTALL)


def main() -> int:
    touched = 0
    skipped = 0
    files: list[Path] = []
    for name in TARGETS:
        files.extend(CAPS_ROOT.rglob(name))
    for path in sorted(files):
        text = path.read_text(encoding="utf-8")
        m = FRONTMATTER_RE.match(text)
        if not m:
            skipped += 1
            continue
        new_text = FRONTMATTER_RE.sub("", text)
        path.write_text(new_text, encoding="utf-8")
        touched += 1
        print(f"  stripped {path.relative_to(CAPS_ROOT.parent.parent.parent)}: "
              f"{len(text)} -> {len(new_text)} chars")
    print(f"\nDone: stripped {touched}, already clean {skipped}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
