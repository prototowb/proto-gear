<!-- proto-gear:header
purpose: Content department state surface — the single source of truth for every piece of content in flight
read-when: Every content session before starting work; before moving any item across a stage gate
priority: required
defines:
  - content-state-yaml
  - queue-table
  - stage-gates
  - published-log
links:
  - AGENTS.md
  - docs/dev/content-module-design.md
-->
# CONTENT QUEUE — Single Source of Truth

> **For Agents**: This is the ONLY source of content state. Every draft, review,
> schedule, and publish decision lives here. Move an item between stages by
> editing its **Stage** — never publish past the approval gate without a human
> sign-off recorded in the **Approved by** column.
> **For Humans**: Current content pipeline and what is waiting on your review.

## Current State

```yaml
module: "content"
pipeline_stages: ["draft", "review", "scheduled", "published"]
publish_gate: "content-approval"   # human sign-off required before `scheduled`
current_owner: null
```

## 📥 Queue

Stages flow left-to-right; the **review → scheduled** transition is a human
supervision gate (see Stage Gates). An item may not skip stages.

| ID | Title | Channel | Stage | Owner | Approved by | Target date |
|----|-------|---------|-------|-------|-------------|-------------|
| _none yet_ | | | draft | | | |

## 🚦 Stage Gates

| Gate | Between | Who approves | Recorded in |
|------|---------|--------------|-------------|
| content-approval | review → scheduled | Human editor | "Approved by" column + SESSION_HANDOFF.md |

> **Escalation rule** (PROJECT_SPECIFICATIONS.md §4): if an item hits an
> undeclared situation (legal question, off-brand request, missing asset), the
> agent stops, records state in `SESSION_HANDOFF.md`, and asks. Silence is never
> consent — nothing reaches `scheduled` or `published` without a name in
> **Approved by**.

## ✅ Published Log

| ID | Title | Channel | Published | Approved by | Link |
|----|-------|---------|-----------|-------------|------|
| _none yet_ | | | | | |

---
*Content department state surface. Managed like PROJECT_STATUS.md is for
engineering — one queue, one truth.*
