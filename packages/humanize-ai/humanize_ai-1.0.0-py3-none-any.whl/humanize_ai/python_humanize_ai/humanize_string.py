#!/usr/bin/env python3
"""
Humanize AI text by converting fancy Unicode characters to standard keyboard equivalents

Copyright (c) 2025
Licensed under the MIT license
"""

import re
import regex

# Constants - set of characters to transform
IGNORABLE_SYMBOLS = "\u00ad\u180e\u200b-\u200f\u202a-\u202e\u2060\u2066-\u2069\ufeff"


class HumanizeOptions:
    def __init__(
        self,
        transform_hidden=True,
        transform_trailing_whitespace=True,
        transform_nbs=True,
        transform_dashes=True,
        transform_quotes=True,
        transform_other=True,
        keyboard_only=False,
    ):
        self.transform_hidden = transform_hidden
        self.transform_trailing_whitespace = transform_trailing_whitespace
        self.transform_nbs = transform_nbs
        self.transform_dashes = transform_dashes
        self.transform_quotes = transform_quotes
        self.transform_other = transform_other
        self.keyboard_only = keyboard_only


def humanize_string(text, options=None):
    """
    Humanize AI-generated text by normalizing characters to standard keyboard equivalents

    Args:
        text (str): The input text to humanize
        options (HumanizeOptions, optional): Options to control transformation behavior

    Returns:
        dict: Dictionary containing 'text' (transformed text) and 'count' (number of changes)
    """
    if options is None:
        options = HumanizeOptions()

    count = 0

    # Define patterns with their replacements and option flags
    patterns = [
        (re.compile(f"[{IGNORABLE_SYMBOLS}]", re.UNICODE), "", "transform_hidden"),
        (re.compile(r"[ \t\v\f]+$", re.MULTILINE), "", "transform_trailing_whitespace"),
        (re.compile("\u00a0"), " ", "transform_nbs"),
        (re.compile("[—–—]"), "-", "transform_dashes"),
        (re.compile('[""«»„]'), '"', "transform_quotes"),
        (re.compile("[" "ʼ]"), "'", "transform_quotes"),
        (re.compile("[…]"), "...", "transform_other"),
    ]

    # Apply each pattern if the corresponding option is enabled
    for pattern, replacement, option_name in patterns:
        if getattr(options, option_name):
            # Count matches
            matches = pattern.findall(text)
            for match in matches:
                count += len(match)

            # Replace
            text = pattern.sub(replacement, text)

    # Handle keyboard_only option
    if options.keyboard_only:
        # Use regex library for Unicode property support
        # Only keep letters, numbers, standard punctuation, emojis
        allowed_pattern = regex.compile(
            r'(\p{Letter}|[0-9~`?!@#$€£%^&*()_\-+={}[\]\\ \n<>/.,:;"\'|]|\p{Emoji})'
        )

        # Count and replace non-matching characters
        new_text = ""
        for char in text:
            if allowed_pattern.fullmatch(char):
                new_text += char
            else:
                count += 1

        text = new_text

    return {"count": count, "text": text}
