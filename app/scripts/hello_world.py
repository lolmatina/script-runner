#!/usr/bin/env python3
"""
Enhanced Hello World Script with Multiple Features
Demonstrates argument processing, help system, and verbose output
"""

import sys
import os
import time
import platform

def show_environment_info():
    """Display detailed environment information."""
    print("ENVIRONMENT INFORMATION:")
    print(f"   • Python version: {sys.version}")
    print(f"   • Platform: {platform.platform()}")
    print(f"   • Machine: {platform.machine()}")
    print(f"   • Processor: {platform.processor()}")
    print(f"   • Current working directory: {os.getcwd()}")
    print(f"   • Script location: {os.path.abspath(__file__)}")
    print(f"   • User: {os.environ.get('USER', os.environ.get('USERNAME', 'Unknown'))}")
    print(f"   • Path entries: {len(sys.path)}")
    print()

def basic_hello():
    """Basic hello world functionality."""
    print("Hello, World!")
    print("This is a simple demonstration script.")
    print()
    print("Features available:")
    print("   • Basic greeting (default)")
    print("   • Verbose mode (--verbose)")
    print("   • Help system (--help)")
    print("   • Environment info (automatic)")
    print()
    print("Tip: Try passing arguments to see more features!")

def verbose_hello(args):
    """Enhanced hello world with detailed information."""
    print("Hello, World! (Verbose Mode)")
    print("=" * 50)
    print()
    
    show_environment_info()
    
    print("COMMAND LINE ARGUMENTS:")
    if len(args) <= 1:
        print("   • No additional arguments provided")
    else:
        print(f"   • Total arguments: {len(args)}")
        for i, arg in enumerate(args):
            print(f"   • Argument {i}: '{arg}'")
    print()
    
    print("VERBOSE MODE ENABLED")
    print("Additional information provided:")
    print(f"   • Script execution time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   • Process ID: {os.getpid()}")
    print(f"   • Parent process ID: {os.getppid()}")
    print(f"   • Python executable: {sys.executable}")
    print(f"   • Python path: {sys.path[0]}")
    print(f"   • Available modules: {len(sys.modules)} loaded")
    print(f"   • Recursion limit: {sys.getrecursionlimit()}")
    print(f"   • File encoding: {sys.getfilesystemencoding()}")
    print()

def analyze_arguments(args):
    """Analyze and display argument details."""
    print("DETAILED ARGUMENT ANALYSIS:")
    print(f"   • Total argument count: {len(args)}")
    print(f"   • Script name: {args[0]}")
    
    if len(args) > 1:
        print(f"   • User arguments: {len(args) - 1}")
        for i, arg in enumerate(args[1:], 1):
            print(f"     {i}. '{arg}' (length: {len(arg)} characters)")
    else:
        print("   • No user arguments provided")
    print()

def show_help():
    """Display comprehensive help information."""
    print("HELLO WORLD SCRIPT HELP")
    print("=" * 30)
    print()
    print("DESCRIPTION:")
    print("   This is an enhanced Hello World script that demonstrates")
    print("   various Python features and argument processing capabilities.")
    print()
    print("USAGE:")
    print("   python hello_world.py [OPTIONS] [ARGUMENTS]")
    print()
    print("OPTIONS:")
    print("   --help, -h     Show this help message and exit")
    print("   --verbose, -v  Enable verbose output mode")
    print("   --env         Show environment information only")
    print("   --version     Show script version information")
    print()
    print("EXAMPLES:")
    print("   python hello_world.py")
    print("   python hello_world.py --verbose")
    print("   python hello_world.py --help")
    print("   python hello_world.py Hello from command line")
    print("   python hello_world.py --verbose arg1 arg2 arg3")
    print()
    print("FEATURES:")
    print("   • Basic greeting and information display")
    print("   • Verbose mode with detailed system information")
    print("   • Command line argument analysis")
    print("   • Environment information display")
    print("   • Cross-platform compatibility")
    print("   • Error handling and user guidance")
    print()

def show_execution_stats():
    """Display execution statistics."""
    print("EXECUTION STATISTICS:")
    print(f"   • Start time: {time.strftime('%H:%M:%S')}")
    print(f"   • Python version: {platform.python_version()}")
    print(f"   • Platform: {platform.system()} {platform.release()}")
    print(f"   • Architecture: {platform.architecture()[0]}")
    print(f"   • Hostname: {platform.node()}")
    print(f"   • CPU count: {os.cpu_count()}")
    
    # Memory info (if available)
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"   • Available memory: {memory.available // (1024**3)} GB")
    except ImportError:
        print("   • Memory info: Not available (psutil not installed)")
    
    print()

def main():
    """Main function that orchestrates the script execution."""
    start_time = time.time()
    
    print("ENHANCED HELLO WORLD SCRIPT")
    print("=" * 35)
    print()
    
    # Parse command line arguments
    args = sys.argv
    verbose_mode = False
    show_help_only = False
    show_env_only = False
    show_version_only = False
    
    # Simple argument parsing
    for arg in args[1:]:
        if arg.lower() in ['--help', '-h', 'help']:
            show_help_only = True
            break
        elif arg.lower() in ['--verbose', '-v', 'verbose']:
            verbose_mode = True
        elif arg.lower() == '--env':
            show_env_only = True
        elif arg.lower() == '--version':
            show_version_only = True
    
    # Handle special modes
    if show_help_only:
        show_help()
        return
    
    if show_version_only:
        print("Hello World Script v2.0")
        print("Enhanced demonstration script with multiple features")
        return
    
    if show_env_only:
        show_environment_info()
        return
    
    # Show execution statistics
    show_execution_stats()
    
    # Main execution
    if verbose_mode:
        verbose_hello(args)
        analyze_arguments(args)
    else:
        basic_hello()
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    print("SCRIPT COMPLETED SUCCESSFULLY!")
    print(f"   • Execution time: {execution_time:.4f} seconds")
    print(f"   • Arguments processed: {len(args)}")
    print(f"   • Mode: {'Verbose' if verbose_mode else 'Basic'}")
    print()
    print("Thank you for running the Enhanced Hello World Script!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1) 