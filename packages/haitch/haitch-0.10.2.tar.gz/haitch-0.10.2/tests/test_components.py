import haitch as H


def test_fragment_element_does_not_render_its_parent_tag():
    dom = H.fragment(
        H.h1("Hello, world!"),
        H.p("Nice to meet you."),
    )

    got = str(dom)
    want = "<h1>Hello, world!</h1><p>Nice to meet you.</p>"

    assert got == want


def test_unsafe_does_not_escape_html_string():
    got = str(H.unsafe("<h1>Hello</h1>"))
    want = "<h1>Hello</h1>"
    assert got == want


def test_html5_component():
    html = H.html5(
        content=H.fragment(
            H.header(
                H.h1("Hello, reader."),
            ),
            H.main(
                H.section(
                    H.p("So why is this a cool page?"),
                    H.a(href="#")("Check the link for more info!"),
                ),
            ),
        ),
        page_title="Cool page",
        language_code="en",
        body_classes="container box",
        links=[
            H.link(href="main.css", rel="stylesheet"),
            H.link(href="custom.css", rel="stylesheet"),
        ],
        scripts=[
            H.script(src="main.js", defer=True),
        ],
    )

    got = str(html)
    want = '<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><meta http-equiv="x-ua-compatible" content="ie=edge"/><title>Cool page</title><link href="main.css" rel="stylesheet"/><link href="custom.css" rel="stylesheet"/><script src="main.js" defer></script></head><body class="container box"><header><h1>Hello, reader.</h1></header><main><section><p>So why is this a cool page?</p><a href="#">Check the link for more info!</a></section></main></body></html>'
    # Pipe this into prettier for improved readability: $ echo '...' | prettier --parser html

    assert got == want


def test_html5_component_just_content():
    html = H.html5(content=H.main())

    got = str(html)
    want = '<!doctype html><html lang=""><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><meta http-equiv="x-ua-compatible" content="ie=edge"/></head><body><main></main></body></html>'
    # Pipe this into prettier for improved readability: $ echo '...' | prettier --parser html

    assert got == want
