"""
Multi-Platform Development Wizard Extension
Adds support for mobile, desktop, and cross-platform development
"""

from .ultimate_setup_wizard import UltimateSetupWizard, UltimateProjectConfig
from .enhanced_setup_wizard import ProjectType
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path


class MobileFramework(Enum):
    """Mobile development frameworks"""
    REACT_NATIVE = "react-native"
    FLUTTER = "flutter"
    IONIC = "ionic"
    NATIVESCRIPT = "nativescript"
    EXPO = "expo"
    CAPACITOR = "capacitor"
    KOTLIN_MULTIPLATFORM = "kotlin-multiplatform"
    XAMARIN = "xamarin"
    SWIFT_UI = "swiftui"
    JETPACK_COMPOSE = "jetpack-compose"
    NONE = "none"


class DesktopFramework(Enum):
    """Desktop development frameworks"""
    ELECTRON = "electron"
    TAURI = "tauri"
    FLUTTER_DESKTOP = "flutter-desktop"
    AVALONIA = "avalonia"
    WAILS = "wails"
    NEUTRALINO = "neutralino"
    PYQT = "pyqt"
    TKINTER = "tkinter"
    WPF = "wpf"
    WINFORMS = "winforms"
    GTK = "gtk"
    QT = "qt"
    JAVAFX = "javafx"
    SWING = "swing"
    NONE = "none"


class PlatformTarget(Enum):
    """Target platforms"""
    IOS = "ios"
    ANDROID = "android"
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    WEB = "web"
    ALL = "all"


class MobileTestFramework(Enum):
    """Mobile testing frameworks"""
    DETOX = "detox"
    APPIUM = "appium"
    ESPRESSO = "espresso"
    XCUITEST = "xcuitest"
    FLUTTER_TEST = "flutter-test"
    MAESTRO = "maestro"
    CALABASH = "calabash"
    NONE = "none"


class AppDistribution(Enum):
    """App distribution platforms"""
    APP_STORE = "app-store"
    GOOGLE_PLAY = "google-play"
    MICROSOFT_STORE = "microsoft-store"
    TESTFLIGHT = "testflight"
    FIREBASE_DISTRIBUTION = "firebase-distribution"
    APP_CENTER = "app-center"
    HOCKEY_APP = "hockey-app"
    INTERNAL = "internal"
    NONE = "none"


class CodeSigning(Enum):
    """Code signing options"""
    APPLE_DEVELOPER = "apple-developer"
    GOOGLE_PLAY_SIGNING = "google-play-signing"
    WINDOWS_AUTHENTICODE = "windows-authenticode"
    SELF_SIGNED = "self-signed"
    NONE = "none"


class CrossPlatformTool(Enum):
    """Cross-platform development tools"""
    MONOREPO_NX = "nx"
    MONOREPO_TURBOREPO = "turborepo"
    MONOREPO_LERNA = "lerna"
    MONOREPO_RUSH = "rush"
    BAZEL = "bazel"
    CMAKE = "cmake"
    GRADLE = "gradle"
    MAVEN = "maven"
    NONE = "none"


class NativeModule(Enum):
    """Native module support"""
    CAMERA = "camera"
    GPS = "gps"
    BLUETOOTH = "bluetooth"
    NFC = "nfc"
    BIOMETRICS = "biometrics"
    PUSH_NOTIFICATIONS = "push-notifications"
    FILE_SYSTEM = "file-system"
    SQLITE = "sqlite"
    KEYCHAIN = "keychain"
    AR_KIT = "arkit"
    ML_KIT = "mlkit"
    HEALTH_KIT = "healthkit"
    MAPS = "maps"
    PAYMENTS = "payments"
    SHARE = "share"
    CONTACTS = "contacts"
    CALENDAR = "calendar"


class MultiPlatformConfig(UltimateProjectConfig):
    """Extended configuration for multi-platform development"""
    
    def __init__(self):
        super().__init__()
        
        # Mobile configuration
        self.mobile_framework = MobileFramework.NONE
        self.mobile_test_framework = MobileTestFramework.NONE
        self.native_modules = []
        
        # Desktop configuration
        self.desktop_framework = DesktopFramework.NONE
        self.auto_updater = False
        self.system_tray = False
        self.deep_linking = False
        
        # Platform targets
        self.platforms = []
        
        # Cross-platform
        self.cross_platform_tool = CrossPlatformTool.NONE
        self.shared_code_strategy = "none"  # none, shared-lib, monorepo
        
        # Distribution
        self.app_distribution = []
        self.code_signing = CodeSigning.NONE
        
        # Build configuration
        self.build_flavors = []  # dev, staging, prod
        self.bundle_identifier = ""
        self.app_icon_generator = False
        self.splash_screen_generator = False
        
        # Performance
        self.code_push = False  # OTA updates
        self.crash_reporting = False
        self.performance_monitoring = False
        self.app_analytics = False
        
        # Platform-specific settings
        self.ios_settings = {
            "min_version": "13.0",
            "swift_version": "5.9",
            "use_cocoapods": True,
            "use_swift_pm": False
        }
        
        self.android_settings = {
            "min_sdk": 21,
            "target_sdk": 34,
            "compile_sdk": 34,
            "kotlin_version": "1.9.0",
            "gradle_version": "8.2"
        }
        
        self.windows_settings = {
            "min_version": "10.0.17763.0",
            "target_version": "10.0.19041.0",
            "architecture": ["x64", "x86", "arm64"]
        }
        
        self.macos_settings = {
            "min_version": "10.15",
            "notarization": False,
            "sandbox": True
        }
        
        self.linux_settings = {
            "package_formats": ["deb", "rpm", "appimage", "snap", "flatpak"],
            "desktop_file": True
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with multi-platform settings"""
        config = super().to_dict()
        
        config['mobile'] = {
            'framework': self.mobile_framework.value if self.mobile_framework else None,
            'test_framework': self.mobile_test_framework.value if self.mobile_test_framework else None,
            'native_modules': self.native_modules
        }
        
        config['desktop'] = {
            'framework': self.desktop_framework.value if self.desktop_framework else None,
            'auto_updater': self.auto_updater,
            'system_tray': self.system_tray,
            'deep_linking': self.deep_linking
        }
        
        config['platforms'] = {
            'targets': [p.value for p in self.platforms],
            'ios': self.ios_settings,
            'android': self.android_settings,
            'windows': self.windows_settings,
            'macos': self.macos_settings,
            'linux': self.linux_settings
        }
        
        config['distribution'] = {
            'stores': [d.value for d in self.app_distribution],
            'code_signing': self.code_signing.value if self.code_signing else None,
            'bundle_identifier': self.bundle_identifier
        }
        
        config['cross_platform'] = {
            'tool': self.cross_platform_tool.value if self.cross_platform_tool else None,
            'shared_code_strategy': self.shared_code_strategy
        }
        
        config['build'] = {
            'flavors': self.build_flavors,
            'icon_generator': self.app_icon_generator,
            'splash_generator': self.splash_screen_generator
        }
        
        config['performance'] = {
            'code_push': self.code_push,
            'crash_reporting': self.crash_reporting,
            'performance_monitoring': self.performance_monitoring,
            'app_analytics': self.app_analytics
        }
        
        return config


class MultiPlatformSetupWizard(UltimateSetupWizard):
    """Setup wizard with full multi-platform development support"""
    
    def __init__(self, base_path: Path = Path("."), dry_run: bool = False):
        super().__init__(base_path, dry_run)
        # Replace config with multi-platform version
        self.config = MultiPlatformConfig()
    
    def run_interactive(self) -> Dict[str, Any]:
        """Run the interactive setup with multi-platform support"""
        print("\n" + "=" * 60)
        print("🚀 Multi-Platform Agent Framework Setup Wizard")
        print("    Complete Mobile, Desktop & Cross-Platform Support")
        print("=" * 60)
        
        try:
            # Check if we should use template or custom
            use_template = self._select_template()
            
            if use_template:
                return self._setup_from_template()
            
            # Custom configuration flow
            self._configure_project_basics()
            
            # Platform-specific configuration based on project type
            if self.config.project_type == ProjectType.MOBILE:
                self._configure_mobile_development()
            elif self.config.project_type == ProjectType.DESKTOP:
                self._configure_desktop_development()
            elif self.config.project_type == ProjectType.FULLSTACK:
                self._configure_cross_platform()
            else:
                # Fall back to parent implementation for web projects
                return super().run_interactive()
            
            # Common configurations
            self._configure_testing_multiplatform()
            self._configure_distribution()
            self._configure_build_tools()
            self._configure_performance_tools()
            
            # Show summary
            self._show_summary()
            
            # Confirm and create
            confirm = input("\n🚀 Create project with this configuration? (y/n) [y]: ") or 'y'
            if confirm.lower() not in ['y', 'yes']:
                return {'status': 'cancelled'}
            
            # Create the project
            result = self.create_project()
            
            if result['status'] == 'success':
                print(f"\n✅ Multi-platform project created successfully!")
                if result.get('path'):
                    print(f"📁 Location: {result.get('path')}")
                self._show_platform_next_steps()
            
            return result
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup cancelled by user")
            return {'status': 'cancelled'}
    
    def _configure_mobile_development(self):
        """Configure mobile development settings"""
        print("\n📱 Mobile Development Configuration")
        print("-" * 40)
        
        # Select mobile framework
        print("\nMobile framework:")
        frameworks = list(MobileFramework)
        for i, fw in enumerate(frameworks, 1):
            desc = self._get_framework_description(fw)
            print(f"  {i}. {fw.value} - {desc}")
        
        choice = input(f"Choice (1-{len(frameworks)}) [1]: ") or "1"
        if choice.isdigit() and 1 <= int(choice) <= len(frameworks):
            self.config.mobile_framework = frameworks[int(choice) - 1]
        
        # Select target platforms
        print("\n📱 Target platforms (comma-separated numbers):")
        platforms = [PlatformTarget.IOS, PlatformTarget.ANDROID, PlatformTarget.WEB]
        for i, platform in enumerate(platforms, 1):
            print(f"  {i}. {platform.value}")
        
        choices = input("Platforms (e.g., 1,2) [1,2]: ") or "1,2"
        selected_platforms = []
        for c in choices.split(','):
            if c.strip().isdigit():
                idx = int(c.strip()) - 1
                if 0 <= idx < len(platforms):
                    selected_platforms.append(platforms[idx])
        
        self.config.platforms = selected_platforms or [PlatformTarget.IOS, PlatformTarget.ANDROID]
        
        # Configure native modules
        print("\n🔧 Native modules needed (comma-separated numbers):")
        modules = list(NativeModule)[:10]  # Show first 10 most common
        for i, module in enumerate(modules, 1):
            print(f"  {i}. {module.value}")
        print(f"  {len(modules)+1}. None")
        
        choices = input("Modules (e.g., 1,3,5): ") or ""
        if choices:
            selected_modules = []
            for c in choices.split(','):
                if c.strip().isdigit():
                    idx = int(c.strip()) - 1
                    if 0 <= idx < len(modules):
                        selected_modules.append(modules[idx].value)
            self.config.native_modules = selected_modules
        
        # Configure platform-specific settings
        if PlatformTarget.IOS in self.config.platforms:
            print("\n🍎 iOS Configuration:")
            self.config.ios_settings['min_version'] = input("  Minimum iOS version [13.0]: ") or "13.0"
            cocoapods = input("  Use CocoaPods? (y/n) [y]: ") or "y"
            self.config.ios_settings['use_cocoapods'] = cocoapods.lower() in ['y', 'yes']
        
        if PlatformTarget.ANDROID in self.config.platforms:
            print("\n🤖 Android Configuration:")
            min_sdk = input("  Minimum SDK (21-34) [21]: ") or "21"
            self.config.android_settings['min_sdk'] = int(min_sdk) if min_sdk.isdigit() else 21
            target_sdk = input("  Target SDK (21-34) [34]: ") or "34"
            self.config.android_settings['target_sdk'] = int(target_sdk) if target_sdk.isdigit() else 34
    
    def _configure_desktop_development(self):
        """Configure desktop development settings"""
        print("\n🖥️  Desktop Development Configuration")
        print("-" * 40)
        
        # Select desktop framework
        print("\nDesktop framework:")
        frameworks = [
            DesktopFramework.ELECTRON,
            DesktopFramework.TAURI,
            DesktopFramework.FLUTTER_DESKTOP,
            DesktopFramework.WAILS,
            DesktopFramework.NEUTRALINO,
            DesktopFramework.NONE
        ]
        
        for i, fw in enumerate(frameworks, 1):
            desc = self._get_desktop_framework_description(fw)
            print(f"  {i}. {fw.value} - {desc}")
        
        choice = input(f"Choice (1-{len(frameworks)}) [1]: ") or "1"
        if choice.isdigit() and 1 <= int(choice) <= len(frameworks):
            self.config.desktop_framework = frameworks[int(choice) - 1]
        
        # Select target platforms
        print("\n💻 Target platforms (comma-separated):")
        platforms = [PlatformTarget.WINDOWS, PlatformTarget.MACOS, PlatformTarget.LINUX]
        for i, platform in enumerate(platforms, 1):
            print(f"  {i}. {platform.value}")
        
        choices = input("Platforms (e.g., 1,2,3) [1,2,3]: ") or "1,2,3"
        selected_platforms = []
        for c in choices.split(','):
            if c.strip().isdigit():
                idx = int(c.strip()) - 1
                if 0 <= idx < len(platforms):
                    selected_platforms.append(platforms[idx])
        
        self.config.platforms = selected_platforms or platforms
        
        # Desktop features
        print("\n⚙️  Desktop Features:")
        auto_update = input("  Auto-updater? (y/n) [y]: ") or "y"
        self.config.auto_updater = auto_update.lower() in ['y', 'yes']
        
        system_tray = input("  System tray support? (y/n) [n]: ") or "n"
        self.config.system_tray = system_tray.lower() in ['y', 'yes']
        
        deep_link = input("  Deep linking support? (y/n) [n]: ") or "n"
        self.config.deep_linking = deep_link.lower() in ['y', 'yes']
        
        # Platform-specific settings
        if PlatformTarget.WINDOWS in self.config.platforms:
            print("\n🪟 Windows Configuration:")
            self.config.windows_settings['min_version'] = input("  Min Windows version [10.0.17763.0]: ") or "10.0.17763.0"
        
        if PlatformTarget.MACOS in self.config.platforms:
            print("\n🍎 macOS Configuration:")
            self.config.macos_settings['min_version'] = input("  Min macOS version [10.15]: ") or "10.15"
            notarize = input("  Enable notarization? (y/n) [n]: ") or "n"
            self.config.macos_settings['notarization'] = notarize.lower() in ['y', 'yes']
        
        if PlatformTarget.LINUX in self.config.platforms:
            print("\n🐧 Linux Configuration:")
            print("  Package formats (comma-separated):")
            print("    1. deb  2. rpm  3. AppImage  4. snap  5. flatpak")
            formats = input("  Formats (e.g., 1,3) [1,3]: ") or "1,3"
            selected_formats = []
            format_map = {1: "deb", 2: "rpm", 3: "appimage", 4: "snap", 5: "flatpak"}
            for f in formats.split(','):
                if f.strip().isdigit() and int(f.strip()) in format_map:
                    selected_formats.append(format_map[int(f.strip())])
            self.config.linux_settings['package_formats'] = selected_formats or ["deb", "appimage"]
    
    def _configure_cross_platform(self):
        """Configure cross-platform development"""
        print("\n🌐 Cross-Platform Development Configuration")
        print("-" * 40)
        
        # Choose development strategy
        print("\nDevelopment strategy:")
        print("  1. Web + Mobile (React Native Web / Ionic)")
        print("  2. Mobile + Desktop (Flutter / React Native)")
        print("  3. Universal (Web + Mobile + Desktop)")
        print("  4. Custom configuration")
        
        strategy = input("Choice (1-4) [3]: ") or "3"
        
        if strategy == "1":
            # Web + Mobile
            self.config.mobile_framework = MobileFramework.REACT_NATIVE
            self.config.platforms = [PlatformTarget.WEB, PlatformTarget.IOS, PlatformTarget.ANDROID]
        elif strategy == "2":
            # Mobile + Desktop
            self.config.mobile_framework = MobileFramework.FLUTTER
            self.config.desktop_framework = DesktopFramework.FLUTTER_DESKTOP
            self.config.platforms = [PlatformTarget.IOS, PlatformTarget.ANDROID, 
                                   PlatformTarget.WINDOWS, PlatformTarget.MACOS]
        elif strategy == "3":
            # Universal
            print("\n🔧 Universal framework:")
            print("  1. Expo (Web + Mobile)")
            print("  2. Ionic + Capacitor (Web + Mobile + Desktop via Electron)")
            print("  3. Flutter (Mobile + Desktop + Web)")
            print("  4. Tauri + Web (Desktop + Web, Mobile coming)")
            
            universal = input("Choice (1-4) [3]: ") or "3"
            if universal == "1":
                self.config.mobile_framework = MobileFramework.EXPO
                self.config.platforms = [PlatformTarget.WEB, PlatformTarget.IOS, PlatformTarget.ANDROID]
            elif universal == "2":
                self.config.mobile_framework = MobileFramework.IONIC
                self.config.desktop_framework = DesktopFramework.ELECTRON
                self.config.platforms = [PlatformTarget.WEB, PlatformTarget.IOS, 
                                       PlatformTarget.ANDROID, PlatformTarget.WINDOWS,
                                       PlatformTarget.MACOS, PlatformTarget.LINUX]
            elif universal == "3":
                self.config.mobile_framework = MobileFramework.FLUTTER
                self.config.desktop_framework = DesktopFramework.FLUTTER_DESKTOP
                self.config.platforms = list(PlatformTarget)[:6]  # All except 'all'
            else:
                self.config.desktop_framework = DesktopFramework.TAURI
                self.config.platforms = [PlatformTarget.WEB, PlatformTarget.WINDOWS,
                                       PlatformTarget.MACOS, PlatformTarget.LINUX]
        else:
            # Custom
            self._configure_mobile_development()
            self._configure_desktop_development()
        
        # Monorepo setup
        print("\n📦 Code organization:")
        print("  1. Monorepo (shared code)")
        print("  2. Separate repositories")
        print("  3. Hybrid (shared libraries)")
        
        org = input("Choice (1-3) [1]: ") or "1"
        
        if org == "1":
            print("\n🔧 Monorepo tool:")
            tools = [CrossPlatformTool.MONOREPO_NX, CrossPlatformTool.MONOREPO_TURBOREPO,
                    CrossPlatformTool.MONOREPO_LERNA, CrossPlatformTool.NONE]
            for i, tool in enumerate(tools, 1):
                print(f"  {i}. {tool.value}")
            
            choice = input(f"Choice (1-{len(tools)}) [1]: ") or "1"
            if choice.isdigit() and 1 <= int(choice) <= len(tools):
                self.config.cross_platform_tool = tools[int(choice) - 1]
            
            self.config.shared_code_strategy = "monorepo"
        elif org == "3":
            self.config.shared_code_strategy = "shared-lib"
    
    def _configure_testing_multiplatform(self):
        """Configure testing for multi-platform projects"""
        print("\n🧪 Testing Configuration")
        print("-" * 40)
        
        # Mobile testing
        if self.config.mobile_framework != MobileFramework.NONE:
            print("\nMobile testing framework:")
            
            # Suggest based on mobile framework
            if self.config.mobile_framework == MobileFramework.REACT_NATIVE:
                frameworks = [MobileTestFramework.DETOX, MobileTestFramework.APPIUM]
            elif self.config.mobile_framework == MobileFramework.FLUTTER:
                frameworks = [MobileTestFramework.FLUTTER_TEST, MobileTestFramework.APPIUM]
            else:
                frameworks = [MobileTestFramework.APPIUM, MobileTestFramework.MAESTRO]
            
            frameworks.append(MobileTestFramework.NONE)
            
            for i, fw in enumerate(frameworks, 1):
                print(f"  {i}. {fw.value}")
            
            choice = input(f"Choice (1-{len(frameworks)}) [1]: ") or "1"
            if choice.isdigit() and 1 <= int(choice) <= len(frameworks):
                self.config.mobile_test_framework = frameworks[int(choice) - 1]
        
        # Also configure standard testing from parent
        super()._configure_testing()
    
    def _configure_distribution(self):
        """Configure app distribution"""
        print("\n📦 Distribution Configuration")
        print("-" * 40)
        
        distributions = []
        
        if PlatformTarget.IOS in self.config.platforms:
            print("\n🍎 iOS Distribution:")
            app_store = input("  App Store? (y/n) [y]: ") or "y"
            if app_store.lower() in ['y', 'yes']:
                distributions.append(AppDistribution.APP_STORE)
            
            testflight = input("  TestFlight? (y/n) [y]: ") or "y"
            if testflight.lower() in ['y', 'yes']:
                distributions.append(AppDistribution.TESTFLIGHT)
        
        if PlatformTarget.ANDROID in self.config.platforms:
            print("\n🤖 Android Distribution:")
            play_store = input("  Google Play? (y/n) [y]: ") or "y"
            if play_store.lower() in ['y', 'yes']:
                distributions.append(AppDistribution.GOOGLE_PLAY)
        
        if PlatformTarget.WINDOWS in self.config.platforms:
            print("\n🪟 Windows Distribution:")
            ms_store = input("  Microsoft Store? (y/n) [n]: ") or "n"
            if ms_store.lower() in ['y', 'yes']:
                distributions.append(AppDistribution.MICROSOFT_STORE)
        
        # Universal distribution options
        if distributions:
            print("\n📱 Additional distribution:")
            firebase = input("  Firebase App Distribution? (y/n) [n]: ") or "n"
            if firebase.lower() in ['y', 'yes']:
                distributions.append(AppDistribution.FIREBASE_DISTRIBUTION)
        
        self.config.app_distribution = distributions
        
        # Code signing
        if distributions:
            print("\n🔐 Code Signing:")
            
            if AppDistribution.APP_STORE in distributions:
                self.config.code_signing = CodeSigning.APPLE_DEVELOPER
                print("  ✓ Apple Developer certificate required")
            elif AppDistribution.GOOGLE_PLAY in distributions:
                self.config.code_signing = CodeSigning.GOOGLE_PLAY_SIGNING
                print("  ✓ Google Play signing configured")
            elif AppDistribution.MICROSOFT_STORE in distributions:
                self.config.code_signing = CodeSigning.WINDOWS_AUTHENTICODE
                print("  ✓ Windows Authenticode required")
            else:
                self.config.code_signing = CodeSigning.SELF_SIGNED
        
        # Bundle identifier
        if self.config.mobile_framework != MobileFramework.NONE or \
           self.config.desktop_framework != DesktopFramework.NONE:
            print("\n📱 App Configuration:")
            bundle = input("  Bundle ID (e.g., com.company.app): ")
            self.config.bundle_identifier = bundle if bundle else f"com.example.{self.config.project.name}"
    
    def _configure_build_tools(self):
        """Configure build tools and flavors"""
        print("\n🔨 Build Configuration")
        print("-" * 40)
        
        # Build flavors
        print("\nBuild flavors/environments:")
        print("  1. Development only")
        print("  2. Dev + Production")
        print("  3. Dev + Staging + Production")
        print("  4. Custom")
        
        flavors = input("Choice (1-4) [3]: ") or "3"
        
        if flavors == "1":
            self.config.build_flavors = ["development"]
        elif flavors == "2":
            self.config.build_flavors = ["development", "production"]
        elif flavors == "3":
            self.config.build_flavors = ["development", "staging", "production"]
        else:
            custom = input("Enter flavors (comma-separated): ")
            self.config.build_flavors = [f.strip() for f in custom.split(',')]
        
        # Asset generation
        if self.config.mobile_framework != MobileFramework.NONE or \
           self.config.desktop_framework != DesktopFramework.NONE:
            print("\n🎨 Asset Generation:")
            
            icon_gen = input("  Auto-generate app icons? (y/n) [y]: ") or "y"
            self.config.app_icon_generator = icon_gen.lower() in ['y', 'yes']
            
            if self.config.mobile_framework != MobileFramework.NONE:
                splash_gen = input("  Auto-generate splash screens? (y/n) [y]: ") or "y"
                self.config.splash_screen_generator = splash_gen.lower() in ['y', 'yes']
    
    def _configure_performance_tools(self):
        """Configure performance and monitoring tools"""
        print("\n📊 Performance & Monitoring")
        print("-" * 40)
        
        if self.config.mobile_framework != MobileFramework.NONE:
            code_push = input("  CodePush (OTA updates)? (y/n) [n]: ") or "n"
            self.config.code_push = code_push.lower() in ['y', 'yes']
        
        crash = input("  Crash reporting? (y/n) [y]: ") or "y"
        self.config.crash_reporting = crash.lower() in ['y', 'yes']
        
        perf = input("  Performance monitoring? (y/n) [y]: ") or "y"
        self.config.performance_monitoring = perf.lower() in ['y', 'yes']
        
        analytics = input("  App analytics? (y/n) [y]: ") or "y"
        self.config.app_analytics = analytics.lower() in ['y', 'yes']
    
    def _get_framework_description(self, framework: MobileFramework) -> str:
        """Get description for mobile framework"""
        descriptions = {
            MobileFramework.REACT_NATIVE: "JavaScript/React for iOS & Android",
            MobileFramework.FLUTTER: "Dart-based, high-performance UI",
            MobileFramework.IONIC: "Web technologies for mobile",
            MobileFramework.EXPO: "React Native with managed workflow",
            MobileFramework.CAPACITOR: "Modern native bridge for web apps",
            MobileFramework.NATIVESCRIPT: "Native APIs with JS/TS",
            MobileFramework.KOTLIN_MULTIPLATFORM: "Kotlin for iOS & Android",
            MobileFramework.XAMARIN: "C#/.NET for mobile",
            MobileFramework.SWIFT_UI: "Native iOS with Swift",
            MobileFramework.JETPACK_COMPOSE: "Native Android with Kotlin",
            MobileFramework.NONE: "No mobile framework"
        }
        return descriptions.get(framework, "")
    
    def _get_desktop_framework_description(self, framework: DesktopFramework) -> str:
        """Get description for desktop framework"""
        descriptions = {
            DesktopFramework.ELECTRON: "Web technologies for desktop",
            DesktopFramework.TAURI: "Rust-based, lightweight alternative to Electron",
            DesktopFramework.FLUTTER_DESKTOP: "Flutter for desktop platforms",
            DesktopFramework.WAILS: "Go + Web frontend",
            DesktopFramework.NEUTRALINO: "Lightweight, portable, minimal",
            DesktopFramework.NONE: "No desktop framework"
        }
        return descriptions.get(framework, "")
    
    def _show_platform_next_steps(self):
        """Show platform-specific next steps"""
        print("\n📝 Next Steps:")
        print("-" * 40)
        
        if self.config.mobile_framework != MobileFramework.NONE:
            print("\n📱 Mobile Development:")
            
            if self.config.mobile_framework == MobileFramework.REACT_NATIVE:
                print("  1. npx react-native run-ios")
                print("  2. npx react-native run-android")
            elif self.config.mobile_framework == MobileFramework.FLUTTER:
                print("  1. flutter doctor")
                print("  2. flutter run")
            elif self.config.mobile_framework == MobileFramework.EXPO:
                print("  1. expo start")
                print("  2. expo build:ios / expo build:android")
            
            if PlatformTarget.IOS in self.config.platforms:
                print("\n  iOS Setup:")
                print("    - Install Xcode from App Store")
                print("    - Set up Apple Developer account")
                print("    - Configure provisioning profiles")
            
            if PlatformTarget.ANDROID in self.config.platforms:
                print("\n  Android Setup:")
                print("    - Install Android Studio")
                print("    - Set up Android SDK")
                print("    - Configure emulators")
        
        if self.config.desktop_framework != DesktopFramework.NONE:
            print("\n💻 Desktop Development:")
            
            if self.config.desktop_framework == DesktopFramework.ELECTRON:
                print("  1. npm run electron:serve")
                print("  2. npm run electron:build")
            elif self.config.desktop_framework == DesktopFramework.TAURI:
                print("  1. npm run tauri dev")
                print("  2. npm run tauri build")
            elif self.config.desktop_framework == DesktopFramework.FLUTTER_DESKTOP:
                print("  1. flutter config --enable-<platform>-desktop")
                print("  2. flutter run -d <platform>")
        
        if self.config.app_distribution:
            print("\n📦 Distribution Setup:")
            
            if AppDistribution.APP_STORE in self.config.app_distribution:
                print("  - Set up App Store Connect")
                print("  - Prepare screenshots and metadata")
            
            if AppDistribution.GOOGLE_PLAY in self.config.app_distribution:
                print("  - Set up Google Play Console")
                print("  - Prepare store listing")
            
            if AppDistribution.TESTFLIGHT in self.config.app_distribution:
                print("  - Configure TestFlight beta testing")
        
        print("\n🚀 Ready to build for multiple platforms!")


def create_wizard(enhanced: bool = False, ultimate: bool = False, multiplatform: bool = False, 
                  base_path: str = ".") -> Any:
    """Factory function to create appropriate wizard version"""
    
    if multiplatform:
        return MultiPlatformSetupWizard(Path(base_path))
    elif ultimate:
        from .ultimate_setup_wizard import UltimateSetupWizard
        return UltimateSetupWizard(Path(base_path))
    elif enhanced:
        from .enhanced_setup_wizard import EnhancedSetupWizard
        return EnhancedSetupWizard(Path(base_path))
    else:
        from .setup_wizard import SetupWizard
        return SetupWizard(base_path)


# CLI entry point
if __name__ == "__main__":
    import sys
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Multi-Platform Setup Wizard")
        print("\nUsage: python multiplatform_wizard.py [options]")
        print("\nOptions:")
        print("  --basic        Use basic wizard")
        print("  --enhanced     Use enhanced wizard")
        print("  --ultimate     Use ultimate wizard")
        print("  --multiplatform Use multi-platform wizard (default)")
        print("  --dry-run      Simulate without creating files")
        print("  --help, -h     Show this help message")
        sys.exit(0)
    
    dry_run = "--dry-run" in sys.argv
    
    if "--basic" in sys.argv:
        wizard = create_wizard(base_path=".")
    elif "--enhanced" in sys.argv:
        wizard = create_wizard(enhanced=True, base_path=".")
    elif "--ultimate" in sys.argv:
        wizard = create_wizard(ultimate=True, base_path=".")
    else:
        wizard = create_wizard(multiplatform=True, base_path=".")
    
    if dry_run:
        wizard.dry_run = True
    
    result = wizard.run_interactive()
    
    if result['status'] == 'success':
        print("\n✨ Project setup complete!")
    else:
        print(f"\n❌ Setup failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)