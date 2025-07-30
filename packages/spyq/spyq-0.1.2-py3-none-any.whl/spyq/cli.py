"""
Command-line interface for SPYQ.
"""

import argparse
import sys
from typing import Optional, List
from pathlib import Path

from .setup_quality_guard import setup_quality_guard

__version__ = "0.1.0"

def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    # First check for version flag
    if "--version" in args or "-v" in args:
        return argparse.Namespace(version=True)
        
    parser = argparse.ArgumentParser(
        description="SPYQ - Shell Python Quality Guard",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    # Add version flag
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show version information and exit"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Setup command
    setup_parser = subparsers.add_parser(
        "setup", help="Setup quality guard in a project"
    )
    setup_parser.add_argument(
        "path",
        nargs="?",
        type=str,
        default=".",
        help="Path to the project directory (default: current directory)"
    )
    setup_parser.add_argument(
        "--force", 
        action="store_true",
        help="Force setup even if files exist"
    )
    
    # Version command
    subparsers.add_parser("version", help="Show version information")
    
    # If no arguments provided, show help
    if len(args) == 0:
        parser.print_help()
        sys.exit(0)
    
    return parser.parse_args(args)

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the SPYQ CLI."""
    if args is None:
        args = sys.argv[1:]
    
    try:
        parsed_args = parse_args(args)
        
        # Handle version flag
        if getattr(parsed_args, 'version', False):
            print(f"SPYQ version {__version__}")
            return 0
            
        # Handle commands
        if parsed_args.command == "version":
            print(f"SPYQ version {__version__}")
            return 0
            
        elif parsed_args.command == "setup":
            project_path = Path(parsed_args.path).resolve()
            print(f"🔧 Setting up Quality Guard in {project_path}")
            
            try:
                setup_quality_guard(project_path, force=getattr(parsed_args, 'force', False))
                print("✅ Successfully set up Quality Guard!")
                return 0
            except Exception as e:
                print(f"❌ Error setting up Quality Guard: {e}", file=sys.stderr)
                return 1
                
        else:
            # No command provided, show help
            if not args:  # No arguments at all
                print("No command provided. Use 'spyq --help' for usage information.")
            else:
                # There were arguments but no valid command
                print(f"Unknown command: {args[0]}. Use 'spyq --help' for usage information.")
            return 1
            
    except Exception as e:
        print(f"❌ An error occurred: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
