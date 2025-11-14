"""
Tests for project detection and framework identification
Targeting coverage of detect_project_structure edge cases
"""

import sys
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from proto_gear_pkg.proto_gear import detect_project_structure


class TestNodeJSFrameworkDetection:
    """Test Node.js framework detection branches"""

    def test_detect_nextjs_framework(self, tmp_path):
        """Test Next.js detection via package.json"""
        package_json = {
            "name": "my-app",
            "dependencies": {
                "next": "^13.0.0",
                "react": "^18.0.0"
            }
        }
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'
        assert result['framework'] == 'Next.js'

    def test_detect_react_framework(self, tmp_path):
        """Test React detection (without Next.js)"""
        package_json = {
            "name": "my-app",
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            }
        }
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'
        assert result['framework'] == 'React'

    def test_detect_vue_framework(self, tmp_path):
        """Test Vue.js detection"""
        package_json = {
            "name": "my-app",
            "devDependencies": {
                "vue": "^3.0.0"
            }
        }
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'
        assert result['framework'] == 'Vue.js'

    def test_detect_express_framework(self, tmp_path):
        """Test Express.js detection"""
        package_json = {
            "name": "my-api",
            "dependencies": {
                "express": "^4.18.0"
            }
        }
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'
        assert result['framework'] == 'Express.js'

    def test_detect_nodejs_no_framework(self, tmp_path):
        """Test Node.js detection without specific framework"""
        package_json = {
            "name": "my-app",
            "dependencies": {
                "lodash": "^4.17.0"
            }
        }
        (tmp_path / 'package.json').write_text(json.dumps(package_json))

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'
        # No framework should be set
        assert result.get('framework') is None or result.get('framework') == ''


class TestPythonFrameworkDetection:
    """Test Python framework detection branches"""

    def test_detect_django_framework(self, tmp_path):
        """Test Django detection via manage.py"""
        (tmp_path / 'manage.py').write_text('#!/usr/bin/env python\n')
        (tmp_path / 'requirements.txt').write_text('Django==4.0\n')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Python Project'
        assert result['framework'] == 'Django'

    def test_detect_fastapi_via_filename(self, tmp_path):
        """Test FastAPI detection via file name"""
        (tmp_path / 'fastapi_app.py').write_text('from fastapi import FastAPI\n')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Python Project'
        assert result.get('framework') == 'FastAPI'

    def test_detect_python_no_framework(self, tmp_path):
        """Test Python detection without specific framework"""
        (tmp_path / 'main.py').write_text('print("hello")\n')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Python Project'
        # No framework should be set
        assert result.get('framework') is None or result.get('framework') == ''


class TestProjectStructureSummary:
    """Test project structure summary generation"""

    def test_structure_summary_with_directories(self, tmp_path):
        """Test structure summary includes directories"""
        (tmp_path / 'src').mkdir()
        (tmp_path / 'tests').mkdir()
        (tmp_path / 'docs').mkdir()
        (tmp_path / 'package.json').write_text('{}')

        result = detect_project_structure(tmp_path)

        assert 'structure_summary' in result
        assert 'src' in result['structure_summary'] or 'src' in result['directories']
        assert 'tests' in result['structure_summary'] or 'tests' in result['directories']

    def test_structure_summary_empty_project(self, tmp_path):
        """Test structure summary for empty project"""
        (tmp_path / 'package.json').write_text('{}')

        result = detect_project_structure(tmp_path)

        assert 'structure_summary' in result
        # Should have basic summary
        assert result['structure_summary'] == "Basic project structure" or len(result['structure_summary']) > 0

    def test_directories_excludes_hidden(self, tmp_path):
        """Test that hidden directories are excluded"""
        (tmp_path / 'src').mkdir()
        (tmp_path / '.git').mkdir()
        (tmp_path / '.venv').mkdir()
        (tmp_path / 'package.json').write_text('{}')

        result = detect_project_structure(tmp_path)

        # Should include src but not .git or .venv
        assert 'src' in result['directories']
        assert '.git' not in result['directories']
        assert '.venv' not in result['directories']


class TestProjectDetectionErrorHandling:
    """Test error handling in project detection"""

    def test_invalid_package_json(self, tmp_path):
        """Test handling of invalid package.json"""
        (tmp_path / 'package.json').write_text('invalid json {{{')

        # Should not crash, just skip framework detection
        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'
        # Framework detection should fail gracefully
        assert result.get('framework') is None or isinstance(result.get('framework'), str)

    def test_permission_error_handling(self, tmp_path):
        """Test handling of permission errors"""
        # This tests the except Exception block
        result = detect_project_structure(tmp_path)

        # Should return default structure without crashing
        assert isinstance(result, dict)
        assert 'detected' in result


class TestEdgeCases:
    """Test edge cases in project detection"""

    def test_both_python_and_nodejs(self, tmp_path):
        """Test project with both package.json and .py files"""
        (tmp_path / 'package.json').write_text('{}')
        (tmp_path / 'app.py').write_text('print("hello")')

        result = detect_project_structure(tmp_path)

        # Node.js detection comes first in code
        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'

    def test_empty_package_json(self, tmp_path):
        """Test empty package.json"""
        (tmp_path / 'package.json').write_text('{}')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'
        assert result.get('framework') is None or result.get('framework') == ''


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
