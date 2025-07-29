import haitch as H


def test_a_element():
    got = str(H.a(href="https://example.com")("Really cool site"))
    want = '<a href="https://example.com">Really cool site</a>'
    assert got == want


def test_body_element():
    got = str(H.body(onload='javascript:alert("document loaded")'))
    want = '<body onload="javascript:alert(&quot;document loaded&quot;)"></body>'
    assert got == want


def test_div_element():
    got = str(H.div("Generic container."))
    want = "<div>Generic container.</div>"
    assert got == want


def test_form_element():
    got = str(H.form(action="/add", method="post"))
    want = '<form action="/add" method="post"></form>'
    assert got == want


def test_h1_element():
    got = str(H.h1("Heading 1"))
    want = "<h1>Heading 1</h1>"
    assert got == want


def test_h2_element():
    got = str(H.h2("Heading 2"))
    want = "<h2>Heading 2</h2>"
    assert got == want


def test_h3_element():
    got = str(H.h3("Heading 3"))
    want = "<h3>Heading 3</h3>"
    assert got == want


def test_h4_element():
    got = str(H.h4("Heading 4"))
    want = "<h4>Heading 4</h4>"
    assert got == want


def test_h5_element():
    got = str(H.h5("Heading 5"))
    want = "<h5>Heading 5</h5>"
    assert got == want


def test_h6_element():
    got = str(H.h6("Heading 6"))
    want = "<h6>Heading 6</h6>"
    assert got == want


def test_head_element():
    got = str(H.head(H.link(href="main.css", rel="stylesheet")))
    want = '<head><link href="main.css" rel="stylesheet"/></head>'
    assert got == want


def test_html_element():
    got = str(H.html(lang="en"))
    want = '<!doctype html><html lang="en"></html>'
    assert got == want


def test_label_element():
    got = str(H.label(for_="username")("Username:"))
    want = '<label for="username">Username:</label>'
    assert got == want


def test_noscript_element():
    got = str(H.noscript("Only show when scripting disabled."))
    want = "<noscript>Only show when scripting disabled.</noscript>"
    assert got == want


def test_ol_element():
    ordered_list = H.ol(type_="i")(
        H.li("First"),
        H.li("Second"),
    )

    got = str(ordered_list)
    want = '<ol type="i"><li>First</li><li>Second</li></ol>'

    assert got == want


def test_p_element():
    got = str(H.p("This is a paragraph."))
    want = "<p>This is a paragraph.</p>"
    assert got == want


def test_pre_element():
    got = str(H.pre("Preformatted text."))
    want = "<pre>Preformatted text.</pre>"
    assert got == want


def test_script_element_src_script_file():
    got = str(H.script(async_=True, type_="module", src="async-script.js"))
    want = '<script async type="module" src="async-script.js"></script>'
    assert got == want


def test_script_element_inline_scripting():
    code = """
    const userInfo = JSON.parse(document.getElementById("data").text);
    console.log("User information: %o", userInfo);
"""

    got = str(H.script(code))
    want = """\
<script>
    const userInfo = JSON.parse(document.getElementById(&quot;data&quot;).text);
    console.log(&quot;User information: %o&quot;, userInfo);
</script>"""

    assert got == want


def test_span_element():
    got = str(H.span("Generic inline container."))
    want = "<span>Generic inline container.</span>"
    assert got == want


def test_style_element():
    styles = """
    p {
      color: blue;
      background-color: yellow;
    }
"""

    got = str(H.style(media="all and (max-width: 500px)")(styles))
    want = """\
<style media="all and (max-width: 500px)">
    p {
      color: blue;
      background-color: yellow;
    }
</style>"""

    assert got == want


def test_table_element():
    table = H.table(
        H.tr(
            H.th("Name"),
            H.th("Age"),
        ),
        H.tr(
            H.td("Mario"),
            H.td("33"),
        ),
    )

    got = str(table)
    want = "<table><tr><th>Name</th><th>Age</th></tr><tr><td>Mario</td><td>33</td></tr></table>"

    assert got == want


def test_ul_element():
    unordered_list = H.ul(
        H.li("First"),
        H.li("Second"),
    )

    got = str(unordered_list)
    want = "<ul><li>First</li><li>Second</li></ul>"

    assert got == want


def test_title_element():
    got = str(H.title("Hello, world!"))
    want = "<title>Hello, world!</title>"
    assert got == want
