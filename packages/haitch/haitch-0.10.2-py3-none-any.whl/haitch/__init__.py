"""
haitch - simplify your HTML building.
=====================================

Import haitch like so:

>>> import haitch as H

Now you have access to any element you like:

>>> H.img(src="my-image.png", alt="cool image") # valid
>>> H.foo("Custom element!") # valid

Both these statements would render correctly; however, the `<img>`
element would have typing and documentation, while the `<foo>` one
would not because it is not a standard element.

Lazily build a dom tree by passing children (args) and/or
attributes (kwargs):

>>> dom = H.a(
...     H.strong("Check out my website"), # arg
...     href="https://example.com", # kwarg
... )

A called element validates its input, attaches the values to itself,
and then returns itself. This enables us to chain calls together:

>>> dom = H.a(href="https://example.com")(
...     H.strong("Check out my website"),
... )

Both instances of `dom` will render the same HTML. I prefer the second
way because it looks more like HTML, and it keeps the attributes closer
to the parent element.

Until now we have only lazily built the dom tree. In order to render it
to HTML, you need to invoke the underlying `__str__` method:

>>> str(dom) # or print(dom)
<a href="https://example.com">
  <strong>Check out my website</strong>
</a>
"""

from haitch._components._fragment import fragment
from haitch._components._html5 import html5
from haitch._components._unsafe import unsafe
from haitch._elements._a import AnchorElement, a
from haitch._elements._article import ArticleElement, article
from haitch._elements._aside import AsideElement, aside
from haitch._elements._body import BodyElement, body
from haitch._elements._details import DetailsElement, details
from haitch._elements._div import DivElement, div
from haitch._elements._element import Element
from haitch._elements._figcaption import FigcaptionElement, figcaption
from haitch._elements._figure import FigureElement, figure
from haitch._elements._footer import FooterElement, footer
from haitch._elements._form import FormElement, form
from haitch._elements._h1 import H1Element, h1
from haitch._elements._h2 import H2Element, h2
from haitch._elements._h3 import H3Element, h3
from haitch._elements._h4 import H4Element, h4
from haitch._elements._h5 import H5Element, h5
from haitch._elements._h6 import H6Element, h6
from haitch._elements._head import HeadElement, head
from haitch._elements._header import HeaderElement, header
from haitch._elements._html import HtmlElement, html
from haitch._elements._label import LabelElement, label
from haitch._elements._li import LiElement, li
from haitch._elements._main import MainElement, main
from haitch._elements._mark import MarkElement, mark
from haitch._elements._nav import NavElement, nav
from haitch._elements._noscript import NoscriptElement, noscript
from haitch._elements._ol import OlElement, ol
from haitch._elements._p import ParagraphElement, p
from haitch._elements._pre import PreElement, pre
from haitch._elements._script import ScriptElement, script
from haitch._elements._section import SectionElement, section
from haitch._elements._span import SpanElement, span
from haitch._elements._style import StyleElement, style
from haitch._elements._summary import SummaryElement, summary
from haitch._elements._table import TableElement, table
from haitch._elements._td import TdElement, td
from haitch._elements._th import ThElement, th
from haitch._elements._time import TimeElement, time
from haitch._elements._title import TitleElement, title
from haitch._elements._tr import TrElement, tr
from haitch._elements._ul import UlElement, ul
from haitch._typing import Child, Html, SupportsHtml
from haitch._void_elements._area import AreaElement, area
from haitch._void_elements._base import BaseElement, base
from haitch._void_elements._br import BrElement, br
from haitch._void_elements._col import ColElement, col
from haitch._void_elements._embed import EmbedElement, embed
from haitch._void_elements._hr import HrElement, hr
from haitch._void_elements._img import ImgElement, img
from haitch._void_elements._input import InputElement, input
from haitch._void_elements._link import LinkElement, link
from haitch._void_elements._meta import MetaElement, meta
from haitch._void_elements._source import SourceElement, source
from haitch._void_elements._track import TrackElement, track
from haitch._void_elements._void_element import VoidElement
from haitch._void_elements._wbr import WbrElement, wbr

__all__ = [
    "AnchorElement",
    "AreaElement",
    "ArticleElement",
    "AsideElement",
    "BaseElement",
    "BodyElement",
    "BrElement",
    "Child",
    "ColElement",
    "DetailsElement",
    "DivElement",
    "Element",
    "EmbedElement",
    "FigcaptionElement",
    "FigureElement",
    "FooterElement",
    "FormElement",
    "FormElement",
    "H1Element",
    "H2Element",
    "H3Element",
    "H4Element",
    "H5Element",
    "H6Element",
    "HeadElement",
    "HeaderElement",
    "HrElement",
    "Html",
    "HtmlElement",
    "ImgElement",
    "InputElement",
    "LabelElement",
    "LiElement",
    "LinkElement",
    "MainElement",
    "MarkElement",
    "MetaElement",
    "NavElement",
    "NoscriptElement",
    "OlElement",
    "ParagraphElement",
    "PreElement",
    "ScriptElement",
    "SectionElement",
    "SourceElement",
    "SpanElement",
    "StyleElement",
    "SummaryElement",
    "SupportsHtml",
    "TableElement",
    "TdElement",
    "ThElement",
    "TimeElement",
    "TitleElement",
    "TrElement",
    "TrackElement",
    "UlElement",
    "VoidElement",
    "WbrElement",
    "a",
    "area",
    "article",
    "aside",
    "base",
    "body",
    "br",
    "col",
    "details",
    "div",
    "embed",
    "figcaption",
    "figure",
    "footer",
    "form",
    "form",
    "fragment",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hr",
    "html",
    "html5",
    "img",
    "input",
    "label",
    "li",
    "link",
    "main",
    "mark",
    "meta",
    "nav",
    "noscript",
    "ol",
    "p",
    "pre",
    "script",
    "section",
    "source",
    "span",
    "style",
    "summary",
    "table",
    "td",
    "th",
    "time",
    "title",
    "tr",
    "track",
    "ul",
    "unsafe",
    "wbr",
]


def __getattr__(tag: str) -> Element:
    return Element(tag)
