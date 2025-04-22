import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):

    def test_props_to_html_multiple(self):
        node = HTMLNode(
            tag="a",
            props={"href": "https://example.com", "target": "_blank"}
        )
        expected = ' href="https://example.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_empty(self):
        node = HTMLNode(tag="p")
        self.assertEqual(node.props_to_html(), "")

    def test_repr(self):
        node = HTMLNode(
            tag="p",
            value="Hello",
            children=[],
            props={"class": "intro"}
        )
        expected_repr = 'HTMLNode(tag=p, value=Hello, children=[], props={\'class\': \'intro\'})'
        self.assertEqual(repr(node), expected_repr)
    
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leaf_to_html_raw_text(self):
        node = LeafNode(None, "Just text")
        self.assertEqual(node.to_html(), "Just text")

    def test_leaf_raises_no_value(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None)

    def test_leaf_repr(self):
        node = LeafNode("strong", "Bold text", {"class": "important"})
        expected = 'HTMLNode(tag=strong, value=Bold text, children=[], props={\'class\': \'important\'})'
        self.assertEqual(repr(node), expected)

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span><b>grandchild</b></span></div>")

    def test_to_html_with_mixed_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(node.to_html(), "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>")

    def test_parentnode_no_tag(self):
        with self.assertRaises(ValueError) as context:
            ParentNode(None, [LeafNode("p", "test")])
        self.assertEqual(str(context.exception), "ParentNode must have a tag")

    def test_parentnode_no_children(self):
        with self.assertRaises(ValueError) as context:
            ParentNode("div", None)
        self.assertEqual(str(context.exception), "ParentNode must have children")

if __name__ == "__main__":
    unittest.main()
