# --- ADD: Module docstring ---
"""Module for parsing LaTeX text with revision and comment tags."""
# --- END ADD ---
import re
import logging

# --- ADD: Configure logging ---
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s] - %(message)s')
logger = logging.getLogger(__name__)
# --- END ADD ---

class LatexParser:
    """
    Parses LaTeX text to identify and extract content marked with
    \\added, \\deleted, \\replaced, \\highlight, and \\comment tags.
    """
    def __init__(self):
        """
        Initializes the LatexParser with predefined regex patterns for LaTeX tags.
        """
        self.RE_ADDED = re.compile(r'(\\added)(\[[^\]]*\])?\{(([^\}]?(\{[^\}]*\})?)*)\}')
        self.RE_DELETED = re.compile(r'(\\deleted)(\[[^\]]*\])?\{(([^\}]?(\{[^\}]*\})?)*)\}')
        self.RE_REPLACED = re.compile(r'(\\replaced)(\[[^\]]*\])?\{(([^\}]?(\{[^\}]*\})?)*)\}\{(([^\}]?(\{[^\}]*\})?)*)\}')
        self.RE_HIGHLIGHT = re.compile(r'(\\highlight)(\[[^\]]*\])?\{(([^\}]?(\{[^\}]*\})?)*)\}')
        self.RE_COMMENT = re.compile(r'(\\comment)(\[[^\]]*\])?\{(([^\}]?(\{[^\}]*\})?)*)\}')
        logger.info("Initialized LatexParser with LaTeX tag regex patterns.")

    def parse_line(self, line: str):
        """
        Parses a single line of LaTeX text and yields extracted tags.

        Args:
            line: A string representing a line of LaTeX text.

        Yields:
            dict: A dictionary containing information about the extracted tag,
                  e.g., {'type': 'added', 'content': '...', 'options': '...'}.
                  For 'replaced', it includes 'original_content' and 'new_content'.
        """
        logger.debug(f"Parsing line: '{line.strip()[:100]}'")
        
        # Find all matches in the line
        matches = []
        for tag_type, regex in {
            'added': self.RE_ADDED,
            'deleted': self.RE_DELETED,
            'replaced': self.RE_REPLACED,
            'highlight': self.RE_HIGHLIGHT,
            'comment': self.RE_COMMENT
        }.items():
            for match in regex.finditer(line):
                matches.append((match.start(), match.end(), tag_type, match))
        
        # Sort matches by their starting position to process them in order
        matches.sort(key=lambda x: x[0])

        for start, end, tag_type, match in matches:
            options = match.group(2) if match.group(2) else '' # e.g., [author=...]
            
            if tag_type == 'replaced':
                original_content = match.group(6) # The second content group
                new_content = match.group(3)      # The first content group
                logger.debug(f"Found replaced tag: original='{original_content[:50]}', new='{new_content[:50]}'")
                yield {
                    'type': tag_type,
                    'full_match': match.group(0),
                    'options': options,
                    'original_content': original_content,
                    'new_content': new_content,
                    'start_pos': start,
                    'end_pos': end
                }
            else:
                content = match.group(3)
                logger.debug(f"Found {tag_type} tag: content='{content[:50]}'")
                yield {
                    'type': tag_type,
                    'full_match': match.group(0),
                    'options': options,
                    'content': content,
                    'start_pos': start,
                    'end_pos': end
                }

    def parse_text(self, text: str):
        """
        Parses a multi-line LaTeX text and yields extracted tags line by line.

        Args:
            text: A string representing multi-line LaTeX text.

        Yields:
            dict: A dictionary containing information about the extracted tag.
        """
        logger.info("Starting multi-line LaTeX text parsing.")
        for line_num, line in enumerate(text.splitlines()):
            for tag_info in self.parse_line(line):
                tag_info['line_num'] = line_num + 1 # Add line number for context
                yield tag_info
        logger.info("Finished multi-line LaTeX text parsing.")
