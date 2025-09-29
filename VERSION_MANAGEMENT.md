# ProtoGear Version Management System

ProtoGear includes a comprehensive version management system that ensures all generated projects use compatible, up-to-date versions of frameworks, libraries, and tools.

## Overview

The version management system handles:

- ✅ **Framework Dependencies** - Proper versions for Next.js, React, Vue, etc.
- ✅ **CSS Framework Dependencies** - Tailwind, Bootstrap, Material-UI, etc.
- ✅ **Backend Dependencies** - Express, FastAPI, Django with compatible versions
- ✅ **Development Tools** - TypeScript, ESLint, Prettier, testing frameworks
- ✅ **Database & ORM** - PostgreSQL, MongoDB, Prisma, Drizzle with proper versions
- ✅ **Authentication & Analytics** - Auth0, Clerk, NextAuth with latest stable versions
- ✅ **Python Requirements** - requirements.txt generation for Python projects

## How Version Handling Works

### 1. **Centralized Version Configuration**

All versions are defined in `core/version_config.py`:

```python
# Example: Next.js with React 19 and latest stable versions
FRONTEND_FRAMEWORKS = {
    'nextjs': {
        'next': '^15.5.0',
        'react': '^19.0.0',
        'react-dom': '^19.0.0',
        '@types/react': '^19.0.0',
        '@types/react-dom': '^19.0.0',
        'eslint-config-next': '^15.5.0'
    }
}
```

### 2. **Version Strategies**

ProtoGear supports multiple version pinning strategies:

- **`LATEST` (Default)** - Uses caret ranges (^X.Y.Z) for latest compatible versions
- **`EXACT`** - Pins to exact versions (X.Y.Z) for reproducible builds
- **`COMPATIBLE`** - Uses tilde ranges (~X.Y.Z) for patch-level updates
- **`MAJOR`** - Uses major version ranges (X.*) for broader compatibility

### 3. **Smart Dependency Resolution**

The system automatically includes dependencies based on your configuration:

```bash
# Next.js + TypeScript + Tailwind + Vitest
Dependencies:
  next: ^15.5.0
  react: ^19.0.0
  react-dom: ^19.0.0
  tailwindcss: ^3.4.0
  autoprefixer: ^10.4.20

Dev Dependencies:
  typescript: ^5.6.0
  @types/node: ^22.7.0
  vitest: ^2.1.0
  @vitest/ui: ^2.1.0
```

### 4. **Framework Compatibility**

Versions are tested for compatibility:

- **Next.js 15.5** + **React 19** + **TypeScript 5.6**
- **Vue 3.5** + **Vite 5.4** + **TypeScript 5.6**
- **Svelte 5.0** + **SvelteKit 2.5** + **Vite 5.4**

## Current Version Matrix (September 2025)

### Frontend Frameworks

| Framework | Version | React/Vue | TypeScript | Node.js |
|-----------|---------|-----------|------------|---------|
| Next.js | ^15.5.0 | React 19 | 5.6+ | 18+ |
| React (Vite) | ^19.0.0 | React 19 | 5.6+ | 18+ |
| Vue.js | ^3.5.0 | Vue 3.5 | 5.6+ | 18+ |
| SvelteKit | ^2.5.0 | Svelte 5.0 | 5.6+ | 18+ |
| Astro | ^4.15.0 | - | 5.6+ | 18+ |

### CSS Frameworks

| Framework | Version | Additional Packages |
|-----------|---------|---------------------|
| Tailwind CSS | ^3.4.0 | autoprefixer, postcss |
| Bootstrap | ^5.3.3 | @types/bootstrap |
| Material-UI | ^6.1.0 | @emotion/react, @emotion/styled |
| Chakra UI | ^2.8.2 | @emotion/react, framer-motion |

### Backend Frameworks

| Framework | Version | Language | Additional Packages |
|-----------|---------|----------|---------------------|
| Express.js | ^4.21.0 | Node.js | cors, helmet, morgan |
| FastAPI | >=0.115.0 | Python | uvicorn, pydantic |
| Django | >=5.1.0 | Python | djangorestframework |

### Testing Frameworks

| Framework | Version | Type | Additional Packages |
|-----------|---------|------|---------------------|
| Vitest | ^2.1.0 | Unit | @vitest/ui, jsdom |
| Jest | ^29.7.0 | Unit | @types/jest, ts-jest |
| Playwright | ^1.47.0 | E2E | playwright |
| Cypress | ^13.14.0 | E2E | @cypress/code-coverage |

## Usage Examples

### 1. **Basic Web App (Next.js + TypeScript + Tailwind)**

```bash
echo -e "2\nmy-app\n1\n\n1\n1\n1\n1\n1,2\n1\n2\ny" | pg init
```

**Generated package.json:**
```json
{
  "dependencies": {
    "next": "^15.5.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.47"
  },
  "devDependencies": {
    "typescript": "^5.6.0",
    "@types/node": "^22.7.0",
    "eslint": "^9.11.0",
    "prettier": "^3.3.0"
  }
}
```

### 2. **Fullstack App (React + Express + PostgreSQL)**

```bash
# Creates both package.json and requirements.txt
echo -e "2\nfullstack-app\n3\n\n5\n2\n1\n1\n1\n2\n1,2\n1\n2\ny" | pg init
```

**Generated package.json:**
```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "express": "^4.21.0",
    "pg": "^8.12.0",
    "cors": "^2.8.5"
  }
}
```

### 3. **Python API (FastAPI + PostgreSQL)**

**Generated requirements.txt:**
```
fastapi>=0.115.0
uvicorn>=0.31.0
pydantic>=2.9.0
psycopg2-binary>=2.9.9
pytest>=8.3.0
```

## Customizing Versions

### Update Version Configuration

Edit `core/version_config.py` to update framework versions:

```python
# Update Next.js version
FRONTEND_FRAMEWORKS = {
    'nextjs': {
        'next': '^15.6.0',  # Updated version
        'react': '^19.0.0',
        # ... other dependencies
    }
}
```

### Change Version Strategy

```python
from version_config import VersionManager, VersionStrategy

# Use exact versions for production
vm = VersionManager(VersionStrategy.EXACT)
deps = vm.get_dependencies_for_config(config)
```

### Add New Framework

```python
# Add new CSS framework
CSS_FRAMEWORKS = {
    'my-framework': {
        'my-css-framework': '^1.0.0',
        'companion-package': '^2.0.0'
    }
}
```

## Version Update Process

### 1. **Research New Versions**
- Check framework release notes
- Verify compatibility between dependencies
- Test with sample projects

### 2. **Update Configuration**
- Modify `core/version_config.py`
- Update compatibility matrix
- Update documentation

### 3. **Test Changes**
```bash
# Run version management tests
python -m pytest tests/test_version_management.py

# Test with real project creation
echo "test input" | pg init --dry-run
```

### 4. **Validate Compatibility**
- Create test projects with different stacks
- Verify dependencies install correctly
- Test build processes

## Best Practices

### ✅ **Do:**
- Use caret ranges (^) for most dependencies
- Keep compatible versions together
- Test framework combinations before updating
- Document breaking changes in version updates
- Use exact versions for critical security dependencies

### ❌ **Don't:**
- Mix incompatible major versions
- Use pre-release versions in production configs
- Update all versions at once without testing
- Ignore peer dependency warnings
- Use wildcard (*) versions

## Troubleshooting

### Common Version Conflicts

**React 18 vs React 19:**
```bash
# Error: peer dependency mismatch
# Solution: Update all React-related packages together
```

**TypeScript Compatibility:**
```bash
# Error: TypeScript version incompatible
# Solution: Ensure TypeScript version supports all framework features
```

### Debugging Version Issues

```bash
# Check generated dependencies
pg init --dry-run

# Validate package.json
npm ls

# Check for vulnerabilities
npm audit
```

## Integration with Package Managers

### npm (Default)
```json
{
  "dependencies": {
    "next": "^15.5.0"
  }
}
```

### pnpm
- Compatible with all version ranges
- Faster installs with proper lockfile

### yarn
- Supports all version strategies
- Good for monorepo setups

### bun
- Fast package manager
- Compatible with npm version ranges

## Monitoring and Updates

### Automated Dependency Updates

ProtoGear version configurations should be updated quarterly:

1. **Q1** - Major framework updates (Next.js, React, Vue)
2. **Q2** - CSS framework and tooling updates
3. **Q3** - Backend framework and database updates
4. **Q4** - Testing and development tool updates

### Version Lock Information

Every generated project includes version lock info:

```yaml
protogear_version: "3.0.0"
config_version: "2025-09-30"
strategy: "latest"
node_version_required: ">=18.0.0"
npm_version_required: ">=10.0.0"
```

---

**The ProtoGear version management system ensures your projects start with the latest, compatible, and secure dependency versions while maintaining flexibility for future updates.**