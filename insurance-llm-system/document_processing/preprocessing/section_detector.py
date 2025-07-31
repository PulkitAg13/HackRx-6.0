import logging
import re
from typing import Dict, List
from ...backend.config import settings

logger = logging.getLogger(__name__)

class SectionDetector:
    def __init__(self):
        self.section_patterns = {
            "header": re.compile(r'^\s*(?:abstract|summary|executive\s+summary)', re.I),
            "clauses": re.compile(r'^\s*(?:clauses?|terms\s+and\s+conditions)', re.I),
            "definitions": re.compile(r'^\s*(?:definitions?|interpretation)', re.I),
            "exclusions": re.compile(r'^\s*(?:exclusions?|limitations?)', re.I),
            "footer": re.compile(r'^\s*(?:notes?|footnotes?|references?)', re.I)
        }
        
    def detect_sections(self, text: str) -> Dict[str, List[Dict]]:
        """Identify document sections and their boundaries"""
        try:
            lines = text.split('\n')
            sections = []
            current_section = None
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                    
                # Check for section headers
                for section_type, pattern in self.section_patterns.items():
                    if pattern.match(line):
                        if current_section:
                            current_section["end_line"] = i - 1
                            sections.append(current_section)
                        
                        current_section = {
                            "type": section_type,
                            "title": line,
                            "start_line": i,
                            "end_line": len(lines) - 1
                        }
                        break
                
            if current_section:
                sections.append(current_section)
            
            # Extract section texts
            result = {}
            for section in sections:
                section_text = "\n".join(
                    lines[section["start_line"]:section["end_line"] + 1]
                )
                if section["type"] not in result:
                    result[section["type"]] = []
                result[section["type"]].append({
                    "title": section["title"],
                    "text": section_text
                })
            
            return result
        except Exception as e:
            logger.error(f"Section detection failed: {str(e)}")
            raise

def detect_sections(text: str) -> Dict[str, List[Dict]]:
    return SectionDetector().detect_sections(text)