#!/usr/bin/env python3

import re
import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Tuple, Optional

# Package configuration
PACKAGE_NAME = "quizy"
PYPROJECT_FILE = "pyproject.toml"
INIT_FILE = "quizy/__init__.py"
ENV_FILE = ".env"

# ANSI color codes
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color
    
    @classmethod
    def is_supported(cls):
        """Check if terminal supports colors"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    @classmethod
    def disable(cls):
        """Disable colors for non-supporting terminals"""
        cls.BLUE = cls.GREEN = cls.YELLOW = cls.RED = cls.NC = ''


# Disable colors on Windows if not supported
if not Colors.is_supported() or os.name == 'nt':
    Colors.disable()


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ{Colors.NC} {message}")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.NC} {message}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.NC} {message}")


def load_env() -> dict:
    """Load environment variables from .env file"""
    env_vars = {}
    
    if not Path(ENV_FILE).exists():
        return env_vars
    
    try:
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print_warning(f"Could not load {ENV_FILE}: {e}")
    
    return env_vars


def get_pypi_token(test_mode: bool = False) -> Optional[str]:
    """Get PyPI token from .env file or environment"""
    env_vars = load_env()
    
    # Determine which token to use
    token_key = 'TEST_PYPI_TOKEN' if test_mode else 'PYPI_TOKEN'
    
    # Check .env file first, then environment variables
    token = env_vars.get(token_key) or os.environ.get(token_key)
    
    if not token:
        env_file_exists = Path(ENV_FILE).exists()
        if env_file_exists:
            print_warning(f"{token_key} not found in {ENV_FILE}")
        else:
            print_warning(f"{ENV_FILE} not found")
        print_info("You can either:")
        print(f"  1. Create {ENV_FILE} with {token_key}=your-token")
        print(f"  2. Set environment variable: export {token_key}=your-token")
        print("  3. Enter credentials when twine prompts you")
        print()
    
    return token


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run shell command"""
    return subprocess.run(
        command,
        shell=True,
        check=check,
        capture_output=False
    )


def get_current_version() -> str:
    """Get current version from pyproject.toml"""
    with open(PYPROJECT_FILE, 'r') as f:
        content = f.read()
    
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError(f"Could not find version in {PYPROJECT_FILE}")
    
    return match.group(1)


def increment_version(version: str, version_type: str) -> str:
    """Increment version number"""
    major, minor, patch = map(int, version.split('.'))
    
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    elif version_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid version type: {version_type}")
    
    return f"{major}.{minor}.{patch}"


def update_version_in_files(new_version: str):
    """Update version in pyproject.toml and __init__.py"""
    # Update pyproject.toml
    with open(PYPROJECT_FILE, 'r') as f:
        content = f.read()
    
    content = re.sub(
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content
    )
    
    with open(PYPROJECT_FILE, 'w') as f:
        f.write(content)
    
    # Update __init__.py
    with open(INIT_FILE, 'r') as f:
        content = f.read()
    
    content = re.sub(
        r'__version__ = "[^"]+"',
        f'__version__ = "{new_version}"',
        content
    )
    
    with open(INIT_FILE, 'w') as f:
        f.write(content)
    
    print_success(f"Updated version to {new_version} in:")
    print(f"  - {PYPROJECT_FILE}")
    print(f"  - {INIT_FILE}")


def clean_build():
    """Clean build artifacts"""
    print_info("Cleaning old build artifacts...")
    
    dirs_to_remove = ['dist', 'build', '*.egg-info', f'{PACKAGE_NAME}.egg-info']
    
    for pattern in dirs_to_remove:
        if '*' in pattern:
            # Handle wildcards
            for path in Path('.').glob(pattern):
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
        else:
            path = Path(pattern)
            if path.exists():
                import shutil
                shutil.rmtree(path)
    
    print_success("Cleaned build directories")


def build_package():
    """Build the package"""
    print_info("Building package...")
    run_command("python -m build")
    print_success("Package built successfully")


def upload_to_pypi(version: str, test_mode: bool = False):
    """Upload package to PyPI or TestPyPI"""
    # Get API token
    token = get_pypi_token(test_mode)
    
    # Build twine command
    if test_mode:
        print_info("Uploading to TestPyPI...")
        if token:
            # Use token authentication
            cmd = f'twine upload --repository testpypi -u __token__ -p "{token}" dist/{PACKAGE_NAME}-{version}*'
        else:
            # Let twine prompt for credentials
            cmd = f'twine upload --repository testpypi dist/{PACKAGE_NAME}-{version}*'
        
        run_command(cmd)
        print_success("Uploaded to TestPyPI")
        print()
        print_info(f"Install with: pip install --index-url https://test.pypi.org/simple/ {PACKAGE_NAME}")
    else:
        print_info("Uploading to PyPI...")
        if token:
            # Use token authentication
            cmd = f'twine upload -u __token__ -p "{token}" dist/{PACKAGE_NAME}-{version}*'
        else:
            # Let twine prompt for credentials
            cmd = f'twine upload dist/{PACKAGE_NAME}-{version}*'
        
        run_command(cmd)
        print_success("Uploaded to PyPI")
        print()
        print_info(f"Install with: pip install --upgrade {PACKAGE_NAME}")


def create_git_tag(version: str, skip_git: bool = False):
    """Create git commit and tag"""
    if skip_git:
        return
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(
            "git rev-parse --git-dir",
            shell=True,
            check=False,
            capture_output=True
        )
        
        if result.returncode == 0:
            print_info(f"Creating git tag v{version}...")
            run_command(f'git add {PYPROJECT_FILE} {INIT_FILE}')
            run_command(f'git commit -m "Bump version to {version}"')
            run_command(f'git tag -a "v{version}" -m "Release version {version}"')
            print_success(f"Created git tag v{version}")
            print_warning("Don't forget to: git push && git push --tags")
    except Exception:
        # Not a git repository or git not available
        pass


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Quizy Release Script - Automated version bump and PyPI release',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python release.py patch              # Bump patch and release
  python release.py minor --test       # Bump minor and test on TestPyPI
  python release.py major --dry-run    # Show what would happen
        """
    )
    
    parser.add_argument(
        'version_type',
        choices=['patch', 'minor', 'major'],
        help='Version type to increment (patch: 0.1.0→0.1.1, minor: 0.1.1→0.2.0, major: 0.2.0→1.0.0)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Upload to TestPyPI instead of PyPI'
    )
    
    parser.add_argument(
        '--no-git',
        action='store_true',
        help='Skip git commit and tag creation'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would happen without making changes'
    )
    
    args = parser.parse_args()
    
    try:
        # Get versions
        current_version = get_current_version()
        new_version = increment_version(current_version, args.version_type)
        
        # Print info
        print()
        print_info(f"Package: {PACKAGE_NAME}")
        print_info(f"Current version: {current_version}")
        print_info(f"New version: {new_version}")
        print_info(f"Version type: {args.version_type}")
        
        if args.test:
            print_warning("Test mode: Will upload to TestPyPI")
        
        if args.no_git:
            print_warning("Skipping git operations")
        
        print()
        
        # Dry run mode
        if args.dry_run:
            print_warning("DRY RUN MODE - No changes will be made")
            print()
            print("Would perform the following steps:")
            print(f"  1. Update version in {PYPROJECT_FILE} and {INIT_FILE}")
            print("  2. Clean build artifacts")
            print("  3. Build package")
            print(f"  4. Upload to {'TestPyPI' if args.test else 'PyPI'}")
            if not args.no_git:
                print(f"  5. Create git commit and tag v{new_version}")
            return 0
        
        # Confirmation prompt
        try:
            response = input(f"{Colors.YELLOW}Continue with release? [y/N]:{Colors.NC} ").strip().lower()
            print()
            if response not in ['y', 'yes']:
                print_error("Release cancelled")
                return 1
        except KeyboardInterrupt:
            print()
            print_error("Release cancelled")
            return 1
        
        # Execute release steps
        update_version_in_files(new_version)
        clean_build()
        build_package()
        
        # Check if .env exists and show info
        if Path(ENV_FILE).exists():
            print_info(f"Using credentials from {ENV_FILE}")
        
        upload_to_pypi(new_version, args.test)
        create_git_tag(new_version, args.no_git)
        
        print()
        print_success(f"Release {new_version} completed successfully! 🎉")
        
        if not args.no_git:
            try:
                result = subprocess.run(
                    "git rev-parse --git-dir",
                    shell=True,
                    check=False,
                    capture_output=True
                )
                if result.returncode == 0:
                    print()
                    print_warning("Next steps:")
                    print("  git push origin main")
                    print(f"  git push origin v{new_version}")
            except Exception:
                pass
        
        return 0
        
    except KeyboardInterrupt:
        print()
        print_error("Release cancelled")
        return 1
    except Exception as e:
        print()
        print_error(f"Release failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())