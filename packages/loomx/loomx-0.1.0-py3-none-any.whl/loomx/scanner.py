from pathlib import Path
from typing import Iterator, Optional
import fnmatch
import pathspec

from .config import LoomxConfig


class Scanner:
    """Scans project directory for markdown files."""
    
    def __init__(self, config: LoomxConfig):
        self.config = config
        self._gitignore_spec = self._load_gitignore()
    
    def scan_files(self) -> Iterator[Path]:
        """Yields markdown files in the project, respecting ignore patterns."""
        for ext in self.config.file_extensions:
            pattern = f"**/*{ext}"
            for file_path in self.config.root_path.glob(pattern):
                if self._should_process_file(file_path):
                    yield file_path
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed based on ignore patterns."""
        # Check if any parent directory matches default ignore patterns
        for part in file_path.parts:
            if part in self.config.ignore_patterns:
                return False
        
        # Check if file path matches any ignore pattern
        path_str = str(file_path)
        for pattern in self.config.ignore_patterns:
            if pattern in path_str:
                return False
        
        # Check additional exclude patterns (these support glob patterns)
        rel_path = file_path.relative_to(self.config.root_path)
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(str(rel_path), pattern):
                return False
            if fnmatch.fnmatch(str(rel_path.as_posix()), pattern):
                return False
        
        # Check gitignore patterns
        if self._gitignore_spec:
            if self._gitignore_spec.match_file(str(rel_path)):
                return False
        
        return True
    
    def _load_gitignore(self) -> Optional[pathspec.PathSpec]:
        """Load .gitignore patterns if the file exists."""
        gitignore_path = self.config.root_path / '.gitignore'
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r') as f:
                    patterns = f.read().splitlines()
                return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
            except Exception:
                # Silently ignore gitignore parse errors
                pass
        return None