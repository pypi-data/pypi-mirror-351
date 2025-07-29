import haitch as H


def test_article_element():
    got = str(H.article("Really cool site"))
    want = "<article>Really cool site</article>"
    assert got == want


def test_aside_element():
    got = str(H.aside("Really cool aside"))
    want = "<aside>Really cool aside</aside>"
    assert got == want


def test_details_element():
    got = str(H.details(open=True)("Really cool details"))
    want = "<details open>Really cool details</details>"
    assert got == want


def test_figcaption_element():
    got = str(H.figcaption("Really cool figcaption"))
    want = "<figcaption>Really cool figcaption</figcaption>"
    assert got == want


def test_figure_element():
    got = str(H.figure("Really cool figure"))
    want = "<figure>Really cool figure</figure>"
    assert got == want


def test_footer_element():
    got = str(H.footer("Really cool footer"))
    want = "<footer>Really cool footer</footer>"
    assert got == want


def test_header_element():
    got = str(H.header("Really cool header"))
    want = "<header>Really cool header</header>"
    assert got == want


def test_main_element():
    got = str(H.main("Really cool main"))
    want = "<main>Really cool main</main>"
    assert got == want


def test_mark_element():
    got = str(H.mark("Really cool mark"))
    want = "<mark>Really cool mark</mark>"
    assert got == want


def test_nav_element():
    got = str(H.nav("Really cool nav"))
    want = "<nav>Really cool nav</nav>"
    assert got == want


def test_section_element():
    got = str(H.section("Really cool section"))
    want = "<section>Really cool section</section>"
    assert got == want


def test_summary_element():
    got = str(H.summary("Really cool summary"))
    want = "<summary>Really cool summary</summary>"
    assert got == want


def test_time_element():
    got = str(H.time(datetime="2024-06-19")("June 19th, 2024"))
    want = '<time datetime="2024-06-19">June 19th, 2024</time>'
    assert got == want
