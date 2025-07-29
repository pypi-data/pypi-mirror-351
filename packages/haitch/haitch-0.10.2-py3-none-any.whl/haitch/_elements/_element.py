from __future__ import annotations

import html
from typing import Iterable, Mapping

from haitch._attrs import AttributeValue, serialize_attribute
from haitch._typing import Child, Html, SupportsHtml


class Element:
    """Lazily built HTML Element.

    An Element represents a Document Object Model (DOM) with optional
    attributes and children. Render the HTML to string by invoking the
    `__str__` method.
    """

    def __init__(self, tag: str, prefix: str = "", unsafe: bool = False) -> None:
        """Initialize element by providing a tag name, ie. "a", "div", etc."""
        self._tag = tag
        self._prefix = prefix
        self._unsafe = unsafe
        self._attrs: Mapping[str, AttributeValue] = {}
        self._children: Iterable[Child] = []

    def __call__(self, *children: Child, **attrs: AttributeValue) -> Element:
        """Add children and/or attributes to element.

        Provide attributes, children, or a combination of both:

        >>> import haitch as H
        >>> H.h1("My heading")
        >>> H.h1(style="color: red;")("My heading")
        """
        self._children = [*self._children, *children]
        self._attrs = {**self._attrs, **attrs}
        return self

    def __str__(self) -> Html:
        """Renders the HTML element as a string."""
        return Html(f"{self._prefix}{self._render()}")

    def _render(self) -> str:
        attrs_ = "".join(serialize_attribute(k, v) for k, v in self._attrs.items())
        children_ = "".join(self._render_child(child) for child in self._children)

        if self._tag == "fragment":
            return children_

        return f"<{self._tag}{attrs_}>{children_}</{self._tag}>"

    def _render_child(self, child: Child) -> str:
        if child is None or child is False:
            return ""

        elif isinstance(child, str):
            return child if self._unsafe else html.escape(child)

        elif isinstance(child, SupportsHtml):
            return child._render()

        elif isinstance(child, Iterable):
            return "".join(str(nested_child) for nested_child in child)

        else:
            raise ValueError(f"Invalid child type: {type(child)}")
