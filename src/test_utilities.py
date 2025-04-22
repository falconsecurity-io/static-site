import unittest
from textnode import TextNode, TextType
from utilities import *
from htmlnode import LeafNode

class TestTextNodeToHtmlNode(unittest.TestCase):

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("Bold!", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold!")

    def test_link(self):
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_image(self):
        node = TextNode("Alt text", TextType.IMAGE, "https://image.com/pic.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "https://image.com/pic.png", "alt": "Alt text"})

    def test_invalid_type_raises(self):
        class FakeType:
            pass
        with self.assertRaises(Exception):
            text_node_to_html_node(TextNode("text", FakeType()))

    def test_link_missing_url_raises(self):
        with self.assertRaises(ValueError):
            text_node_to_html_node(TextNode("Click me", TextType.LINK))

    def test_image_missing_url_raises(self):
        with self.assertRaises(ValueError):
            text_node_to_html_node(TextNode("Alt text", TextType.IMAGE))

class TestSplitNodesDelimiter(unittest.TestCase):

    def test_split_code(self):
        old_nodes = [TextNode("This is `code` text", TextType.TEXT)]
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT),
        ]
        result = split_nodes_delimiter(old_nodes, "`", TextType.CODE)
        self.assertEqual(result, expected)

    def test_split_bold(self):
        old_nodes = [TextNode("This is **bold** text", TextType.TEXT)]
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        result = split_nodes_delimiter(old_nodes, "**", TextType.BOLD)
        self.assertEqual(result, expected)

    def test_split_italic(self):
        old_nodes = [TextNode("This _is_ emphasized", TextType.TEXT)]
        expected = [
            TextNode("This ", TextType.TEXT),
            TextNode("is", TextType.ITALIC),
            TextNode(" emphasized", TextType.TEXT),
        ]
        result = split_nodes_delimiter(old_nodes, "_", TextType.ITALIC)
        self.assertEqual(result, expected)

    def test_non_text_node_untouched(self):
        old_nodes = [TextNode("Bold text", TextType.BOLD)]
        result = split_nodes_delimiter(old_nodes, "**", TextType.BOLD)
        self.assertEqual(result, old_nodes)

    def test_unmatched_delimiter_raises(self):
        old_nodes = [TextNode("This `is broken", TextType.TEXT)]
        with self.assertRaises(Exception) as context:
            split_nodes_delimiter(old_nodes, "`", TextType.CODE)
        self.assertIn("Invalid Markdown syntax", str(context.exception))

class TestMarkdownExtractors(unittest.TestCase):

    def test_extract_markdown_images(self):
        text = "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        expected = [("image", "https://i.imgur.com/zjjcJKZ.png")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_multiple_images(self):
        text = "![a](url1) and ![b](url2)"
        expected = [("a", "url1"), ("b", "url2")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_links(self):
        text = "Check out [Google](https://google.com)"
        expected = [("Google", "https://google.com")]
        self.assertEqual(extract_markdown_links(text), expected)

    def test_extract_multiple_links(self):
        text = "[first](one.com) and [second](two.com)"
        expected = [("first", "one.com"), ("second", "two.com")]
        self.assertEqual(extract_markdown_links(text), expected)

    def test_ignores_images_in_links(self):
        text = "This is ![not a link](img.com) but this is [yes](link.com)"
        expected = [("yes", "link.com")]
        self.assertEqual(extract_markdown_links(text), expected)

class TestSplitMarkdownElements(unittest.TestCase):

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_image_only(self):
        node = TextNode("![only](img.png)", TextType.TEXT)
        result = split_nodes_image([node])
        expected = [TextNode("only", TextType.IMAGE, "img.png")]
        self.assertEqual(result, expected)

    def test_link_only(self):
        node = TextNode("[only link](link.com)", TextType.TEXT)
        result = split_nodes_link([node])
        expected = [TextNode("only link", TextType.LINK, "link.com")]
        self.assertEqual(result, expected)

    def test_no_images(self):
        node = TextNode("Just plain text", TextType.TEXT)
        self.assertEqual(split_nodes_image([node]), [node])

    def test_no_links(self):
        node = TextNode("Still just plain text", TextType.TEXT)
        self.assertEqual(split_nodes_link([node]), [node])

class TestTextToTextNodes(unittest.TestCase):
    def test_full_parsing(self):
        input_text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        result = text_to_textnodes(input_text)
        self.assertEqual(result, expected)

    def test_text_only(self):
        input_text = "Just a regular sentence."
        expected = [TextNode("Just a regular sentence.", TextType.TEXT)]
        self.assertEqual(text_to_textnodes(input_text), expected)

    def test_code_and_bold_only(self):
        input_text = "`code` and **bold**"
        expected = [
            TextNode("code", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
        ]
        self.assertEqual(text_to_textnodes(input_text), expected)

class TestMarkdownToBlocks(unittest.TestCase):

    def test_basic_paragraphs_and_list(self):
        md = """
            This is **bolded** paragraph

            This is another paragraph with _italic_ text and `code` here
            This is the same paragraph on a new line

            - This is a list
            - with items
            """
        blocks = markdown_to_blocks(md)
        expected = [
            "This is **bolded** paragraph",
            "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
            "- This is a list\n- with items",
        ]
        self.assertEqual(blocks, expected)

    def test_only_one_block(self):
        md = "Just a single paragraph with no breaks"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Just a single paragraph with no breaks"])

    def test_empty_input(self):
        md = "\n\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_trailing_and_leading_newlines(self):
        md = "\n\nHello world\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Hello world"])

    def test_multiple_blank_lines(self):
        md = "One block\n\n\n\nTwo block\n\n\nThree block"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["One block", "Two block", "Three block"])

class TestMarkdownToHtmlNode(unittest.TestCase):

    def test_paragraphs(self):
        md = """
            This is **bolded** paragraph
            text in a p
            tag here
            This is another paragraph with _italic_ text and `code` here
            """
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
            This is text that should remain the same even with inline stuff
            """
        html = markdown_to_html_node(md).to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
