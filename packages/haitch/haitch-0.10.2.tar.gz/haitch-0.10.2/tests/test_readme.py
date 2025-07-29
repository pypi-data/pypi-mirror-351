import haitch as H


def test_simple_h1_example():
    # Render known `h1` tag.
    h1 = H.h1("Hello, world")

    got = str(h1)
    want = "<h1>Hello, world</h1>"

    assert got == want


def test_custom_component():
    # Render custom `foo` tag (useful for web components).
    foo = H.foo("Hello, world")

    got = str(foo)
    want = "<foo>Hello, world</foo>"

    assert got == want


def test_emails_example():
    # Fetch emails from data store
    emails = ["jane@aol.com", "bob@example.com", "mark@mail.org", "karen@hr.org"]

    # Build an unordered list of ".org" email addresses
    dom = H.ol(class_="email-list")(
        H.li(H.a(href=f"mailto:{email}")(email))
        for email in sorted(emails)
        if email.endswith(".org")
    )

    got = str(dom)
    want = '<ol class="email-list"><li><a href="mailto:karen@hr.org">karen@hr.org</a></li><li><a href="mailto:mark@mail.org">mark@mail.org</a></li></ol>'
    # Pipe this into prettier for improved readability: $ echo '...' | prettier --parser html

    assert got == want
