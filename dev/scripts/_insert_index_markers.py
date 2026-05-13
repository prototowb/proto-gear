"""One-shot: insert proto-gear:capability-index markers in INDEX templates.

Used during PROTO-036 to convert hand-curated listings into managed blocks.
Run once; the result is committed and this script is no longer needed.
"""
import re
from pathlib import Path

MANAGED_BLOCK_TPL = """<!-- proto-gear:capability-index begin -->

## Available {label}

_Auto-generated from `metadata.yaml`. Run `pg sync-indexes` to refresh. The prose around this marker is hand-written and is preserved across regeneration._

<!-- proto-gear:capability-index end -->"""

# Files where we replace from header (inclusive) up to (but not including)
# the trailing section anchor. The `---` separator just before the anchor is
# also dropped — the managed block reintroduces no separator.
TARGETS = [
    {
        "path": "core/proto_gear_pkg/capabilities/workflows/INDEX.template.md",
        "header": "## Available Workflows",
        "label": "Workflows",
        "next_section": "## How to Use Workflows",
    },
    {
        "path": "core/proto_gear_pkg/capabilities/commands/INDEX.template.md",
        "header": "## Available Slash Commands",
        "label": "Slash Commands",
        "next_section": "## AI Execution Protocol",
    },
]


def main() -> int:
    for t in TARGETS:
        path = Path(t["path"])
        text = path.read_text(encoding="utf-8")

        # Greedy match from header to but not including the next section.
        pattern = re.compile(
            re.escape(t["header"]) + r".*?(?=---\s*\n+" + re.escape(t["next_section"]) + ")",
            re.DOTALL,
        )
        if not pattern.search(text):
            # Fallback if there's no '---' separator.
            pattern = re.compile(
                re.escape(t["header"]) + r".*?(?=\n+" + re.escape(t["next_section"]) + ")",
                re.DOTALL,
            )
            if not pattern.search(text):
                print(f"NOT FOUND in {t['path']}")
                return 1

        new_text = pattern.sub(
            MANAGED_BLOCK_TPL.format(label=t["label"]) + "\n\n",
            text,
        )
        path.write_text(new_text, encoding="utf-8")
        print(f"  rewrote {t['path']}: {len(text)} -> {len(new_text)} chars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
