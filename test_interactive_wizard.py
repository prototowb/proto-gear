"""
Test script to validate interactive wizard functionality
This simulates what happens when a user runs pg init in PowerShell/CMD
"""

import sys
from pathlib import Path

# Add proto_gear_pkg to path
sys.path.insert(0, str(Path(__file__).parent / "core"))

def test_wizard_imports():
    """Test that all wizard components can be imported"""
    print("Testing wizard imports...")

    try:
        from proto_gear_pkg.interactive_wizard import (
            InteractiveWizard,
            run_enhanced_wizard,
            QUESTIONARY_AVAILABLE,
            RICH_AVAILABLE,
            CHARS
        )
        print(f"✓ InteractiveWizard imported successfully")
        print(f"✓ QUESTIONARY_AVAILABLE: {QUESTIONARY_AVAILABLE}")
        print(f"✓ RICH_AVAILABLE: {RICH_AVAILABLE}")
        print(f"✓ CHARS dictionary loaded: {len(CHARS)} symbols")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_encoding_safe_chars():
    """Test that encoding-safe characters are properly defined"""
    print("\nTesting encoding-safe characters...")

    from proto_gear_pkg.interactive_wizard import CHARS

    required_chars = ['check', 'cross', 'bullet', 'line', 'wrench', 'clipboard', 'ticket', 'memo', 'chart']

    for char_name in required_chars:
        if char_name in CHARS:
            print(f"✓ {char_name}: '{CHARS[char_name]}'")
        else:
            print(f"✗ {char_name}: MISSING")
            return False

    return True

def test_wizard_initialization():
    """Test that wizard can be initialized"""
    print("\nTesting wizard initialization...")

    try:
        from proto_gear_pkg.interactive_wizard import InteractiveWizard
        wizard = InteractiveWizard()
        print(f"✓ Wizard initialized")
        print(f"  - Console available: {wizard.console is not None}")
        return True
    except Exception as e:
        print(f"✗ Wizard initialization failed: {e}")
        return False

def test_project_detection():
    """Test project detection in a known directory"""
    print("\nTesting project detection...")

    try:
        from proto_gear_pkg.proto_gear import detect_project_structure, detect_git_config

        # Test on vue-course-app directory
        test_dir = Path("G:/Projects/vue-course-app")
        if test_dir.exists():
            project_info = detect_project_structure(test_dir)
            git_config = detect_git_config()

            print(f"✓ Project detected:")
            print(f"  - Type: {project_info.get('type')}")
            print(f"  - Framework: {project_info.get('framework')}")
            print(f"  - Git repo: {git_config.get('is_git_repo')}")
            return True
        else:
            print(f"⚠ Test directory not found: {test_dir}")
            return True  # Not a failure, just unavailable

    except Exception as e:
        print(f"✗ Project detection failed: {e}")
        return False

def test_panel_creation():
    """Test that wizard can create display panels"""
    print("\nTesting panel creation...")

    try:
        from proto_gear_pkg.interactive_wizard import InteractiveWizard, CHARS
        wizard = InteractiveWizard()

        # Test creating a simple panel
        test_content = f"{CHARS['check']} Test content with encoding-safe chars"
        test_title = f"{CHARS['chart']} Test Panel"

        # This should not raise an encoding error
        wizard.print_panel(test_content, title=test_title, border_style="cyan")
        print(f"✓ Panel created successfully with encoding-safe characters")
        return True

    except UnicodeEncodeError as e:
        print(f"✗ Encoding error in panel creation: {e}")
        return False
    except Exception as e:
        print(f"✗ Panel creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("Proto Gear Interactive Wizard Validation")
    print("=" * 70)

    tests = [
        test_wizard_imports,
        test_encoding_safe_chars,
        test_wizard_initialization,
        test_project_detection,
        test_panel_creation,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test '{test_func.__name__}' crashed: {e}")
            results.append(False)

    print("\n" + "=" * 70)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)

    if all(results):
        print("\n✓ All tests passed! Interactive wizard is ready for PowerShell/CMD")
        print("\nTo test manually in PowerShell:")
        print("  cd G:\\Projects\\vue-course-app")
        print("  pg init")
        return 0
    else:
        print("\n✗ Some tests failed. Review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
