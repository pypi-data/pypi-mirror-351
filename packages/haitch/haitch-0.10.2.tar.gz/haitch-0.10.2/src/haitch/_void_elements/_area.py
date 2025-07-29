from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._void_elements._void_element import VoidElement

AreaElement = NewType("AreaElement", VoidElement)
"""An `<area>` element."""


def area(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[AreaAttrs],
) -> AreaElement:
    """Defines an area inside an image map.

    An image map allows geometric areas on an image to be associated with hypertext
    links. This element is used only within a `<map>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area>
    """
    el = VoidElement("area")(**attrs, **extra_attrs or {})
    return AreaElement(el)


class AreaAttrs(GlobalAttrs):
    """Attributes for the `<area>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area>
    """

    alt: NotRequired[str]
    """A text string alternative to display on browsers that do not display images.

    Note: this attribute is required only if the `href` attribute is used.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#alt>
    """

    coords: NotRequired[str]
    """Details the coordinates of the `shape` attribute in size, shape, and placement.

    Note: this attribute must not be used when `shape` is set to default.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#coords>
    """

    download: NotRequired[str]
    """Indicates the author intends the hyperlink to be used for downloading a resource.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#download>
    """

    href: NotRequired[str]
    """The hyperlink target URL for the area.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#href>
    """

    ping: NotRequired[str]
    """Contains a space-separated list of URLs to ping when hyperlink followed.

    Note: background `POST` requests with the body `PING` will be sent by the browser.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#ping>
    """

    rel: NotRequired[str]
    """Defines the relationship between a linked resource and the current document.

    Valid values: <https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel>

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#rel>
    """

    shape: NotRequired[Literal["default", "rect", "circle", "poly"]]
    """The shape of the associated hot spot.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#shape>
    """

    target: NotRequired[str]
    """A keyword of the browsing context to display the linked resource.

    The following keywords have special meaning: `_self`, `_blank`, `_parent`, `_top`.

    Note: Setting target="_blank" on `<area>` elements implicitly provides the same rel
    behavior as setting rel="noopener" which does not set window.opener. See browser
    compatibility for support status.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#target>
    """
