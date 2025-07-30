import re

from lxml import etree, html

FAKE_ROOT = "pagesmith-root"
HTML_TAG_REPLACEMENT = "pagesmith-html"
TAGS_TO_REPLACE = {
    "html": HTML_TAG_REPLACEMENT,
    "head": "pagesmith-head",
}


def parse_partial_html(input_html: str) -> etree._Element | None:  # noqa: C901,PLR0912
    """Parse string with HTML fragment or full document into an lxml tree.

    Handles malformed HTML gracefully and preserves content structure as much as possible.

    Note:
        The returned element tree have a 'root' wrapper element that
        contains the actual parsed content.
        Use `etree_to_str()` to get the clean HTML output without the wrapper.

    Features:
    - Removes comments and CDATA sections
    - Handles partial/fragment HTML (no need for complete document structure)
    - Recovers from malformed HTML using lxml's error recovery
    - Suppress lxml special handling for tags `html`, `head` and treat them as normal tags

    Returns:
        lxml Element tree, wrapped in a 'root' container element
        or None if parsing completely fails
    """

    # Clean up comments
    open_count = input_html.count("<!--")
    close_count = input_html.count("-->")
    if open_count != close_count:
        input_html = input_html.replace("<!--", "&lt;!--")

    # Clean up CDATA
    input_html = re.sub(r"[\n\r]+", " ", input_html)
    input_html = re.sub(r"(<!\[CDATA\[.*?]]>|<!DOCTYPE[^>]*?>)", "", input_html, flags=re.DOTALL)

    # Temporarily replace HTML tags to avoid special treatment by lxml
    for tag, replacement in TAGS_TO_REPLACE.items():
        input_html = re.sub(
            rf"<{tag}(\s[^>]*)?>",
            rf"<{replacement}\1>",
            input_html,
            flags=re.IGNORECASE,
        )
        input_html = re.sub(rf"</{tag}>", rf"</{replacement}>", input_html, flags=re.IGNORECASE)

    parser = etree.HTMLParser(recover=True, remove_comments=True, remove_pis=True)
    try:
        fragments = html.fragments_fromstring(
            f"<{FAKE_ROOT}>{input_html}</{FAKE_ROOT}>",
            parser=parser,
        )
    except Exception:  # noqa: BLE001
        fragments = html.Element(FAKE_ROOT)
        fragments.text = input_html

    result = fragments[0]

    if isinstance(result, etree._Element):  # noqa: SLF001
        html_tags = result.xpath(f".//{HTML_TAG_REPLACEMENT}")

        # Root element has the target tag - rename it
        if result.tag == HTML_TAG_REPLACEMENT:
            result.tag = "html"
        # Only one element in the entire tree has the target tag - rename it
        elif len(html_tags) == 1:
            html_tags[0].tag = "html"
        # Multiple elements have the target tag - unwrap them all
        else:
            for element in html_tags:
                unwrap_element(element)

        for tag, replacement in TAGS_TO_REPLACE.items():
            for elem in result.xpath(f".//{replacement}"):
                elem.tag = tag

    return result


def etree_to_str(root: etree._Element | None) -> str:
    """Convert etree back to string, removing root wrapper."""
    if root is None:
        return ""

    if isinstance(root, str):
        return root

    # If this is our root wrapper, extract its contents
    if root.tag == FAKE_ROOT:
        result = root.text or ""
        for child in root:
            result += html.tostring(child, encoding="unicode", method="html")
        return result

    # For normal elements, return as-is using HTML serialization
    return html.tostring(root, encoding="unicode", method="html")  # type: ignore[no-any-return]


def unwrap_element(element: etree.Element) -> None:  # noqa: PLR0912,C901
    """Unwrap an element, replacing with its content."""
    parent = element.getparent()
    if parent is None:
        return

    pos = parent.index(element)

    # Handle text content
    if element.text:
        if pos > 0:
            # Add to tail of previous sibling
            prev = parent[pos - 1]
            if prev.tail:
                prev.tail += element.text
            else:
                prev.tail = element.text
        # Add to parent's text
        elif parent.text:
            parent.text += element.text
        else:
            parent.text = element.text

    # Move each child to parent
    children = list(element)
    for i, child in enumerate(children):
        parent.insert(pos + i, child)

    # Handle tail text
    if element.tail:
        if len(children) > 0:
            # Add to tail of last child
            if children[-1].tail:
                children[-1].tail += element.tail
            else:
                children[-1].tail = element.tail
        elif pos > 0:
            # Add to tail of previous sibling
            prev = parent[pos - 1]
            if prev.tail:
                prev.tail += element.tail
            else:
                prev.tail = element.tail
        # Add to parent's text
        elif parent.text:
            parent.text += element.tail
        else:
            parent.text = element.tail

    parent.remove(element)
