#!/usr/bin/env python3
"""
veda_check.py — Production-ready VEDA Compliance Validator CLI.

Recursively validates that your workspace directories conform to the .veda 
lightweight indexing standard. Checks that:
1. Every directory with tracked files has a .veda file.
2. Every physical file in a directory is documented in the local .veda file.
3. Every documented item in .veda physically exists (no dead links).

Usage:
    python3 tests/veda_check.py [directory] [--recursive] [--exclude PATTERNS]
"""

import os
import sys
import re
import argparse

# Colors for terminal output
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"

# Default directories and file patterns to ignore
DEFAULT_EXCLUDES = {
    ".git",
    ".DS_Store",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build"
}

def log_success(message):
    print(f"{COLOR_GREEN}✅ {message}{COLOR_RESET}")

def log_error(message):
    print(f"{COLOR_RED}❌ {message}{COLOR_RESET}", file=sys.stderr)

def log_warn(message):
    print(f"{COLOR_YELLOW}⚠️ {message}{COLOR_RESET}")

def parse_veda_file(veda_path):
    """
    Parses a .veda file and returns a set of documented items (filenames/directories).
    Matches items listed in bullet points: - `item_name` or - `item_name/`
    """
    if not os.path.exists(veda_path):
        return set()
        
    with open(veda_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Match items enclosed in backticks in list items: e.g. - `main.py` — description
    items = set(re.findall(r"-\s+`([^`]+)`", content))
    return items

def check_directory(directory, excludes):
    """
    Checks bidirectional VEDA compliance for a single directory.
    """
    veda_path = os.path.join(directory, ".veda")
    
    # Check if there are any physical files or sub-folders worth documenting
    try:
        raw_items = os.listdir(directory)
    except OSError as e:
        log_error(f"Failed to read directory {directory}: {e}")
        return False

    physical_items = {
        item for item in raw_items
        if item not in excludes
    }

    # If the folder has only ignored items or is empty, .veda is optional
    if not physical_items or physical_items == {".veda"}:
        return True

    # Validate presence of .veda file
    if not os.path.exists(veda_path):
        log_warn(f"Missing .veda file in: {directory}/")
        return False

    # Load documented items from .veda
    documented_items = parse_veda_file(veda_path)

    # Normalize documented items (e.g., removing trailing slashes for directory matching)
    normalized_documented = {item.rstrip('/') for item in documented_items}
    normalized_physical = {item.rstrip('/') for item in physical_items}

    # 1. Bidirectional Check: Documented but physically missing (dead links)
    dead_links = normalized_documented - normalized_physical
    # 2. Bidirectional Check: Physically present but missing from .veda documentation
    undocumented_files = normalized_physical - normalized_documented

    # We allow .veda itself to be optionally undocumented without throwing errors
    undocumented_files.discard(".veda")

    has_errors = False

    if dead_links:
        log_error(f"Error in {directory}/.veda — Documented items do not exist physically: {list(dead_links)}")
        has_errors = True

    if undocumented_files:
        log_error(f"Error in {directory}/.veda — Physical items are missing from .veda: {list(undocumented_files)}")
        has_errors = True

    if not has_errors:
        log_success(f"Directory {directory}/ is fully VEDA-compliant!")
        return True
        
    return False

def main():
    parser = argparse.ArgumentParser(description="Validate .veda compliance across directories.")
    parser.add_argument("directory", nargs="?", default=".", help="Target directory to validate (default: current dir)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively validate all subdirectories")
    parser.add_argument("-e", "--exclude", nargs="*", default=[], help="Additional directory or file names to ignore")

    args = parser.parse_args()

    target_dir = os.path.abspath(args.directory)
    excludes = DEFAULT_EXCLUDES.union(set(args.exclude))

    if not os.path.isdir(target_dir):
        log_error(f"Provided path is not a directory: {target_dir}")
        sys.exit(1)

    print(f"Scanning for .veda compliance in: {target_dir}")
    
    directories_to_check = [target_dir]

    if args.recursive:
        for root, dirs, files in os.walk(target_dir):
            # Modify dirs in-place to skip excluded directories during traversal
            dirs[:] = [d for d in dirs if d not in excludes and not d.startswith('.')]
            for d in dirs:
                directories_to_check.append(os.path.join(root, d))

    failed_directories = []

    for d in directories_to_check:
        # Avoid checking inside excluded or private folders
        relative_path = os.path.relpath(d, target_dir)
        if any(part in excludes or part.startswith('.') for part in relative_path.split(os.sep) if part and part != '.'):
            continue
            
        is_compliant = check_directory(d, excludes)
        if not is_compliant:
            failed_directories.append(d)

    print("\n--- Compliance Summary ---")
    if failed_directories:
        log_error(f"Validation FAILED! {len(failed_directories)} directory/directories are non-compliant:")
        for fd in failed_directories:
            print(f"  - {os.path.relpath(fd, target_dir)}/")
        sys.exit(1)
    else:
        log_success("All scanned directories are 100% VEDA-compliant! Excellent work.")
        sys.exit(0)

if __name__ == "__main__":
    main()
