"""
TDD Testing Workflow for Agent Framework
Handles test generation, execution, and validation
"""

import os
import subprocess
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
from enum import Enum


class TestType(Enum):
    """Types of tests"""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TDDWorkflow:
    """Test-Driven Development workflow manager"""
    
    def __init__(self, config: Dict):
        """Initialize TDD workflow with configuration"""
        self.config = config
        self.test_config = config.get('testing', {})
        self.coverage_threshold = self.test_config.get('coverage_threshold', 80)
        self.test_framework = self.test_config.get('framework', 'pytest')
        self.test_directory = self.test_config.get('test_directory', 'tests')
        
    def create_test_file(self, feature_name: str, module_path: str) -> str:
        """
        Create a test file for a feature following TDD principles
        
        Args:
            feature_name: Name of the feature being tested
            module_path: Path to the module being tested
            
        Returns:
            Path to the created test file
        """
        # Determine test file path
        test_file_name = f"test_{Path(module_path).stem}.py"
        test_file_path = Path(self.test_directory) / test_file_name
        
        # Create test directory if it doesn't exist
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate initial test content
        test_content = self._generate_test_template(feature_name, module_path)
        
        # Write test file
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        print(f"  ✅ Created test file: {test_file_path}")
        return str(test_file_path)
    
    def _generate_test_template(self, feature_name: str, module_path: str) -> str:
        """Generate test template based on feature type"""
        module_name = Path(module_path).stem

        if "api" in feature_name.lower():
            return self._generate_api_test_template(module_name)
        else:
            return self._generate_basic_test_template(module_name)
    
    def _generate_basic_test_template(self, module_name: str) -> str:
        """Generate basic test template"""
        return f'''"""
Tests for {module_name}
Following TDD principles - tests written before implementation
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_framework.core.{module_name} import *


class Test{module_name.title().replace("_", "")}:
    """Test suite for {module_name}"""
    
    def test_module_imports(self):
        """Test that the module can be imported"""
        assert {module_name.title().replace("_", "")} is not None
    
    def test_initialization(self):
        """Test basic initialization"""
        # RED: Write failing test first
        instance = {module_name.title().replace("_", "")}()
        assert instance is not None
    
    def test_core_functionality(self):
        """Test core functionality"""
        # RED: Define expected behavior
        instance = {module_name.title().replace("_", "")}()
        result = instance.execute()
        assert result is not None
        assert result['status'] == 'success'
    
    @pytest.mark.parametrize("input_data,expected", [
        ({{"test": "data"}}, {{"status": "success"}}),
        ({{"invalid": "data"}}, {{"status": "error"}}),
    ])
    def test_various_inputs(self, input_data, expected):
        """Test with various inputs"""
        instance = {module_name.title().replace("_", "")}()
        result = instance.process(input_data)
        assert result['status'] == expected['status']
    
    def test_error_handling(self):
        """Test error handling"""
        instance = {module_name.title().replace("_", "")}()
        with pytest.raises(ValueError):
            instance.process(None)
    
    @pytest.fixture
    def sample_data(self):
        """Fixture for sample test data"""
        return {{
            "test": "data",
            "nested": {{"value": 123}}
        }}
    
    def test_with_fixture(self, sample_data):
        """Test using fixture"""
        instance = {module_name.title().replace("_", "")}()
        result = instance.process(sample_data)
        assert result is not None
'''

    def _generate_api_test_template(self, module_name: str) -> str:
        """Generate test template for API endpoints"""
        return f'''"""
API Tests for {module_name}
TDD approach with request/response testing
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


class TestAPI:
    """API test suite"""
    
    def test_endpoint_exists(self):
        """Test that endpoint exists"""
        response = client.get("/api/endpoint")
        assert response.status_code != 404
    
    def test_successful_request(self):
        """Test successful API request"""
        response = client.post("/api/endpoint", json={{"test": "data"}})
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    def test_validation_error(self):
        """Test validation error handling"""
        response = client.post("/api/endpoint", json={{}})
        assert response.status_code == 422
'''

    def run_tests(self, test_path: Optional[str] = None, 
                  test_type: TestType = TestType.UNIT) -> Dict[str, Any]:
        """
        Run tests and return results
        
        Args:
            test_path: Specific test file/directory to run
            test_type: Type of tests to run
            
        Returns:
            Test results including status, coverage, and failures
        """
        print(f"\n🧪 Running {test_type.value} tests...")
        
        # Determine test command based on framework
        if self.test_framework == 'pytest':
            cmd = self._build_pytest_command(test_path, test_type)
        elif self.test_framework == 'unittest':
            cmd = self._build_unittest_command(test_path, test_type)
        else:
            cmd = self._build_generic_test_command(test_path)
        
        # Run tests
        result = self._execute_test_command(cmd)
        
        # Parse results
        test_results = self._parse_test_results(result)
        
        # Check coverage if enabled
        if self.test_config.get('coverage_enabled', True):
            coverage = self._check_coverage(test_path)
            test_results['coverage'] = coverage
        
        # Print summary
        self._print_test_summary(test_results)
        
        return test_results
    
    def _build_pytest_command(self, test_path: Optional[str], 
                             test_type: TestType) -> str:
        """Build pytest command"""
        cmd_parts = ['pytest']
        
        # Add verbosity
        cmd_parts.append('-v')
        
        # Add coverage if enabled
        if self.test_config.get('coverage_enabled', True):
            cmd_parts.extend(['--cov=.', '--cov-report=term-missing'])
        
        # Add markers for test type
        if test_type == TestType.UNIT:
            cmd_parts.append('-m unit')
        elif test_type == TestType.INTEGRATION:
            cmd_parts.append('-m integration')
        elif test_type == TestType.E2E:
            cmd_parts.append('-m e2e')
        
        # Add specific path if provided
        if test_path:
            cmd_parts.append(test_path)
        else:
            cmd_parts.append(self.test_directory)
        
        # Add JSON output for parsing
        cmd_parts.append('--json-report')
        cmd_parts.append('--json-report-file=test-results.json')
        
        return ' '.join(cmd_parts)
    
    def _build_unittest_command(self, test_path: Optional[str], 
                               test_type: TestType) -> str:
        """Build unittest command"""
        if test_path:
            return f'python -m unittest {test_path}'
        return f'python -m unittest discover {self.test_directory}'
    
    def _build_generic_test_command(self, test_path: Optional[str]) -> str:
        """Build generic test command"""
        if test_path:
            return f'python {test_path}'
        return f'python -m pytest {self.test_directory}'
    
    def _execute_test_command(self, cmd: str) -> Dict[str, Any]:
        """Execute test command and capture output"""
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Test execution timed out',
                'return_code': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'return_code': -1
            }
    
    def _parse_test_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse test results from output"""
        # Try to parse JSON results if available
        json_file = Path('test-results.json')
        if json_file.exists():
            try:
                with open(json_file, 'r') as f:
                    json_results = json.load(f)
                
                return {
                    'status': TestStatus.PASSED if result['success'] else TestStatus.FAILED,
                    'total': json_results.get('summary', {}).get('total', 0),
                    'passed': json_results.get('summary', {}).get('passed', 0),
                    'failed': json_results.get('summary', {}).get('failed', 0),
                    'skipped': json_results.get('summary', {}).get('skipped', 0),
                    'duration': json_results.get('duration', 0),
                    'failures': json_results.get('tests', {}).get('failed', [])
                }
            except:
                pass
        
        # Fallback to parsing stdout
        return self._parse_stdout_results(result)
    
    def _parse_stdout_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse test results from stdout"""
        stdout = result['stdout']
        
        # Parse pytest output
        if 'passed' in stdout or 'failed' in stdout:
            import re
            
            # Extract test counts
            match = re.search(r'(\d+) passed', stdout)
            passed = int(match.group(1)) if match else 0
            
            match = re.search(r'(\d+) failed', stdout)
            failed = int(match.group(1)) if match else 0
            
            match = re.search(r'(\d+) skipped', stdout)
            skipped = int(match.group(1)) if match else 0
            
            return {
                'status': TestStatus.PASSED if failed == 0 else TestStatus.FAILED,
                'total': passed + failed + skipped,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'duration': 0,
                'failures': []
            }
        
        return {
            'status': TestStatus.FAILED if not result['success'] else TestStatus.PASSED,
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'duration': 0,
            'failures': []
        }
    
    def _check_coverage(self, test_path: Optional[str]) -> Dict[str, Any]:
        """Check test coverage"""
        cmd = f'coverage report --format=json'
        
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                coverage_data = json.loads(result.stdout)
                return {
                    'percentage': coverage_data.get('totals', {}).get('percent_covered', 0),
                    'lines_covered': coverage_data.get('totals', {}).get('covered_lines', 0),
                    'lines_total': coverage_data.get('totals', {}).get('num_statements', 0),
                    'meets_threshold': coverage_data.get('totals', {}).get('percent_covered', 0) >= self.coverage_threshold
                }
        except:
            pass
        
        return {
            'percentage': 0,
            'lines_covered': 0,
            'lines_total': 0,
            'meets_threshold': False
        }
    
    def _print_test_summary(self, results: Dict[str, Any]):
        """Print test summary"""
        print(f"\n📊 Test Results:")
        print(f"  Status: {results['status'].value}")
        print(f"  Total: {results['total']}")
        print(f"  ✅ Passed: {results['passed']}")
        print(f"  ❌ Failed: {results['failed']}")
        print(f"  ⏭️  Skipped: {results['skipped']}")
        
        if 'coverage' in results:
            coverage = results['coverage']
            status_icon = "✅" if coverage['meets_threshold'] else "❌"
            print(f"\n📈 Coverage:")
            print(f"  {status_icon} {coverage['percentage']:.1f}% (threshold: {self.coverage_threshold}%)")
            print(f"  Lines: {coverage['lines_covered']}/{coverage['lines_total']}")
        
        if results['failed'] > 0 and results.get('failures'):
            print(f"\n❌ Failed Tests:")
            for failure in results['failures'][:5]:  # Show first 5 failures
                print(f"  - {failure}")
    
    def generate_test_report(self, results: Dict[str, Any], 
                            output_format: str = 'html') -> str:
        """Generate test report in specified format"""
        timestamp = datetime.now().isoformat()
        
        if output_format == 'html':
            return self._generate_html_report(results, timestamp)
        elif output_format == 'json':
            return json.dumps(results, indent=2)
        else:
            return self._generate_text_report(results, timestamp)
    
    def _generate_html_report(self, results: Dict[str, Any], 
                             timestamp: str) -> str:
        """Generate HTML test report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .summary {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Test Report</h1>
    <p>Generated: {timestamp}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Status: <span class="{results['status'].value.lower()}">{results['status'].value}</span></p>
        <p>Total Tests: {results['total']}</p>
        <p>Passed: {results['passed']}</p>
        <p>Failed: {results['failed']}</p>
        <p>Skipped: {results['skipped']}</p>
    </div>
    
    {'<div class="coverage"><h2>Coverage</h2><p>' + str(results.get('coverage', {}).get('percentage', 0)) + '%</p></div>' if 'coverage' in results else ''}
</body>
</html>
"""
        return html
    
    def _generate_text_report(self, results: Dict[str, Any], 
                             timestamp: str) -> str:
        """Generate text test report"""
        report = f"""
TEST REPORT
Generated: {timestamp}
{'=' * 50}

Status: {results['status'].value}
Total Tests: {results['total']}
Passed: {results['passed']}
Failed: {results['failed']}
Skipped: {results['skipped']}

"""
        if 'coverage' in results:
            report += f"Coverage: {results['coverage']['percentage']:.1f}%\n"
        
        return report
    
    def verify_tdd_compliance(self, module_path: str) -> bool:
        """
        Verify that TDD was followed (tests exist before implementation)
        
        Args:
            module_path: Path to module to verify
            
        Returns:
            True if TDD compliance is met
        """
        test_file = Path(self.test_directory) / f"test_{Path(module_path).stem}.py"
        
        if not test_file.exists():
            print("  ❌ No test file found - TDD requires tests first!")
            return False
        
        # Check that test file was created before module
        if Path(module_path).exists():
            test_mtime = test_file.stat().st_mtime
            module_mtime = Path(module_path).stat().st_mtime
            
            if test_mtime > module_mtime:
                print("  ⚠️  Tests were created after implementation - not following TDD!")
                return False
        
        print("  ✅ TDD compliance verified")
        return True


class TestRunner:
    """Manages test execution for the framework"""
    
    def __init__(self, tdd_workflow: TDDWorkflow):
        self.tdd_workflow = tdd_workflow
        self.test_history = []
    
    def run_for_ticket(self, ticket_id: str, ticket_type: str = 'feature') -> bool:
        """
        Run tests for a specific ticket
        
        Args:
            ticket_id: Ticket identifier
            ticket_type: Type of ticket (feature, bugfix, etc.)
            
        Returns:
            True if all tests pass
        """
        print(f"\n🎫 Running tests for ticket {ticket_id}")
        
        # Determine test type based on ticket type
        if ticket_type == 'bugfix':
            test_type = TestType.INTEGRATION
        elif ticket_type == 'feature':
            test_type = TestType.UNIT
        else:
            test_type = TestType.UNIT
        
        # Run tests
        results = self.tdd_workflow.run_tests(test_type=test_type)
        
        # Store results
        self.test_history.append({
            'ticket_id': ticket_id,
            'timestamp': datetime.now().isoformat(),
            'results': results
        })
        
        # Return success status
        return results['status'] == TestStatus.PASSED
    
    def get_test_history(self) -> List[Dict]:
        """Get test execution history"""
        return self.test_history
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary of all test runs"""
        if not self.test_history:
            return {'total_runs': 0}
        
        passed = sum(1 for h in self.test_history 
                    if h['results']['status'] == TestStatus.PASSED)
        failed = sum(1 for h in self.test_history 
                    if h['results']['status'] == TestStatus.FAILED)
        
        return {
            'total_runs': len(self.test_history),
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / len(self.test_history)) * 100 if self.test_history else 0,
            'last_run': self.test_history[-1] if self.test_history else None
        }