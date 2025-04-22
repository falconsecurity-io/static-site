import re
from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
from block_classifier import block_to_block_type, BlockType

def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        if text_node.url is None:
            raise ValueError("LINK TextNode must have a URL")
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        if text_node.url is None:
            raise ValueError("IMAGE TextNode must have a URL")
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise Exception(f"Unsupported text type: {text_node.text_type}")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        # Split based on the delimiter
        split_parts = node.text.split(delimiter)

        # Must have even number of delimiters to be valid
        if len(split_parts) % 2 == 0:
            raise Exception(f"Invalid Markdown syntax: unmatched {delimiter}")

        for i, part in enumerate(split_parts):
            if part == "":
                continue
            if i % 2 == 0:
                # Normal text
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                # Delimited text
                new_nodes.append(TextNode(part, text_type))

    return new_nodes

def extract_markdown_images(text):
    # Matches ![alt text](url)
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)

def extract_markdown_links(text):
    # Matches [text](url) but not ![alt](url)
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)

def split_nodes_image(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        images = extract_markdown_images(text)

        if not images:
            new_nodes.append(node)
            continue

        for alt, url in images:
            split_text = text.split(f"![{alt}]({url})", 1)
            before = split_text[0]
            after = split_text[1] if len(split_text) > 1 else ""

            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))
            text = after

        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        links = extract_markdown_links(text)

        if not links:
            new_nodes.append(node)
            continue

        for anchor, url in links:
            split_text = text.split(f"[{anchor}]({url})", 1)
            before = split_text[0]
            after = split_text[1] if len(split_text) > 1 else ""

            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))
            new_nodes.append(TextNode(anchor, TextType.LINK, url))
            text = after

        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))

    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

    return nodes

def markdown_to_blocks(markdown):
    raw_blocks = markdown.strip().split("\n\n")
    blocks = []
    for block in raw_blocks:
        lines = block.strip().split("\n")
        stripped_lines = [line.strip() for line in lines]
        blocks.append("\n".join(stripped_lines))
    return [block for block in blocks if block]

def text_to_children(text):
    nodes = text_to_textnodes(text)
    return [text_node_to_html_node(node) for node in nodes]

def paragraph_to_html_node(block):
    inline_text = block.replace("\n", " ")
    return ParentNode("p", text_to_children(inline_text))

def heading_to_html_node(block):
    level = len(block.split(" ")[0])  # number of '#' characters
    content = block[level+1:] if block[level] == " " else block[level:]
    return ParentNode(f"h{level}", text_to_children(content.strip()))

def quote_to_html_node(block):
    lines = [line.lstrip("> ").strip() for line in block.split("\n")]
    text = " ".join(lines)
    return ParentNode("blockquote", text_to_children(text))

def unordered_list_to_html_node(block):
    items = block.split("\n")
    li_nodes = [ParentNode("li", text_to_children(item[2:].strip())) for item in items]
    return ParentNode("ul", li_nodes)

def ordered_list_to_html_node(block):
    items = block.split("\n")
    li_nodes = [ParentNode("li", text_to_children(item.split(". ", 1)[1].strip())) for item in items]
    return ParentNode("ol", li_nodes)

def code_to_html_node(block):
    lines = block.split("\n")
    if lines[0].strip() == "```" and lines[-1].strip() == "```":
        content = "\n".join(lines[1:-1]) + "\n"  # add \n at end like Markdown expects
        return ParentNode("pre", [ParentNode("code", [LeafNode(None, content)])])
    raise ValueError("Invalid code block formatting")

def block_to_html_node(block):
    block_type = block_to_block_type(block)
    match block_type:
        case BlockType.PARAGRAPH: return paragraph_to_html_node(block)
        case BlockType.HEADING: return heading_to_html_node(block)
        case BlockType.CODE: return code_to_html_node(block)
        case BlockType.QUOTE: return quote_to_html_node(block)
        case BlockType.UNORDERED_LIST: return unordered_list_to_html_node(block)
        case BlockType.ORDERED_LIST: return ordered_list_to_html_node(block)
        case _: raise ValueError(f"Unknown block type: {block_type}")

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = [block_to_html_node(block) for block in blocks]
    return ParentNode("div", children)