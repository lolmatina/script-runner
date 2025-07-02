import subprocess
import sys
import re
import ast
from typing import List, Tuple, Dict, Set
from pathlib import Path

class PackageManager:
    """Handle Python package management for script execution"""
    
    def __init__(self):
        self.standard_library = {
            'os', 'sys', 'subprocess', 'datetime', 'time', 'json', 'csv', 'sqlite3',
            'math', 'random', 'collections', 'itertools', 'functools', 're', 'uuid',
            'pathlib', 'typing', 'ast', 'threading', 'multiprocessing', 'socket',
            'urllib', 'http', 'email', 'smtplib', 'ftplib', 'zipfile', 'tarfile',
            'configparser', 'logging', 'argparse', 'shutil', 'tempfile', 'pickle',
            'base64', 'hashlib', 'hmac', 'secrets', 'getpass', 'platform',
            'traceback', 'warnings', 'inspect', 'gc', 'weakref', 'copy', 'pprint'
        }
    
    def get_installed_packages(self) -> Set[str]:
        """Get list of installed packages"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=freeze'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                packages = set()
                for line in result.stdout.strip().split('\n'):
                    if '==' in line:
                        package_name = line.split('==')[0].lower()
                        packages.add(package_name)
                return packages
            return set()
        except Exception:
            return set()
    
    def detect_imports_from_script(self, script_path: str) -> Set[str]:
        """Analyze Python script to detect imported packages"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Get base package name (e.g., 'matplotlib.pyplot' -> 'matplotlib')
                        base_package = alias.name.split('.')[0]
                        imports.add(base_package.lower())
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Get base package name
                        base_package = node.module.split('.')[0]
                        imports.add(base_package.lower())
            
            # Filter out standard library modules
            third_party_imports = imports - self.standard_library
            return third_party_imports
            
        except Exception as e:
            print(f"Error analyzing script imports: {e}")
            return set()
    
    def check_missing_packages(self, required_packages: List[str]) -> Tuple[List[str], List[str]]:
        """
        Check which packages are missing
        Returns: (installed_packages, missing_packages)
        """
        if not required_packages:
            return [], []
        
        installed = self.get_installed_packages()
        required_set = {pkg.strip().lower() for pkg in required_packages}
        
        missing = []
        available = []
        
        for pkg in required_set:
            # Handle package names with version specifiers (e.g., 'requests>=2.0')
            clean_pkg = re.split(r'[><=!]', pkg)[0].strip()
            
            if clean_pkg in installed:
                available.append(clean_pkg)
            else:
                missing.append(pkg)  # Keep original format for installation
        
        return available, missing
    
    def install_packages(self, packages: List[str]) -> Tuple[bool, str]:
        """
        Install missing packages using pip
        Returns: (success, message)
        """
        if not packages:
            return True, "No packages to install"
        
        try:
            # Install packages
            cmd = [sys.executable, '-m', 'pip', 'install'] + packages
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                return True, f"✅ Successfully installed: {', '.join(packages)}"
            else:
                return False, f"❌ Installation failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "❌ Installation timed out (5 minutes)"
        except Exception as e:
            return False, f"❌ Installation error: {str(e)}"
    
    def get_package_install_command(self, packages: List[str]) -> str:
        """Get the pip install command for manual installation"""
        if not packages:
            return ""
        return f"pip install {' '.join(packages)}"
    
    def analyze_script_dependencies(self, script_path: str, declared_requirements: str = None) -> Dict:
        """
        Analyze script dependencies and return comprehensive report
        """
        # Get imports from script analysis
        detected_imports = self.detect_imports_from_script(script_path)
        
        # Parse declared requirements
        declared = []
        if declared_requirements:
            declared = [pkg.strip() for pkg in declared_requirements.split(',') if pkg.strip()]
        
        # Check what's missing
        all_requirements = list(detected_imports) + declared
        installed, missing = self.check_missing_packages(all_requirements)
        
        return {
            'detected_imports': sorted(detected_imports),
            'declared_requirements': declared,
            'installed_packages': sorted(installed),
            'missing_packages': sorted(missing),
            'install_command': self.get_package_install_command(missing) if missing else None,
            'all_requirements': sorted(set(all_requirements))
        }

# Global instance
package_manager = PackageManager() 