from pathlib import Path
from typing import List
import yaml

# Create a custom Dumper class that adds indentation
class IndentedDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

class LoomxFormatter:
    """Formats and inserts @loomx metadata blocks."""
    
    def format_metadata(self, references: List[str], backlinks: List[str]) -> str:
        """Create formatted @loomx metadata block."""
        metadata = {
            'references': references if references else [],
            'backlinks': backlinks if backlinks else []
        }
        
        # Format YAML and add base indentation in one step
        yaml_lines = []
        yaml_lines.append('<!-- @loomx')
        
        # Dump YAML and process each line
        yaml_content = yaml.dump(
            metadata,
            Dumper=IndentedDumper,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            allow_unicode=True
        )
        
        # Add proper indentation to each line
        for line in yaml_content.rstrip('\n').split('\n'):
            yaml_lines.append(f"  {line}")
        
        yaml_lines.append('-->')
        
        return '\n'.join(yaml_lines)
    
    def update_file(self, file_path: Path, references: List[str], backlinks: List[str]) -> str:
        """Update file content with new @loomx metadata."""
        content = file_path.read_text(encoding='utf-8')
        
        # Check if file starts with @loomx block (after whitespace)
        stripped_content = content.lstrip()
        has_loomx_at_start = stripped_content.startswith('<!-- @loomx')
        
        new_block = self.format_metadata(references, backlinks)
        
        if has_loomx_at_start:
            # Find the end of the existing block
            end_index = stripped_content.find('-->')
            if end_index != -1:
                # Calculate how much whitespace was stripped
                whitespace_count = len(content) - len(stripped_content)
                actual_end = whitespace_count + end_index + 3  # +3 for '-->
                
                # Replace existing block, preserving any leading whitespace
                updated_content = content[:whitespace_count] + new_block + content[actual_end:]
            else:
                # Malformed block, insert new one at the beginning
                updated_content = new_block + '\n\n' + content
        else:
            # Insert at the beginning of the file
            # Check if file starts with a heading
            lines = content.split('\n')
            insert_pos = 0
            
            # Skip any blank lines at the start
            while insert_pos < len(lines) and not lines[insert_pos].strip():
                insert_pos += 1
            
            # Insert the block
            lines.insert(insert_pos, new_block)
            lines.insert(insert_pos + 1, '')  # Add blank line after
            
            updated_content = '\n'.join(lines)
        
        return updated_content