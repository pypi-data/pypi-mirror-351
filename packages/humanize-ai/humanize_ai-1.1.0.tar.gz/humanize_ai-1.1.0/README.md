# Humanize AI

A Python library to humanize AI-generated text by normalizing Unicode characters to standard keyboard equivalents.

[![PyPI version](https://img.shields.io/pypi/v/humanize-ai.svg)](https://pypi.org/project/humanize-ai/)
[![Python versions](https://img.shields.io/pypi/pyversions/humanize-ai.svg)](https://pypi.org/project/humanize-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Why Clean Up AI Text?

AI-generated content often contains subtle markers that make it obvious to readers (and algorithms) that the text wasn't written by a human:

- Em-dashes (—) instead of regular dash (-)
- Fancy quotes (" ") instead of standard ones (")
- Unnecessary whitespace or hidden Unicode characters
- And other symbols

Cleaning these up makes the text flow more naturally, improving readability and keeping readers engaged.

## Installation

```bash
pip install humanize-ai
```

## Usage

### As a Library

```python
from humanize_ai import humanize_string, HumanizeOptions

# With default options
result = humanize_string(input_text)

# Or with custom options
options = HumanizeOptions(
    transform_hidden=True,
    transform_trailing_whitespace=True,
    transform_nbs=True,
    transform_dashes=True,
    transform_quotes=True,
    transform_other=True,
    keyboard_only=False
)
result = humanize_string(input_text, options)

print(result['text'])  # Humanized text
print(result['count'])  # Number of changed symbols
```

### Command Line

After installation, you can use the `humanize-ai` command:

```bash
# Basic usage
humanize-ai "Hello — world with fancy "quotes" and…more"

# Read from stdin
cat fancy_text.txt | humanize-ai

# Show count of transformed characters
humanize-ai --show-count "Hello — world"

# Only keep keyboard-typeable characters
humanize-ai --keyboard-only "Hello — world with 💪 emoji"
```

Available options:

- `--no-hidden`: Don't remove hidden Unicode characters
- `--no-trailing`: Don't remove trailing whitespace
- `--no-nbs`: Don't transform non-breaking spaces
- `--no-dashes`: Don't transform fancy dashes
- `--no-quotes`: Don't transform fancy quotes
- `--no-other`: Don't transform other symbols like ellipsis
- `--keyboard-only`: Only keep keyboard-typeable characters
- `--show-count`: Show the number of transformed characters

## Options

| Parameter                       | Type   | Default | Description                                                                                             |
| ------------------------------- | ------ | ------- | ------------------------------------------------------------------------------------------------------- |
| `transform_hidden`              | `bool` | `True`  | Removes hidden unicode symbols                                                                          |
| `transform_trailing_whitespace` | `bool` | `True`  | Removes spaces at the end of line                                                                       |
| `transform_nbs`                 | `bool` | `True`  | Replaces **Non-Breaking Space** character with regular space                                            |
| `transform_dashes`              | `bool` | `True`  | Replaces fancy dashes with regular dash (-)                                                             |
| `transform_quotes`              | `bool` | `True`  | Replaces fancy single and double quotes with regular quotes (' and ")                                   |
| `transform_other`               | `bool` | `True`  | Replaces `…` with `...`                                                                                 |
| `keyboard_only`                 | `bool` | `False` | Removes all symbols that cannot be typed with regular keyboard. Applied after all other transformations |

## Dependencies

- Python 3.6+
- regex (for Unicode property support)

## License

MIT

## Credits

This project was inspired by the need to improve the readability of AI-generated text and make it more human-friendly. It uses Unicode normalization techniques to achieve this. The project is python port of [humanize-ai-lib](https://github.com/Nordth/humanize-ai-lib).
