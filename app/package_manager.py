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
        
        # Package substitutions for common problematic packages
        self.package_substitutions = {
            'psycopg2': 'psycopg2-binary',  # PostgreSQL adapter - use binary version
            'mysqlclient': 'PyMySQL',       # MySQL client - use pure Python alternative
            'pycrypto': 'pycryptodome',     # Crypto library - use maintained fork
            'PIL': 'Pillow',                # Python Imaging Library - use Pillow
        }
        
        # Common installation fixes and alternatives
        self.installation_fixes = {
            'psycopg2': {
                'alternative': 'psycopg2-binary',
                'reason': 'PostgreSQL headers required for compilation',
                'solution': 'Using pre-compiled binary version instead'
            },
            'mysqlclient': {
                'alternative': 'PyMySQL',
                'reason': 'MySQL headers required for compilation',
                'solution': 'Using pure Python MySQL connector instead'
            },
            'pycrypto': {
                'alternative': 'pycryptodome',
                'reason': 'Package is deprecated and unmaintained',
                'solution': 'Using actively maintained fork instead'
            }
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
    
    def substitute_problematic_packages(self, packages: List[str]) -> Tuple[List[str], List[str]]:
        """
        Substitute problematic packages with working alternatives
        Returns: (substituted_packages, substitution_messages)
        """
        substituted = []
        messages = []
        
        for pkg in packages:
            # Extract package name (remove version specifiers)
            clean_pkg = re.split(r'[><=!]', pkg)[0].strip()
            version_spec = pkg[len(clean_pkg):].strip() if len(pkg) > len(clean_pkg) else ''
            
            if clean_pkg.lower() in self.package_substitutions:
                original = clean_pkg
                alternative = self.package_substitutions[clean_pkg.lower()]
                substituted_pkg = alternative + version_spec
                substituted.append(substituted_pkg)
                
                if clean_pkg.lower() in self.installation_fixes:
                    fix_info = self.installation_fixes[clean_pkg.lower()]
                    messages.append(f"📦 Substituting '{original}' with '{alternative}': {fix_info['solution']}")
                else:
                    messages.append(f"📦 Substituting '{original}' with '{alternative}'")
            else:
                substituted.append(pkg)
        
        return substituted, messages
    
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
            
            # Check if the package or its alternative is installed
            is_installed = clean_pkg in installed
            
            # Also check if an alternative is installed (e.g., psycopg2-binary for psycopg2)
            if not is_installed and clean_pkg in self.package_substitutions:
                alternative = self.package_substitutions[clean_pkg].lower()
                is_installed = alternative in installed
            
            if is_installed:
                available.append(clean_pkg)
            else:
                missing.append(pkg)  # Keep original format for installation
        
        return available, missing
    
    def verify_packages_available(self, packages: List[str]) -> Tuple[bool, List[str], List[str]]:
        """
        Verify that packages can actually be imported
        Returns: (all_available, successful_imports, failed_imports)
        """
        successful = []
        failed = []
        
        for pkg in packages:
            # Extract clean package name (remove version specifiers)
            clean_pkg = re.split(r'[><=!]', pkg)[0].strip()
            
            # Try to import the package
            try:
                # Use subprocess to test import in a clean environment
                test_cmd = [sys.executable, '-c', f'import {clean_pkg}']
                result = subprocess.run(
                    test_cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    successful.append(clean_pkg)
                else:
                    # Try alternative import names for common packages
                    alt_imports = self.get_alternative_import_names(clean_pkg)
                    import_worked = False
                    
                    for alt_name in alt_imports:
                        try:
                            alt_cmd = [sys.executable, '-c', f'import {alt_name}']
                            alt_result = subprocess.run(
                                alt_cmd,
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            if alt_result.returncode == 0:
                                successful.append(f"{clean_pkg} (as {alt_name})")
                                import_worked = True
                                break
                        except:
                            continue
                    
                    if not import_worked:
                        failed.append(clean_pkg)
                        
            except Exception as e:
                failed.append(f"{clean_pkg} (error: {str(e)})")
        
        return len(failed) == 0, successful, failed
    
    def get_alternative_import_names(self, package_name: str) -> List[str]:
        """Get alternative import names for packages that have different import names"""
        alternatives = {
            'pillow': ['PIL'],
            'pyyaml': ['yaml'],
            'beautifulsoup4': ['bs4'],
            'python-dateutil': ['dateutil'],
            'msgpack-python': ['msgpack'],
            'psycopg2-binary': ['psycopg2'],
            'pymysql': ['pymysql', 'MySQLdb'],  # Can be used as MySQLdb replacement
        }
        
        return alternatives.get(package_name.lower(), [])

    def install_packages(self, packages: List[str]) -> Tuple[bool, str]:
        """
        Install missing packages using pip with intelligent substitutions and verification
        Returns: (success, message)
        """
        if not packages:
            return True, "No packages to install"
        
        # Apply package substitutions
        substituted_packages, substitution_messages = self.substitute_problematic_packages(packages)
        
        try:
            # Install packages
            cmd = [sys.executable, '-m', 'pip', 'install'] + substituted_packages
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            success_msg = ""
            if substitution_messages:
                success_msg += "\n".join(substitution_messages) + "\n"
            
            if result.returncode == 0:
                success_msg += f"✅ Pip installation completed: {', '.join(substituted_packages)}\n"
                
                # Verify packages are actually importable
                import time
                time.sleep(2)  # Brief pause to allow installation to complete
                
                all_available, successful_imports, failed_imports = self.verify_packages_available(substituted_packages)
                
                if all_available:
                    success_msg += f"✅ Verification successful: All packages can be imported"
                    return True, success_msg
                else:
                    error_msg = f"❌ Package verification failed!\n"
                    error_msg += f"✅ Successfully imported: {', '.join(successful_imports) if successful_imports else 'None'}\n"
                    error_msg += f"❌ Failed to import: {', '.join(failed_imports)}\n"
                    error_msg += f"🔄 Try running the script again, or restart the application"
                    return False, error_msg
            else:
                # Try to provide helpful error messages
                error_msg = result.stderr
                helpful_msg = self.get_helpful_error_message(error_msg, packages)
                return False, f"❌ Installation failed: {helpful_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "❌ Installation timed out (5 minutes)"
        except Exception as e:
            return False, f"❌ Installation error: {str(e)}"
    
    def get_helpful_error_message(self, error_output: str, original_packages: List[str]) -> str:
        """Generate helpful error messages based on common installation failures"""
        
        # Check for specific error patterns
        if "pg_config executable not found" in error_output:
            return (
                "PostgreSQL development headers not found. "
                "Try installing 'psycopg2-binary' instead of 'psycopg2', "
                "or install PostgreSQL development packages on your system."
            )
        
        if "Microsoft Visual C++" in error_output:
            return (
                "Microsoft Visual C++ compiler required. "
                "Install Visual Studio Build Tools or try binary packages instead."
            )
        
        if "mysql_config not found" in error_output:
            return (
                "MySQL development headers not found. "
                "Try installing 'PyMySQL' instead of 'mysqlclient', "
                "or install MySQL development packages."
            )
        
        if "No module named '_ctypes'" in error_output:
            return (
                "Python was compiled without ctypes support. "
                "Please reinstall Python with ctypes support."
            )
        
        if "error: subprocess-exited-with-error" in error_output:
            # Check if any packages have known alternatives
            suggestions = []
            for pkg in original_packages:
                clean_pkg = re.split(r'[><=!]', pkg)[0].strip().lower()
                if clean_pkg in self.installation_fixes:
                    fix_info = self.installation_fixes[clean_pkg]
                    suggestions.append(f"Try '{fix_info['alternative']}' instead of '{clean_pkg}'")
            
            if suggestions:
                return f"Build failed. Suggestions: {'; '.join(suggestions)}"
        
        # Return a truncated version of the original error
        lines = error_output.split('\n')
        if len(lines) > 10:
            return f"{' '.join(lines[:5])}... (truncated)"
        else:
            return error_output
    
    def get_package_install_command(self, packages: List[str]) -> str:
        """Get the pip install command for manual installation with substitutions"""
        if not packages:
            return ""
        
        substituted_packages, _ = self.substitute_problematic_packages(packages)
        return f"pip install {' '.join(substituted_packages)}"
    
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
        
        # Get substitution info for missing packages
        substituted_missing, substitution_messages = self.substitute_problematic_packages(missing)
        
        return {
            'detected_imports': sorted(detected_imports),
            'declared_requirements': declared,
            'installed_packages': sorted(installed),
            'missing_packages': sorted(missing),
            'substituted_packages': sorted(substituted_missing),
            'substitution_messages': substitution_messages,
            'install_command': self.get_package_install_command(missing) if missing else None,
            'all_requirements': sorted(set(all_requirements))
        }

# Global instance
package_manager = PackageManager() 