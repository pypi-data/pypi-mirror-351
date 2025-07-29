import haitch as H


def test_area_element():
    el = H.area(
        shape="poly",
        coords="129,0,260,95,129,138",
        href="https://developer.mozilla.org/docs/",
    )

    got = str(el)
    want = '<area shape="poly" coords="129,0,260,95,129,138" href="https://developer.mozilla.org/docs/"/>'

    assert got == want


def test_base_element():
    got = str(H.base(href="https://example.com"))
    want = '<base href="https://example.com"/>'
    assert got == want


def test_br_element():
    got = str(H.br())
    want = "<br/>"
    assert got == want


def test_col_element():
    got = str(H.col(span=2))
    want = '<col span="2"/>'
    assert got == want


def test_embed_element():
    el = H.embed(
        type_="video/quicktime",
        src="movie.mov",
        width=640,
        height=480,
        title="Title of my video",
    )

    got = str(el)
    want = '<embed type="video/quicktime" src="movie.mov" width="640" height="480" title="Title of my video"/>'

    assert got == want


def test_hr_element():
    got = str(H.hr())
    want = "<hr/>"
    assert got == want


def test_img_element():
    got = str(H.img(src="photo.png", alt="My image"))
    want = '<img src="photo.png" alt="My image"/>'
    assert got == want


def test_input_element():
    got = str(H.input(name="my-button", type_="button"))
    want = '<input name="my-button" type="button"/>'
    assert got == want


def test_link_element():
    got = str(H.link(href="default.css", rel="stylesheet"))
    want = '<link href="default.css" rel="stylesheet"/>'
    assert got == want


def test_meta_element():
    got = str(H.meta(charset="utf-8"))
    want = '<meta charset="utf-8"/>'
    assert got == want


def test_source_element():
    got = str(H.source(src="foo.mov", type_="video/quicktime"))
    want = '<source src="foo.mov" type="video/quicktime"/>'
    assert got == want


def test_track_element():
    got = str(H.track(src="captions.vtt", kind="captions"))
    want = '<track src="captions.vtt" kind="captions"/>'
    assert got == want


def test_wbr_element():
    got = str(H.wbr())
    want = "<wbr/>"
    assert got == want


def test_void_element_with_extra_attrs():
    el = H.img(
        src="photo.png",
        alt="My image",
        extra_attrs={"foo": "bar"},
    )

    got = str(el)
    want = '<img src="photo.png" alt="My image" foo="bar"/>'

    assert got == want
