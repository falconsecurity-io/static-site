import unittest
from block_classifier import block_to_block_type, BlockType

class TestBlockToBlockType(unittest.TestCase):

    def test_heading(self):
        self.assertEqual(block_to_block_type("# Heading text"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Deep heading"), BlockType.HEADING)

    def test_invalid_heading_too_many_hashes(self):
        self.assertEqual(block_to_block_type("####### Too much"), BlockType.PARAGRAPH)

    def test_code_block(self):
        code = "```\ndef foo():\n  return 'bar'\n```"
        self.assertEqual(block_to_block_type(code), BlockType.CODE)

    def test_quote(self):
        quote = "> This is a quote\n> Continued quote"
        self.assertEqual(block_to_block_type(quote), BlockType.QUOTE)

    def test_unordered_list(self):
        block = "- item one\n- item two\n- item three"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        block = "1. First\n2. Second\n3. Third"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_wrong_index(self):
        block = "1. First\n3. Wrong"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph(self):
        block = "This is a normal paragraph.\nStill the same paragraph."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

if __name__ == "__main__":
    unittest.main()
