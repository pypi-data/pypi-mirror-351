from dataclasses import dataclass

@dataclass
class Comment:
    id: str
    author: str
    date: str
    text: str
    # Optional: Add 'range_text' if precise text association is achieved

@dataclass
class Revision:
    type: str  # "inserted" or "deleted"
    author: str
    date: str
    text: str
