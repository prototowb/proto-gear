#!/usr/bin/env python3
"""
Pre-defined Agent Templates for Quick Agent Creation

Provides ready-to-use agent configurations for common development roles.
"""

from datetime import datetime
from .agent_config import AgentConfiguration, AgentCapabilities


# Template definitions
AGENT_TEMPLATES = {
    "minimal": {
        "name": "Minimal Agent",
        "description": "Minimal agent with just core project management",
        "capabilities": AgentCapabilities(
            skills=[],
            workflows=[],
            commands=["commands/create-ticket"]
        ),
        "context_priority": [
            "PROJECT_STATUS.md",
            "AGENTS.md"
        ],
        "agent_instructions": [
            "Focus on understanding project structure",
            "Read PROJECT_STATUS.md before starting work",
            "Update ticket status regularly"
        ],
        "required_files": ["PROJECT_STATUS.md", "AGENTS.md"],
        "optional_files": [],
        "tags": ["minimal", "basic"]
    },

    "testing-focused": {
        "name": "Testing-Focused Agent",
        "description": "Agent specialized in test-driven development and quality assurance",
        "capabilities": AgentCapabilities(
            skills=["skills/testing", "skills/debugging", "skills/code-review"],
            workflows=["workflows/bug-fix", "workflows/feature-development"],
            commands=["commands/analyze-coverage", "commands/create-ticket"]
        ),
        "context_priority": [
            "TESTING.md",
            "PROJECT_STATUS.md",
            "test/ directory",
            "AGENTS.md"
        ],
        "agent_instructions": [
            "Always write tests before implementation (TDD)",
            "Maintain minimum 80% code coverage",
            "Run tests before committing changes",
            "Review test pyramid balance",
            "Update TESTING.md with new patterns"
        ],
        "required_files": ["TESTING.md", "PROJECT_STATUS.md", "AGENTS.md"],
        "optional_files": ["pytest.ini", "jest.config.js", "coverage/"],
        "tags": ["testing", "tdd", "quality", "qa"]
    },

    "backend-developer": {
        "name": "Backend Developer",
        "description": "Full-featured backend development agent with testing and debugging",
        "capabilities": AgentCapabilities(
            skills=["skills/testing", "skills/debugging", "skills/refactoring", "skills/security"],
            workflows=["workflows/feature-development", "workflows/bug-fix", "workflows/release"],
            commands=["commands/create-ticket", "commands/analyze-coverage"]
        ),
        "context_priority": [
            "PROJECT_STATUS.md",
            "TESTING.md",
            "src/ or app/ directory",
            "API documentation",
            "AGENTS.md"
        ],
        "agent_instructions": [
            "Follow TDD practices for all new features",
            "Validate input at API boundaries",
            "Write comprehensive API documentation",
            "Consider security implications of changes",
            "Update PROJECT_STATUS.md with progress"
        ],
        "required_files": ["PROJECT_STATUS.md", "AGENTS.md", "TESTING.md"],
        "optional_files": ["API.md", "SECURITY.md", "requirements.txt", "package.json"],
        "tags": ["backend", "api", "server", "testing"]
    },

    "frontend-developer": {
        "name": "Frontend Developer",
        "description": "Frontend development agent with focus on testing and code review",
        "capabilities": AgentCapabilities(
            skills=["skills/testing", "skills/code-review", "skills/refactoring", "skills/performance"],
            workflows=["workflows/feature-development", "workflows/bug-fix"],
            commands=["commands/create-ticket", "commands/analyze-coverage"]
        ),
        "context_priority": [
            "PROJECT_STATUS.md",
            "TESTING.md",
            "src/components/ or pages/",
            "Design system documentation",
            "AGENTS.md"
        ],
        "agent_instructions": [
            "Write component tests for all UI components",
            "Follow accessibility best practices (WCAG)",
            "Optimize for performance (Core Web Vitals)",
            "Maintain consistent UI/UX patterns",
            "Document component APIs and usage"
        ],
        "required_files": ["PROJECT_STATUS.md", "AGENTS.md", "TESTING.md"],
        "optional_files": ["CONTRIBUTING.md", "package.json", "tsconfig.json"],
        "tags": ["frontend", "ui", "components", "testing"]
    },

    "fullstack-developer": {
        "name": "Full-Stack Developer",
        "description": "Complete full-stack development suite with all core capabilities",
        "capabilities": AgentCapabilities(
            skills=["skills/testing", "skills/debugging", "skills/code-review", "skills/refactoring",
                    "skills/security", "skills/performance"],
            workflows=["workflows/feature-development", "workflows/bug-fix", "workflows/release"],
            commands=["commands/create-ticket", "commands/analyze-coverage", "commands/generate-changelog"]
        ),
        "context_priority": [
            "PROJECT_STATUS.md",
            "TESTING.md",
            "ARCHITECTURE.md",
            "Full codebase",
            "AGENTS.md"
        ],
        "agent_instructions": [
            "Maintain full-stack awareness in all changes",
            "Write tests for both frontend and backend",
            "Consider API contracts when modifying interfaces",
            "Follow security best practices across stack",
            "Document architectural decisions"
        ],
        "required_files": ["PROJECT_STATUS.md", "AGENTS.md", "TESTING.md"],
        "optional_files": ["ARCHITECTURE.md", "SECURITY.md", "API.md"],
        "tags": ["fullstack", "complete", "comprehensive"]
    },

    "devops-engineer": {
        "name": "DevOps Engineer",
        "description": "DevOps-focused agent for deployment, release, and infrastructure",
        "capabilities": AgentCapabilities(
            skills=["skills/testing", "skills/security"],
            workflows=["workflows/release", "workflows/hotfix", "workflows/cicd-setup",
                      "workflows/monitoring-setup", "workflows/dependency-update"],
            commands=["commands/generate-changelog", "commands/create-ticket"]
        ),
        "context_priority": [
            "PROJECT_STATUS.md",
            "CI/CD configuration",
            "Infrastructure as Code",
            "Deployment scripts",
            "AGENTS.md"
        ],
        "agent_instructions": [
            "Follow semantic versioning strictly",
            "Automate all deployment processes",
            "Maintain comprehensive changelog",
            "Monitor system health and performance",
            "Document infrastructure changes"
        ],
        "required_files": ["PROJECT_STATUS.md", "AGENTS.md"],
        "optional_files": ["CHANGELOG.md", ".github/workflows/", "Dockerfile", "docker-compose.yml"],
        "tags": ["devops", "deployment", "release", "infrastructure"]
    },

    "qa-engineer": {
        "name": "QA Engineer",
        "description": "Quality assurance agent focused on testing and bug fixing",
        "capabilities": AgentCapabilities(
            skills=["skills/testing", "skills/debugging", "skills/code-review"],
            workflows=["workflows/bug-fix", "workflows/feature-development"],
            commands=["commands/analyze-coverage", "commands/create-ticket"]
        ),
        "context_priority": [
            "TESTING.md",
            "PROJECT_STATUS.md",
            "test/ directory",
            "Bug reports",
            "AGENTS.md"
        ],
        "agent_instructions": [
            "Write comprehensive test cases for all features",
            "Maintain test documentation and examples",
            "Identify edge cases and boundary conditions",
            "Track and verify bug fixes thoroughly",
            "Report quality metrics regularly"
        ],
        "required_files": ["TESTING.md", "PROJECT_STATUS.md", "AGENTS.md"],
        "optional_files": ["test-plan.md", "bug-reports/"],
        "tags": ["qa", "testing", "quality", "bugs"]
    }
}


def get_template(template_name: str) -> dict:
    """
    Get agent template by name.

    Args:
        template_name: Name of template (e.g., "backend-developer")

    Returns:
        Template dict or None if not found
    """
    return AGENT_TEMPLATES.get(template_name)


def list_templates() -> list:
    """Get list of all available template names"""
    return sorted(AGENT_TEMPLATES.keys())


def create_agent_from_template(template_name: str, agent_name: str = None,
                               author: str = None) -> AgentConfiguration:
    """
    Create an AgentConfiguration from a template.

    Args:
        template_name: Name of template to use
        agent_name: Optional custom name (defaults to template name)
        author: Optional author name

    Returns:
        AgentConfiguration instance

    Raises:
        ValueError: If template not found
    """
    template = get_template(template_name)
    if not template:
        raise ValueError(f"Template not found: {template_name}")

    # Use custom name or template name
    name = agent_name if agent_name else template["name"]

    return AgentConfiguration(
        name=name,
        version="1.0.0",
        description=template["description"],
        created=datetime.now().strftime("%Y-%m-%d"),
        author=author if author else "Proto Gear",
        capabilities=template["capabilities"],
        context_priority=template["context_priority"],
        agent_instructions=template["agent_instructions"],
        required_files=template["required_files"],
        optional_files=template["optional_files"],
        tags=template["tags"],
        status="active"
    )


def get_template_description(template_name: str) -> str:
    """Get short description of a template"""
    template = get_template(template_name)
    if not template:
        return ""
    return template["description"]


def print_available_templates():
    """Print all available templates with descriptions"""
    from .ui_helper import Colors

    print(f"\n{Colors.HEADER}Available Agent Templates:{Colors.ENDC}\n")

    for name in list_templates():
        template = get_template(name)
        cap_count = len(template["capabilities"].all_capabilities())
        print(f"{Colors.CYAN}{name:20}{Colors.ENDC} - {template['description']}")
        print(f"                     ({cap_count} capabilities)")

    print(f"\n{Colors.GRAY}Use with: pg agent create --template <name>{Colors.ENDC}\n")
