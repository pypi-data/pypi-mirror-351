<img width="200px" src="https://git.sr.ht/~loges/haitch/blob/master/docs/img/logo.svg" alt='haitch logo'>

_simplify your HTML building._

[![builds.sr.ht status](https://builds.sr.ht/~loges/haitch.svg)](https://builds.sr.ht/~loges/haitch?)
[![PyPI - Version](https://img.shields.io/pypi/v/haitch.svg)](https://pypi.org/project/haitch)

# haitch

> alternative pronunciation for the letter "H"

The `haitch` library provides a builder for composing HTML elements together.
The element nodes are functional and will only be rendered when invoked.

Why write your HTML in templates when you can do it in Python?

## Features

- Compose HTML elements.
- Lazily evaluate DOM tree.
- 100% test coverage.
- 100% type annotated codebase.
- Zero dependencies.
- Document common elements.

## Roadmap

This library will reach v1 when all HTML elements are supported and documented.
At that point the library will be considered feature complete and I will shift
my focus to improving the documentation.

## Requirements

Python 3.8+

## Quickstart

Install `haitch` using pip:

```console
$ pip install haitch
```

Import the library like so:

```python
import haitch as H
```

By importing the root module, you now have access to any element you want:

```python
# Render known `h1` tag.
h1 = H.h1("Hello, world")
print(h1) # <h1>Hello, world</h1>

# Render custom `foo` tag (useful for web components).
foo = H.foo("Hello, world")
print(foo) # <foo>Hello, world!</foo>
```

Here is a simple example that showcases the advantage of writing HTML in
Python. Let's say we want an ordered list of stored org domain emails:

```python
# Fetch emails from data store.
emails = ["jane@aol.com", "bob@example.com", "mark@mail.org", "karen@hr.org"]

# Build an ordered list with org domain emails.
dom = H.ol(class_="email-list")(
    H.li(H.a(href=f"mailto:{email}")(email))
    for email in sorted(emails)
    if email.endswith(".org")
)

print(dom)
# <ol class="email-list">
#   <li><a href="mailto:karen@hr.org">karen@hr.org</a></li>
#   <li><a href="mailto:mark@mail.org">mark@mail.org</a></li>
# </ol>
```

The printed output above is prettified for better readability. The actual
output is a minified string with no formatting.

## Documentation

Activate your virtual environment where `haitch` is installed and run:

```console
$ python -c "help('haitch')"
```

## Motivation

Inspired by the fantastic [htbuilder](https://github.com/tvst/htbuilder)
library as an alternative to template engines. The library met most of my
needs, but I really wanted to expand its functionality by leveraging modern
Python features like typing. This coincided with my excitement for
[Hypermedia-Driven Applications
(HDAs)](https://htmx.org/essays/hypermedia-driven-applications/) with tools
like `htmx` and `alpine`.

While writing HDAs has simplified my application logic, the lack of
autocompletion and diagnostics in templates are quite annoying. Therefore, my
goal with this package is to make writing HTML as simple and fun as writing
normal Python code _by writing normal Python code_.

## Non-goals

The following features will _not_ be supported:

- **Deprecated elements and attributes**: if you want to use them, that is fine
by me as `haitch` supports generic elements and attributes. However, I am not
going to write the annotations and documentation for them.
- **100% input validation**: this library is meant to assist the developer to
write valid HTML with the help of type annotations and documentation. In the
end, it is up to the developer and browser to verify that the input is of the
correct type. So for example, I will not add any validation to make sure that a
`<col>` element is directly nested inside of a `<colgroup>` element or that the
`span` attribute for the `<col>` element is a positive integer.

## Releases

This library adheres to [semantic versioning](https://semver.org/) and keeps a
[changelog](./CHANGELOG.md).

## Examples

Intended to help you to integrate `haitch` into your application:

- [FastAPI minimal example](https://git.sr.ht/~loges/haitch-example-fastapi)
- [Django minimal example](https://git.sr.ht/~loges/haitch-example-django)

## License

`haitch` is distributed under the terms of the
[BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) license.
