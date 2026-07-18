"""Project, environment, and git detection for Proto Gear.

Pure inspection of the working directory: what tech stack is present, whether
Proto Gear is already initialised, and local git/remote configuration. No
template, presentation, or init logic. Extracted from the proto_gear.py
monolith (PROTO-042, ADR-001 Phase A) and re-exported there for compatibility.
"""

from pathlib import Path


def detect_existing_environment(project_dir: Path) -> dict:
    """
    Detect if Proto Gear files already exist in the project.

    Returns dict with:
    - is_existing: bool - True if any Proto Gear files exist
    - existing_files: list - List of existing Proto Gear files
    - existing_capabilities: bool - True if .proto-gear/ directory exists
    """
    # Draw the scanned set from the shared scaffold taxonomy so detection can
    # never drift from what init actually writes (SESSION_HANDOFF.md,
    # AGENT_CONTEXT.md and the host-config mirrors were previously created but
    # not detected, so the update wizard reported them as absent/untracked).
    from .templates import (
        CORE_ALWAYS_FILES,
        SYNC_GENERATED_FILES,
        OPTIONAL_TEMPLATE_FILES,
    )

    # De-duplicate while preserving order (BRANCHING.md lives in the optional
    # list; nothing else overlaps).
    proto_gear_files = list(
        dict.fromkeys(
            CORE_ALWAYS_FILES + SYNC_GENERATED_FILES + OPTIONAL_TEMPLATE_FILES
        )
    )

    existing_files = []
    for filename in proto_gear_files:
        if (project_dir / filename).exists():
            existing_files.append(filename)

    capabilities_dir = project_dir / ".proto-gear"

    return {
        "is_existing": len(existing_files) > 0 or capabilities_dir.exists(),
        "existing_files": existing_files,
        "existing_capabilities": capabilities_dir.exists(),
    }


def detect_project_structure(project_path):
    """Detect existing project structure and technologies

    Supports detection for:
    - Node.js projects (Angular, Svelte, Next.js, React, Vue.js, Express, NestJS, Nuxt.js, Gatsby)
    - Python projects (Django, FastAPI, Flask, Pyramid)
    - Ruby projects (Ruby on Rails, Sinatra)
    - PHP projects (Laravel, Symfony)
    - Java projects (Spring Boot, Micronaut, Quarkus)
    - C# projects (ASP.NET)
    - Rust projects (Actix Web, Rocket, Axum, Warp, Tauri, Yew)
    - Go projects (Gin, Echo, Fiber, Chi)
    - Kotlin projects (Ktor, Spring Boot Kotlin)
    """
    import json

    info = {
        "detected": False,
        "type": None,
        "framework": None,
        "directories": [],
        "structure_summary": "",
    }

    try:
        # Check for Angular (angular.json)
        if (project_path / "angular.json").exists():
            info["detected"] = True
            info["type"] = "Node.js Project"
            info["framework"] = "Angular"

        # Check for Svelte/SvelteKit (svelte.config.js)
        elif (project_path / "svelte.config.js").exists():
            info["detected"] = True
            info["type"] = "Node.js Project"
            info["framework"] = "SvelteKit"

        # Check for Rust (Cargo.toml)
        elif (project_path / "Cargo.toml").exists():
            info["detected"] = True
            info["type"] = "Rust Project"

            # Try to detect specific frameworks/patterns
            try:
                with open(project_path / "Cargo.toml") as f:
                    cargo_content = f.read()
                    if "actix-web" in cargo_content:
                        info["framework"] = "Actix Web"
                    elif "rocket" in cargo_content:
                        info["framework"] = "Rocket"
                    elif "axum" in cargo_content:
                        info["framework"] = "Axum"
                    elif "warp" in cargo_content:
                        info["framework"] = "Warp"
                    elif "tauri" in cargo_content:
                        info["framework"] = "Tauri"
                    elif "yew" in cargo_content:
                        info["framework"] = "Yew"
            except:
                pass

        # Check for Go (go.mod)
        elif (project_path / "go.mod").exists():
            info["detected"] = True
            info["type"] = "Go Project"

            # Try to detect specific frameworks
            try:
                with open(project_path / "go.mod") as f:
                    go_mod_content = f.read()
                    if "github.com/gin-gonic/gin" in go_mod_content:
                        info["framework"] = "Gin"
                    elif "github.com/labstack/echo" in go_mod_content:
                        info["framework"] = "Echo"
                    elif "github.com/gofiber/fiber" in go_mod_content:
                        info["framework"] = "Fiber"
                    elif "github.com/go-chi/chi" in go_mod_content:
                        info["framework"] = "Chi"
            except:
                pass

        # Check for package.json (Node.js project)
        elif (project_path / "package.json").exists():
            package_json = project_path / "package.json"
            info["detected"] = True
            info["type"] = "Node.js Project"

            try:
                with open(package_json) as f:
                    package_data = json.load(f)
                    deps = {
                        **package_data.get("dependencies", {}),
                        **package_data.get("devDependencies", {}),
                    }

                    # Check for specific frameworks (ordered by specificity)
                    if "next" in deps:
                        info["framework"] = "Next.js"
                    elif "nuxt" in deps:
                        info["framework"] = "Nuxt.js"
                    elif "@nestjs/core" in deps or "@nestjs/common" in deps:
                        info["framework"] = "NestJS"
                    elif "gatsby" in deps:
                        info["framework"] = "Gatsby"
                    elif "@angular/core" in deps:
                        info["framework"] = "Angular"
                    elif "svelte" in deps:
                        info["framework"] = "Svelte"
                    elif "react" in deps:
                        info["framework"] = "React"
                    elif "vue" in deps:
                        info["framework"] = "Vue.js"
                    elif "express" in deps:
                        info["framework"] = "Express.js"
            except:
                pass

        # Check for Ruby (Gemfile)
        elif (project_path / "Gemfile").exists():
            info["detected"] = True
            info["type"] = "Ruby Project"

            # Check for Rails
            if (project_path / "config" / "application.rb").exists():
                info["framework"] = "Ruby on Rails"
            else:
                try:
                    with open(project_path / "Gemfile") as f:
                        gemfile_content = f.read()
                        if "rails" in gemfile_content.lower():
                            info["framework"] = "Ruby on Rails"
                        elif "sinatra" in gemfile_content.lower():
                            info["framework"] = "Sinatra"
                except:
                    pass

        # Check for PHP (composer.json)
        elif (project_path / "composer.json").exists():
            info["detected"] = True
            info["type"] = "PHP Project"

            # Check for Laravel
            if (project_path / "artisan").exists():
                info["framework"] = "Laravel"
            else:
                try:
                    with open(project_path / "composer.json") as f:
                        composer_data = json.load(f)
                        requires = composer_data.get("require", {})
                        if "laravel/framework" in requires:
                            info["framework"] = "Laravel"
                        elif (
                            "symfony/symfony" in requires
                            or "symfony/framework-bundle" in requires
                        ):
                            info["framework"] = "Symfony"
                except:
                    pass

        # Check for Java/Kotlin (pom.xml or build.gradle)
        elif (
            (project_path / "pom.xml").exists()
            or (project_path / "build.gradle").exists()
            or (project_path / "build.gradle.kts").exists()
        ):
            info["detected"] = True

            # Check if Kotlin
            if (project_path / "build.gradle.kts").exists():
                info["type"] = "Kotlin Project"
            else:
                info["type"] = "Java Project"

            # Check for frameworks in pom.xml
            if (project_path / "pom.xml").exists():
                try:
                    with open(project_path / "pom.xml") as f:
                        pom_content = f.read()
                        if "kotlin" in pom_content.lower():
                            info["type"] = "Kotlin Project"

                        if "spring-boot" in pom_content.lower():
                            info["framework"] = "Spring Boot"
                        elif "micronaut" in pom_content.lower():
                            info["framework"] = "Micronaut"
                        elif "quarkus" in pom_content.lower():
                            info["framework"] = "Quarkus"
                        elif "io.ktor" in pom_content:
                            info["framework"] = "Ktor"
                            info["type"] = "Kotlin Project"
                except:
                    pass

            # Check for frameworks in build.gradle or build.gradle.kts
            gradle_file = (
                project_path / "build.gradle.kts"
                if (project_path / "build.gradle.kts").exists()
                else project_path / "build.gradle"
            )
            if not info["framework"] and gradle_file.exists():
                try:
                    with open(gradle_file) as f:
                        gradle_content = f.read()
                        if "kotlin" in gradle_content.lower():
                            info["type"] = "Kotlin Project"

                        if (
                            "spring-boot" in gradle_content.lower()
                            or "org.springframework.boot" in gradle_content
                        ):
                            info["framework"] = "Spring Boot"
                        elif "micronaut" in gradle_content.lower():
                            info["framework"] = "Micronaut"
                        elif "quarkus" in gradle_content.lower():
                            info["framework"] = "Quarkus"
                        elif "io.ktor" in gradle_content:
                            info["framework"] = "Ktor"
                            info["type"] = "Kotlin Project"
                except:
                    pass

        # Check for ASP.NET (*.csproj)
        elif any(project_path.glob("*.csproj")):
            info["detected"] = True
            info["type"] = "C# Project"

            # Check for ASP.NET in csproj files
            try:
                for csproj in project_path.glob("*.csproj"):
                    with open(csproj) as f:
                        csproj_content = f.read()
                        if (
                            "Microsoft.AspNetCore" in csproj_content
                            or "Microsoft.NET.Sdk.Web" in csproj_content
                        ):
                            info["framework"] = "ASP.NET"
                            break
            except:
                pass

        # Check for Python files
        elif (
            any(project_path.glob("*.py"))
            or (project_path / "requirements.txt").exists()
        ):
            info["detected"] = True
            info["type"] = "Python Project"

            if (project_path / "manage.py").exists():
                info["framework"] = "Django"
            elif any("fastapi" in f.name.lower() for f in project_path.glob("*.py")):
                info["framework"] = "FastAPI"
            else:
                # Check requirements.txt for frameworks
                if (project_path / "requirements.txt").exists():
                    try:
                        with open(project_path / "requirements.txt") as f:
                            reqs_content = f.read().lower()
                            if "flask" in reqs_content:
                                info["framework"] = "Flask"
                            elif "pyramid" in reqs_content:
                                info["framework"] = "Pyramid"
                    except:
                        pass

        # Scan directories
        for item in project_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                info["directories"].append(item.name)

        # Create structure summary
        if info["directories"]:
            info["structure_summary"] = (
                f"Project contains: {', '.join(info['directories'])}"
            )
        else:
            info["structure_summary"] = "Basic project structure"

    except Exception:
        pass

    return info


def detect_git_config():
    """Detect Git configuration and workflow capabilities"""
    import subprocess

    config = {
        "is_git_repo": False,
        "has_remote": False,
        "remote_name": None,
        "main_branch": "main",
        "dev_branch": "development",
        "has_gh_cli": False,
        "workflow_mode": "local_only",  # local_only, remote_manual, remote_automated
    }

    try:
        # Check if it's a Git repo
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"], capture_output=True, text=True, timeout=5
        )
        config["is_git_repo"] = result.returncode == 0

        if config["is_git_repo"]:
            # Check for remote
            result = subprocess.run(
                ["git", "remote"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                config["has_remote"] = True
                config["remote_name"] = result.stdout.strip().split()[0]

        # Check for GitHub CLI (gh)
        try:
            result = subprocess.run(
                ["gh", "--version"], capture_output=True, text=True, timeout=5
            )
            config["has_gh_cli"] = result.returncode == 0
        except FileNotFoundError:
            config["has_gh_cli"] = False

        # Determine workflow mode
        if not config["is_git_repo"]:
            config["workflow_mode"] = "no_git"
        elif not config["has_remote"]:
            config["workflow_mode"] = "local_only"
        elif config["has_remote"] and config["has_gh_cli"]:
            config["workflow_mode"] = "remote_automated"
        elif config["has_remote"] and not config["has_gh_cli"]:
            config["workflow_mode"] = "remote_manual"
    except:
        pass

    return config
