# Skills Index

> **Modular, reusable expertise** - Skills provide focused knowledge in specific domains

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

---

## How to Use Skills

Skills are modular expertise areas that you can activate when relevant to your current task.

### For AI Agents

1. **Scan this index** to see available skills
2. **Match your task** - Does your current work require this expertise?
3. **Load the skill** - Read the SKILL.md file for detailed patterns
4. **Apply patterns** - Follow the guidance using native tools

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
