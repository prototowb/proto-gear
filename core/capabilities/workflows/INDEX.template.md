# Workflows Index

> **Multi-step processes** - Workflows orchestrate complete tasks from start to finish

## Available Workflows

### Feature Development
**File**: `feature-development.md`
**Version**: 1.0.0
**Description**: Complete workflow for building new features from concept to deployment
**Tags**: feature, development, workflow, sprint, tdd
**Category**: development
**Steps**: 7
**Duration**: 2-4 hours per feature
**Status**: Stable

**Dependencies**:
- skills/testing
- commands/create-ticket

**Relevance**:
- Trigger keywords: "new feature", "implement feature", "build feature", "add feature"
- Context: Starting work on a new user-facing capability


### Bug Fix
**File**: `bug-fix.md`
**Version**: 1.0.0
**Description**: Systematic workflow for investigating and fixing software defects
**Tags**: bug, fix, debugging, workflow, testing
**Category**: maintenance
**Steps**: 8
**Duration**: 1-3 hours per bug
**Status**: Stable

**Dependencies**:
- skills/debugging
- skills/testing
- commands/create-ticket

**Relevance**:
- Trigger keywords: "bug", "defect", "error", "issue", "broken", "not working", "failing"
- Context: When existing functionality is broken or behaving incorrectly

### Hotfix
**File**: `hotfix.md`
**Version**: 1.0.0
**Description**: Emergency workflow for critical production bugs requiring immediate fixes
**Tags**: hotfix, production, emergency, critical, urgent
**Category**: maintenance
**Steps**: 9
**Duration**: 30 minutes - 2 hours
**Status**: Stable

**Dependencies**:
- skills/debugging
- skills/testing

**Relevance**:
- Trigger keywords: "hotfix", "production bug", "critical", "emergency", "urgent fix", "outage"
- Context: When production is broken and requires immediate fix

### Release
**File**: `release.md`
**Version**: 1.0.0
**Description**: Complete workflow for preparing, testing, and deploying software releases
**Tags**: release, deployment, versioning, changelog, production
**Category**: deployment
**Steps**: 10
**Duration**: 2-4 hours
**Status**: Stable

**Dependencies**:
- skills/testing
- commands/create-ticket

**Relevance**:
- Trigger keywords: "release", "deploy", "ship", "version", "publish"
- Context: When ready to release new version to production

### Finalize Release
**File**: `finalize-release.md`
**Version**: 1.0.0
**Description**: Post-release verification and dogfooding installation workflow
**Tags**: finalize, post-release, verification, dogfooding, installation
**Category**: deployment
**Steps**: 8
**Duration**: 15-30 minutes
**Status**: Stable

**Dependencies**:
- workflows/release (must be completed first)

**Relevance**:
- Trigger keywords: "finalize release", "post-release", "verify installation", "dogfooding setup"
- Context: After pushing a version tag and creating a GitHub release

---

## How to Use Workflows

Workflows provide step-by-step guidance for accomplishing larger, multi-step tasks.

### For AI Agents

1. **Identify your task type** - Is it a feature, bug fix, refactoring, etc.?
2. **Find matching workflow** - Use trigger keywords to find the right workflow
3. **Check dependencies** - Ensure required skills/commands are available
4. **Follow step-by-step** - Execute each step in order
5. **Use native tools** - git, pytest, npm, etc. as described

### Workflow Structure

Each workflow contains:
- **Prerequisites** - What must be true before starting
- **Step-by-step process** - Numbered, actionable steps
- **Success criteria** - How to know you're done
- **Common pitfalls** - Mistakes to avoid
- **Related capabilities** - Links to relevant skills/commands

### Example: Using Feature Development Workflow

```
Task: Add user login feature

1. Read workflows/feature-development.md
2. Step 1: Create ticket in PROJECT_STATUS.md
3. Step 2: Create feature branch
4. Step 3: Write failing tests (RED)
5. Step 4: Implement feature (GREEN)
6. Step 5: Refactor code
7. Step 6: Commit changes
8. Step 7: Create pull request
```

---

## Workflow Decision Tree

**Choose the right workflow for your task:**

```
What are you working on?

├─ New functionality → feature-development.md
├─ Fixing a bug → bug-fix.md
├─ Critical production issue → hotfix.md
├─ Ready to release → release.md
├─ Just pushed a release tag → finalize-release.md
├─ Improving code structure → refactoring.md (if available)
├─ Making code faster → performance-optimization.md (if available)
└─ Other tasks → Check commands/ for single-action patterns
```

---

## Adding Custom Workflows

To add a new workflow to this project:

1. Create file: `workflows/your-workflow-name.md`
2. Add YAML frontmatter:
   ```yaml
   ---
   name: "Your Workflow Name"
   type: "workflow"
   version: "1.0.0"
   description: "Brief description"
   tags: ["keyword1", "keyword2"]
   category: "development"
   relevance:
     - trigger: "keywords that suggest this workflow"
     - context: "when to use this workflow"
   dependencies: ["skills/testing"]
   steps: 5
   estimated_duration: "1-2 hours"
   status: "stable"
   ---
   ```
3. Write numbered steps with clear instructions
4. Include prerequisites, success criteria, and common pitfalls
5. Update this INDEX.md to list your new workflow

---

*Proto Gear Workflows Index*
