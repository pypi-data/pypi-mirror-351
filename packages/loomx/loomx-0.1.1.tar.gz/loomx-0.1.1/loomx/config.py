from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class LoomxConfig:
    """Configuration for loomx operations."""
    
    # Default patterns to always ignore
    DEFAULT_IGNORE_PATTERNS = [
        '.git', 
        'node_modules', 
        '__pycache__',
        '.pytest_cache',
        'venv',
        '.venv',
        'dist',
        'build',
        '.tox',
        '.eggs',
        '*.egg-info',
        '.mypy_cache',
        '.ruff_cache',
        'htmlcov',
        '.coverage',
    ]
    
    # File patterns to ignore
    ignore_patterns: list[str] = field(default_factory=lambda: LoomxConfig.DEFAULT_IGNORE_PATTERNS.copy())
    
    # Additional exclude patterns from config
    exclude_patterns: list[str] = field(default_factory=list)
    
    # File extensions to process
    file_extensions: list[str] = field(default_factory=lambda: ['.md', '.mdx'])
    
    # Root directory to scan
    root_path: Path = field(default_factory=Path.cwd)
    
    # Whether to update files in place
    dry_run: bool = False
    
    # Verbose output
    verbose: bool = False
    
    @classmethod
    def from_pyproject(cls, root_path: Optional[Path] = None, **kwargs) -> 'LoomxConfig':
        """Load configuration from pyproject.toml if it exists."""
        config = cls(root_path=root_path or Path.cwd(), **kwargs)
        
        pyproject_path = config.root_path / 'pyproject.toml'
        if pyproject_path.exists():
            try:
                with open(pyproject_path, 'rb') as f:
                    data = tomllib.load(f)
                
                loomx_config = data.get('tool', {}).get('loomx', {})
                
                # Load exclude patterns
                if 'exclude' in loomx_config:
                    config.exclude_patterns = loomx_config['exclude']
                
                # Load file extensions if specified
                if 'file_extensions' in loomx_config:
                    config.file_extensions = loomx_config['file_extensions']
            
            except Exception:
                # Silently ignore config errors
                pass
        
        return config