# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project infrastructure: CI workflow, changelog, and development requirements.

### Fixed

- Unified package version to `2.1.0` across `setup.py`, `pyproject.toml`, and `__init__.py`.
- Corrected repository URLs in `setup.py` and `pyproject.toml` to match the actual GitHub repository name.
- Reformatted `CONTRIBUTING.md` so it renders correctly as Markdown instead of being wrapped in a code block.
- Removed empty `release.py` placeholder file.

## [2.1.0] - 2024-XX-XX

### Added

- Multi-language negation detection support for Chinese, English, Japanese, and Korean.
- Improved harmonic monitor with configurable consecutive low threshold.
- Retry backtrack strategy with adaptive parameter passing.

### Changed

- Enhanced decorator backtrack logic to validate result quality before returning.

## [2.0.1] - 2024-XX-XX

### Added

- Initial release of ThinkCheck-lib, a harmonic-theory based LLM reasoning quality monitoring framework.
