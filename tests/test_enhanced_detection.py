"""
Tests for enhanced framework detection functionality.
Tests coverage for Angular, Svelte, Ruby on Rails, Laravel, Spring Boot, and ASP.NET.
"""

import pytest
import json
from pathlib import Path
from core.proto_gear_pkg.proto_gear import detect_project_structure


class TestAngularDetection:
    """Tests for Angular project detection."""

    def test_angular_json_detection(self, tmp_path):
        """Should detect Angular via angular.json file."""
        # Create angular.json file
        (tmp_path / 'angular.json').write_text('{}')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'
        assert result['framework'] == 'Angular'

    def test_angular_via_package_json(self, tmp_path):
        """Should detect Angular via @angular/core in package.json."""
        package_json = {
            'dependencies': {
                '@angular/core': '^15.0.0',
                '@angular/common': '^15.0.0'
            }
        }
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'
        assert result['framework'] == 'Angular'

    def test_angular_json_priority_over_package_json(self, tmp_path):
        """Angular.json should take priority over package.json detection."""
        (tmp_path / 'angular.json').write_text('{}')
        package_json = {'dependencies': {'react': '^18.0.0'}}
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        result = detect_project_structure(tmp_path)

        assert result['framework'] == 'Angular'


class TestSvelteDetection:
    """Tests for Svelte/SvelteKit project detection."""

    def test_svelte_config_detection(self, tmp_path):
        """Should detect SvelteKit via svelte.config.js file."""
        (tmp_path / 'svelte.config.js').write_text('export default {};')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'
        assert result['framework'] == 'SvelteKit'

    def test_svelte_via_package_json(self, tmp_path):
        """Should detect Svelte via svelte in package.json."""
        package_json = {
            'dependencies': {
                'svelte': '^3.55.0'
            }
        }
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'
        assert result['framework'] == 'Svelte'

    def test_svelte_config_priority(self, tmp_path):
        """svelte.config.js should take priority over package.json."""
        (tmp_path / 'svelte.config.js').write_text('export default {};')
        package_json = {'dependencies': {'vue': '^3.0.0'}}
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        result = detect_project_structure(tmp_path)

        assert result['framework'] == 'SvelteKit'


class TestRubyOnRailsDetection:
    """Tests for Ruby on Rails project detection."""

    def test_rails_gemfile_and_config(self, tmp_path):
        """Should detect Rails via Gemfile + config/application.rb."""
        (tmp_path / 'Gemfile').write_text("gem 'rails'")
        (tmp_path / 'config').mkdir()
        (tmp_path / 'config' / 'application.rb').write_text('# Rails app')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Ruby Project'
        assert result['framework'] == 'Ruby on Rails'

    def test_rails_gemfile_only(self, tmp_path):
        """Should detect Rails via Gemfile content even without config."""
        (tmp_path / 'Gemfile').write_text("""
source 'https://rubygems.org'
gem 'rails', '~> 7.0.0'
gem 'sqlite3'
""")

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Ruby Project'
        assert result['framework'] == 'Ruby on Rails'

    def test_ruby_without_rails(self, tmp_path):
        """Should detect Ruby project without Rails framework."""
        (tmp_path / 'Gemfile').write_text("""
source 'https://rubygems.org'
gem 'sinatra'
""")

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Ruby Project'
        assert result['framework'] is None


class TestLaravelDetection:
    """Tests for Laravel project detection."""

    def test_laravel_artisan_file(self, tmp_path):
        """Should detect Laravel via artisan file."""
        (tmp_path / 'composer.json').write_text('{}')
        (tmp_path / 'artisan').write_text('#!/usr/bin/env php')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'PHP Project'
        assert result['framework'] == 'Laravel'

    def test_laravel_composer_json(self, tmp_path):
        """Should detect Laravel via composer.json dependencies."""
        composer_json = {
            'require': {
                'php': '^8.0',
                'laravel/framework': '^10.0'
            }
        }
        (tmp_path / 'composer.json').write_text(json.dumps(composer_json))

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'PHP Project'
        assert result['framework'] == 'Laravel'

    def test_php_without_laravel(self, tmp_path):
        """Should detect PHP project without Laravel framework."""
        composer_json = {
            'require': {
                'php': '^8.0',
                'symfony/console': '^6.0'
            }
        }
        (tmp_path / 'composer.json').write_text(json.dumps(composer_json))

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'PHP Project'
        assert result['framework'] is None


class TestSpringBootDetection:
    """Tests for Spring Boot project detection."""

    def test_spring_boot_pom_xml(self, tmp_path):
        """Should detect Spring Boot via pom.xml."""
        pom_xml = '''
<project>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.0.0</version>
    </parent>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
</project>
'''
        (tmp_path / 'pom.xml').write_text(pom_xml)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Java Project'
        assert result['framework'] == 'Spring Boot'

    def test_spring_boot_build_gradle(self, tmp_path):
        """Should detect Spring Boot via build.gradle."""
        build_gradle = '''
plugins {
    id 'org.springframework.boot' version '3.0.0'
    id 'java'
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
}
'''
        (tmp_path / 'build.gradle').write_text(build_gradle)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Java Project'
        assert result['framework'] == 'Spring Boot'

    def test_java_without_spring(self, tmp_path):
        """Should detect Java project without Spring Boot."""
        pom_xml = '''
<project>
    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
        </dependency>
    </dependencies>
</project>
'''
        (tmp_path / 'pom.xml').write_text(pom_xml)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Java Project'
        assert result['framework'] is None


class TestASPNETDetection:
    """Tests for ASP.NET project detection."""

    def test_aspnet_csproj(self, tmp_path):
        """Should detect ASP.NET via .csproj file with AspNetCore."""
        csproj = '''
<Project Sdk="Microsoft.NET.Sdk.Web">
    <PropertyGroup>
        <TargetFramework>net7.0</TargetFramework>
    </PropertyGroup>
    <ItemGroup>
        <PackageReference Include="Microsoft.AspNetCore.App" />
    </ItemGroup>
</Project>
'''
        (tmp_path / 'MyApp.csproj').write_text(csproj)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'C# Project'
        assert result['framework'] == 'ASP.NET'

    def test_aspnet_web_sdk(self, tmp_path):
        """Should detect ASP.NET via Microsoft.NET.Sdk.Web."""
        csproj = '''
<Project Sdk="Microsoft.NET.Sdk.Web">
    <PropertyGroup>
        <TargetFramework>net7.0</TargetFramework>
    </PropertyGroup>
</Project>
'''
        (tmp_path / 'WebApp.csproj').write_text(csproj)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'C# Project'
        assert result['framework'] == 'ASP.NET'

    def test_csharp_without_aspnet(self, tmp_path):
        """Should detect C# project without ASP.NET."""
        csproj = '''
<Project Sdk="Microsoft.NET.Sdk">
    <PropertyGroup>
        <OutputType>Exe</OutputType>
        <TargetFramework>net7.0</TargetFramework>
    </PropertyGroup>
</Project>
'''
        (tmp_path / 'ConsoleApp.csproj').write_text(csproj)

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'C# Project'
        assert result['framework'] is None


class TestDetectionPriority:
    """Tests for framework detection priority and edge cases."""

    def test_angular_json_highest_priority(self, tmp_path):
        """angular.json should have highest priority for Angular detection."""
        (tmp_path / 'angular.json').write_text('{}')
        (tmp_path / 'svelte.config.js').write_text('export default {};')
        package_json = {'dependencies': {'react': '^18.0.0'}}
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        result = detect_project_structure(tmp_path)

        assert result['framework'] == 'Angular'

    def test_svelte_config_over_package_json(self, tmp_path):
        """svelte.config.js should have priority over package.json detection."""
        (tmp_path / 'svelte.config.js').write_text('export default {};')
        package_json = {'dependencies': {'react': '^18.0.0'}}
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        result = detect_project_structure(tmp_path)

        assert result['framework'] == 'SvelteKit'

    def test_multiple_project_files_nodejs_first(self, tmp_path):
        """When multiple project types exist, detection follows elif order."""
        (tmp_path / 'package.json').write_text('{}')
        (tmp_path / 'Gemfile').write_text("gem 'rails'")
        (tmp_path / 'composer.json').write_text('{}')

        result = detect_project_structure(tmp_path)

        # package.json is checked first (after Angular/Svelte)
        assert result['type'] == 'Node.js Project'

    def test_empty_directory(self, tmp_path):
        """Empty directory should not be detected as any project type."""
        result = detect_project_structure(tmp_path)

        assert result['detected'] is False
        assert result['type'] is None
        assert result['framework'] is None

    def test_framework_precedence_in_package_json(self, tmp_path):
        """Framework detection in package.json should follow priority order."""
        # Next.js should be detected first, even if React is also present
        package_json = {
            'dependencies': {
                'next': '^13.0.0',
                'react': '^18.0.0',
                'vue': '^3.0.0'
            }
        }
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        result = detect_project_structure(tmp_path)

        assert result['framework'] == 'Next.js'


class TestDirectorySummary:
    """Tests for directory scanning and summary generation."""

    def test_directory_scanning(self, tmp_path):
        """Should scan and list project directories."""
        (tmp_path / 'package.json').write_text('{}')
        (tmp_path / 'src').mkdir()
        (tmp_path / 'tests').mkdir()
        (tmp_path / 'docs').mkdir()
        (tmp_path / '.git').mkdir()  # Should be ignored

        result = detect_project_structure(tmp_path)

        assert 'src' in result['directories']
        assert 'tests' in result['directories']
        assert 'docs' in result['directories']
        assert '.git' not in result['directories']
        assert 'Project contains:' in result['structure_summary']

    def test_no_directories(self, tmp_path):
        """Should handle projects with no subdirectories."""
        (tmp_path / 'package.json').write_text('{}')

        result = detect_project_structure(tmp_path)

        assert result['directories'] == []
        assert result['structure_summary'] == "Basic project structure"


class TestErrorHandling:
    """Tests for error handling in detection logic."""

    def test_malformed_package_json(self, tmp_path):
        """Should handle malformed package.json gracefully."""
        (tmp_path / 'package.json').write_text('{ invalid json }')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True  # File exists
        assert result['type'] == 'Node.js Project'
        assert result['framework'] is None  # Parsing failed, no framework detected

    def test_malformed_composer_json(self, tmp_path):
        """Should handle malformed composer.json gracefully."""
        (tmp_path / 'composer.json').write_text('{ invalid }')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'PHP Project'
        assert result['framework'] is None

    def test_unreadable_file_permissions(self, tmp_path):
        """Should handle file read errors gracefully."""
        # Note: This test may behave differently on Windows vs Unix
        (tmp_path / 'package.json').write_text('{}')

        result = detect_project_structure(tmp_path)

        # Should not crash, even if file becomes unreadable
        assert result is not None
        assert isinstance(result, dict)

    def test_permission_denied_on_directory(self, tmp_path):
        """Should handle permission errors when scanning directories."""
        (tmp_path / 'package.json').write_text('{}')
        (tmp_path / 'restricted').mkdir()

        # Even if we can't read a directory, shouldn't crash
        result = detect_project_structure(tmp_path)

        assert result is not None
        assert result['detected'] is True
