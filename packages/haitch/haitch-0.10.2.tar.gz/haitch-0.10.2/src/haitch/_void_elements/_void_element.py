from __future__ import annotations

from typing import Literal, Mapping

from haitch._attrs import AttributeValue, serialize_attribute
from haitch._typing import Html


class VoidElement:
    """Lazily built HTML Void Element.

    <https://developer.mozilla.org/en-US/docs/Glossary/Void_element>
    """

    def __init__(self, tag: VoidElementTag) -> None:
        """Initialize element by providing a void tag name, e.g. `<img>`, `<hr>`, etc."""
        self._tag = tag
        self._attrs: Mapping[str, AttributeValue] = {}

    def __call__(self, **attrs: AttributeValue) -> VoidElement:
        """Add attributes to void element."""
        self._attrs = {**self._attrs, **attrs}
        return self

    def __str__(self) -> Html:
        """Renders the HTML Void Element as a string."""
        return Html(self._render())

    def _render(self) -> str:
        attrs_ = "".join(serialize_attribute(k, v) for k, v in self._attrs.items())
        return "<%(tag)s%(attrs)s/>" % {"tag": self._tag, "attrs": attrs_}


VoidElementTag = Literal[
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "line",
    "link",
    "meta",
    "source",
    "track",
    "wbr",
]
