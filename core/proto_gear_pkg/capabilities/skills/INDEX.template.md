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

<!-- proto-gear:capability-index begin -->

## Available Skills

_Auto-generated from `metadata.yaml`. Run `pg sync-indexes` to refresh. The list above this marker is hand-written prose and is preserved across regeneration._

<!-- proto-gear:capability-index end -->

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
