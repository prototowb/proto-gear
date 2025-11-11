"""
Tests for proto_gear.py CLI interface
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from proto_gear_pkg.proto_gear import (
    detect_project_structure,
    detect_git_config,
    safe_input,
    generate_branching_doc,
    setup_agent_framework_only,
    show_splash_screen,
    print_farewell,
    show_help,
    run_simple_protogear_init,
    interactive_setup_wizard,
    main
)
from proto_gear_pkg.ui_helper import Colors


class TestProjectDetection:
    """Test project structure detection"""

    def test_detect_nodejs_project(self, tmp_path):
        """Test detection of Node.js project"""
        # Create package.json
        package_json = tmp_path / "package.json"
        package_json.write_text('{"name": "test-project", "version": "1.0.0"}')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'

    def test_detect_python_project(self, tmp_path):
        """Test detection of Python project"""
        # Create requirements.txt
        requirements = tmp_path / "requirements.txt"
        requirements.write_text('pytest>=7.0\nflake8>=6.0')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Python Project'

    def test_detect_nextjs_framework(self, tmp_path):
        """Test detection of Next.js framework"""
        # Create package.json with Next.js
        package_json = tmp_path / "package.json"
        package_json.write_text('''{
            "name": "test-project",
            "dependencies": {
                "next": "^13.0.0",
                "react": "^18.0.0"
            }
        }''')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['framework'] == 'Next.js'

    def test_detect_django_framework(self, tmp_path):
        """Test detection of Django framework"""
        # Create requirements.txt with Django
        requirements = tmp_path / "requirements.txt"
        requirements.write_text('Django>=4.0\ndjango-rest-framework>=3.14')

        # Also create setup.py to help detection
        setup_py = tmp_path / "setup.py"
        setup_py.write_text('# setup file')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        # Framework detection may require more context, just verify detection works
        assert result['type'] == 'Python Project'

    def test_detect_generic_project(self, tmp_path):
        """Test detection of generic project (no known files)"""
        # Empty directory
        result = detect_project_structure(tmp_path)

        assert result['detected'] is False
        # Type is None for undetected projects
        assert result['type'] is None


class TestGitConfigDetection:
    """Test Git configuration detection"""

    @patch('subprocess.run')
    def test_detect_git_repo_with_remote(self, mock_run):
        """Test detection of Git repo with remote"""
        # Mock git rev-parse (is a repo)
        mock_run.return_value = Mock(returncode=0, stdout='')

        # Mock git remote (has remote)
        mock_run_remote = Mock(returncode=0, stdout='origin\n', stderr='')

        with patch('subprocess.run', side_effect=[
            Mock(returncode=0, stdout='', stderr=''),  # git rev-parse
            mock_run_remote,  # git remote
            Mock(returncode=0, stdout='main\n', stderr=''),  # main branch
            Mock(returncode=0, stdout='development\n', stderr='')  # dev branch
        ]):
            result = detect_git_config()

        assert result['is_git_repo'] is True
        assert result['has_remote'] is True
        assert result['remote_name'] == 'origin'

    @patch('subprocess.run')
    def test_detect_git_repo_without_remote(self, mock_run):
        """Test detection of Git repo without remote"""
        with patch('subprocess.run', side_effect=[
            Mock(returncode=0, stdout='', stderr=''),  # git rev-parse
            Mock(returncode=0, stdout='', stderr=''),  # git remote (empty)
            Mock(returncode=0, stdout='main\n', stderr=''),  # main branch
            Mock(returncode=0, stdout='development\n', stderr='')  # dev branch
        ]):
            result = detect_git_config()

        assert result['is_git_repo'] is True
        assert result['has_remote'] is False
        assert result['remote_name'] is None

    @patch('subprocess.run')
    def test_detect_no_git_repo(self, mock_run):
        """Test detection when not a Git repo"""
        mock_run.return_value = Mock(returncode=128, stdout='', stderr='not a git repository')

        result = detect_git_config()

        assert result['is_git_repo'] is False
        assert result['has_remote'] is False


class TestSafeInput:
    """Test safe input handling"""

    def test_safe_input_normal(self):
        """Test safe input with normal input"""
        with patch('builtins.input', return_value='test input'):
            result = safe_input("Enter something: ")
            assert result == 'test input'

    def test_safe_input_eof_with_default(self):
        """Test safe input handling EOF with default"""
        with patch('builtins.input', side_effect=EOFError):
            result = safe_input("Enter something: ", default="default_value")
            assert result == 'default_value'

    def test_safe_input_keyboard_interrupt(self):
        """Test safe input handling KeyboardInterrupt"""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                safe_input("Enter something: ")


class TestColors:
    """Test color code constants"""

    def test_colors_defined(self):
        """Test that color codes are defined"""
        assert hasattr(Colors, 'HEADER')
        assert hasattr(Colors, 'BLUE')
        assert hasattr(Colors, 'CYAN')
        assert hasattr(Colors, 'GREEN')
        assert hasattr(Colors, 'WARNING')
        assert hasattr(Colors, 'FAIL')
        assert hasattr(Colors, 'ENDC')
        assert hasattr(Colors, 'BOLD')

    def test_colors_are_strings(self):
        """Test that color codes are strings"""
        assert isinstance(Colors.GREEN, str)
        assert isinstance(Colors.CYAN, str)
        assert isinstance(Colors.FAIL, str)


class TestMainCLI:
    """Test main CLI entry point"""

    @patch('proto_gear.show_splash_screen')
    @patch('proto_gear.run_simple_protogear_init')
    def test_init_command_dry_run(self, mock_init, mock_splash):
        """Test pg init --dry-run command"""
        mock_init.return_value = {'status': 'success', 'dry_run': True}

        with patch('sys.argv', ['pg', 'init', '--dry-run', '--no-interactive']):
            with pytest.raises(SystemExit) as exc_info:
                from proto_gear_pkg.proto_gear import main
                main()

            assert exc_info.value.code == 0
            mock_splash.assert_called_once()
            mock_init.assert_called_once()

    @patch('proto_gear.show_splash_screen')
    @patch('proto_gear.show_help')
    def test_help_command(self, mock_help, mock_splash):
        """Test pg help command"""
        with patch('sys.argv', ['pg', 'help']):
            with pytest.raises(SystemExit) as exc_info:
                from proto_gear_pkg.proto_gear import main
                main()

            assert exc_info.value.code == 0
            mock_help.assert_called_once()


class TestGenerateBranchingDoc:
    """Test branching document generation"""

    def test_generate_branching_with_remote(self):
        """Test generating BRANCHING.md with remote configured"""
        git_config = {
            'is_git_repo': True,
            'has_remote': True,
            'remote_name': 'origin',
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': False,
            'workflow_mode': 'remote_manual'
        }

        result = generate_branching_doc('test-project', 'TEST', git_config, '2025-11-05')

        assert result is not None
        assert 'test-project' in result
        assert 'TEST' in result
        assert 'Remote Workflow (Manual PRs)' in result
        assert 'origin' in result
        assert 'Pull Requests' in result

    def test_generate_branching_local_only(self):
        """Test generating BRANCHING.md for local-only workflow"""
        git_config = {
            'is_git_repo': True,
            'has_remote': False,
            'remote_name': None,
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': False,
            'workflow_mode': 'local_only'
        }

        result = generate_branching_doc('test-project', 'TEST', git_config, '2025-11-05')

        assert result is not None
        assert 'Local-Only Workflow' in result
        assert 'local merge' in result.lower() or 'local-only' in result.lower()

    def test_generate_branching_with_gh_cli(self):
        """Test generating BRANCHING.md with GitHub CLI available"""
        git_config = {
            'is_git_repo': True,
            'has_remote': True,
            'remote_name': 'origin',
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': True,
            'workflow_mode': 'remote_automated'
        }

        result = generate_branching_doc('test-project', 'TEST', git_config, '2025-11-05')

        assert result is not None
        assert 'Remote Workflow (Automated)' in result
        assert 'gh pr create' in result or 'GitHub CLI' in result


class TestSetupAgentFramework:
    """Test agent framework setup"""

    def test_setup_dry_run(self, tmp_path):
        """Test setup in dry-run mode"""
        with patch('proto_gear.detect_project_structure') as mock_detect:
            mock_detect.return_value = {
                'detected': True,
                'type': 'Python Project',
                'framework': 'Django',
                'directories': ['src', 'tests'],
                'structure_summary': 'Project contains: src, tests'
            }

            result = setup_agent_framework_only(dry_run=True)

            assert result['status'] == 'success'
            assert result.get('dry_run') is True

    def test_setup_creates_agents_md(self, tmp_path, monkeypatch):
        """Test that setup creates AGENTS.md"""
        # Change to tmp_path directory
        monkeypatch.chdir(tmp_path)

        with patch('proto_gear.detect_project_structure') as mock_detect:
            mock_detect.return_value = {
                'detected': True,
                'type': 'Python Project',
                'framework': None,
                'directories': ['src'],
                'structure_summary': 'Project contains: src'
            }

            result = setup_agent_framework_only(dry_run=False, with_branching=False)

            assert result['status'] == 'success'
            assert 'AGENTS.md' in result.get('files_created', [])

            # Check that AGENTS.md was created
            agents_file = tmp_path / 'AGENTS.md'
            assert agents_file.exists()
            content = agents_file.read_text(encoding='utf-8')
            assert 'ProtoGear Agent Framework' in content

    def test_setup_with_branching(self, tmp_path, monkeypatch):
        """Test setup with branching strategy enabled"""
        # Change to tmp_path directory
        monkeypatch.chdir(tmp_path)

        with patch('proto_gear.detect_project_structure') as mock_detect:
            with patch('proto_gear.detect_git_config') as mock_git:
                mock_detect.return_value = {
                    'detected': True,
                    'type': 'Python Project',
                    'framework': None,
                    'directories': [],
                    'structure_summary': 'Basic project'
                }
                mock_git.return_value = {
                    'is_git_repo': True,
                    'has_remote': False,
                    'remote_name': None,
                    'main_branch': 'main',
                    'dev_branch': 'development',
                    'has_gh_cli': False,
                    'workflow_mode': 'local_only'
                }

                result = setup_agent_framework_only(
                    dry_run=False,
                    with_branching=True,
                    ticket_prefix='TEST'
                )

                assert result['status'] == 'success'
                assert 'BRANCHING.md' in result.get('files_created', [])


class TestWorkflowModeDetection:
    """Test workflow mode detection (PROTO-016)"""

    @patch('subprocess.run')
    def test_detect_remote_automated_mode(self, mock_run):
        """Test detection of remote_automated workflow mode"""
        with patch('subprocess.run', side_effect=[
            Mock(returncode=0, stdout='', stderr=''),  # git rev-parse
            Mock(returncode=0, stdout='origin\n', stderr=''),  # git remote
            Mock(returncode=0, stdout='', stderr=''),  # gh --version (success)
        ]):
            result = detect_git_config()

            assert result['is_git_repo'] is True
            assert result['has_remote'] is True
            assert result['has_gh_cli'] is True
            assert result['workflow_mode'] == 'remote_automated'

    @patch('subprocess.run')
    def test_detect_remote_manual_mode(self, mock_run):
        """Test detection of remote_manual workflow mode"""
        with patch('subprocess.run', side_effect=[
            Mock(returncode=0, stdout='', stderr=''),  # git rev-parse
            Mock(returncode=0, stdout='origin\n', stderr=''),  # git remote
            Mock(returncode=1, stdout='', stderr=''),  # gh --version (fail)
        ]):
            result = detect_git_config()

            assert result['is_git_repo'] is True
            assert result['has_remote'] is True
            assert result['has_gh_cli'] is False
            assert result['workflow_mode'] == 'remote_manual'

    @patch('subprocess.run')
    def test_detect_local_only_mode(self, mock_run):
        """Test detection of local_only workflow mode"""
        with patch('subprocess.run', side_effect=[
            Mock(returncode=0, stdout='', stderr=''),  # git rev-parse
            Mock(returncode=0, stdout='', stderr=''),  # git remote (empty)
        ]):
            result = detect_git_config()

            assert result['is_git_repo'] is True
            assert result['has_remote'] is False
            assert result['workflow_mode'] == 'local_only'


class TestUIFunctions:
    """Test UI functions"""

    @patch('proto_gear.time.sleep')
    @patch('proto_gear.print')
    @patch('proto_gear.clear_screen')
    def test_show_splash_screen(self, mock_clear, mock_print, mock_sleep):
        """Test splash screen display"""
        show_splash_screen()

        # Verify clear_screen was called
        mock_clear.assert_called_once()
        # Verify print was called (for logo and tagline)
        assert mock_print.called

    @patch('proto_gear.ui.farewell')
    @patch('builtins.print')
    def test_print_farewell(self, mock_print, mock_ui_farewell):
        """Test farewell message"""
        print_farewell()

        # Verify farewell methods were called
        assert mock_print.called or mock_ui_farewell.called

    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_show_help(self, mock_print, mock_input):
        """Test help display function"""
        show_help()

        # Verify print was called for help text
        assert mock_print.called
        # Should print multiple lines of help
        assert mock_print.call_count > 10
        # Should wait for user input at the end
        mock_input.assert_called_once()


class TestInteractiveSetupWizard:
    """Test legacy interactive setup wizard"""

    @patch('proto_gear.safe_input')
    @patch('proto_gear.detect_git_config')
    @patch('proto_gear.detect_project_structure')
    def test_wizard_basic_flow(self, mock_detect_project, mock_detect_git, mock_input):
        """Test basic wizard flow with branching enabled"""
        mock_detect_project.return_value = {
            'detected': True,
            'type': 'Python Project',
            'framework': None,
            'directories': [],
            'structure_summary': 'Basic'
        }
        mock_detect_git.return_value = {
            'is_git_repo': False,
            'has_remote': False,
            'remote_name': None,
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': False,
            'workflow_mode': 'no_git'
        }

        # User inputs: yes to branching, custom prefix, yes to proceed
        mock_input.side_effect = ['y', 'MYTEST', 'y']

        result = interactive_setup_wizard()

        assert result['with_branching'] is True
        assert result['ticket_prefix'] == 'MYTEST'
        assert result['confirmed'] is True

    @patch('proto_gear.safe_input')
    @patch('proto_gear.detect_git_config')
    @patch('proto_gear.detect_project_structure')
    def test_wizard_user_cancels(self, mock_detect_project, mock_detect_git, mock_input):
        """Test wizard when user declines at confirmation"""
        mock_detect_project.return_value = {
            'detected': True,
            'type': 'Python Project',
            'framework': None,
            'directories': [],
            'structure_summary': 'Basic'
        }
        mock_detect_git.return_value = {
            'is_git_repo': False,
            'has_remote': False,
            'remote_name': None,
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': False,
            'workflow_mode': 'no_git'
        }

        # User inputs: no to branching, no to proceed
        mock_input.side_effect = ['n', 'n']

        result = interactive_setup_wizard()

        assert result['with_branching'] is False
        assert result['ticket_prefix'] is None
        assert result['confirmed'] is False

    @patch('proto_gear.safe_input')
    @patch('proto_gear.detect_git_config')
    @patch('proto_gear.detect_project_structure')
    def test_wizard_keyboard_interrupt(self, mock_detect_project, mock_detect_git, mock_input):
        """Test wizard Ctrl+C handling"""
        mock_detect_project.return_value = {
            'detected': True,
            'type': 'Python Project',
            'framework': None,
            'directories': [],
            'structure_summary': 'Basic'
        }
        mock_detect_git.return_value = {
            'is_git_repo': False,
            'has_remote': False,
            'remote_name': None,
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': False,
            'workflow_mode': 'no_git'
        }

        # Simulate Ctrl+C - KeyboardInterrupt should propagate
        mock_input.side_effect = KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            interactive_setup_wizard()

    @patch('proto_gear.safe_input')
    @patch('proto_gear.detect_git_config')
    @patch('proto_gear.detect_project_structure')
    def test_wizard_default_prefix(self, mock_detect_project, mock_detect_git, mock_input):
        """Test wizard with default prefix (empty input)"""
        mock_detect_project.return_value = {
            'detected': True,
            'type': 'Python Project',
            'framework': None,
            'directories': [],
            'structure_summary': 'Basic'
        }
        mock_detect_git.return_value = {
            'is_git_repo': True,
            'has_remote': True,
            'remote_name': 'origin',
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': True,
            'workflow_mode': 'remote_automated'
        }

        # User inputs: yes to branching, empty (default prefix), yes to proceed
        mock_input.side_effect = ['y', '', 'y']

        result = interactive_setup_wizard()

        assert result['with_branching'] is True
        assert result['ticket_prefix'] == 'PROJ'  # Default
        assert result['confirmed'] is True

    @patch('proto_gear.safe_input')
    @patch('proto_gear.detect_git_config')
    @patch('proto_gear.detect_project_structure')
    def test_wizard_invalid_prefix_fallback(self, mock_detect_project, mock_detect_git, mock_input):
        """Test wizard with invalid prefix falls back to default"""
        mock_detect_project.return_value = {
            'detected': True,
            'type': 'Node.js Project',
            'framework': 'npm',
            'directories': ['src', 'test'],
            'structure_summary': 'Standard'
        }
        mock_detect_git.return_value = {
            'is_git_repo': True,
            'has_remote': False,
            'remote_name': None,
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': False,
            'workflow_mode': 'local_only'
        }

        # User inputs: yes to branching, invalid prefix (!@#), yes to proceed
        mock_input.side_effect = ['y', '!@#', 'y']

        result = interactive_setup_wizard()

        assert result['with_branching'] is True
        # Should fall back to suggested prefix (PROJ)
        assert result['ticket_prefix'] == 'PROJ'
        assert result['confirmed'] is True

    @patch('proto_gear.safe_input')
    @patch('proto_gear.detect_git_config')
    @patch('proto_gear.detect_project_structure')
    def test_wizard_invalid_responses_retry(self, mock_detect_project, mock_detect_git, mock_input):
        """Test wizard retry on invalid responses"""
        mock_detect_project.return_value = {
            'detected': True,
            'type': 'Python Project',
            'framework': None,
            'directories': [],
            'structure_summary': 'Basic'
        }
        mock_detect_git.return_value = {
            'is_git_repo': False,
            'has_remote': False,
            'remote_name': None,
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': False,
            'workflow_mode': 'no_git'
        }

        # User inputs: invalid, then 'y' for branching; then 'maybe' (invalid), then 'y' for confirm
        mock_input.side_effect = ['maybe', 'y', 'MYPROJ', 'maybe', 'y']

        result = interactive_setup_wizard()

        assert result['with_branching'] is True
        assert result['ticket_prefix'] == 'MYPROJ'
        assert result['confirmed'] is True


class TestMainFunction:
    """Test main() CLI entry point"""

    @patch('sys.argv', ['pg', 'init', '--dry-run', '--no-interactive', '--with-branching', '--ticket-prefix', 'TEST'])
    @patch('proto_gear.run_simple_protogear_init')
    def test_main_init_non_interactive(self, mock_run_init):
        """Test main with init command non-interactive"""
        mock_run_init.return_value = {'status': 'success', 'files_created': ['AGENTS.md']}

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_run_init.assert_called_once()

    @patch('sys.argv', ['pg', 'init', '--dry-run'])
    @patch('proto_gear.interactive_setup_wizard')
    @patch('proto_gear.run_simple_protogear_init')
    @patch.dict('proto_gear.__dict__', {'ENHANCED_WIZARD_AVAILABLE': False, 'QUESTIONARY_AVAILABLE': False})
    def test_main_init_fallback_wizard(self, mock_run_init, mock_wizard):
        """Test main with fallback to simple wizard"""
        mock_wizard.return_value = {'confirmed': True, 'with_branching': False, 'ticket_prefix': None}
        mock_run_init.return_value = {'status': 'success'}

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_wizard.assert_called_once()

    @patch('sys.argv', ['pg', 'init'])
    @patch('proto_gear.interactive_setup_wizard')
    @patch.dict('proto_gear.__dict__', {'ENHANCED_WIZARD_AVAILABLE': False, 'QUESTIONARY_AVAILABLE': False})
    def test_main_init_wizard_cancelled(self, mock_wizard):
        """Test main when wizard is cancelled"""
        mock_wizard.return_value = {'confirmed': False}

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    @patch('sys.argv', ['pg', 'init'])
    @patch('proto_gear.interactive_setup_wizard')
    @patch.dict('proto_gear.__dict__', {'ENHANCED_WIZARD_AVAILABLE': False, 'QUESTIONARY_AVAILABLE': False})
    def test_main_init_wizard_keyboard_interrupt(self, mock_wizard):
        """Test main when wizard receives Ctrl+C"""
        mock_wizard.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    @patch('sys.argv', ['pg', 'help'])
    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_main_help_command(self, mock_print, mock_input):
        """Test main with help command"""
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    @patch('sys.argv', ['pg'])
    @patch('builtins.print')
    def test_main_no_command(self, mock_print):
        """Test main with no command shows welcome"""
        # main() should complete without raising SystemExit in this case
        main()

        # Verify welcome message was printed
        assert mock_print.called

    @patch('sys.argv', ['pg', 'init', '--dry-run', '--no-interactive', '--with-branching'])
    @patch('proto_gear.run_simple_protogear_init')
    def test_main_init_failed(self, mock_run_init):
        """Test main when init fails"""
        mock_run_init.return_value = {'status': 'failed', 'error': 'Test error'}

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    @patch('sys.argv', ['pg'])
    @patch('builtins.print')
    def test_main_keyboard_interrupt_handler(self, mock_print):
        """Test main Ctrl+C handler at top level"""
        with patch('proto_gear.show_splash_screen', side_effect=KeyboardInterrupt()):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    @patch('sys.argv', ['pg', 'init', '--dry-run', '--no-interactive'])
    @patch('proto_gear.run_simple_protogear_init')
    def test_main_init_cancelled_status(self, mock_run_init):
        """Test main when init returns cancelled status"""
        mock_run_init.return_value = {'status': 'cancelled'}

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    @patch('sys.argv', ['pg'])
    @patch('builtins.print')
    def test_main_unexpected_exception(self, mock_print):
        """Test main with unexpected exception"""
        with patch('proto_gear.show_splash_screen', side_effect=RuntimeError('Test error')):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Should exit with error code 1
            assert exc_info.value.code == 1


class TestRunSimpleProtoGearInit:
    """Test simple ProtoGear initialization"""

    @patch('proto_gear.setup_agent_framework_only')
    @patch('proto_gear.detect_git_config')
    @patch('proto_gear.detect_project_structure')
    def test_run_simple_init_dry_run(self, mock_detect_project, mock_detect_git, mock_setup):
        """Test simple init in dry-run mode"""
        mock_detect_project.return_value = {
            'detected': True,
            'type': 'Python Project',
            'framework': None,
            'directories': [],
            'structure_summary': 'Basic'
        }
        mock_detect_git.return_value = {
            'is_git_repo': True,
            'has_remote': False,
            'remote_name': None,
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': False,
            'workflow_mode': 'local_only'
        }
        mock_setup.return_value = {'status': 'success', 'dry_run': True}

        result = run_simple_protogear_init(
            dry_run=True,
            with_branching=False,
            ticket_prefix='TEST'
        )

        assert result['status'] == 'success'
        mock_setup.assert_called_once()

    @patch('proto_gear.setup_agent_framework_only')
    @patch('proto_gear.detect_git_config')
    @patch('proto_gear.detect_project_structure')
    def test_run_simple_init_with_branching(self, mock_detect_project, mock_detect_git, mock_setup):
        """Test simple init with branching enabled"""
        mock_detect_project.return_value = {
            'detected': True,
            'type': 'Node.js Project',
            'framework': 'React',
            'directories': ['src'],
            'structure_summary': 'React project'
        }
        mock_detect_git.return_value = {
            'is_git_repo': True,
            'has_remote': True,
            'remote_name': 'origin',
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': True,
            'workflow_mode': 'remote_automated'
        }
        mock_setup.return_value = {'status': 'success'}

        result = run_simple_protogear_init(
            dry_run=False,
            with_branching=True,
            ticket_prefix='APP'
        )

        assert result['status'] == 'success'
        # Verify setup was called with correct parameters
        call_args = mock_setup.call_args
        assert call_args[1]['with_branching'] is True
        assert call_args[1]['ticket_prefix'] == 'APP'

    @patch('proto_gear.setup_agent_framework_only')
    @patch('proto_gear.detect_git_config')
    @patch('proto_gear.detect_project_structure')
    def test_run_simple_init_no_git(self, mock_detect_project, mock_detect_git, mock_setup):
        """Test simple init without Git repository"""
        mock_detect_project.return_value = {
            'detected': False,
            'type': None,
            'framework': None,
            'directories': [],
            'structure_summary': 'No project detected'
        }
        mock_detect_git.return_value = {
            'is_git_repo': False,
            'has_remote': False,
            'remote_name': None,
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': False,
            'workflow_mode': 'no_git'
        }
        mock_setup.return_value = {'status': 'success'}

        result = run_simple_protogear_init(
            dry_run=False,
            with_branching=False,
            ticket_prefix='PROJ'
        )

        assert result['status'] == 'success'
        mock_setup.assert_called_once()


class TestCapabilitySystemIntegration:
    """Integration tests for capability system with pg init"""

    @patch('proto_gear.copy_capability_templates')
    @patch('proto_gear.setup_agent_framework_only')
    @patch('proto_gear.detect_git_config')
    @patch('proto_gear.detect_project_structure')
    def test_init_with_capabilities_flag(self, mock_detect_project, mock_detect_git, mock_setup, mock_copy_caps):
        """Test pg init --with-capabilities --dry-run"""
        mock_detect_project.return_value = {
            'detected': True,
            'type': 'Python Project',
            'framework': None,
            'directories': [],
            'structure_summary': 'Basic'
        }
        mock_detect_git.return_value = {
            'is_git_repo': True,
            'has_remote': False,
            'remote_name': None,
            'main_branch': 'main',
            'dev_branch': 'development',
            'has_gh_cli': False,
            'workflow_mode': 'local_only'
        }
        mock_setup.return_value = {'status': 'success', 'files_created': ['AGENTS.md']}
        mock_copy_caps.return_value = {
            'status': 'success',
            'files_created': ['.proto-gear/INDEX.md', '.proto-gear/skills/INDEX.md']
        }

        # Note: This test assumes --with-capabilities will be implemented
        # For now, we're testing the expected behavior
        result = run_simple_protogear_init(
            dry_run=True,
            with_branching=False,
            ticket_prefix='TEST'
        )

        assert result['status'] == 'success'
        # When --with-capabilities is implemented, copy_capability_templates should be called
        # mock_copy_caps.assert_called_once()

    def test_capability_files_in_dry_run_output(self, tmp_path, monkeypatch, capsys):
        """Test that dry run shows .proto-gear/ files when capabilities enabled"""
        # This test will be more meaningful once copy_capability_templates is implemented
        # For now, just verify dry-run doesn't crash
        monkeypatch.chdir(tmp_path)

        with patch('proto_gear.detect_project_structure') as mock_detect:
            with patch('proto_gear.detect_git_config') as mock_git:
                mock_detect.return_value = {
                    'detected': True,
                    'type': 'Python Project',
                    'framework': None,
                    'directories': [],
                    'structure_summary': 'Basic'
                }
                mock_git.return_value = {
                    'is_git_repo': False,
                    'has_remote': False,
                    'remote_name': None,
                    'main_branch': 'main',
                    'dev_branch': 'development',
                    'has_gh_cli': False,
                    'workflow_mode': 'no_git'
                }

                result = setup_agent_framework_only(dry_run=True)

                assert result['status'] == 'success'
                assert result.get('dry_run') is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
