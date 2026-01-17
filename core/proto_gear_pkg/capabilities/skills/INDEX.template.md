# Skills Index

> **Implicit, continuous expertise** - Skills are activated automatically when contextually relevant

## Skills vs Slash Commands

| Aspect | Skills | Slash Commands |
|--------|--------|----------------|
| **Invocation** | Implicit (AI decides) | Explicit (`/command-name`) |
| **Nature** | Continuous expertise | Discrete action |
| **Duration** | Throughout task | Start → Finish |
| **Example** | "testing" skill during TDD | `/create-ticket "Add auth"` |

**Key insight**: Skills are **expertise you apply based on context**. They don't have a `/` prefix and aren't explicitly invoked by the user.

---

## Available Skills

### Testing
**File**: `testing/SKILL.md`
**Version**: 1.0.0
**Description**: TDD methodology with red-green-refactor cycle for quality code
**Tags**: testing, tdd, quality, red-green-refactor, coverage
**When to Use**: Before implementing features, fixing bugs, or refactoring code
**Patterns**: 3 (unit, integration, e2e)
**Examples**: 1 (red-green-refactor example)
**Status**: Stable

**Relevance**:
- Trigger keywords: "write tests", "testing", "test coverage", "tdd", "quality assurance"
- Context: Use when you need to ensure code quality through automated testing

### Debugging & Troubleshooting
**File**: `debugging/SKILL.md`
**Version**: 1.0.0
**Description**: Systematic debugging methodology for identifying and fixing software issues
**Tags**: debugging, troubleshooting, problem-solving, root-cause-analysis, investigation
**When to Use**: When code behaves unexpectedly, tests fail, or errors occur
**Patterns**: 4 (scientific-method, divide-and-conquer, rubber-duck, binary-search)
**Status**: Stable

**Relevance**:
- Trigger keywords: "debug", "troubleshoot", "bug", "error", "issue", "failing", "broken"
- Context: Use when investigating code problems or fixing defects

### Code Review
**File**: `code-review/SKILL.md`
**Version**: 1.0.0
**Description**: Effective code review practices for quality, learning, and collaboration
**Tags**: code-review, quality, collaboration, feedback, best-practices
**When to Use**: When reviewing pull requests or having your code reviewed
**Patterns**: 3 (constructive-feedback, checklist-based, security-first)
**Status**: Stable

**Relevance**:
- Trigger keywords: "review", "pr", "pull request", "feedback", "check code"
- Context: Use during PR reviews or code quality assessments

### Refactoring
**File**: `refactoring/SKILL.md`
**Version**: 1.0.0
**Description**: Systematic code improvement while preserving behavior
**Tags**: refactoring, code-quality, clean-code, maintainability, technical-debt
**When to Use**: When code works but needs improvement in structure or readability
**Patterns**: 4 (red-green-refactor, extract-method, rename, simplify)
**Status**: Stable

**Relevance**:
- Trigger keywords: "refactor", "clean up", "improve", "simplify", "restructure", "technical debt"
- Context: Use when improving code quality without changing behavior

---

## How to Use Skills

Skills are **implicit expertise** - you don't invoke them with `/`, you activate them based on context.

### For AI Agents

**Skills are NOT slash commands!** There is no `/testing` or `/debugging` command. Instead:

1. **Recognize context** - Is the current task related to testing, debugging, code review, etc.?
2. **Load relevant skill** - Read the SKILL.md file for expertise
3. **Apply continuously** - Use the skill's patterns throughout your work
4. **No explicit invocation** - Skills are active when relevant, not triggered by user command

### When to Activate Skills

- **Testing skill**: When writing tests, implementing features with TDD, fixing bugs
- **Debugging skill**: When investigating errors, troubleshooting issues
- **Code Review skill**: When reviewing PRs, checking code quality
- **Refactoring skill**: When improving code structure

### Skill Structure

Each skill contains:
- **SKILL.md** - Main skill definition with philosophy and overview
- **patterns/** - Detailed sub-patterns for specific scenarios
- **examples/** - Concrete demonstrations of skill application

### Example: Using the Testing Skill

```
Task: Implement a new user authentication feature

1. Read skills/testing/SKILL.md
2. Learn the Red-Green-Refactor cycle
3. Read patterns/unit-testing.md for detailed guidance
4. Write failing test first
5. Implement minimal code to pass
6. Refactor while keeping tests green
```

---

## Adding Custom Skills

To add a new skill to this project:

1. Create directory: `skills/your-skill-name/`
2. Create `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: "Your Skill Name"
   type: "skill"
   version: "1.0.0"
   description: "Brief description"
   tags: ["keyword1", "keyword2"]
   category: "your-category"
   relevance:
     - trigger: "keywords that suggest this skill"
     - context: "when to use this skill"
   status: "stable"
   ---
   ```
3. Write detailed content with patterns and examples
4. Update this INDEX.md to list your new skill

---

*Proto Gear Skills Index*
