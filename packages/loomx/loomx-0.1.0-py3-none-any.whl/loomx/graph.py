from pathlib import Path
from typing import Dict, Set, List, Optional
from collections import defaultdict


class LinkGraph:
    """Manages the graph of links between documents."""
    
    def __init__(self, root_path: Optional[Path] = None):
        # Forward references: file -> set of files it references
        self.references: Dict[Path, Set[Path]] = defaultdict(set)
        
        # Backward references: file -> set of files that reference it
        self.backlinks: Dict[Path, Set[Path]] = defaultdict(set)
        
        # Project root directory (for relative path calculations)
        self.root_path = root_path
    
    def add_references(self, source: Path, targets: Set[str], check_exists: bool = True):
        """Add references from source file to target files."""
        source = source.resolve()
        
        for target in targets:
            # Resolve target path relative to source file's directory
            target_path = (source.parent / target).resolve()
            
            if not check_exists or target_path.exists():
                self.references[source].add(target_path)
                self.backlinks[target_path].add(source)
    
    def get_references(self, file_path: Path) -> List[str]:
        """Get sorted list of references from a file."""
        file_path = file_path.resolve()
        refs = self.references.get(file_path, set())
        
        # Find the root directory (where .git usually is)
        root = self._find_project_root(file_path)
        
        # Convert to absolute paths from project root
        absolute_refs = []
        for ref in refs:
            try:
                # Make path relative to project root
                rel_to_root = ref.relative_to(root)
                absolute_refs.append('/' + rel_to_root.as_posix())
            except ValueError:
                # If can't make relative to root, use absolute system path
                absolute_refs.append(str(ref))
        
        return sorted(absolute_refs)
    
    def get_backlinks(self, file_path: Path) -> List[str]:
        """Get sorted list of backlinks to a file."""
        file_path = file_path.resolve()
        links = self.backlinks.get(file_path, set())
        
        # Find the root directory (where .git usually is)
        root = self._find_project_root(file_path)
        
        # Convert to absolute paths from project root
        absolute_links = []
        for link in links:
            try:
                # Make path relative to project root
                rel_to_root = link.relative_to(root)
                absolute_links.append('/' + rel_to_root.as_posix())
            except ValueError:
                # If can't make relative to root, use absolute system path
                absolute_links.append(str(link))
        
        return sorted(absolute_links)
    
    def _find_project_root(self, file_path: Path) -> Path:
        """Find the project root directory."""
        # If root_path was explicitly set, use it
        if self.root_path is not None:
            return self.root_path.resolve()
        
        # Otherwise, try to find .git directory
        current = file_path.resolve()
        if current.is_file():
            current = current.parent
        
        # Walk up the directory tree looking for .git
        while current != current.parent:
            if (current / '.git').exists():
                return current
            current = current.parent
        
        # If no .git found, return the file's parent directory
        return file_path.parent if file_path.is_file() else file_path