from enum import Enum

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block):
    lines = block.split("\n")

    # Heading: starts with 1-6 '#' followed by a space
    if len(lines) == 1 and lines[0].startswith("#"):
        if lines[0].lstrip("#").startswith(" ") and 1 <= len(lines[0]) - len(lines[0].lstrip("#")) <= 6:
            return BlockType.HEADING

    # Code block: starts and ends with ``` on their own lines
    if lines[0].strip() == "```" and lines[-1].strip() == "```":
        return BlockType.CODE

    # Quote: every line starts with '>'
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    # Unordered list: every line starts with '- '
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    # Ordered list: lines start with 1., 2., 3., etc.
    if all(
        line.split(". ")[0].isdigit() and
        line.startswith(f"{i + 1}. ")
        for i, line in enumerate(lines)
    ):
        return BlockType.ORDERED_LIST

    # Otherwise, it's a paragraph
    return BlockType.PARAGRAPH
