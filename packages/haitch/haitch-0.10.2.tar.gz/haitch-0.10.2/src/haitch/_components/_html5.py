from typing import Iterable

from haitch._elements._body import body
from haitch._elements._element import Element
from haitch._elements._head import head
from haitch._elements._html import html
from haitch._elements._script import ScriptElement
from haitch._elements._title import title
from haitch._typing import SupportsHtml
from haitch._void_elements._link import LinkElement
from haitch._void_elements._meta import meta


def html5(
    *,
    content: SupportsHtml,
    page_title: str = "",
    language_code: str = "",
    body_classes: str = "",
    links: Iterable[LinkElement] = (),
    scripts: Iterable[ScriptElement] = (),
) -> Element:
    """Base HTML5 document container."""
    return html(lang=language_code)(
        head(
            meta(charset="utf-8"),
            meta(name="viewport", content="width=device-width, initial-scale=1"),
            meta(http_equiv="x-ua-compatible", content="ie=edge"),
            page_title and title(page_title),
            links,
            scripts,
        ),
        body(class_=body_classes)(content) if body_classes else body(content),
    )
