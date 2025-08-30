# PROJECT STATUS - Single Source of Truth

> **For Agents**: This is the ONLY source of project state. All examples and test data should be ignored.
> **For Humans**: Current development status and progress tracking.

## 📊 Current State

```yaml
project_phase: "{{PHASE}}"  # Planning, Development, Testing, Production
current_sprint: {{SPRINT_NUMBER}}  # null for pre-development
current_branch: "{{CURRENT_BRANCH}}"
last_ticket_id: {{LAST_TICKET_ID}}  # Next ticket will increment from this
ticket_prefix: "{{TICKET_PREFIX}}"  # e.g., "PROJ", "MCP", etc.
```

## 🎫 Active Tickets

| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
{{ACTIVE_TICKETS}}

## ✅ Completed Tickets

| ID | Title | Completed | PR |
|----|-------|-----------|-----|
{{COMPLETED_TICKETS}}

## 🚧 Blocked Tickets

| ID | Title | Blocker | Since |
|----|-------|---------|-------|
{{BLOCKED_TICKETS}}

## 📈 Feature Progress

| Feature | Status | Progress | Notes |
|---------|--------|----------|-------|
{{FEATURE_PROGRESS}}

## 🔄 Recent Updates
{{RECENT_UPDATES}}

## 🎯 Next Milestones

### Sprint {{NEXT_SPRINT}} Goals
{{SPRINT_GOALS}}

### Upcoming Features
{{UPCOMING_FEATURES}}

## 📊 Metrics

```yaml
velocity: {{VELOCITY}}  # points/sprint
test_coverage: {{COVERAGE}}%
documentation: {{DOC_COVERAGE}}%
tech_debt_ratio: {{TECH_DEBT}}%
```

## 🔍 Sprint Configuration

```yaml
sprint_type: "{{SPRINT_TYPE}}"  # feature_development, bug_fixing, etc.
active_agents:
  core:
    {{CORE_AGENTS}}
  flex:
    {{FLEX_AGENTS}}
```

---
*This file is the authoritative source for project state. Updated by Lead AI and Project Lead.*