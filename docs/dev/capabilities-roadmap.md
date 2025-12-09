# Proto Gear Capabilities Roadmap

**Date**: 2025-12-09 (Updated)
**Status**: Living Document
**Version**: v0.7.3

---

## Vision

Proto Gear's capability system should enable users to **assemble their own AI sub-agents** by composing modular capabilities. Each capability is a self-contained pattern that agents can dynamically load and use.

**End Goal**: Users can build specialized AI agents (testing agent, deployment agent, review agent, etc.) by selecting and combining capabilities like building blocks.

---

## Design Philosophy

### Quality Over Quantity

**Current Approach (v0.4.1):**
- Start with **few, high-quality** capabilities
- Each capability is:
  - ✅ **Well-documented** - Clear purpose, usage, and examples
  - ✅ **Battle-tested** - Proven patterns from real projects
  - ✅ **Self-contained** - Works independently
  - ✅ **Composable** - Can combine with other capabilities

**Why Quality First:**
1. Sets the standard for future capabilities
2. Users learn the system with solid examples
3. Easy to expand once pattern is established
4. Avoids bloat and maintenance burden

### Three-Phase Evolution

1. **Phase 1: Foundation (v0.4.x - v0.5.0)** - Establish quality baseline
2. **Phase 2: Expansion (v0.5.0 - v0.7.0)** - Add more capabilities
3. **Phase 3: Composition (v0.8.0 - v1.0.0)** - Enable custom sub-agent assembly

---

## Current State (v0.7.3)

### Available Capabilities

#### Core Templates (8)
- **AGENTS.md** - AI agent collaboration guide ✅
- **PROJECT_STATUS.md** - Project state tracking ✅
- **TESTING.md** - TDD workflow and patterns ✅
- **BRANCHING.md** - Git workflow conventions ✅
- **CONTRIBUTING.md** - Contributor guidelines ✅
- **SECURITY.md** - Security policy ✅
- **ARCHITECTURE.md** - System design documentation ✅
- **CODE_OF_CONDUCT.md** - Community standards ✅

#### Skills (4)
- **testing** - TDD methodology and test pyramid ✅
- **debugging** - Systematic debugging approach ✅
- **code-review** - Review checklist and standards ✅
- **refactoring** - Safe refactoring strategies ✅

#### Workflows (5)
- **feature-development** - 7-step development process ✅
- **bug-fix** - Issue triage to deployment ✅
- **hotfix** - Emergency patch workflow ✅
- **release** - Version bump to publish ✅
- **finalize** - Project completion workflow ✅

#### Commands (1)
- **create-ticket** - Ticket documentation ✅

### Key Achievements (v0.4.1 → v0.7.3)

1. ✅ **Template Auto-Discovery** - Zero-code extensibility (v0.6.0)
2. ✅ **8 Core Templates** - All Phase 1 targets completed (v0.5.0)
3. ✅ **14 Total Capabilities** - Exceeded Phase 1 goal of 10-15
4. ✅ **Granular Selection** - 3-level capability selection (v0.6.0)
5. ✅ **Optimal Test Coverage** - 47% coverage, all business logic tested (v0.7.0)
6. ✅ **Template Metadata System** - YAML frontmatter for conditional content (v0.7.0)
7. ✅ **Enhanced Project Detection** - 14 frameworks across 7 languages (v0.7.0)
8. ✅ **Cross-Reference Network** - All 8 templates interconnected (v0.7.3)
9. ✅ **Mandatory Capability Discovery** - 3-step workflow ensures usage (v0.7.3)
10. ✅ **Professional Template Quality** - Production-ready documentation (v0.7.3)

---

## Phase 1: Foundation (v0.4.1 - v0.5.0) ✅ COMPLETED

**Timeline**: Nov 2025 (3 weeks actual vs 3-4 months planned)
**Goal**: Establish 10-15 high-quality capabilities across all categories
**Result**: ✅ EXCEEDED - 14 capabilities + 8 templates

### Core Templates - COMPLETED

| Template | Purpose | Status | Completed |
|----------|---------|--------|-----------|
| CONTRIBUTING.md | Contributor guidelines | ✅ DONE | v0.5.0 |
| CODE_OF_CONDUCT.md | Community standards | ✅ DONE | v0.5.0 |
| SECURITY.md | Security policy & reporting | ✅ DONE | v0.5.0 |
| ARCHITECTURE.md | System design documentation | ✅ DONE | v0.5.0 |
| ~~API.md~~ | ~~API documentation patterns~~ | ⏭️ DEFERRED | Future |
| ~~DEPLOYMENT.md~~ | ~~Deployment workflow~~ | ⏭️ DEFERRED | Future |

**Implementation:**
```python
# In ask_core_templates_selection()
choices = questionary.checkbox(
    "Select additional templates:",
    choices=[
        questionary.Choice("TESTING.md - TDD workflow", value='TESTING'),
        questionary.Choice("CONTRIBUTING.md - Contributor guidelines", value='CONTRIBUTING'),
        questionary.Choice("SECURITY.md - Security policy", value='SECURITY'),
        questionary.Choice("ARCHITECTURE.md - System design", value='ARCHITECTURE'),
        questionary.Choice("API.md - API documentation", value='API'),
        questionary.Choice("DEPLOYMENT.md - Deployment workflow", value='DEPLOYMENT'),
    ],
    style=PROTO_GEAR_STYLE
).ask()
```

### Skills Expansion - PARTIALLY COMPLETED

| Skill | Purpose | Status | Completed |
|-------|---------|--------|-----------|
| debugging | Systematic debugging methodology | ✅ DONE | v0.5.0 |
| code-review | Review checklist and best practices | ✅ DONE | v0.5.0 |
| refactoring | Safe refactoring strategies | ✅ DONE | v0.5.0 |
| performance | Profiling and optimization | ⏭️ DEFERRED | Future |
| security-review | Security audit checklist | ⏭️ DEFERRED | Future |
| documentation | Writing effective docs | ⏭️ DEFERRED | Future |

**Structure** (each skill):
```
.proto-gear/skills/{skill-name}/
  SKILL.md           # Methodology and patterns
  EXAMPLES.md        # Real-world examples
  CHECKLIST.md       # Step-by-step checklist
```

### Workflows Expansion - PARTIALLY COMPLETED

| Workflow | Purpose | Status | Completed |
|----------|---------|--------|-----------|
| bug-fix | Issue triage to deployment | ✅ DONE | v0.5.0 |
| hotfix | Emergency patch workflow | ✅ DONE | v0.5.0 |
| release | Version bump to publish | ✅ DONE | v0.5.0 |
| finalize | Project completion workflow | ✅ DONE | v0.5.0 |
| code-review-process | PR creation to merge | ⏭️ DEFERRED | Future |
| incident-response | Production issue handling | ⏭️ DEFERRED | Future |
| migration | Breaking change workflow | ⏭️ DEFERRED | Future |

### Commands Expansion - DEFERRED

**Status**: Phase 1 focused on quality over quantity - 1 command sufficient for now

| Command | Purpose | Status | Target |
|---------|---------|--------|--------|
| create-ticket | Ticket documentation | ✅ DONE | v0.5.0 |
| update-status | Status tracking and updates | ⏭️ DEFERRED | Phase 2 |
| create-branch | Branch from ticket | ⏭️ DEFERRED | Phase 2 |
| close-ticket | Completion checklist | ⏭️ DEFERRED | Phase 2 |
| start-sprint | Sprint initialization | ⏭️ DEFERRED | Phase 2 |
| end-sprint | Sprint retrospective | ⏭️ DEFERRED | Phase 2 |
| generate-changelog | Automated changelog | ⏭️ DEFERRED | Phase 2 |

### Agents Category (New)

**Priority: LOW (Future-focused)**

Placeholder for future sub-agent definitions:
```
.proto-gear/agents/
  testing-agent.md      # Composed from: testing skill + bug-fix workflow
  deployment-agent.md   # Composed from: deployment skill + release workflow
  review-agent.md       # Composed from: code-review skill + review workflow
```

**Note**: Agents are compositions of skills, workflows, and commands. This category is for v0.6.0+.

---

## Phase 2: Expansion (v0.5.0 - v0.7.0)

**Timeline**: 4-8 months from now
**Goal**: Reach 30-40 capabilities with tech-stack specific variants

### Tech-Stack Specific Capabilities

Allow users to generate capabilities tailored to their stack:

**Example: Python-specific testing skill**
```
.proto-gear/skills/testing/python/
  SKILL.md              # pytest, unittest, tox patterns
  EXAMPLES.md           # Python-specific examples
```

**Example: React-specific workflows**
```
.proto-gear/workflows/component-development/
  WORKFLOW.md           # Generic component workflow
  react/                # React-specific variant
    WORKFLOW.md         # Hooks, testing, storybook
```

### Capability Metadata System

**Implementation Target: v0.5.0**

Each capability gets metadata for discovery and composition:

```yaml
# .proto-gear/skills/testing/metadata.yaml
name: "TDD Methodology"
version: "1.0.0"
category: "skill"
tags: ["testing", "tdd", "quality"]
dependencies: []
tech_stacks: ["agnostic"]
ai_agent_role: "Testing Agent"
composable_with:
  - "workflows/bug-fix"
  - "workflows/feature-development"
```

### Capability Discovery

**Implementation Target: v0.6.0**

```bash
# List all capabilities
pg capabilities list

# Search capabilities
pg capabilities search --tag testing

# Show capability details
pg capabilities show skills/testing

# Install specific capability
pg capabilities add skills/performance
```

---

## Phase 3: Composition (v0.8.0 - v1.0.0)

**Timeline**: 8-12 months from now
**Goal**: Enable custom sub-agent assembly

### Sub-Agent Builder

Allow users to define custom AI agents by composing capabilities:

```yaml
# .proto-gear/agents/my-testing-agent.yaml
name: "Testing Agent"
description: "Specialized agent for TDD and test automation"
capabilities:
  skills:
    - testing/tdd
    - debugging/systematic
    - code-review/testing-focus
  workflows:
    - bug-fix
    - feature-development
  commands:
    - create-ticket
    - update-status
context_priority:
  - "Read test files first"
  - "Check coverage reports"
  - "Review recent failures"
```

### Capability Composition Engine

**Features:**
1. **Dependency Resolution** - Auto-include required capabilities
2. **Conflict Detection** - Warn about incompatible capabilities
3. **Context Optimization** - Load only needed capabilities per task
4. **Custom Instructions** - Agent-specific guidance

### Wizard Enhancement (v0.8.0+)

New option in wizard:
```
[CONFIG] Setup Configuration

Choose configuration approach:
  1. ⚡ Quick Start (Recommended)
  2. 📦 Full Setup (All features)
  3. 🎯 Minimal (Core only)
  4. 🔧 Custom (Select capabilities)
  5. 🤖 Build Sub-Agent (NEW!)  ← Compose custom agent
```

**Build Sub-Agent Flow:**
```
Step 1: Define agent role
  → Name: "My Testing Agent"
  → Purpose: "TDD and automated testing"

Step 2: Select skills
  [✓] testing/tdd
  [✓] debugging/systematic
  [ ] performance/profiling

Step 3: Select workflows
  [✓] feature-development
  [✓] bug-fix
  [ ] hotfix

Step 4: Select commands
  [✓] create-ticket
  [✓] update-status
  [ ] generate-changelog

Step 5: Preview agent configuration
  → Shows composed capabilities
  → Highlights any conflicts
  → Suggests missing capabilities

Step 6: Generate agent files
  ✓ .proto-gear/agents/my-testing-agent.yaml
  ✓ .proto-gear/agents/my-testing-agent/GUIDE.md
  ✓ Selected capability files
```

---

## Quality Standards

Every capability must meet these standards before inclusion:

### Documentation Requirements

1. **Clear Purpose** - What problem does it solve?
2. **Usage Examples** - How do AI agents use it?
3. **Step-by-Step Guide** - Actionable instructions
4. **Failure Modes** - What can go wrong and how to handle it
5. **Composition Notes** - Works well with X, conflicts with Y

### Testing Requirements

1. **Manual Testing** - Used in real project by maintainers
2. **AI Agent Testing** - Verified with Claude Code, Cursor, etc.
3. **Cross-Platform** - Works on Windows, macOS, Linux
4. **Tech-Stack Agnostic** - Unless explicitly tech-specific

### Maintenance Requirements

1. **Version Tracking** - Each capability has version number
2. **Update Log** - Changes documented in capability file
3. **Deprecation Policy** - 2 versions notice before removal
4. **Migration Guide** - If capability structure changes

---

## Contribution Guidelines

### Adding New Capabilities

1. **Propose First** - Open issue with capability proposal
2. **Get Feedback** - Discuss with maintainers
3. **Follow Template** - Use existing capabilities as template
4. **Test Thoroughly** - Use in real project for 1+ week
5. **Document Well** - Meet documentation standards
6. **Submit PR** - Include capability + tests + docs update

### Capability Template

```markdown
# [Capability Name] - [Category]

> **Version**: 1.0.0
> **Status**: Stable
> **Tech Stack**: Agnostic / Python / JavaScript / etc.
> **Composable With**: [list related capabilities]

## Purpose

[Clear 2-3 sentence description]

## When to Use

- [Scenario 1]
- [Scenario 2]
- [Scenario 3]

## How AI Agents Use This

[Natural language description of the pattern]

## Step-by-Step Guide

1. [First step]
2. [Second step]
3. [etc.]

## Examples

### Example 1: [Scenario Name]

[Concrete example with code/commands]

### Example 2: [Another Scenario]

[Another concrete example]

## Common Issues

### Issue 1: [Problem]

**Solution**: [How to resolve]

### Issue 2: [Problem]

**Solution**: [How to resolve]

## Related Capabilities

- [Link to related skill]
- [Link to related workflow]
- [Link to related command]

---

*Last Updated: YYYY-MM-DD*
*Version: X.Y.Z*
```

---

## Success Metrics

### Phase 1 (v0.5.0)
- ✅ 10-15 high-quality capabilities
- ✅ All capabilities battle-tested
- ✅ 5+ optional core templates
- ✅ Documentation coverage: 100%

### Phase 2 (v0.7.0)
- ✅ 30-40 capabilities
- ✅ Metadata system implemented
- ✅ Capability discovery CLI
- ✅ 3+ tech-stack specific variants

### Phase 3 (v1.0.0)
- ✅ Sub-agent builder wizard
- ✅ Composition engine
- ✅ 50+ capabilities
- ✅ 10+ example sub-agent templates
- ✅ Community contributions: 5+ external capabilities

---

## Community Engagement

### Capability Marketplace (Future v1.5.0+)

Vision for community-contributed capabilities:

```bash
# Browse community capabilities
pg marketplace browse

# Install community capability
pg marketplace install username/capability-name

# Publish your capability
pg marketplace publish ./my-capability/

# Rate and review capabilities
pg marketplace review username/capability-name --stars 5
```

---

## Roadmap Summary (Updated for v0.7.3)

| Version | Focus | Status | Key Deliverables |
|---------|-------|--------|------------------|
| v0.4.1 | Granular wizard | ✅ DONE | Custom path, category selection |
| v0.5.0 | Foundation | ✅ DONE | 14 capabilities, 8 templates (exceeded goal!) |
| v0.6.0 | Auto-Discovery | ✅ DONE | Template auto-discovery, granular selection |
| v0.6.4 | Quality & Testing | ✅ DONE | 47% optimal test coverage, test philosophy |
| v0.7.0 | Metadata & Detection | ✅ DONE | Template metadata, enhanced project detection, Rust |
| v0.7.1 | Incremental Updates | ✅ DONE | File protection, incremental wizard |
| v0.7.2 | Bugfixes | ✅ DONE | Critical bugfixes, AGENTS.md enhancement |
| v0.7.3 | Template Quality | ✅ DONE | Cross-references, capability discovery, professional quality |
| **v0.8.0** | **Composition** | 🚧 NEXT | Sub-agent builder, composition engine |
| v0.9.0 | Community | 📋 PLANNED | Capability contributions, documentation |
| v1.0.0 | Production | 📋 PLANNED | Production-ready, stable APIs |
| v1.5.0+ | Marketplace | 💭 FUTURE | Community marketplace, ratings |

---

## Next Steps (v0.8.0 - Planning Phase)

**Phase 1 & 2 Review**: ✅ EXCEEDED all goals
- 14 capabilities, 8 templates, auto-discovery
- Template metadata system with conditional content
- Enhanced project detection (14 frameworks, 7 languages)
- Cross-reference network across all templates
- Mandatory capability discovery
- Production-ready quality (9.2/10)

**For v0.8.0 (Next Major Feature):**

1. **Sub-Agent Builder Wizard** (Priority: HIGH)
   - Interactive wizard for composing custom AI agents
   - Select skills, workflows, commands from available capabilities
   - Generate agent configuration files
   - Preview composed agent capabilities

2. **Composition Engine** (Priority: HIGH)
   - Dependency resolution (auto-include required capabilities)
   - Conflict detection (warn about incompatible capabilities)
   - Context optimization (load only needed capabilities per task)
   - Validation system (ensure composed agents are viable)

3. **Agent Configuration System** (Priority: HIGH)
   - YAML-based agent definitions
   - Custom context priority rules
   - Agent-specific instructions
   - Capability composition rules

4. **Enhanced Capability Management** (Priority: MEDIUM)
   - CLI commands for capability discovery
   - Capability metadata expansion
   - Search and filter capabilities
   - Show capability details and dependencies

5. **Additional Language Support** (Priority: LOW - Based on Demand)
   - Go, Kotlin, Swift, etc.
   - Only add if user feedback indicates need

**Estimated Effort**: 60-80 hours (major feature)
**Target Date**: v0.8.0 (2-3 months) - No rush, quality first

---

## Feedback & Iteration

This roadmap is a living document. As we learn from user feedback and see how AI agents actually use capabilities, we'll adjust:

- **What works?** Double down on those patterns
- **What doesn't?** Deprecate or refactor
- **What's missing?** Add based on real needs

**Feedback Channels:**
- GitHub Issues (feature requests)
- Discussions (capability proposals)
- Community Discord (future)
- User surveys (quarterly)

---

*Last Updated: 2025-12-09*
*Document Version: 3.0.0*
*Proto Gear Version: v0.7.3*
