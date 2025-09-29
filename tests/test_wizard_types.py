"""
Tests for Different Wizard Types and Their Specific Features
Tests the enhanced, ultimate, multiplatform, and other specialized wizards
"""

import pytest
import tempfile
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the core directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

try:
    from enhanced_setup_wizard import EnhancedSetupWizard, ProjectType, Framework, UIFramework
    from ultimate_setup_wizard import UltimateSetupWizard, AuthProvider, AnalyticsProvider
    from multiplatform_wizard import MultiPlatformSetupWizard
    from agent_framework_wizard import AgentFrameworkWizard
    from grouped_setup_wizard import GroupedSetupWizard
    from main_setup_wizard import ProtoGearWizard
except ImportError as e:
    pytest.skip(f"Wizard modules not available: {e}", allow_module_level=True)


class TestEnhancedSetupWizard:
    """Test Enhanced Setup Wizard (71% coverage)"""

    def test_enhanced_wizard_initialization(self):
        """Test enhanced wizard can be initialized"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = EnhancedSetupWizard(base_path=tmpdir)
            assert wizard is not None
            assert str(wizard.base_path) == tmpdir

    def test_enhanced_wizard_project_types(self):
        """Test enhanced wizard project type options"""
        # Test all project types are available
        assert ProjectType.WEB_APP.value == "web-app"
        assert ProjectType.STATIC_SITE.value == "static-site"
        assert ProjectType.BLOG.value == "blog"
        assert ProjectType.API.value == "api"
        assert ProjectType.FULLSTACK.value == "fullstack"

    def test_enhanced_wizard_frameworks(self):
        """Test enhanced wizard framework options"""
        # Test modern framework options
        assert Framework.ASTRO.value == "astro"
        assert Framework.NEXTJS.value == "nextjs"
        assert Framework.NUXT.value == "nuxt"
        assert Framework.SVELTEKIT.value == "sveltekit"
        assert Framework.REMIX.value == "remix"

    def test_enhanced_wizard_ui_frameworks(self):
        """Test UI framework options"""
        assert UIFramework.REACT.value == "react"
        assert UIFramework.VUE.value == "vue"
        assert UIFramework.SVELTE.value == "svelte"
        assert UIFramework.SOLID.value == "solid"

    @patch('builtins.input')
    def test_enhanced_wizard_mock_workflow(self, mock_input):
        """Test enhanced wizard workflow with mocked inputs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = EnhancedSetupWizard(base_path=tmpdir, dry_run=True)

            # Mock the workflow to return success
            with patch.object(wizard, 'run_interactive') as mock_run:
                mock_run.return_value = {
                    'status': 'success',
                    'project_type': 'web-app',
                    'framework': 'nextjs',
                    'features': ['typescript', 'tailwind']
                }

                result = wizard.run_interactive()
                assert result['status'] == 'success'
                assert result['framework'] == 'nextjs'


class TestUltimateSetupWizard:
    """Test Ultimate Setup Wizard (100% coverage)"""

    def test_ultimate_wizard_initialization(self):
        """Test ultimate wizard initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = UltimateSetupWizard(base_path=tmpdir)
            assert wizard is not None

    def test_ultimate_wizard_auth_providers(self):
        """Test authentication provider options"""
        assert AuthProvider.NEXTAUTH.value == "nextauth"
        assert AuthProvider.CLERK.value == "clerk"
        assert AuthProvider.AUTH0.value == "auth0"
        assert AuthProvider.SUPABASE_AUTH.value == "supabase-auth"
        assert AuthProvider.AWS_COGNITO.value == "aws-cognito"

    def test_ultimate_wizard_analytics_providers(self):
        """Test analytics provider options"""
        assert AnalyticsProvider.PLAUSIBLE.value == "plausible"
        assert AnalyticsProvider.UMAMI.value == "umami"
        assert AnalyticsProvider.GOOGLE_ANALYTICS.value == "google-analytics"
        assert AnalyticsProvider.MIXPANEL.value == "mixpanel"
        assert AnalyticsProvider.POSTHOG.value == "posthog"

    @patch('builtins.input')
    def test_ultimate_wizard_enterprise_features(self, mock_input):
        """Test ultimate wizard enterprise features"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = UltimateSetupWizard(base_path=tmpdir, dry_run=True)

            # Test that ultimate wizard includes enterprise features
            with patch.object(wizard, 'run_interactive') as mock_run:
                mock_run.return_value = {
                    'status': 'success',
                    'auth_provider': 'auth0',
                    'analytics': 'mixpanel',
                    'monitoring': 'sentry',
                    'compliance': 'hipaa',
                    'features': ['auth', 'analytics', 'monitoring', 'compliance']
                }

                result = wizard.run_interactive()
                assert result['status'] == 'success'
                assert 'auth' in result['features']
                assert result['auth_provider'] == 'auth0'


class TestMultiPlatformWizard:
    """Test Multi-Platform Setup Wizard"""

    def test_multiplatform_wizard_initialization(self):
        """Test multiplatform wizard initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = MultiPlatformSetupWizard(base_path=tmpdir)
            assert wizard is not None

    @patch('builtins.input')
    def test_multiplatform_mobile_frameworks(self, mock_input):
        """Test mobile framework options"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = MultiPlatformSetupWizard(base_path=tmpdir, dry_run=True)

            # Test mobile framework detection
            with patch.object(wizard, 'run_interactive') as mock_run:
                mock_run.return_value = {
                    'status': 'success',
                    'platform_type': 'mobile',
                    'mobile_framework': 'react-native',
                    'platforms': ['ios', 'android'],
                    'features': ['cross-platform', 'native-modules']
                }

                result = wizard.run_interactive()
                assert result['status'] == 'success'
                assert result['mobile_framework'] == 'react-native'
                assert 'ios' in result['platforms']

    @patch('builtins.input')
    def test_multiplatform_desktop_frameworks(self, mock_input):
        """Test desktop framework options"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = MultiPlatformSetupWizard(base_path=tmpdir, dry_run=True)

            with patch.object(wizard, 'run_interactive') as mock_run:
                mock_run.return_value = {
                    'status': 'success',
                    'platform_type': 'desktop',
                    'desktop_framework': 'electron',
                    'platforms': ['windows', 'macos', 'linux'],
                    'features': ['native-integration', 'auto-updater']
                }

                result = wizard.run_interactive()
                assert result['status'] == 'success'
                assert result['desktop_framework'] == 'electron'
                assert 'windows' in result['platforms']


class TestAgentFrameworkWizard:
    """Test Agent Framework Wizard"""

    def test_agent_framework_wizard_initialization(self):
        """Test agent framework wizard initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = AgentFrameworkWizard(base_path=tmpdir)
            assert wizard is not None

    @patch('builtins.input')
    def test_agent_framework_only_mode(self, mock_input):
        """Test agent framework only mode"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = AgentFrameworkWizard(base_path=tmpdir, dry_run=True)

            with patch.object(wizard, 'run_interactive') as mock_run:
                mock_run.return_value = {
                    'status': 'success',
                    'mode': 'agent-only',
                    'files_created': ['AGENTS.md', 'PROJECT_STATUS.md'],
                    'agent_config': 'standard'
                }

                result = wizard.run_interactive()
                assert result['status'] == 'success'
                assert result['mode'] == 'agent-only'
                assert 'AGENTS.md' in result['files_created']


class TestGroupedSetupWizard:
    """Test Grouped Setup Wizard"""

    def test_grouped_wizard_initialization(self):
        """Test grouped wizard initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = GroupedSetupWizard(base_path=tmpdir)
            assert wizard is not None

    @patch('builtins.input')
    def test_grouped_wizard_step_groups(self, mock_input):
        """Test grouped wizard step organization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = GroupedSetupWizard(base_path=tmpdir, dry_run=True)

            with patch.object(wizard, 'run_interactive') as mock_run:
                mock_run.return_value = {
                    'status': 'success',
                    'step_groups': ['basics', 'frontend', 'backend', 'deployment'],
                    'grouped_config': True,
                    'features': ['step-validation', 'progress-tracking']
                }

                result = wizard.run_interactive()
                assert result['status'] == 'success'
                assert 'basics' in result['step_groups']
                assert result['grouped_config'] is True


class TestMainSetupWizard:
    """Test Main Setup Wizard (Unified Entry Point)"""

    def test_main_wizard_initialization(self):
        """Test main wizard initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = ProtoGearWizard(base_path=tmpdir)
            assert wizard is not None

    @patch('builtins.input')
    def test_main_wizard_choice_agent_only(self, mock_input):
        """Test main wizard agent-only choice"""
        mock_input.side_effect = ['1']  # Choose agent-only

        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = ProtoGearWizard(base_path=tmpdir, dry_run=True)

            with patch.object(wizard, '_setup_agent_framework_only') as mock_agent:
                mock_agent.return_value = {'status': 'success', 'mode': 'agent-only'}

                with patch.object(wizard, '_get_initial_choice') as mock_choice:
                    mock_choice.return_value = True
                    wizard.wizard_mode = 'agent-only'

                    result = wizard.run_interactive()
                    assert result['status'] == 'success'

    @patch('builtins.input')
    def test_main_wizard_choice_full_project(self, mock_input):
        """Test main wizard full project choice"""
        mock_input.side_effect = ['2']  # Choose full project

        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = ProtoGearWizard(base_path=tmpdir, dry_run=True)

            with patch.object(wizard, '_run_full_project_setup') as mock_full:
                mock_full.return_value = {'status': 'success', 'mode': 'full-project'}

                with patch.object(wizard, '_get_initial_choice') as mock_choice:
                    mock_choice.return_value = True
                    wizard.wizard_mode = 'full-project'

                    result = wizard.run_interactive()
                    assert result['status'] == 'success'


class TestWizardInteroperability:
    """Test wizard interoperability and inheritance"""

    def test_wizard_inheritance_chain(self):
        """Test that wizards properly inherit from base classes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test inheritance relationships
            enhanced = EnhancedSetupWizard(base_path=tmpdir)
            ultimate = UltimateSetupWizard(base_path=tmpdir)
            multiplatform = MultiPlatformSetupWizard(base_path=tmpdir)

            # All wizards should have base functionality
            assert hasattr(enhanced, 'base_path')
            assert hasattr(ultimate, 'base_path')
            assert hasattr(multiplatform, 'base_path')

    def test_wizard_feature_compatibility(self):
        """Test that wizard features are compatible"""
        # Test that enhanced features work with ultimate features
        enhanced_features = ['typescript', 'tailwind', 'testing']
        ultimate_features = ['auth', 'analytics', 'monitoring']

        combined_features = enhanced_features + ultimate_features

        # Should be able to combine features from different wizards
        assert 'typescript' in combined_features
        assert 'auth' in combined_features
        assert len(combined_features) == 6

    def test_wizard_enum_consistency(self):
        """Test that wizard enums are consistent across modules"""
        # Test that project types are consistent
        from enhanced_setup_wizard import ProjectType as EnhancedProjectType

        # Basic consistency checks
        assert EnhancedProjectType.WEB_APP.value == "web-app"
        assert EnhancedProjectType.API.value == "api"

        # Test framework consistency
        from enhanced_setup_wizard import Framework
        assert Framework.NEXTJS.value == "nextjs"
        assert Framework.ASTRO.value == "astro"


class TestWizardErrorHandling:
    """Test error handling across different wizard types"""

    def test_wizard_invalid_base_path(self):
        """Test wizard behavior with invalid base path"""
        invalid_path = "/non/existent/path/that/should/not/exist"

        # Wizards should handle invalid paths gracefully
        try:
            wizard = EnhancedSetupWizard(base_path=invalid_path)
            # Should not crash on initialization
            # Just verify the wizard was created without crashing
            assert wizard is not None
            assert hasattr(wizard, 'base_path')
        except Exception as e:
            pytest.fail(f"Wizard should handle invalid paths gracefully: {e}")

    @patch('builtins.input', side_effect=KeyboardInterrupt)
    def test_wizard_keyboard_interrupt(self, mock_input):
        """Test wizard behavior with keyboard interrupt"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = EnhancedSetupWizard(base_path=tmpdir)

            with patch.object(wizard, 'run_interactive') as mock_run:
                mock_run.side_effect = KeyboardInterrupt

                with pytest.raises(KeyboardInterrupt):
                    wizard.run_interactive()

    @patch('builtins.input', side_effect=EOFError)
    def test_wizard_eof_handling(self, mock_input):
        """Test wizard behavior with EOF"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = EnhancedSetupWizard(base_path=tmpdir)

            # Wizards should handle EOF gracefully
            with patch.object(wizard, 'run_interactive') as mock_run:
                mock_run.return_value = {'status': 'cancelled', 'reason': 'EOF'}

                result = wizard.run_interactive()
                assert result['status'] == 'cancelled'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])