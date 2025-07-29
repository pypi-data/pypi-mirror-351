"""Main processor for loomx operations, orchestrating scanning, parsing, and updating."""
from pathlib import Path
from typing import Dict, List, Tuple

from .config import LoomxConfig
from .scanner import Scanner
from .parser import MarkdownParser
from .graph import LinkGraph
from .formatter import LoomxFormatter


class LoomxProcessor:
    """Main processor for loomx operations."""
    
    def __init__(self, config: LoomxConfig):
        self.config = config
        self.scanner = Scanner(config)
        self.graph = LinkGraph(root_path=config.root_path)
        self.formatter = LoomxFormatter()
    
    def analyze(self) -> Dict[Path, Tuple[List[str], List[str]]]:
        """Analyze all markdown files and return their references and backlinks.
        
        Returns:
            Dict mapping file paths to tuples of (references, backlinks)
        """
        # First pass: build the graph
        files_found = []
        for file_path in self.scanner.scan_files():
            files_found.append(file_path)
            parser = MarkdownParser(file_path)
            references = parser.extract_references()
            self.graph.add_references(file_path, references)
        
        # Collect results
        results: Dict[Path, Tuple[List[str], List[str]]] = {}
        for file_path in files_found:
            ref_list: List[str] = self.graph.get_references(file_path)
            backlink_list: List[str] = self.graph.get_backlinks(file_path)
            if ref_list or backlink_list:
                results[file_path] = (ref_list, backlink_list)
        
        return results
    
    def get_updated_content(self, file_path: Path, references: List[str], backlinks: List[str]) -> str:
        """Get the updated content for a file without writing it.
        
        Args:
            file_path: Path to the file
            references: List of references
            backlinks: List of backlinks
            
        Returns:
            Updated file content
        """
        return self.formatter.update_file(file_path, references, backlinks)
    
    def update_files(self) -> Dict[Path, str]:
        """Update all files and return the changes.
        
        Returns:
            Dict mapping file paths to their updated content.
            Only includes files that would be changed.
        """
        analysis = self.analyze()
        updates = {}
        
        for file_path, (references, backlinks) in analysis.items():
            original_content = file_path.read_text(encoding='utf-8')
            updated_content = self.get_updated_content(file_path, references, backlinks)
            
            if original_content != updated_content:
                if not self.config.dry_run:
                    file_path.write_text(updated_content, encoding='utf-8')
                updates[file_path] = updated_content
        
        return updates