# Migration Guide: Separating Framework from Project

This guide explains how to migrate an existing project (like MCAS) to use the separated Agent Framework.

## Overview

The Agent Framework has been extracted from the MCAS project to be:
- **Reusable**: Can be used in any software project
- **Configurable**: Customize agents for your specific needs
- **Maintainable**: Framework updates independent of project code
- **Distributable**: Can be packaged and shared

## Migration Steps

### Step 1: Backup Current Setup

```bash
# Create a backup branch
git checkout -b pre-framework-migration
git add .
git commit -m "Backup: Before agent framework separation"
```

### Step 2: Install Agent Framework

```bash
# Copy framework to your project
cp -r agent-framework/ .

# Or install as package (when available)
npm install @your-org/agent-framework
```

### Step 3: Create Configuration File

Create `mcas-agents.config.yaml` with your project-specific configuration:

```yaml
project:
  name: "MCAS Management App"
  description: "Medical app for MCAS patient management"
  type: "web-app"
  
agents:
  core:
    - id: "research_backend"
      name: "Research & Backend Agent"
      description: "Medical research processing and API development"
      responsibilities:
        - "Process medical research papers"
        - "Develop FastAPI backend services"
        - "Design PostgreSQL/Supabase schemas"
        - "Validate medical accuracy"
        
    - id: "ui_ux"
      name: "UI/UX Agent"
      description: "Frontend specialist for medical UI/UX"
      responsibilities:
        - "Vue 3/Nuxt 3 development"
        - "Tailwind CSS implementation"
        - "WCAG accessibility compliance"
        - "Offline-first PWA features"
        
    - id: "testing"
      name: "Testing Agent"
      description: "Quality assurance guardian"
      responsibilities:
        - "Unit tests (80%+ coverage)"
        - "Integration testing"
        - "E2E test scenarios"
        - "Offline functionality tests"
        
    - id: "security_compliance"
      name: "Security & Compliance Agent"
      description: "Privacy and regulatory specialist"
      responsibilities:
        - "GDPR compliance"
        - "DiGA requirements"
        - "Security scanning"
        - "German healthcare regulations"
```

### Step 4: Update AGENTS.md Files

Replace the framework code in AGENTS.md with imports:

```markdown
# AGENTS.md - MCAS Project Configuration

> **Framework**: Using Agent Framework v1.0
> **Configuration**: mcas-agents.config.yaml

## Project-Specific Context

### Medical Domain Requirements
- MCAS/MCAD clinical knowledge integration
- German healthcare system compliance (DiGA)
- ICD-10-GM code support
- Patient data privacy (GDPR)

### Research Processing
Research documents in `/assets/research-md/` are processed to:
- Extract diagnostic criteria
- Identify biomarkers
- Update treatment protocols
- Generate feature tickets

## Agent Customizations

### Research & Backend Agent Extensions
- Validates against Molderings et al. 2014 criteria
- Implements Theoharides protocol recommendations
- German medical terminology support

### UI/UX Agent Extensions
- Medical UI patterns for symptom tracking
- Accessibility for autoimmune conditions
- German localization requirements

## Workflow Triggers

The standard Agent Framework workflow is extended with:
1. Medical research scanning (when new papers added)
2. DiGA compliance checking
3. German localization validation

---
*Powered by Agent Framework - See agent-framework/README.md for core documentation*
```

### Step 5: Create Project Bindings

Create `agent-bindings.py` to connect project-specific logic:

```python
from agent_framework import WorkflowOrchestrator, Agent

class MedicalResearchAgent(Agent):
    """MCAS-specific research processing agent"""
    
    def execute(self, context):
        # Process medical research
        papers = self.scan_research_directory()
        findings = self.extract_medical_findings(papers)
        tickets = self.generate_medical_tickets(findings)
        return tickets

# Register custom agents
orchestrator = WorkflowOrchestrator('mcas-agents.config.yaml')
orchestrator.register_agent('research_backend', MedicalResearchAgent)
```

### Step 6: Update Directory AGENTS.md Files

Update subdirectory AGENTS.md files to reference the framework:

```markdown
# AGENTS.md - Backend Context

> **Framework**: Inherits from Agent Framework
> **Parent**: `/AGENTS.md`
> **Domain**: Medical backend services

## Local Medical Context
- FastAPI for medical data APIs
- Supabase for HIPAA-compliant storage
- German ICD-10-GM integration
- FHIR compatibility layer

[Rest of local context...]
```

## Benefits After Migration

### For MCAS Project
- **Cleaner codebase**: Framework logic separated from medical logic
- **Easier updates**: Update framework without touching medical code
- **Better testing**: Test framework and project separately

### For Other Projects
- **Reusable framework**: Use the same agent system in new projects
- **Proven patterns**: Battle-tested workflow automation
- **Quick start**: Initialize new projects in minutes

## Maintaining Separation

### Framework Updates
```bash
# Update framework independently
cd agent-framework
git pull origin main
npm version patch
```

### Project-Specific Changes
- Keep medical/domain logic in project files
- Use configuration for agent customization
- Extend base agents rather than modifying framework

## Example: Using Framework in New Project

```bash
# Create new project
mkdir new-project && cd new-project

# Initialize with framework
./agent-framework/scripts/init-project.sh

# Customize configuration
vim agent-framework.config.yaml

# Start development
python -m agent_framework.orchestrate
```

## Troubleshooting

### Common Issues

1. **Configuration not found**
   - Ensure `agent-framework.config.yaml` exists
   - Check file path in initialization

2. **Agent inheritance issues**
   - Verify AGENTS.md files declare inheritance
   - Check for circular dependencies

3. **Workflow not triggering**
   - Confirm AGENTS.md has trigger notice
   - Check framework is properly imported

## Next Steps

1. Complete the migration for MCAS
2. Test the separated framework
3. Document project-specific extensions
4. Consider packaging as npm/pip package
5. Share with other projects