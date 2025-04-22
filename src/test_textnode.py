import unittest
from textnode import TextNode, TextType

class TestTextNode(unittest.TestCase):

    def test_eq_same_text_type(self):
        node1 = TextNode("hello", TextType.TEXT)
        node2 = TextNode("hello", TextType.TEXT)
        self.assertEqual(node1, node2)

    def test_not_eq_different_text(self):
        node1 = TextNode("hello", TextType.TEXT)
        node2 = TextNode("hi", TextType.TEXT)
        self.assertNotEqual(node1, node2)

    def test_not_eq_different_type(self):
        node1 = TextNode("hello", TextType.TEXT)
        node2 = TextNode("hello", TextType.BOLD)
        self.assertNotEqual(node1, node2)

    def test_eq_with_url(self):
        node1 = TextNode("Click me", TextType.LINK, "https://boot.dev")
        node2 = TextNode("Click me", TextType.LINK, "https://boot.dev")
        self.assertEqual(node1, node2)

    def test_not_eq_different_url(self):
        node1 = TextNode("Click me", TextType.LINK, "https://boot.dev")
        node2 = TextNode("Click me", TextType.LINK, "https://example.com")
        self.assertNotEqual(node1, node2)

if __name__ == "__main__":
    unittest.main()