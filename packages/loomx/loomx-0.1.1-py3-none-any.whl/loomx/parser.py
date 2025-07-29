from pathlib import Path
from typing import Optional, Set, Dict, Any, List
import yaml
import mistune


class MarkdownParser:
    """Parses markdown files to extract links and loomx metadata."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = file_path.read_text(encoding='utf-8')
    
    def extract_references(self) -> Set[str]:
        """Extract all markdown links from the file using mistune."""
        references: Set[str] = set()
        
        # Create markdown parser with AST renderer
        markdown = mistune.create_markdown(renderer='ast')
        
        # Parse content to AST
        ast = markdown(self.content)
        
        # Walk through AST to find links
        if isinstance(ast, list):
            self._extract_links_from_ast(ast, references)
        
        return references
    
    def _extract_links_from_ast(self, nodes: List[Dict], references: Set[str]):
        """Recursively extract links from AST nodes."""
        for node in nodes:
            if node['type'] == 'link':
                # Get URL from attrs
                attrs = node.get('attrs', {})
                link_target = attrs.get('url', '')
                # Only process relative links to markdown files
                if self._is_relative_markdown_link(link_target):
                    normalized = self._normalize_link(link_target)
                    if normalized:
                        references.add(normalized)
            
            # Recursively process children
            children = node.get('children', [])
            if children:
                self._extract_links_from_ast(children, references)
    
    def extract_loomx_metadata(self) -> Optional[Dict[str, Any]]:
        """Extract existing @loomx metadata block from the beginning of the file."""
        # Strip leading whitespace
        stripped_content = self.content.lstrip()
        
        # Check if file starts with <!-- @loomx
        if not stripped_content.startswith('<!-- @loomx'):
            return None
        
        # Find the closing -->
        end_index = stripped_content.find('-->')
        if end_index == -1:
            return None
        
        # Extract the full comment block
        comment_block = stripped_content[:end_index + 3]
        
        # Extract YAML content (between @loomx and -->)
        yaml_start = comment_block.find('@loomx') + 6  # Skip '@loomx'
        yaml_end = comment_block.find('-->')
        yaml_content = comment_block[yaml_start:yaml_end].strip()
        
        if not yaml_content:
            return None
        
        # Remove leading whitespace from each line to fix YAML indentation
        lines = yaml_content.split('\n')
        if lines:
            # Find minimum indentation (excluding empty lines)
            indents = [len(line) - len(line.lstrip()) 
                      for line in lines if line.strip()]
            if indents:
                min_indent = min(indents)
                # Remove that amount of indentation from all lines
                yaml_content = '\n'.join(line[min_indent:] if len(line) > min_indent else line 
                                       for line in lines)
        
        if yaml_content:
            try:
                return yaml.safe_load(yaml_content)
            except yaml.YAMLError:
                return None
        return None
    
    def _is_relative_markdown_link(self, link: str) -> bool:
        """Check if link is a relative markdown file link."""
        if link.startswith(('http://', 'https://', '/', '#', 'mailto:')):
            return False
        
        # Remove fragment before checking
        link_without_fragment = link.split('#')[0]
        if not link_without_fragment:
            return False
            
        # Check if it's a markdown file or directory that might contain markdown
        return link_without_fragment.endswith(('.md', '.mdx')) or '.' not in Path(link_without_fragment).name
    
    def _normalize_link(self, link: str) -> Optional[str]:
        """Normalize a relative link to a consistent format."""
        # Remove any fragment identifiers
        link = link.split('#')[0]
        
        # Remove query parameters
        link = link.split('?')[0]
        
        if not link:
            return None
        
        # Convert to Path for normalization
        link_path = Path(link)
        
        # If it's a directory reference, check if README.md exists
        if not link_path.suffix:
            # Calculate the actual path from current file location
            current_dir = self.file_path.parent
            target_path = current_dir / link_path
            readme_path = target_path / 'README.md'
            
            # Only add README.md if it actually exists
            if readme_path.exists():
                link_path = link_path / 'README.md'
            else:
                # Skip directory links without README.md
                return None
        
        # Ensure it starts with './' if it doesn't start with '../'
        result = link_path.as_posix()
        if not result.startswith('../') and not result.startswith('./'):
            result = './' + result
        
        return result