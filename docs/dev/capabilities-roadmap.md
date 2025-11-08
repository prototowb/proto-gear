# Proto Gear Capabilities Roadmap

**Date**: 2025-11-07
**Status**: Living Document
**Version**: v0.4.1+

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

## Current State (v0.4.1)

### Available Capabilities

#### Skills (1)
- **testing/TDD** - Red-green-refactor cycle, test pyramid, coverage targets
  - Status: ✅ Complete
  - Quality: High
  - Documentation: Complete

#### Workflows (1)
- **feature-development** - 7-step process from planning to deployment
  - Status: ✅ Complete
  - Quality: High
  - Documentation: Complete

#### Commands (1)
- **create-ticket** - Ticket documentation and tracking
  - Status: ✅ Complete
  - Quality: High
  - Documentation: Complete

### Current Limitations

1. **Limited Template Selection** - Only TESTING.md as optional core template
2. **No Sub-Agent Assembly** - Can select categories but not compose agents
3. **Fixed Capability Structure** - No custom capability loading yet
4. **No Capability Dependencies** - Capabilities can't reference each other

---

## Phase 1: Foundation (v0.4.1 - v0.5.0)

**Timeline**: Current → 3-4 months
**Goal**: Establish 10-15 high-quality capabilities across all categories

### Additional Core Templates

**Priority: HIGH**

| Template | Purpose | Effort | Target |
|----------|---------|--------|--------|
| CONTRIBUTING.md | Contributor guidelines | 2-4h | v0.5.0 |
| CODE_OF_CONDUCT.md | Community standards | 1-2h | v0.5.0 |
| SECURITY.md | Security policy & reporting | 2-3h | v0.5.0 |
| ARCHITECTURE.md | System design documentation | 4-6h | v0.5.0 |
| API.md | API documentation patterns | 3-5h | v0.5.0 |
| DEPLOYMENT.md | Deployment workflow | 3-5h | v0.5.0 |

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

### Skills Expansion

**Priority: MEDIUM-HIGH**

| Skill | Purpose | Effort | Target |
|-------|---------|--------|--------|
| debugging | Systematic debugging methodology | 3-4h | v0.5.0 |
| code-review | Review checklist and best practices | 3-4h | v0.5.0 |
| refactoring | Safe refactoring strategies | 4-5h | v0.5.0 |
| performance | Profiling and optimization | 4-6h | v0.5.0 |
| security-review | Security audit checklist | 4-6h | v0.6.0 |
| documentation | Writing effective docs | 3-4h | v0.6.0 |

**Structure** (each skill):
```
.proto-gear/skills/{skill-name}/
  SKILL.md           # Methodology and patterns
  EXAMPLES.md        # Real-world examples
  CHECKLIST.md       # Step-by-step checklist
```

### Workflows Expansion

**Priority: MEDIUM-HIGH**

| Workflow | Purpose | Effort | Target |
|----------|---------|--------|--------|
| bug-fix | Issue triage to deployment | 3-4h | v0.5.0 |
| hotfix | Emergency patch workflow | 2-3h | v0.5.0 |
| release | Version bump to publish | 4-5h | v0.5.0 |
| code-review-process | PR creation to merge | 3-4h | v0.5.0 |
| incident-response | Production issue handling | 5-6h | v0.6.0 |
| migration | Breaking change workflow | 4-5h | v0.6.0 |

### Commands Expansion

**Priority: MEDIUM**

| Command | Purpose | Effort | Target |
|---------|---------|--------|--------|
| update-status | Status tracking and updates | 2-3h | v0.5.0 |
| create-branch | Branch from ticket | 2h | v0.5.0 |
| close-ticket | Completion checklist | 2h | v0.5.0 |
| start-sprint | Sprint initialization | 3-4h | v0.5.0 |
| end-sprint | Sprint retrospective | 3-4h | v0.5.0 |
| generate-changelog | Automated changelog | 4-5h | v0.6.0 |

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

## Roadmap Summary

| Version | Focus | Timeline | Key Deliverables |
|---------|-------|----------|------------------|
| v0.4.1 | Granular wizard | Current | Custom path, category selection |
| v0.5.0 | Foundation | 3-4 months | 10-15 capabilities, 5+ templates |
| v0.6.0 | Expansion | 5-6 months | 20-30 capabilities, metadata system |
| v0.7.0 | Discovery | 7-8 months | 30-40 capabilities, CLI discovery |
| v0.8.0 | Composition | 9-10 months | Sub-agent builder, composition engine |
| v0.9.0 | Polish | 11 months | 40-50 capabilities, community prep |
| v1.0.0 | Production | 12 months | 50+ capabilities, sub-agent system |
| v1.5.0+ | Marketplace | Future | Community contributions, ratings |

---

## Next Steps (Immediate)

**For v0.5.0 (Next Release):**

1. **Add 4-5 Core Templates** (Priority: HIGH)
   - CONTRIBUTING.md
   - SECURITY.md
   - ARCHITECTURE.md
   - CODE_OF_CONDUCT.md

2. **Add 3-4 Skills** (Priority: MEDIUM)
   - debugging
   - code-review
   - refactoring

3. **Add 2-3 Workflows** (Priority: MEDIUM)
   - bug-fix
   - hotfix
   - release

4. **Add 2-3 Commands** (Priority: LOW)
   - update-status
   - create-branch
   - close-ticket

5. **Implement Metadata System** (Priority: MEDIUM)
   - Add metadata.yaml to existing capabilities
   - Create validation schema
   - Update wizard to show metadata

**Estimated Effort**: 40-60 hours
**Target Date**: v0.5.0 (3-4 months)

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

*Last Updated: 2025-11-07*
*Document Version: 1.0.0*
*Proto Gear Version: v0.4.1*
