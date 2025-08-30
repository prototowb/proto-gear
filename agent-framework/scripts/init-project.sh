#!/bin/bash

# Agent Framework Project Initializer
# This script sets up a new project with the Agent Framework

set -e

echo "🚀 Agent Framework Project Initializer"
echo "======================================"
echo ""

# Get project information
read -p "Project name: " PROJECT_NAME
read -p "Project type (web-app/api/library/mobile-app/cli-tool): " PROJECT_TYPE
read -p "Main programming language: " MAIN_LANGUAGE
read -p "Ticket prefix (e.g., PROJ, APP): " TICKET_PREFIX
read -p "Main branch name (main/master): " MAIN_BRANCH
MAIN_BRANCH=${MAIN_BRANCH:-main}
read -p "Development branch name (development/develop): " DEV_BRANCH
DEV_BRANCH=${DEV_BRANCH:-development}

echo ""
echo "📁 Creating project structure..."

# Create essential directories
mkdir -p docs
mkdir -p tests
mkdir -p scripts

# Determine project-specific directories based on type
case $PROJECT_TYPE in
  "web-app")
    mkdir -p frontend backend
    DIRS="frontend backend"
    ;;
  "api")
    mkdir -p api tests/api
    DIRS="api"
    ;;
  "library")
    mkdir -p src tests/unit
    DIRS="src"
    ;;
  "mobile-app")
    mkdir -p app tests/app
    DIRS="app"
    ;;
  "cli-tool")
    mkdir -p cmd pkg
    DIRS="cmd pkg"
    ;;
  *)
    mkdir -p src
    DIRS="src"
    ;;
esac

echo "✅ Project directories created"

# Copy and customize AGENTS.md
echo ""
echo "📝 Setting up AGENTS.md files..."

# Function to replace placeholders
replace_placeholders() {
  local file=$1
  sed -i.bak \
    -e "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" \
    -e "s/{{PROJECT_TYPE}}/$PROJECT_TYPE/g" \
    -e "s/{{TICKET_PREFIX}}/$TICKET_PREFIX/g" \
    -e "s/{{MAIN_BRANCH}}/$MAIN_BRANCH/g" \
    -e "s/{{DEV_BRANCH}}/$DEV_BRANCH/g" \
    -e "s/{{MAIN_LANGUAGE}}/$MAIN_LANGUAGE/g" \
    -e "s/{{MIN_COVERAGE}}/80/g" \
    -e "s/{{SPRINT_DURATION}}/14 days/g" \
    "$file"
  rm "${file}.bak" 2>/dev/null || true
}

# Copy root AGENTS.md
cp agent-framework/core/AGENTS.template.md AGENTS.md
replace_placeholders AGENTS.md

# Create directory-specific AGENTS.md files
for dir in $DIRS; do
  cat > "$dir/AGENTS.md" << 'EOF'
# AGENTS.md - {{DIR}} Context

> **Inheritance**: This file extends root `/AGENTS.md`
> **Owner**: [Specify which core agent owns this domain]
> **DO NOT** duplicate information from parent AGENTS.md files

## Local Context
**Purpose**: [What this directory contains]
**Stack**: [Technology stack specific to this directory]
**Principle**: [Key principles for this domain]

## Agent Instructions

### When Working Here
- ✅ [Specific instruction 1]
- ✅ [Specific instruction 2]
- ✅ [Reference parent for: general rules]

## Local Patterns
[Directory-specific patterns and conventions]

## DO NOT
- Duplicate parent documentation
- Override security/compliance rules
- Create conflicting standards

## Reference Parent For
- General coding standards
- Security requirements
- Sprint configuration
- Agent communication protocols

---
*{{DIR}} Context - [Agent Domain]*
EOF
  
  # Replace directory name placeholder
  sed -i.bak "s/{{DIR}}/${dir}/g" "$dir/AGENTS.md"
  rm "$dir/AGENTS.md.bak" 2>/dev/null || true
done

echo "✅ AGENTS.md hierarchy created"

# Create PROJECT_STATUS.md
echo ""
echo "📊 Creating PROJECT_STATUS.md..."

cat > PROJECT_STATUS.md << EOF
# PROJECT STATUS - Single Source of Truth

> **For Agents**: This is the ONLY source of project state.
> **For Humans**: Current development status and progress tracking.

## 📊 Current State

\`\`\`yaml
project_phase: "Planning"
current_sprint: null
current_branch: "$MAIN_BRANCH"
last_ticket_id: 0
ticket_prefix: "$TICKET_PREFIX"
\`\`\`

## 🎫 Active Tickets
*No active tickets - project in planning phase*

## ✅ Completed Tickets
*None yet*

## 🚧 Blocked Tickets
*None*

## 📈 Feature Progress

| Feature | Status | Progress | Notes |
|---------|--------|----------|-------|
| Core Setup | Not Started | 0% | Initial framework setup |

## 🔄 Recent Updates
- $(date +%Y-%m-%d): Project initialized with Agent Framework

## 🎯 Next Milestones

### Sprint 1 Goals
- [ ] Complete project setup
- [ ] Define core features
- [ ] Set up development environment

---
*This file is the authoritative source for project state.*
EOF

echo "✅ PROJECT_STATUS.md created"

# Copy configuration file
echo ""
echo "⚙️ Setting up configuration..."

cp agent-framework/core/agent-framework.config.yaml agent-framework.config.yaml

# Update config with project info
sed -i.bak \
  -e "s/Your Project Name/$PROJECT_NAME/g" \
  -e "s/web-app/$PROJECT_TYPE/g" \
  -e "s/PROJ/$TICKET_PREFIX/g" \
  -e "s/main/$MAIN_BRANCH/g" \
  -e "s/development/$DEV_BRANCH/g" \
  agent-framework.config.yaml
rm agent-framework.config.yaml.bak 2>/dev/null || true

echo "✅ Configuration file created"

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
  echo ""
  echo "📄 Creating .gitignore..."
  cat > .gitignore << 'EOF'
# Agent Framework
agent-framework.log
*.bak
.processed

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Dependencies
node_modules/
venv/
__pycache__/
*.pyc
EOF
  echo "✅ .gitignore created"
fi

# Create initial documentation structure
echo ""
echo "📚 Setting up documentation structure..."

cat > docs/README.md << EOF
# $PROJECT_NAME Documentation

## Overview
This directory contains all project documentation.

## Structure
- \`/technical\` - Technical specifications and architecture
- \`/features\` - Feature documentation
- \`/api\` - API documentation (if applicable)

## Documentation Standards
See root \`AGENTS.md\` for documentation standards and the DRY principle.
EOF

# Initialize git if not already initialized
if [ ! -d .git ]; then
  echo ""
  echo "🔗 Initializing git repository..."
  git init
  git checkout -b $MAIN_BRANCH
  echo "✅ Git repository initialized"
fi

# Create initial commit
echo ""
echo "💾 Creating initial commit..."
git add .
git commit -m "🎉 Initialize project with Agent Framework

- Set up AGENTS.md hierarchy
- Create PROJECT_STATUS.md
- Configure agent system
- Establish project structure
" || echo "⚠️ Could not create commit (files may already be committed)"

echo ""
echo "✨ Project initialization complete!"
echo ""
echo "Next steps:"
echo "1. Edit agent-framework.config.yaml to customize agents for your project"
echo "2. Update AGENTS.md with project-specific details"
echo "3. Define your core agents' responsibilities"
echo "4. Start creating tickets in PROJECT_STATUS.md"
echo ""
echo "To activate the framework:"
echo "- Have an AI agent read AGENTS.md to trigger the workflow"
echo "- The Lead AI will initialize and start orchestrating development"
echo ""
echo "Happy coding! 🚀"