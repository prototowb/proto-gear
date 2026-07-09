#!/usr/bin/env python3
"""
Integration script for v0.5.0 templates
Adds CLI flags and generation functions to proto_gear.py
"""

import re
from pathlib import Path


def integrate_templates():
    """Integrate new templates into proto_gear.py"""

    proto_gear_path = Path(__file__).parent / 'core' / 'proto_gear.py'

    print(f"Reading {proto_gear_path}...")
    with open(proto_gear_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Step 1: Add CLI flags
    print("Step 1: Adding CLI flags...")
    cli_flags_pattern = r"(    init_parser\.add_argument\(\s+'--with-capabilities',\s+action='store_true',\s+help='Generate \.proto-gear/ capability system \(skills, workflows, commands\)'\s+\))\s+(    init_parser\.add_argument\(\s+'--no-interactive',)"

    cli_flags_addition = r"""\1
    init_parser.add_argument(
        '--with-contributing',
        action='store_true',
        help='Generate CONTRIBUTING.md with contribution guidelines'
    )
    init_parser.add_argument(
        '--with-security',
        action='store_true',
        help='Generate SECURITY.md with security policies'
    )
    init_parser.add_argument(
        '--with-architecture',
        action='store_true',
        help='Generate ARCHITECTURE.md with system design documentation'
    )
    init_parser.add_argument(
        '--with-coc',
        action='store_true',
        help='Generate CODE_OF_CONDUCT.md with community guidelines'
    )
    \2"""

    content = re.sub(cli_flags_pattern, cli_flags_addition, content, flags=re.MULTILINE)

    if content == original_content:
        print("  ⚠️  CLI flags pattern not found or already added")
    else:
        print("  ✓ CLI flags added")

    # Step 2: Add template generation functions (after generate_branching_doc)
    print("Step 2: Adding template generation functions...")

    generation_functions = '''

def generate_contributing_doc(project_name, ticket_prefix, git_config, generation_date, framework):
    """Generate CONTRIBUTING.md from template"""
    template_path = Path(__file__).parent / 'CONTRIBUTING.template.md'

    if not template_path.exists():
        return None

    try:
        template = template_path.read_text(encoding='utf-8')

        # Basic placeholders
        content = template.replace('{{PROJECT_NAME}}', project_name)
        content = content.replace('{{TICKET_PREFIX}}', ticket_prefix)
        content = content.replace('{{GENERATION_DATE}}', generation_date)
        content = content.replace('{{FRAMEWORK}}', framework or 'Generic')

        # Repository URL
        repo_url = git_config.get('remote_url', 'https://github.com/your-org/your-repo')
        content = content.replace('{{REPOSITORY_URL}}', repo_url)

        # Placeholder defaults for now (can be enhanced later)
        content = content.replace('{{PREREQUISITES}}', '- Git installed\\n- Development environment set up\\n- Dependencies installed')
        content = content.replace('{{SETUP_INSTRUCTIONS}}', 'See README.md for setup instructions')
        content = content.replace('{{VERIFY_COMMAND}}', 'Run your project\\'s test command')
        content = content.replace('{{EXPECTED_OUTPUT}}', 'All tests passing')
        content = content.replace('{{COVERAGE_TARGET}}', '70')
        content = content.replace('{{NEW_CODE_COVERAGE}}', '80')
        content = content.replace('{{RUN_ALL_TESTS}}', 'Run your test suite')
        content = content.replace('{{RUN_UNIT_TESTS}}', 'Run unit tests')
        content = content.replace('{{RUN_INTEGRATION_TESTS}}', 'Run integration tests')
        content = content.replace('{{RUN_E2E_TESTS}}', 'Run E2E tests')
        content = content.replace('{{RUN_COVERAGE}}', 'Run tests with coverage')
        content = content.replace('{{RUN_LINTER}}', 'Run linter')
        content = content.replace('{{AUTO_FIX_COMMAND}}', 'Auto-fix linting issues')
        content = content.replace('{{FORMAT_COMMAND}}', 'Format code')
        content = content.replace('{{NAMING_CONVENTION}}', 'Follow your language conventions')
        content = content.replace('{{FILE_NAMING_CONVENTION}}', 'Use clear, descriptive names')
        content = content.replace('{{CODE_STYLE_GUIDE}}', 'Follow language-specific style guides')
        content = content.replace('{{TEST_EXAMPLE_LANGUAGE}}', 'python')
        content = content.replace('{{TEST_EXAMPLE}}', '# Write clear, descriptive tests')
        content = content.replace('{{RUN_SPECIFIC_TESTS}}', 'Run specific test file')
        content = content.replace('{{RUN_WITH_COVERAGE}}', 'Run with coverage report')
        content = content.replace('{{RUN_WATCH_MODE}}', 'Run in watch mode (if available)')
        content = content.replace('{{DOCUMENTATION_EXAMPLE}}', '# Document your code clearly')
        content = content.replace('{{DOCUMENTATION_STRUCTURE}}', 'See docs/ directory')
        content = content.replace('{{CREATE_PR_INSTRUCTIONS}}', 'Create PR via GitHub interface or gh CLI')
        content = content.replace('{{REVIEW_TURNAROUND}}', '2-3')
        content = content.replace('{{POST_APPROVAL_STEPS}}', 'PR will be merged after approval')
        content = content.replace('{{COMMUNICATION_CHANNELS}}', 'GitHub Issues and Discussions')
        content = content.replace('{{ISSUE_RESPONSE_TIME}}', '2-3 business days')
        content = content.replace('{{PR_RESPONSE_TIME}}', '2-3 business days')
        content = content.replace('{{QUESTION_RESPONSE_TIME}}', 'Best effort')
        content = content.replace('{{REPORTING_MECHANISM}}', 'Contact project maintainers')
        content = content.replace('{{RECOGNITION_METHODS}}', 'Contributors list in README')
        content = content.replace('{{DOCUMENTATION_URL}}', 'See docs/')
        content = content.replace('{{ISSUES_URL}}', repo_url + '/issues')
        content = content.replace('{{DISCUSSION_URL}}', repo_url + '/discussions')
        content = content.replace('{{CHAT_URL}}', 'N/A')
        content = content.replace('{{RELEASE_PROCESS}}', 'See maintainer documentation')
        content = content.replace('{{LICENSE}}', 'the project license')
        content = content.replace('{{CONTACT_INFO}}', 'Open an issue for questions')

        return content
    except Exception as e:
        print(f"Error generating contributing doc: {e}")
        return None


def generate_security_doc(project_name, generation_date):
    """Generate SECURITY.md from template"""
    template_path = Path(__file__).parent / 'SECURITY.template.md'

    if not template_path.exists():
        return None

    try:
        template = template_path.read_text(encoding='utf-8')

        # Basic placeholders
        content = template.replace('{{PROJECT_NAME}}', project_name)
        content = content.replace('{{GENERATION_DATE}}', generation_date)

        # Placeholder defaults
        content = content.replace('{{SECURITY_CONTACT}}', 'security@example.com (update this)')
        content = content.replace('{{SUPPORTED_VERSIONS_TABLE}}', '| Latest | ✅ | Active |')
        content = content.replace('{{SECURITY_REPORTING_CHANNEL}}', 'Email: security@example.com')
        content = content.replace('{{ACKNOWLEDGMENT_TIME}}', '48 hours')
        content = content.replace('{{ASSESSMENT_TIME}}', '5 business')
        content = content.replace('{{UPDATE_FREQUENCY}}', '7')
        content = content.replace('{{RESOLUTION_TARGET}}', '30')
        content = content.replace('{{CRITICAL_RESPONSE_TIME}}', '24 hours')
        content = content.replace('{{CRITICAL_FIX_TIME}}', '7 days')
        content = content.replace('{{HIGH_RESPONSE_TIME}}', '3 days')
        content = content.replace('{{HIGH_FIX_TIME}}', '14 days')
        content = content.replace('{{MEDIUM_RESPONSE_TIME}}', '5 days')
        content = content.replace('{{MEDIUM_FIX_TIME}}', '30 days')
        content = content.replace('{{LOW_RESPONSE_TIME}}', '10 days')
        content = content.replace('{{LOW_FIX_TIME}}', '60 days')
        content = content.replace('{{SECURITY_NOTIFICATION_CHANNELS}}', '- GitHub Security Advisories\\n- Release notes')
        content = content.replace('{{UPDATE_INSTRUCTIONS}}', 'Follow standard update process')
        content = content.replace('{{VERSION_CHECK_COMMAND}}', 'Check application version')
        content = content.replace('{{EXPECTED_VERSION_OUTPUT}}', 'Current version number')
        content = content.replace('{{SECURE_CONFIGURATION}}', 'Use secure defaults')
        content = content.replace('{{FILE_PERMISSIONS}}', 'Restrict file access appropriately')
        content = content.replace('{{MONITORING_RECOMMENDATIONS}}', 'Monitor logs and metrics')
        content = content.replace('{{LOG_RETENTION}}', '90 days')
        content = content.replace('{{DEPENDENCY_SCAN_COMMAND}}', 'Run dependency scanner')
        content = content.replace('{{SAST_COMMAND}}', 'Run static analysis')
        content = content.replace('{{SECURITY_LINT_COMMAND}}', 'Run security linter')
        content = content.replace('{{CURRENT_SECURITY_MEASURES}}', 'Standard security practices')
        content = content.replace('{{KNOWN_LIMITATIONS}}', 'None currently documented')
        content = content.replace('{{PROTECTED_ASSETS}}', 'User data, system resources')
        content = content.replace('{{THREAT_SCENARIOS}}', 'Common attack vectors')
        content = content.replace('{{MITIGATION_STRATEGIES}}', 'Defense in depth')
        content = content.replace('{{DISCLOSURE_TIMELINE}}', '90 days')
        content = content.replace('{{ADVISORY_LOCATION}}', 'GitHub Security Advisories')
        content = content.replace('{{SECURITY_HALL_OF_FAME}}', 'To be established')
        content = content.replace('{{SECURITY_DOCS_URL}}', 'See documentation')
        content = content.replace('{{ADVISORIES_URL}}', 'GitHub Security tab')
        content = content.replace('{{BEST_PRACTICES_URL}}', 'See security documentation')
        content = content.replace('{{SECURITY_TOOLS}}', 'Standard security tooling')
        content = content.replace('{{EMERGENCY_CONTACTS}}', 'security@example.com')
        content = content.replace('{{COMPLIANCE_STANDARDS}}', 'Industry best practices')
        content = content.replace('{{SECURITY_CERTIFICATIONS}}', 'None currently')
        content = content.replace('{{AUDIT_REQUIREMENTS}}', 'Standard audit practices')
        content = content.replace('{{SECURITY_ROADMAP}}', 'Continuous improvement')
        content = content.replace('{{SECURITY_QUESTIONS_CHANNEL}}', 'GitHub Discussions')
        content = content.replace('{{SECURITY_FEEDBACK_CHANNEL}}', 'GitHub Issues')
        content = content.replace('{{ACKNOWLEDGMENTS_LIST}}', 'To be established')
        content = content.replace('{{POLICY_UPDATE_CHANNEL}}', 'GitHub releases')
        content = content.replace('{{POLICY_VERSION}}', '1.0.0')
        content = content.replace('{{LEGAL_DISCLAIMER}}', 'Standard legal disclaimers apply')

        return content
    except Exception as e:
        print(f"Error generating security doc: {e}")
        return None


def generate_architecture_doc(project_name, framework, generation_date):
    """Generate ARCHITECTURE.md from template"""
    template_path = Path(__file__).parent / 'ARCHITECTURE.template.md'

    if not template_path.exists():
        return None

    try:
        template = template_path.read_text(encoding='utf-8')

        # Basic placeholders
        content = template.replace('{{PROJECT_NAME}}', project_name)
        content = template.replace('{{FRAMEWORK}}', framework or 'Generic')
        content = template.replace('{{GENERATION_DATE}}', generation_date)

        # Architecture placeholder defaults (users should customize these)
        content = content.replace('{{PROJECT_DESCRIPTION}}', 'Project description goes here')
        content = content.replace('{{KEY_FEATURES}}', '- Feature 1\\n- Feature 2\\n- Feature 3')
        content = content.replace('{{SYSTEM_CONTEXT_DIAGRAM}}', '[Diagram to be added]')
        content = content.replace('{{EXTERNAL_SYSTEMS}}', 'External dependencies')
        content = content.replace('{{USER_TYPES}}', 'End users, administrators')
        content = content.replace('{{PRINCIPLE_1}}', 'Simplicity')
        content = content.replace('{{PRINCIPLE_1_DESCRIPTION}}', 'Keep it simple')
        content = content.replace('{{PRINCIPLE_2}}', 'Maintainability')
        content = content.replace('{{PRINCIPLE_2_DESCRIPTION}}', 'Easy to maintain')
        content = content.replace('{{PRINCIPLE_3}}', 'Scalability')
        content = content.replace('{{PRINCIPLE_3_DESCRIPTION}}', 'Scales with demand')
        content = content.replace('{{PRINCIPLE_4}}', 'Security')
        content = content.replace('{{PRINCIPLE_4_DESCRIPTION}}', 'Secure by default')
        content = content.replace('{{PERFORMANCE_GOALS}}', 'Fast response times')
        content = content.replace('{{SCALABILITY_GOALS}}', 'Horizontal scaling')
        content = content.replace('{{MAINTAINABILITY_GOALS}}', 'Easy to modify')
        content = content.replace('{{SECURITY_GOALS}}', 'Secure by design')
        content = content.replace('{{RELIABILITY_GOALS}}', 'High availability')
        content = content.replace('{{TRADEOFFS_TABLE}}', '| Example | Chosen | Alternative | Reason |')
        content = content.replace('{{ARCHITECTURE_STYLE}}', 'Layered architecture')
        content = content.replace('{{ARCHITECTURE_CHARACTERISTICS}}', 'Modular, testable, maintainable')
        content = content.replace('{{HIGH_LEVEL_DIAGRAM}}', '[Architecture diagram]')

        # Layer placeholders
        for i in range(1, 4):
            content = content.replace(f'{{{{LAYER_{i}_NAME}}}}', f'Layer {i}')
            content = content.replace(f'{{{{LAYER_{i}_RESPONSIBILITY}}}}', f'Layer {i} responsibilities')
            content = content.replace(f'{{{{LAYER_{i}_COMPONENTS}}}}', f'Layer {i} components')
            content = content.replace(f'{{{{LAYER_{i}_TECH}}}}', f'Layer {i} technologies')

        # Component placeholders
        for i in range(1, 4):
            content = content.replace(f'{{{{COMPONENT_{i}_NAME}}}}', f'Component {i}')
            content = content.replace(f'{{{{COMPONENT_{i}_PURPOSE}}}}', f'Component {i} purpose')
            content = content.replace(f'{{{{COMPONENT_{i}_RESP_1}}}}', f'Responsibility 1')
            content = content.replace(f'{{{{COMPONENT_{i}_RESP_2}}}}', f'Responsibility 2')
            content = content.replace(f'{{{{COMPONENT_{i}_RESP_3}}}}', f'Responsibility 3')
            content = content.replace(f'{{{{COMPONENT_{i}_DEPENDENCIES}}}}', f'Dependencies')
            content = content.replace(f'{{{{COMPONENT_{i}_INTERFACE}}}}', f'// Interface code')
            content = content.replace(f'{{{{COMPONENT_{i}_NOTES}}}}', f'Implementation notes')

        content = content.replace('{{COMPONENT_INTERACTION_DIAGRAM}}', '[Component interactions]')
        content = content.replace('{{PROJECT_STRUCTURE}}', '[Directory structure]')
        content = content.replace('{{STRUCTURE_CONVENTIONS}}', 'Follow standard conventions')
        content = content.replace('{{CODE_LANGUAGE}}', 'python')

        # Data architecture
        content = content.replace('{{CONCEPTUAL_DATA_MODEL}}', '[Data model diagram]')
        content = content.replace('{{LOGICAL_DATA_MODEL}}', '[Logical model]')
        content = content.replace('{{PHYSICAL_DATA_MODEL}}', '[Physical model]')
        content = content.replace('{{PRIMARY_STORAGE}}', 'Database system')
        content = content.replace('{{CACHE_LAYER}}', 'Caching strategy')
        content = content.replace('{{FILE_STORAGE}}', 'File storage approach')
        content = content.replace('{{DATA_FLOW_DIAGRAM}}', '[Data flow]')
        content = content.replace('{{DATA_FLOW_STEP_1}}', 'Data input')
        content = content.replace('{{DATA_FLOW_STEP_2}}', 'Data processing')
        content = content.replace('{{DATA_FLOW_STEP_3}}', 'Data storage')
        content = content.replace('{{DATA_FLOW_STEP_4}}', 'Data output')
        content = content.replace('{{SCHEMA_MANAGEMENT}}', 'Schema versioning')
        content = content.replace('{{MIGRATION_STRATEGY}}', 'Database migrations')
        content = content.replace('{{BACKUP_STRATEGY}}', 'Regular backups')
        content = content.replace('{{RETENTION_POLICY}}', 'Data retention rules')

        # Infrastructure
        content = content.replace('{{DEPLOYMENT_DIAGRAM}}', '[Deployment topology]')
        content = content.replace('{{DEV_ENVIRONMENT}}', 'Development setup')
        content = content.replace('{{STAGING_ENVIRONMENT}}', 'Staging setup')
        content = content.replace('{{PRODUCTION_ENVIRONMENT}}', 'Production setup')
        content = content.replace('{{COMPUTE_INFRASTRUCTURE}}', 'Compute resources')
        content = content.replace('{{NETWORK_INFRASTRUCTURE}}', 'Network setup')
        content = content.replace('{{STORAGE_INFRASTRUCTURE}}', 'Storage configuration')
        content = content.replace('{{MONITORING_INFRASTRUCTURE}}', 'Monitoring tools')
        content = content.replace('{{DEPLOYMENT_PROCESS}}', 'Deployment steps')

        # Security
        content = content.replace('{{SECURITY_LAYERS_DIAGRAM}}', '[Security layers]')
        content = content.replace('{{AUTH_MECHANISM}}', 'Authentication approach')
        content = content.replace('{{AUTHZ_MECHANISM}}', 'Authorization approach')
        content = content.replace('{{SESSION_MANAGEMENT}}', 'Session handling')
        content = content.replace('{{ENCRYPTION_AT_REST}}', 'Data encryption')
        content = content.replace('{{ENCRYPTION_IN_TRANSIT}}', 'TLS/SSL')
        content = content.replace('{{KEY_MANAGEMENT}}', 'Key management')
        content = content.replace('{{FIREWALL_CONFIG}}', 'Firewall rules')
        content = content.replace('{{API_SECURITY}}', 'API security')
        content = content.replace('{{DDOS_PROTECTION}}', 'DDoS mitigation')
        content = content.replace('{{INPUT_VALIDATION}}', 'Input validation')
        content = content.replace('{{OUTPUT_ENCODING}}', 'Output encoding')
        content = content.replace('{{CSRF_PROTECTION}}', 'CSRF protection')
        content = content.replace('{{XSS_PREVENTION}}', 'XSS prevention')

        # Patterns
        for i in range(1, 4):
            content = content.replace(f'{{{{PATTERN_{i}_NAME}}}}', f'Pattern {i}')
            content = content.replace(f'{{{{PATTERN_{i}_USE_CASE}}}}', f'When to use pattern {i}')
            content = content.replace(f'{{{{PATTERN_{i}_EXAMPLE}}}}', f'// Pattern {i} example')
            content = content.replace(f'{{{{PATTERN_{i}_BENEFITS}}}}', f'Pattern {i} benefits')

        for i in range(1, 4):
            content = content.replace(f'{{{{ORG_PATTERN_{i}}}}}', f'Organization pattern {i}')
            content = content.replace(f'{{{{ORG_PATTERN_{i}_DESC}}}}', f'Description {i}')

        # Technology stack
        content = content.replace('{{LANGUAGES_TABLE}}', '| Language | Version | Use |')
        content = content.replace('{{FRAMEWORK_VERSION}}', 'Latest')
        content = content.replace('{{FRAMEWORK_DESCRIPTION}}', 'Framework details')
        content = content.replace('{{LIBRARIES_TABLE}}', '| Library | Version | Purpose |')
        content = content.replace('{{RUNTIME}}', 'Runtime environment')
        content = content.replace('{{PACKAGE_MANAGER}}', 'Package manager')
        content = content.replace('{{BUILD_TOOL}}', 'Build tool')
        content = content.replace('{{CICD_PLATFORM}}', 'CI/CD platform')
        content = content.replace('{{RECOMMENDED_IDE}}', 'Recommended IDE')
        content = content.replace('{{LINTER}}', 'Linter tool')
        content = content.replace('{{FORMATTER}}', 'Code formatter')
        content = content.replace('{{TEST_FRAMEWORK}}', 'Testing framework')

        # Other sections
        content = content.replace('{{ARCHITECTURAL_DECISIONS}}', 'See ADR documents')
        content = content.replace('{{PERFORMANCE_REQUIREMENTS}}', 'Performance targets')
        content = content.replace('{{CACHING_STRATEGY}}', 'Caching approach')
        content = content.replace('{{DATABASE_OPTIMIZATION}}', 'DB optimization')
        content = content.replace('{{NETWORK_OPTIMIZATION}}', 'Network optimization')
        content = content.replace('{{CODE_OPTIMIZATION}}', 'Code optimization')
        content = content.replace('{{PERFORMANCE_MONITORING}}', 'Performance monitoring')
        content = content.replace('{{PERFORMANCE_TARGETS}}', '| Metric | Target | Current |')
        content = content.replace('{{HORIZONTAL_SCALING}}', 'Scale horizontally')
        content = content.replace('{{VERTICAL_SCALING}}', 'Scale vertically')
        content = content.replace('{{AUTO_SCALING}}', 'Auto-scaling rules')
        content = content.replace('{{BOTTLENECKS_TABLE}}', '| Bottleneck | Impact | Mitigation |')
        content = content.replace('{{LOAD_BALANCING_STRATEGY}}', 'Load balancing')
        content = content.replace('{{UPTIME_SLA}}', '99.9%')
        content = content.replace('{{MTBF}}', 'Mean time between failures')
        content = content.replace('{{MTTR}}', 'Mean time to recovery')
        content = content.replace('{{RTO}}', 'Recovery time objective')
        content = content.replace('{{RPO}}', 'Recovery point objective')
        content = content.replace('{{REDUNDANCY_STRATEGY}}', 'Redundancy approach')
        content = content.replace('{{FAILOVER_MECHANISM}}', 'Failover process')
        content = content.replace('{{HEALTH_CHECKS}}', 'Health check endpoints')
        content = content.replace('{{DISASTER_RECOVERY_PLAN}}', 'DR plan')
        content = content.replace('{{METRICS_SYSTEM}}', 'Metrics collection')
        content = content.replace('{{LOGGING_SYSTEM}}', 'Logging infrastructure')
        content = content.replace('{{TRACING_SYSTEM}}', 'Distributed tracing')
        content = content.replace('{{ALERTING_SYSTEM}}', 'Alerting rules')
        content = content.replace('{{KEY_METRICS}}', 'Key performance indicators')
        content = content.replace('{{LOGGING_STRATEGY}}', 'Logging approach')
        content = content.replace('{{PLANNED_IMPROVEMENTS}}', 'Future enhancements')
        content = content.replace('{{TECHNICAL_DEBT}}', 'Known tech debt')
        content = content.replace('{{MIGRATION_PATH}}', 'Migration strategy')
        content = content.replace('{{CONSTRAINTS}}', 'Current constraints')
        content = content.replace('{{LIMITATIONS}}', 'Known limitations')
        content = content.replace('{{ASSUMPTIONS}}', 'Design assumptions')
        content = content.replace('{{GLOSSARY_TABLE}}', '| Term | Definition |')
        content = content.replace('{{INTERNAL_DOCS}}', 'Internal documentation')
        content = content.replace('{{EXTERNAL_RESOURCES}}', 'External references')
        content = content.replace('{{STANDARDS}}', 'Related standards')
        content = content.replace('{{ADDITIONAL_DIAGRAMS}}', 'Additional diagrams')
        content = content.replace('{{CODE_EXAMPLES}}', 'Code examples')
        content = content.replace('{{CONFIG_SAMPLES}}', 'Configuration samples')
        content = content.replace('{{VERSION_HISTORY}}', '| 1.0.0 | ' + generation_date + ' | Initial | Proto Gear |')

        return content
    except Exception as e:
        print(f"Error generating architecture doc: {e}")
        return None


def generate_code_of_conduct_doc(project_name, generation_date):
    """Generate CODE_OF_CONDUCT.md from template"""
    template_path = Path(__file__).parent / 'CODE_OF_CONDUCT.template.md'

    if not template_path.exists():
        return None

    try:
        template = template_path.read_text(encoding='utf-8')

        # Basic placeholders
        content = template.replace('{{PROJECT_NAME}}', project_name)
        content = content.replace('{{GENERATION_DATE}}', generation_date)

        # CoC placeholder defaults
        content = content.replace('{{REPOSITORY_URL}}', 'https://github.com/your-org/your-repo')
        content = content.replace('{{COMMUNICATION_CHANNELS}}', '- GitHub Discussions\\n- Issue tracker')
        content = content.replace('{{CONDUCT_CONTACT}}', 'conduct@example.com (update this)')
        content = content.replace('{{ANONYMOUS_REPORTING_METHOD}}', 'Anonymous reporting form (to be set up)')
        content = content.replace('{{URGENT_CONTACT}}', 'conduct@example.com')
        content = content.replace('{{ACKNOWLEDGMENT_TIME}}', '48 hours')
        content = content.replace('{{INITIAL_RESPONSE_TIME}}', '5 business days')
        content = content.replace('{{RESOLUTION_TIME}}', '30 days')
        content = content.replace('{{APPEAL_CONTACT}}', 'conduct-appeal@example.com')
        content = content.replace('{{APPEAL_WINDOW}}', '14')
        content = content.replace('{{APPEAL_DECISION_TIME}}', '30 days')
        content = content.replace('{{COMMUNITY_LEADERS}}', 'To be designated')
        content = content.replace('{{GOVERNANCE_MODEL}}', 'See project governance')
        content = content.replace('{{DECISION_MAKING_PROCESS}}', 'Consensus-based decision making')
        content = content.replace('{{RECOGNITION_PROGRAM}}', 'Contributors list and acknowledgments')
        content = content.replace('{{KINDNESS_HALL_OF_FAME}}', 'To be established')
        content = content.replace('{{SUPPORT_CHANNEL_1}}', 'GitHub Discussions')
        content = content.replace('{{SUPPORT_CHANNEL_2}}', 'Issue tracker')
        content = content.replace('{{SUPPORT_CHANNEL_3}}', 'Community forum')
        content = content.replace('{{INCLUSIVE_LANGUAGE_URL}}', 'https://example.com/inclusive-language')
        content = content.replace('{{ALLY_SKILLS_URL}}', 'https://example.com/ally-skills')
        content = content.replace('{{BIAS_URL}}', 'https://example.com/unconscious-bias')
        content = content.replace('{{AMENDMENT_PROCESS}}', 'Submit PR with proposed changes')
        content = content.replace('{{VERSION_HISTORY}}', '| 1.0.0 | ' + generation_date + ' | Initial version | Proto Gear |')
        content = content.replace('{{QUESTIONS_CONTACT}}', 'conduct@example.com')
        content = content.replace('{{ACCESSIBILITY_COMMITMENT}}', 'Committed to accessibility')
        content = content.replace('{{ACCESSIBILITY_CONTACT}}', 'accessibility@example.com')

        return content
    except Exception as e:
        print(f"Error generating code of conduct: {e}")
        return None

'''

    # Find where to insert (after generate_branching_doc function)
    insert_marker = r"(def generate_branching_doc\(.*?\n.*?\n(?:.*?\n)*?        return None\n)\n\n"

    match = re.search(insert_marker, content, re.MULTILINE | re.DOTALL)
    if match:
        insert_position = match.end()
        content = content[:insert_position] + generation_functions + content[insert_position:]
        print("  ✓ Template generation functions added")
    else:
        print("  ⚠️  Could not find insertion point for generation functions")

    # Step 3: Update run_simple_protogear_init() function signature
    print("Step 3: Updating function signatures...")

    # Update function signature
    old_sig = r"def run_simple_protogear_init\(dry_run=False, with_branching=False, ticket_prefix=None,\s*with_capabilities=False, capabilities_config=None\):"
    new_sig = "def run_simple_protogear_init(dry_run=False, with_branching=False, ticket_prefix=None,\n                              with_capabilities=False, capabilities_config=None,\n                              with_contributing=False, with_security=False,\n                              with_architecture=False, with_coc=False):"

    content = re.sub(old_sig, new_sig, content)
    print("  ✓ Function signature updated")

    # Step 4: Add template generation calls (this is more complex, so we'll add a marker comment for manual review)
    print("Step 4: Adding marker for template generation calls...")
    print("  ⚠️  Manual review needed: Add template generation calls after BRANCHING.md generation")

    # Step 5: Update CLI argument passing
    print("Step 5: Updating CLI argument passing...")

    # For wizard path
    wizard_pattern = r"(result = run_simple_protogear_init\(\s+dry_run=args\.dry_run,\s+with_branching=wizard_config\.get\('with_branching', False\),\s+ticket_prefix=wizard_config\.get\('ticket_prefix'\),\s+with_capabilities=wizard_config\.get\('with_capabilities', False\),\s+capabilities_config=wizard_config\.get\('capabilities_config'\))"

    wizard_replacement = r"""\1,
                    with_contributing=wizard_config.get('with_contributing', False),
                    with_security=wizard_config.get('with_security', False),
                    with_architecture=wizard_config.get('with_architecture', False),
                    with_coc=wizard_config.get('with_coc', False)"""

    content = re.sub(wizard_pattern, wizard_replacement, content, flags=re.MULTILINE)

    # For CLI path
    cli_pattern = r"(result = run_simple_protogear_init\(\s+dry_run=args\.dry_run,\s+with_branching=args\.with_branching,\s+ticket_prefix=args\.ticket_prefix,\s+with_capabilities=args\.with_capabilities)"

    cli_replacement = r"""\1,
                    with_contributing=args.with_contributing,
                    with_security=args.with_security,
                    with_architecture=args.with_architecture,
                    with_coc=args.with_coc"""

    content = re.sub(cli_pattern, cli_replacement, content, flags=re.MULTILINE)
    print("  ✓ CLI argument passing updated")

    # Write the modified content
    print(f"\nWriting modified content to {proto_gear_path}...")
    with open(proto_gear_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n✅ Integration complete!")
    print("\nNext steps:")
    print("1. Review the changes in proto_gear.py")
    print("2. Add template generation calls in run_simple_protogear_init() after BRANCHING.md generation")
    print("3. Test with: pg init --dry-run --with-contributing")


if __name__ == '__main__':
    integrate_templates()
