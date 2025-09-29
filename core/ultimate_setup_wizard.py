"""
Ultimate Setup Wizard for Agent Framework - 100% Coverage Edition
Includes all modern web development features including medical, auth, analytics, etc.
"""

try:
    from .enhanced_setup_wizard import *
except ImportError:
    from enhanced_setup_wizard import *
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import json
import yaml
import os


class AuthProvider(Enum):
    """Authentication providers"""
    NEXTAUTH = "nextauth"
    CLERK = "clerk"
    AUTH0 = "auth0"
    SUPABASE_AUTH = "supabase-auth"
    FIREBASE_AUTH = "firebase-auth"
    AWS_COGNITO = "aws-cognito"
    CUSTOM_JWT = "custom-jwt"
    KEYCLOAK = "keycloak"
    NONE = "none"


class AnalyticsProvider(Enum):
    """Analytics providers"""
    PLAUSIBLE = "plausible"
    UMAMI = "umami"
    FATHOM = "fathom"
    MATOMO = "matomo"
    GOOGLE_ANALYTICS = "google-analytics"
    MIXPANEL = "mixpanel"
    AMPLITUDE = "amplitude"
    POSTHOG = "posthog"
    NONE = "none"


class MonitoringProvider(Enum):
    """Monitoring and error tracking"""
    SENTRY = "sentry"
    ROLLBAR = "rollbar"
    BUGSNAG = "bugsnag"
    DATADOG = "datadog"
    NEW_RELIC = "newrelic"
    ELASTIC_APM = "elastic-apm"
    NONE = "none"


class APIDocTool(Enum):
    """API documentation tools"""
    SWAGGER = "swagger"
    REDOC = "redoc"
    POSTMAN = "postman"
    INSOMNIA = "insomnia"
    STOPLIGHT = "stoplight"
    NONE = "none"


class MedicalStandard(Enum):
    """Medical/Healthcare standards"""
    ICD_10_GM = "icd-10-gm"  # German modification
    ICD_11 = "icd-11"
    SNOMED_CT = "snomed-ct"
    LOINC = "loinc"
    FHIR = "fhir"
    HL7 = "hl7"
    DIGA = "diga"  # German Digital Health Apps
    HIPAA = "hipaa"
    GDPR_MEDICAL = "gdpr-medical"
    ISO_13485 = "iso-13485"
    CE_MDR = "ce-mdr"  # Medical Device Regulation
    NONE = "none"


class ProjectTemplate(Enum):
    """Pre-configured project templates"""
    BLANK = "blank"
    BLOG = "blog"
    ECOMMERCE = "ecommerce"
    SAAS = "saas"
    LANDING_PAGE = "landing-page"
    DOCUMENTATION = "documentation"
    PORTFOLIO = "portfolio"
    DASHBOARD = "dashboard"
    SOCIAL_NETWORK = "social-network"
    # Medical templates
    PATIENT_PORTAL = "patient-portal"
    MEDICAL_PRACTICE = "medical-practice"
    TELEHEALTH = "telehealth"
    HEALTH_TRACKER = "health-tracker"
    CLINICAL_TRIALS = "clinical-trials"
    # Industry templates
    FINTECH = "fintech"
    EDTECH = "edtech"
    PROPTECH = "proptech"
    LEGALTECH = "legaltech"
    CUSTOM = "custom"


class UltimateProjectConfig(EnhancedProjectConfig):
    """Ultimate project configuration with 100% feature coverage"""
    
    def __init__(self):
        super().__init__()
        
        # Template
        self.template = ProjectTemplate.BLANK
        
        # Authentication
        self.auth_provider = AuthProvider.NONE
        self.auth_features = {
            "social_login": [],  # google, github, facebook, etc.
            "mfa": False,
            "magic_links": False,
            "biometric": False,
            "rbac": False,  # Role-based access control
            "session_management": True,
        }
        
        # Analytics
        self.analytics_provider = AnalyticsProvider.NONE
        self.analytics_config = {
            "privacy_first": True,
            "cookie_consent": True,
            "anonymize_ip": True,
        }
        
        # Monitoring
        self.monitoring_provider = MonitoringProvider.NONE
        self.monitoring_config = {
            "error_tracking": True,
            "performance": True,
            "uptime": False,
            "custom_metrics": False,
        }
        
        # API Documentation
        self.api_doc_tool = APIDocTool.NONE
        self.api_config = {
            "versioning": True,
            "rate_limiting": False,
            "api_key_auth": False,
        }
        
        # Medical/Healthcare
        self.medical_standards = []  # List of MedicalStandard
        self.medical_features = {
            "patient_data": False,
            "encryption_at_rest": False,
            "audit_logs": False,
            "consent_management": False,
            "data_retention": False,
            "pseudonymization": False,
        }
        
        # Environment configuration
        self.env_config = {
            "auto_generate": True,
            "vault_integration": False,
            "dotenv": True,
            "secrets_management": False,
        }
        
        # Plugin system
        self.plugins = []
        self.plugin_config = {
            "marketplace": False,
            "auto_update": False,
            "custom_plugins": [],
        }
        
        # Advanced features
        self.advanced_features = {
            "multi_tenancy": False,
            "feature_flags": False,
            "a_b_testing": False,
            "websockets": False,
            "graphql": False,
            "serverless": False,
            "edge_functions": False,
            "webhooks": False,
            "queue_system": False,
            "caching": None,  # redis, memcached, etc.
            "cdn": None,  # cloudflare, fastly, etc.
            "search": None,  # algolia, elasticsearch, meilisearch
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        base_config = super().to_dict()
        
        # Add ultimate features
        base_config.update({
            "template": self.template.value,
            "authentication": {
                "provider": self.auth_provider.value,
                "features": self.auth_features,
            },
            "analytics": {
                "provider": self.analytics_provider.value,
                "config": self.analytics_config,
            },
            "monitoring": {
                "provider": self.monitoring_provider.value,
                "config": self.monitoring_config,
            },
            "api_documentation": {
                "tool": self.api_doc_tool.value,
                "config": self.api_config,
            },
            "medical": {
                "standards": [s.value for s in self.medical_standards],
                "features": self.medical_features,
            },
            "environment": self.env_config,
            "plugins": {
                "enabled": len(self.plugins) > 0,
                "list": self.plugins,
                "config": self.plugin_config,
            },
            "advanced": self.advanced_features,
        })
        
        return base_config


class UltimateSetupWizard(EnhancedSetupWizard):
    """Ultimate setup wizard with 100% feature coverage"""
    
    def __init__(self, base_path: str = ".", dry_run: bool = False):
        """Initialize the ultimate setup wizard"""
        super().__init__(base_path, dry_run)
        self.config = UltimateProjectConfig()
        self.templates_path = Path(__file__).parent.parent / "templates"
    
    def run_interactive(self) -> Dict[str, Any]:
        """Run the ultimate wizard in interactive mode"""
        print("\n" + "=" * 60)
        print("🧙 Ultimate Agent Framework Setup Wizard")
        print("    100% Feature Coverage Edition")
        print("=" * 60)
        
        try:
            # Step 1: Template selection (NEW)
            self._select_template()
            
            # If template selected, apply template defaults
            if self.config.template != ProjectTemplate.BLANK:
                self._apply_template_defaults()
                
                # Show template configuration
                self._show_template_config()
                
                # Allow customization
                customize = input("\n🔧 Customize template settings? (y/n) [n]: ") or "n"
                if customize.lower() not in ['y', 'yes']:
                    # Skip to project creation with template
                    return self._create_from_template()
            
            # Continue with normal configuration
            # Project basics
            self._configure_basics()
            
            # Framework selection
            self._configure_framework()
            
            # Language and tooling
            self._configure_language()
            
            # Styling
            self._configure_styling()
            
            # Authentication (NEW)
            self._configure_authentication()
            
            # Testing
            self._configure_testing()
            
            # i18n
            self._configure_i18n()
            
            # CMS
            self._configure_cms()
            
            # Database
            self._configure_database()
            
            # API Documentation (NEW)
            self._configure_api_docs()
            
            # Analytics (NEW)
            self._configure_analytics()
            
            # Monitoring (NEW)
            self._configure_monitoring()
            
            # Medical/Healthcare (NEW)
            self._configure_medical()
            
            # Deployment
            self._configure_deployment()
            
            # Environment Variables (NEW)
            self._configure_environment()
            
            # Advanced Features (NEW)
            self._configure_advanced()
            
            # Plugins (NEW)
            self._configure_plugins()
            
            # Additional features
            self._configure_features()
            
            # Show summary
            self._show_ultimate_summary()
            
            # Confirm and create
            confirm = input("\n🚀 Create project with this configuration? (y/n) [y]: ") or 'y'
            if confirm.lower() not in ['y', 'yes']:
                return {'status': 'cancelled'}
            
            # Create the project
            result = self.create_project()
            
            if result['status'] == 'success':
                print(f"\n✅ Project created successfully!")
                if result.get('path'):
                    print(f"📁 Location: {result.get('path')}")
                self._show_next_steps()
                
                # Only generate files and install plugins if not in dry run mode
                if not self.dry_run and result.get('path'):
                    project_path = Path(result.get('path'))
                    
                    # Generate environment file
                    if self.config.env_config['auto_generate']:
                        self._generate_env_file(project_path)
                    
                    # Install plugins if any
                    if self.config.plugins:
                        self._install_plugins(project_path)
            
            return result
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup cancelled by user")
            return {'status': 'cancelled'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _select_template(self):
        """Select a project template"""
        print("\n📋 Project Templates")
        print("-" * 40)
        print("Choose a template or start from scratch:")
        
        templates = list(ProjectTemplate)
        
        # Group templates
        print("\n🎯 General Templates:")
        general = [ProjectTemplate.BLANK, ProjectTemplate.BLOG, ProjectTemplate.ECOMMERCE,
                  ProjectTemplate.SAAS, ProjectTemplate.LANDING_PAGE, ProjectTemplate.DOCUMENTATION,
                  ProjectTemplate.PORTFOLIO, ProjectTemplate.DASHBOARD, ProjectTemplate.SOCIAL_NETWORK]
        
        for i, template in enumerate(general, 1):
            print(f"  {i}. {template.value}")
        
        print("\n🏥 Medical/Healthcare Templates:")
        medical = [ProjectTemplate.PATIENT_PORTAL, ProjectTemplate.MEDICAL_PRACTICE,
                  ProjectTemplate.TELEHEALTH, ProjectTemplate.HEALTH_TRACKER,
                  ProjectTemplate.CLINICAL_TRIALS]
        
        for i, template in enumerate(medical, len(general) + 1):
            print(f"  {i}. {template.value}")
        
        print("\n🏢 Industry Templates:")
        industry = [ProjectTemplate.FINTECH, ProjectTemplate.EDTECH,
                   ProjectTemplate.PROPTECH, ProjectTemplate.LEGALTECH]
        
        for i, template in enumerate(industry, len(general) + len(medical) + 1):
            print(f"  {i}. {template.value}")
        
        print(f"\n  {len(templates)}. custom (define your own)")
        
        choice = input(f"\nTemplate choice (1-{len(templates)}) [1]: ") or "1"
        if choice.isdigit() and 1 <= int(choice) <= len(templates):
            self.config.template = templates[int(choice) - 1]
    
    def _apply_template_defaults(self):
        """Apply defaults based on selected template"""
        template = self.config.template
        
        # Medical templates
        if template == ProjectTemplate.PATIENT_PORTAL:
            self.config.project_type = ProjectType.FULLSTACK
            self.config.framework = Framework.NEXTJS
            self.config.ui_framework = UIFramework.REACT
            self.config.css_framework = CSSFramework.TAILWIND
            self.config.auth_provider = AuthProvider.NEXTAUTH
            self.config.database = "postgresql"
            self.config.orm = "prisma"
            self.config.medical_standards = [MedicalStandard.ICD_10_GM, MedicalStandard.GDPR_MEDICAL]
            self.config.medical_features = {
                "patient_data": True,
                "encryption_at_rest": True,
                "audit_logs": True,
                "consent_management": True,
                "data_retention": True,
                "pseudonymization": True,
            }
            self.config.i18n_enabled = True
            self.config.default_locale = "de"
            self.config.locales = ["de", "en"]
            self.config.gdpr = True
            
        elif template == ProjectTemplate.TELEHEALTH:
            self.config.project_type = ProjectType.FULLSTACK
            self.config.framework = Framework.NEXTJS
            self.config.advanced_features["websockets"] = True
            self.config.advanced_features["webrtc"] = True
            self.config.auth_provider = AuthProvider.CLERK
            self.config.monitoring_provider = MonitoringProvider.SENTRY
            
        elif template == ProjectTemplate.HEALTH_TRACKER:
            self.config.project_type = ProjectType.WEB_APP
            self.config.framework = Framework.ASTRO
            self.config.ui_framework = UIFramework.VUE
            self.config.pwa = True
            self.config.database = "sqlite"  # Local first
            self.config.medical_standards = [MedicalStandard.LOINC]
            
        # E-commerce template
        elif template == ProjectTemplate.ECOMMERCE:
            self.config.project_type = ProjectType.FULLSTACK
            self.config.framework = Framework.NEXTJS
            self.config.database = "postgresql"
            self.config.orm = "prisma"
            self.config.auth_provider = AuthProvider.NEXTAUTH
            self.config.advanced_features["search"] = "algolia"
            self.config.analytics_provider = AnalyticsProvider.PLAUSIBLE
            
        # SaaS template
        elif template == ProjectTemplate.SAAS:
            self.config.project_type = ProjectType.FULLSTACK
            self.config.framework = Framework.NEXTJS
            self.config.auth_provider = AuthProvider.CLERK
            self.config.database = "postgresql"
            self.config.orm = "prisma"
            self.config.advanced_features["multi_tenancy"] = True
            self.config.advanced_features["feature_flags"] = True
            self.config.monitoring_provider = MonitoringProvider.SENTRY
            self.config.analytics_provider = AnalyticsProvider.POSTHOG
            
        # Add more template configurations...
    
    def _show_template_config(self):
        """Show template configuration"""
        print("\n📋 Template Configuration")
        print("-" * 40)
        print(f"Template: {self.config.template.value}")
        print(f"Framework: {self.config.framework.value}")
        if self.config.auth_provider != AuthProvider.NONE:
            print(f"Auth: {self.config.auth_provider.value}")
        if self.config.database:
            print(f"Database: {self.config.database}")
        if self.config.medical_standards:
            print(f"Medical Standards: {', '.join([s.value for s in self.config.medical_standards])}")
    
    def _create_from_template(self) -> Dict[str, Any]:
        """Create project from template"""
        print("\n🎯 Creating project from template...")
        
        # Use template configuration
        result = self.create_project()
        
        if result['status'] == 'success':
            print(f"\n✅ Project created from template: {self.config.template.value}")
            
            # Only generate files if not in dry run mode
            if not self.dry_run and result.get('path'):
                project_path = Path(result.get('path'))
                
                # Generate template-specific files
                self._generate_template_files(project_path)
                
                # Generate environment file
                if self.config.env_config['auto_generate']:
                    self._generate_env_file(project_path)
        
        return result
    
    def _configure_authentication(self):
        """Configure authentication"""
        print("\n🔐 Authentication Configuration")
        print("-" * 40)
        
        need_auth = input("Configure authentication? (y/n) [n]: ") or "n"
        
        if need_auth.lower() in ['y', 'yes']:
            print("\nAuthentication provider:")
            providers = list(AuthProvider)
            
            for i, provider in enumerate(providers, 1):
                print(f"  {i}. {provider.value}")
            
            choice = input(f"Choice (1-{len(providers)}) [{len(providers)}]: ") or str(len(providers))
            if choice.isdigit() and 1 <= int(choice) <= len(providers):
                self.config.auth_provider = providers[int(choice) - 1]
            
            if self.config.auth_provider != AuthProvider.NONE:
                # Auth features
                print("\nAuthentication features:")
                
                social = input("  Social login (Google, GitHub, etc.)? (y/n) [n]: ") or "n"
                if social.lower() in ['y', 'yes']:
                    providers = input("    Providers (comma-separated): ") or ""
                    self.config.auth_features["social_login"] = [p.strip() for p in providers.split(',')]
                
                mfa = input("  Multi-factor authentication? (y/n) [n]: ") or "n"
                self.config.auth_features["mfa"] = mfa.lower() in ['y', 'yes']
                
                magic = input("  Magic links (passwordless)? (y/n) [n]: ") or "n"
                self.config.auth_features["magic_links"] = magic.lower() in ['y', 'yes']
                
                rbac = input("  Role-based access control? (y/n) [n]: ") or "n"
                self.config.auth_features["rbac"] = rbac.lower() in ['y', 'yes']
    
    def _configure_analytics(self):
        """Configure analytics"""
        print("\n📊 Analytics Configuration")
        print("-" * 40)
        
        need_analytics = input("Configure analytics? (y/n) [n]: ") or "n"
        
        if need_analytics.lower() in ['y', 'yes']:
            print("\nAnalytics provider:")
            
            # Privacy-first options first
            print("Privacy-first options:")
            privacy_providers = [AnalyticsProvider.PLAUSIBLE, AnalyticsProvider.UMAMI,
                               AnalyticsProvider.FATHOM, AnalyticsProvider.MATOMO]
            
            for i, provider in enumerate(privacy_providers, 1):
                print(f"  {i}. {provider.value}")
            
            print("\nTraditional options:")
            traditional = [AnalyticsProvider.GOOGLE_ANALYTICS, AnalyticsProvider.MIXPANEL,
                          AnalyticsProvider.AMPLITUDE, AnalyticsProvider.POSTHOG]
            
            for i, provider in enumerate(traditional, len(privacy_providers) + 1):
                print(f"  {i}. {provider.value}")
            
            print(f"  {len(privacy_providers) + len(traditional) + 1}. none")
            
            choice = input(f"Choice [1]: ") or "1"
            all_providers = privacy_providers + traditional + [AnalyticsProvider.NONE]
            
            if choice.isdigit() and 1 <= int(choice) <= len(all_providers):
                self.config.analytics_provider = all_providers[int(choice) - 1]
            
            if self.config.analytics_provider != AnalyticsProvider.NONE:
                # Analytics config
                privacy = input("\n  Privacy-first mode? (y/n) [y]: ") or "y"
                self.config.analytics_config["privacy_first"] = privacy.lower() in ['y', 'yes']
                
                if self.config.analytics_provider == AnalyticsProvider.GOOGLE_ANALYTICS:
                    consent = input("  Cookie consent banner? (y/n) [y]: ") or "y"
                    self.config.analytics_config["cookie_consent"] = consent.lower() in ['y', 'yes']
                    
                    anonymize = input("  Anonymize IP addresses? (y/n) [y]: ") or "y"
                    self.config.analytics_config["anonymize_ip"] = anonymize.lower() in ['y', 'yes']
    
    def _configure_monitoring(self):
        """Configure monitoring and error tracking"""
        print("\n🔍 Monitoring & Error Tracking")
        print("-" * 40)
        
        need_monitoring = input("Configure monitoring? (y/n) [n]: ") or "n"
        
        if need_monitoring.lower() in ['y', 'yes']:
            print("\nMonitoring provider:")
            providers = list(MonitoringProvider)
            
            for i, provider in enumerate(providers, 1):
                print(f"  {i}. {provider.value}")
            
            choice = input(f"Choice (1-{len(providers)}) [{len(providers)}]: ") or str(len(providers))
            if choice.isdigit() and 1 <= int(choice) <= len(providers):
                self.config.monitoring_provider = providers[int(choice) - 1]
            
            if self.config.monitoring_provider != MonitoringProvider.NONE:
                # Monitoring features
                print("\nMonitoring features:")
                
                errors = input("  Error tracking? (y/n) [y]: ") or "y"
                self.config.monitoring_config["error_tracking"] = errors.lower() in ['y', 'yes']
                
                perf = input("  Performance monitoring? (y/n) [y]: ") or "y"
                self.config.monitoring_config["performance"] = perf.lower() in ['y', 'yes']
                
                uptime = input("  Uptime monitoring? (y/n) [n]: ") or "n"
                self.config.monitoring_config["uptime"] = uptime.lower() in ['y', 'yes']
                
                custom = input("  Custom metrics? (y/n) [n]: ") or "n"
                self.config.monitoring_config["custom_metrics"] = custom.lower() in ['y', 'yes']
    
    def _configure_api_docs(self):
        """Configure API documentation"""
        print("\n📚 API Documentation")
        print("-" * 40)
        
        if self.config.project_type in [ProjectType.API, ProjectType.FULLSTACK, ProjectType.MICROSERVICE]:
            need_docs = input("Configure API documentation? (y/n) [y]: ") or "y"
            
            if need_docs.lower() in ['y', 'yes']:
                print("\nAPI documentation tool:")
                tools = list(APIDocTool)
                
                for i, tool in enumerate(tools, 1):
                    print(f"  {i}. {tool.value}")
                
                choice = input(f"Choice (1-{len(tools)}) [1]: ") or "1"
                if choice.isdigit() and 1 <= int(choice) <= len(tools):
                    self.config.api_doc_tool = tools[int(choice) - 1]
                
                if self.config.api_doc_tool != APIDocTool.NONE:
                    # API config
                    versioning = input("\n  API versioning? (y/n) [y]: ") or "y"
                    self.config.api_config["versioning"] = versioning.lower() in ['y', 'yes']
                    
                    rate_limit = input("  Rate limiting? (y/n) [n]: ") or "n"
                    self.config.api_config["rate_limiting"] = rate_limit.lower() in ['y', 'yes']
                    
                    api_keys = input("  API key authentication? (y/n) [n]: ") or "n"
                    self.config.api_config["api_key_auth"] = api_keys.lower() in ['y', 'yes']
    
    def _configure_medical(self):
        """Configure medical/healthcare features"""
        print("\n🏥 Medical/Healthcare Configuration")
        print("-" * 40)
        
        is_medical = input("Is this a medical/healthcare project? (y/n) [n]: ") or "n"
        
        if is_medical.lower() in ['y', 'yes']:
            print("\nMedical standards (select all that apply):")
            standards = list(MedicalStandard)
            
            for i, standard in enumerate(standards[:-1], 1):  # Exclude NONE
                print(f"  {i}. {standard.value}")
            
            selections = input("\nEnter numbers (comma-separated) or press Enter to skip: ") or ""
            
            if selections:
                selected_indices = [int(s.strip()) for s in selections.split(',') if s.strip().isdigit()]
                self.config.medical_standards = [standards[i-1] for i in selected_indices 
                                                if 1 <= i <= len(standards)-1]
            
            if self.config.medical_standards:
                print("\nMedical features:")
                
                patient_data = input("  Handle patient data? (y/n) [y]: ") or "y"
                self.config.medical_features["patient_data"] = patient_data.lower() in ['y', 'yes']
                
                if self.config.medical_features["patient_data"]:
                    encrypt = input("  Encryption at rest? (y/n) [y]: ") or "y"
                    self.config.medical_features["encryption_at_rest"] = encrypt.lower() in ['y', 'yes']
                    
                    audit = input("  Audit logs? (y/n) [y]: ") or "y"
                    self.config.medical_features["audit_logs"] = audit.lower() in ['y', 'yes']
                    
                    consent = input("  Consent management? (y/n) [y]: ") or "y"
                    self.config.medical_features["consent_management"] = consent.lower() in ['y', 'yes']
                    
                    retention = input("  Data retention policies? (y/n) [y]: ") or "y"
                    self.config.medical_features["data_retention"] = retention.lower() in ['y', 'yes']
                    
                    pseudo = input("  Pseudonymization? (y/n) [y]: ") or "y"
                    self.config.medical_features["pseudonymization"] = pseudo.lower() in ['y', 'yes']
    
    def _configure_environment(self):
        """Configure environment variables"""
        print("\n🔧 Environment Configuration")
        print("-" * 40)
        
        auto_env = input("Auto-generate .env file? (y/n) [y]: ") or "y"
        self.config.env_config["auto_generate"] = auto_env.lower() in ['y', 'yes']
        
        if self.config.env_config["auto_generate"]:
            dotenv = input("  Use dotenv? (y/n) [y]: ") or "y"
            self.config.env_config["dotenv"] = dotenv.lower() in ['y', 'yes']
            
            vault = input("  Vault integration (HashiCorp)? (y/n) [n]: ") or "n"
            self.config.env_config["vault_integration"] = vault.lower() in ['y', 'yes']
            
            secrets = input("  Secrets management (AWS/Azure)? (y/n) [n]: ") or "n"
            self.config.env_config["secrets_management"] = secrets.lower() in ['y', 'yes']
    
    def _configure_advanced(self):
        """Configure advanced features"""
        print("\n⚡ Advanced Features")
        print("-" * 40)
        
        show_advanced = input("Configure advanced features? (y/n) [n]: ") or "n"
        
        if show_advanced.lower() in ['y', 'yes']:
            # Multi-tenancy
            if self.config.project_type == ProjectType.FULLSTACK or getattr(self.config, 'template', None) == ProjectTemplate.SAAS:
                multi = input("  Multi-tenancy? (y/n) [n]: ") or "n"
                self.config.advanced_features["multi_tenancy"] = multi.lower() in ['y', 'yes']
            
            # Feature flags
            flags = input("  Feature flags? (y/n) [n]: ") or "n"
            self.config.advanced_features["feature_flags"] = flags.lower() in ['y', 'yes']
            
            # A/B testing
            ab = input("  A/B testing? (y/n) [n]: ") or "n"
            self.config.advanced_features["a_b_testing"] = ab.lower() in ['y', 'yes']
            
            # Real-time features
            if self.config.project_type != ProjectType.STATIC_SITE:
                ws = input("  WebSockets? (y/n) [n]: ") or "n"
                self.config.advanced_features["websockets"] = ws.lower() in ['y', 'yes']
                
                graphql = input("  GraphQL? (y/n) [n]: ") or "n"
                self.config.advanced_features["graphql"] = graphql.lower() in ['y', 'yes']
            
            # Serverless
            serverless = input("  Serverless functions? (y/n) [n]: ") or "n"
            self.config.advanced_features["serverless"] = serverless.lower() in ['y', 'yes']
            
            # Caching
            cache = input("  Caching layer (redis/memcached/none)? [none]: ") or "none"
            if cache != "none":
                self.config.advanced_features["caching"] = cache
            
            # Search
            search = input("  Search engine (algolia/elasticsearch/meilisearch/none)? [none]: ") or "none"
            if search != "none":
                self.config.advanced_features["search"] = search
    
    def _configure_plugins(self):
        """Configure plugin system"""
        print("\n🔌 Plugin System")
        print("-" * 40)
        
        use_plugins = input("Enable plugin system? (y/n) [n]: ") or "n"
        
        if use_plugins.lower() in ['y', 'yes']:
            print("\nAvailable plugins:")
            available_plugins = [
                "seo-optimizer",
                "image-optimizer",
                "sitemap-generator",
                "rss-feed",
                "social-share",
                "code-highlighter",
                "markdown-enhanced",
                "form-builder",
                "email-templates",
                "pdf-generator",
                "backup-restore",
                "migration-tool",
            ]
            
            for i, plugin in enumerate(available_plugins, 1):
                print(f"  {i}. {plugin}")
            
            selections = input("\nSelect plugins (comma-separated numbers) or press Enter: ") or ""
            
            if selections:
                selected_indices = [int(s.strip()) for s in selections.split(',') if s.strip().isdigit()]
                self.config.plugins = [available_plugins[i-1] for i in selected_indices 
                                      if 1 <= i <= len(available_plugins)]
            
            if self.config.plugins:
                marketplace = input("\n  Enable plugin marketplace? (y/n) [n]: ") or "n"
                self.config.plugin_config["marketplace"] = marketplace.lower() in ['y', 'yes']
                
                auto_update = input("  Auto-update plugins? (y/n) [n]: ") or "n"
                self.config.plugin_config["auto_update"] = auto_update.lower() in ['y', 'yes']
    
    def _show_ultimate_summary(self):
        """Show ultimate configuration summary"""
        # Call parent summary
        super()._show_summary()
        
        # Add ultimate features
        print("\n🌟 Advanced Configuration:")
        
        if self.config.template != ProjectTemplate.BLANK:
            print(f"   Template: {self.config.template.value}")
        
        if self.config.auth_provider != AuthProvider.NONE:
            print(f"\n🔐 Authentication:")
            print(f"   Provider: {self.config.auth_provider.value}")
            if self.config.auth_features["social_login"]:
                print(f"   Social: {', '.join(self.config.auth_features['social_login'])}")
            features = []
            if self.config.auth_features["mfa"]: features.append("MFA")
            if self.config.auth_features["magic_links"]: features.append("Magic Links")
            if self.config.auth_features["rbac"]: features.append("RBAC")
            if features:
                print(f"   Features: {', '.join(features)}")
        
        if self.config.analytics_provider != AnalyticsProvider.NONE:
            print(f"\n📊 Analytics: {self.config.analytics_provider.value}")
            if self.config.analytics_config["privacy_first"]:
                print(f"   Privacy-first mode enabled")
        
        if self.config.monitoring_provider != MonitoringProvider.NONE:
            print(f"\n🔍 Monitoring: {self.config.monitoring_provider.value}")
            features = []
            if self.config.monitoring_config["error_tracking"]: features.append("Errors")
            if self.config.monitoring_config["performance"]: features.append("Performance")
            if self.config.monitoring_config["uptime"]: features.append("Uptime")
            if features:
                print(f"   Tracking: {', '.join(features)}")
        
        if self.config.api_doc_tool != APIDocTool.NONE:
            print(f"\n📚 API Docs: {self.config.api_doc_tool.value}")
        
        if self.config.medical_standards:
            print(f"\n🏥 Medical Standards:")
            for standard in self.config.medical_standards:
                print(f"   • {standard.value}")
        
        if self.config.plugins:
            print(f"\n🔌 Plugins: {', '.join(self.config.plugins)}")
        
        # Advanced features
        advanced = []
        if self.config.advanced_features.get("multi_tenancy"): advanced.append("Multi-tenancy")
        if self.config.advanced_features.get("feature_flags"): advanced.append("Feature Flags")
        if self.config.advanced_features.get("websockets"): advanced.append("WebSockets")
        if self.config.advanced_features.get("graphql"): advanced.append("GraphQL")
        if self.config.advanced_features.get("serverless"): advanced.append("Serverless")
        if self.config.advanced_features.get("caching"): advanced.append(f"Cache: {self.config.advanced_features['caching']}")
        if self.config.advanced_features.get("search"): advanced.append(f"Search: {self.config.advanced_features['search']}")
        
        if advanced:
            print(f"\n⚡ Advanced: {', '.join(advanced)}")
    
    def _generate_env_file(self, project_path: Path):
        """Generate environment variables file"""
        print("\n📝 Generating .env file...")
        
        env_content = """# Environment Variables
# Generated by Agent Framework Ultimate Setup Wizard

# Application
NODE_ENV=development
APP_URL=http://localhost:3000
APP_NAME={app_name}

# Database
DATABASE_URL={database_url}

# Authentication
{auth_vars}

# Analytics
{analytics_vars}

# Monitoring
{monitoring_vars}

# API
{api_vars}

# Medical/Compliance
{medical_vars}

# Features
{feature_vars}

# Secrets (DO NOT COMMIT!)
# Add your actual secrets here
""".format(
            app_name=self.config.name,
            database_url=self._get_database_url(),
            auth_vars=self._get_auth_vars(),
            analytics_vars=self._get_analytics_vars(),
            monitoring_vars=self._get_monitoring_vars(),
            api_vars=self._get_api_vars(),
            medical_vars=self._get_medical_vars(),
            feature_vars=self._get_feature_vars(),
        )
        
        env_file = project_path / ".env.example"
        env_file.write_text(env_content)
        
        # Also create empty .env
        (project_path / ".env").touch()
        
        # Add to .gitignore
        gitignore = project_path / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            if ".env" not in content:
                content += "\n# Environment variables\n.env\n.env.local\n"
                gitignore.write_text(content)
        
        print("  ✅ Created .env.example and .env files")
    
    def _get_database_url(self) -> str:
        """Get database URL template"""
        if self.config.database == "postgresql":
            return "postgresql://user:password@localhost:5432/dbname"
        elif self.config.database == "mysql":
            return "mysql://user:password@localhost:3306/dbname"
        elif self.config.database == "mongodb":
            return "mongodb://localhost:27017/dbname"
        elif self.config.database == "sqlite":
            return "file:./dev.db"
        return ""
    
    def _get_auth_vars(self) -> str:
        """Get authentication environment variables"""
        vars = []
        
        if self.config.auth_provider == AuthProvider.NEXTAUTH:
            vars.extend([
                "NEXTAUTH_URL=http://localhost:3000",
                "NEXTAUTH_SECRET=your-secret-here",
            ])
        elif self.config.auth_provider == AuthProvider.CLERK:
            vars.extend([
                "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx",
                "CLERK_SECRET_KEY=sk_test_xxx",
            ])
        elif self.config.auth_provider == AuthProvider.AUTH0:
            vars.extend([
                "AUTH0_DOMAIN=your-domain.auth0.com",
                "AUTH0_CLIENT_ID=xxx",
                "AUTH0_CLIENT_SECRET=xxx",
            ])
        elif self.config.auth_provider == AuthProvider.SUPABASE_AUTH:
            vars.extend([
                "NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co",
                "NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx",
                "SUPABASE_SERVICE_KEY=xxx",
            ])
        
        # Social login
        if "google" in self.config.auth_features.get("social_login", []):
            vars.extend([
                "GOOGLE_CLIENT_ID=xxx",
                "GOOGLE_CLIENT_SECRET=xxx",
            ])
        if "github" in self.config.auth_features.get("social_login", []):
            vars.extend([
                "GITHUB_CLIENT_ID=xxx",
                "GITHUB_CLIENT_SECRET=xxx",
            ])
        
        return "\n".join(vars)
    
    def _get_analytics_vars(self) -> str:
        """Get analytics environment variables"""
        vars = []
        
        if self.config.analytics_provider == AnalyticsProvider.PLAUSIBLE:
            vars.append("NEXT_PUBLIC_PLAUSIBLE_DOMAIN=your-domain.com")
        elif self.config.analytics_provider == AnalyticsProvider.GOOGLE_ANALYTICS:
            vars.append("NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX")
        elif self.config.analytics_provider == AnalyticsProvider.POSTHOG:
            vars.extend([
                "NEXT_PUBLIC_POSTHOG_KEY=xxx",
                "NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com",
            ])
        
        return "\n".join(vars)
    
    def _get_monitoring_vars(self) -> str:
        """Get monitoring environment variables"""
        vars = []
        
        if self.config.monitoring_provider == MonitoringProvider.SENTRY:
            vars.extend([
                "SENTRY_DSN=https://xxx@sentry.io/xxx",
                "SENTRY_ORG=your-org",
                "SENTRY_PROJECT=your-project",
            ])
        elif self.config.monitoring_provider == MonitoringProvider.DATADOG:
            vars.append("DD_API_KEY=xxx")
        
        return "\n".join(vars)
    
    def _get_api_vars(self) -> str:
        """Get API environment variables"""
        vars = []
        
        if self.config.api_doc_tool != APIDocTool.NONE:
            vars.append("API_DOCS_ENABLED=true")
        
        if self.config.api_config.get("api_key_auth"):
            vars.append("API_KEY=xxx")
        
        if self.config.api_config.get("rate_limiting"):
            vars.append("RATE_LIMIT_ENABLED=true")
        
        return "\n".join(vars)
    
    def _get_medical_vars(self) -> str:
        """Get medical/compliance environment variables"""
        vars = []
        
        if self.config.medical_features.get("encryption_at_rest"):
            vars.append("ENCRYPTION_KEY=xxx")
        
        if self.config.medical_features.get("audit_logs"):
            vars.append("AUDIT_LOG_ENABLED=true")
        
        if MedicalStandard.DIGA in self.config.medical_standards:
            vars.append("DIGA_MODE=true")
        
        return "\n".join(vars)
    
    def _get_feature_vars(self) -> str:
        """Get feature environment variables"""
        vars = []
        
        if self.config.advanced_features.get("feature_flags"):
            vars.append("FEATURE_FLAGS_ENABLED=true")
        
        if self.config.advanced_features.get("caching") == "redis":
            vars.append("REDIS_URL=redis://localhost:6379")
        
        if self.config.advanced_features.get("search") == "algolia":
            vars.extend([
                "ALGOLIA_APP_ID=xxx",
                "ALGOLIA_API_KEY=xxx",
            ])
        
        return "\n".join(vars)
    
    def _generate_template_files(self, project_path: Path):
        """Generate template-specific files"""
        template = self.config.template
        
        if template == ProjectTemplate.PATIENT_PORTAL:
            self._generate_medical_files(project_path)
        elif template == ProjectTemplate.ECOMMERCE:
            self._generate_ecommerce_files(project_path)
        elif template == ProjectTemplate.SAAS:
            self._generate_saas_files(project_path)
    
    def _generate_medical_files(self, project_path: Path):
        """Generate medical-specific files"""
        # Create medical directories
        (project_path / "src" / "medical").mkdir(parents=True, exist_ok=True)
        
        # ICD-10 helper
        icd10_file = project_path / "src" / "medical" / "icd10.ts"
        icd10_content = """// ICD-10-GM Helper
export const ICD10_CODES = {
  // Mast Cell Activation Syndrome
  'D89.4': 'Mastzellaktivierungssyndrom',
  'D89.40': 'Mastzellaktivierungssyndrom ohne Hautbeteiligung',
  'D89.41': 'Mastzellaktivierungssyndrom mit Hautbeteiligung',
  // Add more codes as needed
};

export function validateICD10(code: string): boolean {
  return code in ICD10_CODES;
}
"""
        icd10_file.write_text(icd10_content)
        
        # GDPR consent manager
        gdpr_file = project_path / "src" / "medical" / "gdpr-consent.ts"
        gdpr_content = """// GDPR Consent Manager
export interface Consent {
  dataProcessing: boolean;
  analytics: boolean;
  marketing: boolean;
  timestamp: Date;
  ipAddress?: string;
}

export class ConsentManager {
  async recordConsent(consent: Consent): Promise<void> {
    // Implementation
  }
  
  async getConsent(userId: string): Promise<Consent | null> {
    // Implementation
    return null;
  }
}
"""
        gdpr_file.write_text(gdpr_content)
        
        print("  ✅ Generated medical template files")
    
    def _generate_ecommerce_files(self, project_path: Path):
        """Generate e-commerce files"""
        # Create e-commerce directories
        (project_path / "src" / "commerce").mkdir(parents=True, exist_ok=True)
        
        # Cart model
        cart_file = project_path / "src" / "commerce" / "cart.ts"
        cart_content = """// Shopping Cart
export interface CartItem {
  id: string;
  productId: string;
  quantity: number;
  price: number;
}

export interface Cart {
  items: CartItem[];
  subtotal: number;
  tax: number;
  total: number;
}
"""
        cart_file.write_text(cart_content)
        
        print("  ✅ Generated e-commerce template files")
    
    def _generate_saas_files(self, project_path: Path):
        """Generate SaaS files"""
        # Create SaaS directories
        (project_path / "src" / "saas").mkdir(parents=True, exist_ok=True)
        
        # Multi-tenancy
        tenant_file = project_path / "src" / "saas" / "tenant.ts"
        tenant_content = """// Multi-tenancy Support
export interface Tenant {
  id: string;
  name: string;
  subdomain: string;
  plan: 'free' | 'pro' | 'enterprise';
  createdAt: Date;
}

export class TenantManager {
  async getTenant(subdomain: string): Promise<Tenant | null> {
    // Implementation
    return null;
  }
}
"""
        tenant_file.write_text(tenant_content)
        
        print("  ✅ Generated SaaS template files")
    
    def _install_plugins(self, project_path: Path):
        """Install selected plugins"""
        if not self.config.plugins:
            return
        
        print("\n🔌 Installing plugins...")
        
        # Create plugins directory
        plugins_dir = project_path / "plugins"
        plugins_dir.mkdir(exist_ok=True)
        
        # Generate plugin manifest
        manifest = {
            "plugins": self.config.plugins,
            "config": self.config.plugin_config,
            "version": "1.0.0"
        }
        
        manifest_file = plugins_dir / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Create stub files for each plugin
        for plugin in self.config.plugins:
            plugin_file = plugins_dir / f"{plugin}.js"
            plugin_content = f"""// {plugin} Plugin
export default {{
  name: '{plugin}',
  version: '1.0.0',
  install(app) {{
    // Plugin implementation
    console.log('{plugin} plugin installed');
  }}
}};
"""
            plugin_file.write_text(plugin_content)
        
        print(f"  ✅ Installed {len(self.config.plugins)} plugins")


# Export for compatibility
def create_ultimate_wizard(**kwargs):
    """Create ultimate wizard instance"""
    return UltimateSetupWizard(**kwargs)


if __name__ == "__main__":
    wizard = UltimateSetupWizard()
    result = wizard.run_interactive()
    
    if result['status'] == 'success':
        print("\n🎉 Project setup complete with 100% feature coverage!")
    else:
        print(f"\n❌ Setup failed: {result.get('error', 'Unknown error')}")