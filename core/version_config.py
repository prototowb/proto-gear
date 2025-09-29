"""
Version Configuration for ProtoGear
Centralized version management for all frameworks, tools, and dependencies
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class VersionStrategy(Enum):
    """Version pinning strategies"""
    LATEST = "latest"           # ^X.Y.Z - caret range (recommended)
    EXACT = "exact"            # X.Y.Z - exact version
    COMPATIBLE = "compatible"   # ~X.Y.Z - tilde range
    MAJOR = "major"            # X.* - major version range


class FrameworkVersions:
    """
    Centralized version configuration for all supported frameworks
    Updated based on compatibility testing and LTS recommendations
    Last updated: September 2025
    """

    # Frontend Frameworks
    FRONTEND_FRAMEWORKS = {
        'nextjs': {
            'next': '^15.5.0',
            'react': '^19.0.0',
            'react-dom': '^19.0.0',
            '@types/react': '^19.0.0',
            '@types/react-dom': '^19.0.0',
            'eslint-config-next': '^15.5.0'
        },
        'nuxt': {
            'nuxt': '^3.13.0',
            'vue': '^3.5.0',
            '@nuxt/typescript-build': '^3.0.2'
        },
        'sveltekit': {
            '@sveltejs/kit': '^2.5.0',
            'svelte': '^5.0.0',
            '@sveltejs/adapter-auto': '^3.2.0',
            'vite': '^5.4.0'
        },
        'astro': {
            'astro': '^4.15.0',
            '@astrojs/react': '^3.6.0',
            '@astrojs/tailwind': '^5.1.0'
        },
        'react': {
            'react': '^19.0.0',
            'react-dom': '^19.0.0',
            'vite': '^5.4.0',
            '@vitejs/plugin-react': '^4.3.0',
            '@types/react': '^19.0.0',
            '@types/react-dom': '^19.0.0'
        },
        'vue': {
            'vue': '^3.5.0',
            'vite': '^5.4.0',
            '@vitejs/plugin-vue': '^5.1.0',
            '@vue/typescript': '^2.1.0'
        },
        'remix': {
            '@remix-run/node': '^2.12.0',
            '@remix-run/react': '^2.12.0',
            '@remix-run/serve': '^2.12.0',
            'react': '^19.0.0',
            'react-dom': '^19.0.0'
        }
    }

    # CSS Frameworks
    CSS_FRAMEWORKS = {
        'tailwind': {
            'tailwindcss': '^3.4.0',
            '@tailwindcss/typography': '^0.5.15',
            '@tailwindcss/forms': '^0.5.9',
            'autoprefixer': '^10.4.20',
            'postcss': '^8.4.47'
        },
        'bootstrap': {
            'bootstrap': '^5.3.3',
            '@types/bootstrap': '^5.2.10'
        },
        'mui': {
            '@mui/material': '^6.1.0',
            '@mui/styled-engine-sc': '^6.1.0',
            '@emotion/react': '^11.13.0',
            '@emotion/styled': '^11.13.0'
        },
        'chakra': {
            '@chakra-ui/react': '^2.8.2',
            '@emotion/react': '^11.13.0',
            '@emotion/styled': '^11.13.0',
            'framer-motion': '^11.5.0'
        },
        'styled-components': {
            'styled-components': '^6.1.0',
            '@types/styled-components': '^5.1.34'
        }
    }

    # Backend Frameworks
    BACKEND_FRAMEWORKS = {
        'express': {
            'express': '^4.21.0',
            '@types/express': '^4.17.21',
            'cors': '^2.8.5',
            'helmet': '^8.0.0',
            'morgan': '^1.10.0'
        },
        'fastapi': {
            # Python dependencies (for requirements.txt)
            'fastapi': '>=0.115.0',
            'uvicorn': '>=0.31.0',
            'pydantic': '>=2.9.0',
            'python-multipart': '>=0.0.12'
        },
        'django': {
            'Django': '>=5.1.0',
            'djangorestframework': '>=3.15.0',
            'django-cors-headers': '>=4.4.0',
            'psycopg2-binary': '>=2.9.9'
        }
    }

    # Database & ORM
    DATABASES = {
        'postgresql': {
            'pg': '^8.12.0',
            '@types/pg': '^8.11.8'
        },
        'mysql': {
            'mysql2': '^3.11.0',
            '@types/mysql': '^2.15.26'
        },
        'mongodb': {
            'mongodb': '^6.9.0',
            '@types/mongodb': '^4.0.7'
        },
        'prisma': {
            'prisma': '^5.20.0',
            '@prisma/client': '^5.20.0'
        },
        'drizzle': {
            'drizzle-orm': '^0.34.0',
            'drizzle-kit': '^0.25.0'
        },
        'mongoose': {
            'mongoose': '^8.6.0',
            '@types/mongoose': '^5.11.97'
        }
    }

    # Testing Frameworks
    TESTING_FRAMEWORKS = {
        'vitest': {
            'vitest': '^2.1.0',
            '@vitest/ui': '^2.1.0',
            'jsdom': '^25.0.0'
        },
        'jest': {
            'jest': '^29.7.0',
            '@types/jest': '^29.5.13',
            'ts-jest': '^29.2.5'
        },
        'playwright': {
            '@playwright/test': '^1.47.0',
            'playwright': '^1.47.0'
        },
        'cypress': {
            'cypress': '^13.14.0',
            '@cypress/code-coverage': '^3.12.0'
        },
        'pytest': {
            'pytest': '>=8.3.0',
            'pytest-cov': '>=5.0.0',
            'pytest-asyncio': '>=0.24.0'
        }
    }

    # Development Tools
    DEV_TOOLS = {
        'typescript': {
            'typescript': '^5.6.0',
            '@types/node': '^22.7.0'
        },
        'eslint': {
            'eslint': '^9.11.0',
            '@typescript-eslint/eslint-plugin': '^8.7.0',
            '@typescript-eslint/parser': '^8.7.0'
        },
        'prettier': {
            'prettier': '^3.3.0',
            'prettier-plugin-tailwindcss': '^0.6.6'
        },
        'husky': {
            'husky': '^9.1.0',
            'lint-staged': '^15.2.0'
        }
    }

    # Package Managers
    PACKAGE_MANAGERS = {
        'npm': {
            'min_version': '10.0.0',
            'recommended': '10.8.0'
        },
        'pnpm': {
            'min_version': '9.0.0',
            'recommended': '9.11.0'
        },
        'yarn': {
            'min_version': '4.0.0',
            'recommended': '4.5.0'
        },
        'bun': {
            'min_version': '1.1.0',
            'recommended': '1.1.28'
        }
    }

    # Authentication Providers
    AUTH_PROVIDERS = {
        'nextauth': {
            'next-auth': '^4.24.0',
            '@auth/prisma-adapter': '^2.4.0'
        },
        'clerk': {
            '@clerk/nextjs': '^5.7.0',
            '@clerk/themes': '^2.1.0'
        },
        'auth0': {
            '@auth0/nextjs-auth0': '^3.5.0'
        },
        'supabase-auth': {
            '@supabase/supabase-js': '^2.45.0',
            '@supabase/auth-helpers-nextjs': '^0.10.0'
        }
    }

    # Analytics Providers
    ANALYTICS_PROVIDERS = {
        'google-analytics': {
            'gtag': '^1.0.1',
            'react-gtm-module': '^2.0.11'
        },
        'plausible': {
            'plausible-tracker': '^0.3.9'
        },
        'mixpanel': {
            'mixpanel-browser': '^2.54.0'
        },
        'posthog': {
            'posthog-js': '^1.166.0',
            'posthog-node': '^4.2.0'
        }
    }


class VersionManager:
    """Manages version resolution and dependency generation"""

    def __init__(self, strategy: VersionStrategy = VersionStrategy.LATEST):
        self.strategy = strategy
        self.versions = FrameworkVersions()

    def get_dependencies_for_config(self, config: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Generate dependencies and devDependencies based on project configuration"""
        dependencies = {}
        dev_dependencies = {}

        # Frontend framework dependencies
        if config.get('frontend_framework') and config['frontend_framework'] != 'none':
            framework_deps = self.versions.FRONTEND_FRAMEWORKS.get(config['frontend_framework'], {})
            dependencies.update(framework_deps)

        # CSS framework dependencies
        if config.get('css_framework') and config['css_framework'] != 'none':
            css_deps = self.versions.CSS_FRAMEWORKS.get(config['css_framework'], {})
            dependencies.update(css_deps)

        # Backend framework dependencies
        if config.get('backend_framework') and config['backend_framework'] != 'none':
            backend_deps = self.versions.BACKEND_FRAMEWORKS.get(config['backend_framework'], {})
            dependencies.update(backend_deps)

        # Database dependencies
        if config.get('database') and config['database'] != 'none':
            db_deps = self.versions.DATABASES.get(config['database'], {})
            dependencies.update(db_deps)

        # ORM dependencies
        if config.get('orm') and config['orm'] != 'none':
            orm_deps = self.versions.DATABASES.get(config['orm'], {})
            dependencies.update(orm_deps)

        # Feature-based dependencies
        features = config.get('features', [])

        if 'typescript' in features:
            ts_deps = self.versions.DEV_TOOLS['typescript']
            dev_dependencies.update(ts_deps)

        if 'linting' in features:
            eslint_deps = self.versions.DEV_TOOLS['eslint']
            prettier_deps = self.versions.DEV_TOOLS['prettier']
            dev_dependencies.update(eslint_deps)
            dev_dependencies.update(prettier_deps)

        if 'git-hooks' in features:
            husky_deps = self.versions.DEV_TOOLS['husky']
            dev_dependencies.update(husky_deps)

        # Testing framework dependencies
        if config.get('testing_framework') and config['testing_framework'] != 'none':
            test_deps = self.versions.TESTING_FRAMEWORKS.get(config['testing_framework'], {})
            dev_dependencies.update(test_deps)

        # Authentication dependencies
        if 'auth' in features and config.get('auth_provider'):
            auth_deps = self.versions.AUTH_PROVIDERS.get(config['auth_provider'], {})
            dependencies.update(auth_deps)

        # Analytics dependencies
        if 'analytics' in features and config.get('analytics_provider'):
            analytics_deps = self.versions.ANALYTICS_PROVIDERS.get(config['analytics_provider'], {})
            dependencies.update(analytics_deps)

        return {
            'dependencies': dependencies,
            'devDependencies': dev_dependencies
        }

    def get_python_requirements(self, config: Dict[str, Any]) -> List[str]:
        """Generate requirements.txt content for Python projects"""
        requirements = []

        if config.get('backend_framework') == 'fastapi':
            fastapi_deps = self.versions.BACKEND_FRAMEWORKS['fastapi']
            for package, version in fastapi_deps.items():
                requirements.append(f"{package}{version}")

        elif config.get('backend_framework') == 'django':
            django_deps = self.versions.BACKEND_FRAMEWORKS['django']
            for package, version in django_deps.items():
                requirements.append(f"{package}{version}")

        if config.get('testing_framework') == 'pytest':
            pytest_deps = self.versions.TESTING_FRAMEWORKS['pytest']
            for package, version in pytest_deps.items():
                requirements.append(f"{package}{version}")

        return requirements

    def get_package_manager_info(self, package_manager: str) -> Dict[str, str]:
        """Get package manager version requirements"""
        return self.versions.PACKAGE_MANAGERS.get(package_manager, {})

    def apply_version_strategy(self, version: str) -> str:
        """Apply version strategy to a version string"""
        if self.strategy == VersionStrategy.EXACT:
            return version.lstrip('^~')
        elif self.strategy == VersionStrategy.COMPATIBLE:
            return f"~{version.lstrip('^~')}"
        elif self.strategy == VersionStrategy.MAJOR:
            major = version.lstrip('^~').split('.')[0]
            return f"{major}.*"
        else:  # LATEST (caret)
            return f"^{version.lstrip('^~')}"

    def get_compatibility_matrix(self) -> Dict[str, Dict[str, List[str]]]:
        """Get framework compatibility matrix"""
        return {
            'nextjs': {
                'react': ['19.x'],
                'node': ['18.x', '20.x', '22.x'],
                'typescript': ['5.x']
            },
            'react': {
                'react': ['19.x'],
                'node': ['18.x', '20.x', '22.x'],
                'typescript': ['5.x']
            },
            'vue': {
                'vue': ['3.x'],
                'node': ['18.x', '20.x', '22.x'],
                'typescript': ['5.x']
            }
        }

    def validate_compatibility(self, config: Dict[str, Any]) -> List[str]:
        """Validate framework compatibility and return warnings"""
        warnings = []
        compatibility = self.get_compatibility_matrix()

        frontend = config.get('frontend_framework')
        if frontend and frontend in compatibility:
            # Add compatibility validation logic here
            pass

        return warnings

    def get_version_update_date(self) -> str:
        """Get the last update date for version configurations"""
        return "2025-09-30"  # Update this when versions are updated

    def generate_version_lock_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate version lock information for reproducible builds"""
        return {
            'protogear_version': '3.0.0',
            'config_version': self.get_version_update_date(),
            'strategy': self.strategy.value,
            'generated_at': datetime.now().isoformat(),
            'node_version_required': '>=18.0.0',
            'npm_version_required': '>=10.0.0'
        }


# Global version manager instance
version_manager = VersionManager()


def get_latest_versions() -> FrameworkVersions:
    """Get the latest version configurations"""
    return FrameworkVersions()


def create_package_json_with_versions(config: Dict[str, Any]) -> Dict[str, Any]:
    """Create a complete package.json with proper dependency versions"""
    vm = VersionManager()
    deps = vm.get_dependencies_for_config(config)

    base_package_json = {
        "name": config['name'],
        "version": "0.1.0",
        "description": config['description'],
        "main": "src/index.js",
        "scripts": {},
        "keywords": ["protogear"],
        "author": "",
        "license": "MIT"
    }

    # Add dependencies
    if deps['dependencies']:
        base_package_json['dependencies'] = deps['dependencies']

    if deps['devDependencies']:
        base_package_json['devDependencies'] = deps['devDependencies']

    # Add framework-specific scripts
    if config.get('frontend_framework') == 'nextjs':
        base_package_json['scripts'].update({
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "lint": "next lint"
        })
    elif config.get('frontend_framework') == 'react':
        base_package_json['scripts'].update({
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        })
    elif config.get('frontend_framework') == 'vue':
        base_package_json['scripts'].update({
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        })

    # Add testing scripts
    if config.get('testing_framework') == 'vitest':
        base_package_json['scripts']['test'] = "vitest"
        base_package_json['scripts']['test:ui'] = "vitest --ui"
    elif config.get('testing_framework') == 'jest':
        base_package_json['scripts']['test'] = "jest"
        base_package_json['scripts']['test:watch'] = "jest --watch"
    elif config.get('testing_framework') == 'playwright':
        base_package_json['scripts']['test'] = "playwright test"
        base_package_json['scripts']['test:headed'] = "playwright test --headed"

    return base_package_json


if __name__ == "__main__":
    # Example usage
    config = {
        'name': 'test-project',
        'description': 'Test project with versions',
        'frontend_framework': 'nextjs',
        'css_framework': 'tailwind',
        'backend_framework': 'none',
        'database': 'none',
        'orm': 'none',
        'testing_framework': 'vitest',
        'features': ['typescript', 'linting']
    }

    package_json = create_package_json_with_versions(config)
    print("Generated package.json with proper versions:")
    import json
    print(json.dumps(package_json, indent=2))