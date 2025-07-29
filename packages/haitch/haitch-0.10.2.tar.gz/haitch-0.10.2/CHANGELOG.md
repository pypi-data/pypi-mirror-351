# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.10.2 - 2025-05-27

### Changed

- Avoid using `dict` as default argument for elements.

### Fixed

- Void element class should match `SupportsHtml` protocol.

## 0.10.1 - 2024-07-12

### Changed

- Adapt where the `<!doctype html>` is prepended to the `html` element.
- Improve performance by switching to f-strings.

## 0.10.0 - 2024-06-19

### Added

- Add support for the most common semantic elements. ([#9](https://todo.sr.ht/~loges/haitch/9))

## 0.9.0 - 2024-04-25

### Added

- Add `unsafe` component for passed unescaped HTML as an element. ([#12](https://todo.sr.ht/~loges/haitch/12))

### Fixed

- Quiet diagnostic warning by using `elif` control flow.

## 0.8.2 - 2024-03-22

### Changed

- Simplify the showcase example in the readme.

## 0.8.1 - 2024-03-22

### Added

- Add documentation section to readme.

### Changed

- Improve package level help documentation.

## 0.8.0 - 2024-03-08

### Added

- Export `Child` type from package.
- Add `py.typed` file for external tooling (i.e. mypy).

## 0.7.0 - 2024-02-29

### Added

- Add documentation for `form` and `label` elements. ([#11](https://todo.sr.ht/~loges/haitch/11))

## 0.6.0 - 2024-02-22

### Added

- Add `html5` component for improved HTML document creation. ([#8](https://todo.sr.ht/~loges/haitch/8))

### Fixed

- Specify which files to include in the `sdist` target build.

## 0.5.0 - 2024-02-21

### Added

- Add type support and documentation for most common elements. ([#7](https://todo.sr.ht/~loges/haitch/7))

### Changed

- Rename `HtmlElement` protocol type to `SupportsHtml`.
- Make doctype prefix lowercase for `<html>` element.

### Fixed

- Copypasta in `<link>` element attribute docstring.
- Adapt bad attribute type error message.

## 0.4.0 - 2024-02-14

### Added

- Separate void elements into their own `VoidElement` class. ([#5](https://todo.sr.ht/~loges/haitch/5))
- Add typing for HTML global attributes.
- Add type support and documentation for known void elements. ([#6](https://todo.sr.ht/~loges/haitch/6))
- Expose `Html` and `HtmlElement` types.

### Fixed

- Support integer attribute value when serializing.

## 0.3.0 - 2024-01-16

### Added

- Do not render children if value is `False` or `None`.
- Render `Html` new type based on the `str` type.
- Support iterable as element child.

## 0.2.0 - 2024-01-09

### Added

- Add special `fragment` tag element. ([#3](https://todo.sr.ht/~loges/haitch/3))
- Prepend html DOCTYPE to `html` tag element. ([#4](https://todo.sr.ht/~loges/haitch/4))

## 0.1.0 - 2024-01-06

### Added

- Add `Element` class for lazily building HTML elements.
- Handle reserved words in attributes.
- Support self closing void elements.
- Escape inner HTML and attribute values.
