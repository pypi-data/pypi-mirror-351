"""Formatter

This module provides the main comment-formatting utility class.
"""
# ───────────────────────────── import statements ─────────────────────────────
import re
import sys
from pathlib import Path
from typing import List, Set

import click


class CommentFormatter:
    MAX_LINE_LENGTH = 80

    @staticmethod
    def format_file(file_path: Path, lang: str = "python") -> bool:
        """Format a single file. Returns True if file was modified."""
        formatter_map = {
            "python": CommentFormatter.format_python,
            # future language support can go here
        }

        if lang not in formatter_map:
            raise ValueError(f"Unsupported language: {lang}")

        return formatter_map[lang](file_path)

    @staticmethod
    def format_python(file_path: Path) -> bool:
        """Format Python file. Returns True if file was modified."""
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        updated_lines = []
        modified = False
        
        with file_path.open('r', encoding='utf-8') as f:
            for line in f:
                processed_line = CommentFormatter._process_line(line)
                updated_lines.append(processed_line)
                if processed_line != line:
                    modified = True

        if modified:
            with file_path.open('w', encoding='utf-8') as f:
                f.writelines(updated_lines)

        return modified

     
    @staticmethod
    def _process_line(line: str) -> str:
        """Process a single line, formatting starch comments."""
        match = re.match(r'^(\s*)# :(.*)$', line)
        if not match:
            return line

        indent, comment = match.groups()
        comment = comment.strip()
        prefix = f"{indent}# ─── "

        if indent == "":
            suffix = " ✦✦ ──"
        else:
            suffix = ""

        # One space between comment and padding
        spacer = " "

        max_comment_length = (
            CommentFormatter.MAX_LINE_LENGTH - len(prefix) - len(spacer) - len(suffix)
        )

        trimmed_comment = comment[:max_comment_length]
        padding = max_comment_length - len(trimmed_comment)
        padded_comment = trimmed_comment + spacer + "─" * padding

        return f"{prefix}{padded_comment}{suffix}\n"


    @staticmethod
    def get_python_files(path: Path, ignore_patterns: List[str]) -> List[Path]:
        """Get all Python files in a directory recursively, respecting ignore patterns."""
        python_files = []
        ignore_set = set(ignore_patterns)
        
        def should_ignore(file_path: Path) -> bool:
            """Check if a path should be ignored."""
            path_str = str(file_path)
            path_name = file_path.name
            
            # Check if any part of the path matches ignore patterns
            for pattern in ignore_set:
                if pattern in path_str or pattern == path_name:
                    return True
                # Check if any parent directory matches the pattern
                for parent in file_path.parents:
                    if parent.name == pattern:
                        return True
            return False

        if path.is_file():
            if path.suffix == '.py' and not should_ignore(path):
                python_files.append(path)
        elif path.is_dir():
            for py_file in path.rglob('*.py'):
                if not should_ignore(py_file):
                    python_files.append(py_file)
        
        return sorted(python_files)


@click.command()
@click.argument('target', type=click.Path(exists=True, path_type=Path))
@click.option('--lang', '-l', default='python', 
              help='Language of the source files (default: python)')
@click.option('--ignore', '-i', multiple=True, 
              help='Directory or file patterns to ignore (can be used multiple times)')
@click.option('--verbose', '-v', is_flag=True, 
              help='Show verbose output')
@click.option('--dry-run', '-n', is_flag=True, 
              help='Show what would be formatted without making changes')
def main(target: Path, lang: str, ignore: tuple, verbose: bool, dry_run: bool):
    """Format decorated comment lines in Python files.
    
    TARGET can be a file or directory. If a directory is provided,
    all Python files in the directory and subdirectories will be processed.
    
    Examples:
        starch .                    # Format all Python files in current directory
        starch src/                 # Format all Python files in src/ directory
        starch file.py              # Format a single file
        starch . -i __pycache__ -i .git  # Ignore specific directories
    """
    ignore_patterns = list(ignore)
    
    # Add common ignore patterns if none specified
    if not ignore_patterns:
        ignore_patterns = ['__pycache__', '.git', '.venv', 'venv', '.pytest_cache', 'node_modules']
    
    try:
        if target.is_file():
            files_to_process = [target] if target.suffix == '.py' else []
        else:
            files_to_process = CommentFormatter.get_python_files(target, ignore_patterns)
        
        if not files_to_process:
            click.echo("No Python files found to process.")
            return
        
        if verbose:
            click.echo(f"Found {len(files_to_process)} Python file(s) to process")
            if ignore_patterns:
                click.echo(f"Ignoring patterns: {', '.join(ignore_patterns)}")
        
        modified_count = 0
        
        for file_path in files_to_process:
            try:
                if dry_run:
                    # For dry run, we need to check if file would be modified
                    with file_path.open('r', encoding='utf-8') as f:
                        would_modify = False
                        for line in f:
                            if CommentFormatter._process_line(line) != line:
                                would_modify = True
                                break
                    
                    if would_modify:
                        click.echo(f"Would format: {file_path}")
                        modified_count += 1
                    elif verbose:
                        click.echo(f"No changes needed: {file_path}")
                else:
                    was_modified = CommentFormatter.format_file(file_path, lang)
                    if was_modified:
                        if verbose:
                            click.echo(f"Formatted: {file_path}")
                        modified_count += 1
                    elif verbose:
                        click.echo(f"No changes needed: {file_path}")
                        
            except Exception as e:
                click.echo(f"Error processing {file_path}: {e}", err=True)
                continue
        
        if dry_run:
            click.echo(f"\nDry run complete. Would format {modified_count} file(s).")
        else:
            click.echo(f"Formatted {modified_count} file(s).")
            
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if not match:
        return line

    indent, comment = match.groups()
    comment = comment.strip()
    prefix = f"{indent}# ─── "
    
    # Different suffixes for top-level vs indented lines
    if indent == "":
        suffix = " ✦✦ ──"
    else:
        suffix = "──"

    max_comment_length = CommentFormatter.MAX_LINE_LENGTH - len(prefix) - len(suffix)
    trimmed_comment = comment[:max_comment_length]
    padding = max_comment_length - len(trimmed_comment)
    padded_comment = trimmed_comment + "─" * padding

    return f"{prefix}{padded_comment}{suffix}\n"

    @staticmethod
    def get_python_files(path: Path, ignore_patterns: List[str]) -> List[Path]:
        """Get all Python files in a directory recursively, respecting ignore patterns."""
        python_files = []
        ignore_set = set(ignore_patterns)
        
        def should_ignore(file_path: Path) -> bool:
            """Check if a path should be ignored."""
            path_str = str(file_path)
            path_name = file_path.name
            
            # Check if any part of the path matches ignore patterns
            for pattern in ignore_set:
                if pattern in path_str or pattern == path_name:
                    return True
                # Check if any parent directory matches the pattern
                for parent in file_path.parents:
                    if parent.name == pattern:
                        return True
            return False

        if path.is_file():
            if path.suffix == '.py' and not should_ignore(path):
                python_files.append(path)
        elif path.is_dir():
            for py_file in path.rglob('*.py'):
                if not should_ignore(py_file):
                    python_files.append(py_file)
        
        return sorted(python_files)


@click.command()
@click.argument('target', type=click.Path(exists=True, path_type=Path))
@click.option('--lang', '-l', default='python', 
              help='Language of the source files (default: python)')
@click.option('--ignore', '-i', multiple=True, 
              help='Directory or file patterns to ignore (can be used multiple times)')
@click.option('--verbose', '-v', is_flag=True, 
              help='Show verbose output')
@click.option('--dry-run', '-n', is_flag=True, 
              help='Show what would be formatted without making changes')
def main(target: Path, lang: str, ignore: tuple, verbose: bool, dry_run: bool):
    """Format decorated comment lines in Python files.
    
    TARGET can be a file or directory. If a directory is provided,
    all Python files in the directory and subdirectories will be processed.
    
    Examples:
        starch .                    # Format all Python files in current directory
        starch src/                 # Format all Python files in src/ directory
        starch file.py              # Format a single file
        starch . -i __pycache__ -i .git  # Ignore specific directories
    """
    ignore_patterns = list(ignore)
    
    # Add common ignore patterns if none specified
    if not ignore_patterns:
        ignore_patterns = ['__pycache__', '.git', '.venv', 'venv', '.pytest_cache', 'node_modules']
    
    try:
        if target.is_file():
            files_to_process = [target] if target.suffix == '.py' else []
        else:
            files_to_process = CommentFormatter.get_python_files(target, ignore_patterns)
        
        if not files_to_process:
            click.echo("No Python files found to process.")
            return
        
        if verbose:
            click.echo(f"Found {len(files_to_process)} Python file(s) to process")
            if ignore_patterns:
                click.echo(f"Ignoring patterns: {', '.join(ignore_patterns)}")
        
        modified_count = 0
        
        for file_path in files_to_process:
            try:
                if dry_run:
                    # For dry run, we need to check if file would be modified
                    with file_path.open('r', encoding='utf-8') as f:
                        would_modify = False
                        for line in f:
                            if CommentFormatter._process_line(line) != line:
                                would_modify = True
                                break
                    
                    if would_modify:
                        click.echo(f"Would format: {file_path}")
                        modified_count += 1
                    elif verbose:
                        click.echo(f"No changes needed: {file_path}")
                else:
                    was_modified = CommentFormatter.format_file(file_path, lang)
                    if was_modified:
                        if verbose:
                            click.echo(f"Formatted: {file_path}")
                        modified_count += 1
                    elif verbose:
                        click.echo(f"No changes needed: {file_path}")
                        
            except Exception as e:
                click.echo(f"Error processing {file_path}: {e}", err=True)
                continue
        
        if dry_run:
            click.echo(f"\nDry run complete. Would format {modified_count} file(s).")
        else:
            click.echo(f"Formatted {modified_count} file(s).")
            
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
