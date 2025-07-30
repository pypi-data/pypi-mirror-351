"""
Description
-----------

StringExtension provides the standard string functions.


.. autoclass:: StringExtension


.. py:function:: slugify(lhs, **kwargs)

    Slugifies the value with python-slugify

    https://pypi.org/project/python-slugify/

    Make a slug from the given text.

    :param text (str): initial text
    :param entities (bool): converts html entities to unicode (foo &amp; bar -> foo-bar)
    :param decimal (bool): converts html decimal to unicode (&#381; -> Ž -> z)
    :param hexadecimal (bool): converts html hexadecimal to unicode (&#x17D; -> Ž -> z)
    :param max_length (int): output string length
    :param word_boundary (bool): truncates to end of full words (length may be shorter than max_length)
    :param save_order (bool): if parameter is True and max_length > 0 return whole words in the initial order
    :param separator (str): separator between words
    :param stopwords (iterable): words to discount
    :param regex_pattern (str): regex pattern for disallowed characters
    :param lowercase (bool): activate case sensitivity by setting it to False
    :param replacements (iterable): list of replacement rules e.g. [['|', 'or'], ['%', 'percent']]
    :param allow_unicode (bool): allow unicode characters

    Available as a function and a filter. For the latter case, *lhs* is automatically specified as the left hand side of the filter.

    .. code-block:: jinja

        # Returns "hello-world"
        {{ "Hello, World!" | slugify }}

        # Returns "hello_world"
        {{ slugify("Hello, World!", separator="_") }}


.. py:function:: random_string(length, punctuation=False, lowercase=True, uppercase=True, digits=True)

    Return a random string of length characters from the character sets selected.

    Uses :py:func:`secrets.choice` module to generate random strings.

    :param punctuation: Use the :py:data:`string.punctuation` set.
    :param lowercase: Use the :py:data:`string.ascii_lowercase` set.
    :param uppercase: Use the :py:data:`string.ascii_uppercase` set.
    :param digits: Use the :py:data:`string.digits` set.

    .. code-block:: jinja

        {{ random_string(8, punctuation=True) }}
"""

import string
from secrets import choice

from jinja2.ext import Extension
from slugify import slugify as pyslugify


def _slugify(text, **kwargs):
    """
    Slugifies the value.
    https://pypi.org/project/python-slugify/

    Make a slug from the given text.
    :param text (str): initial text
    :param entities (bool): converts html entities to unicode (foo &amp; bar -> foo-bar)
    :param decimal (bool): converts html decimal to unicode (&#381; -> Ž -> z)
    :param hexadecimal (bool): converts html hexadecimal to unicode (&#x17D; -> Ž -> z)
    :param max_length (int): output string length
    :param word_boundary (bool): truncates to end of full words (length may be shorter than max_length)
    :param save_order (bool): if parameter is True and max_length > 0 return whole words in the initial order
    :param separator (str): separator between words
    :param stopwords (iterable): words to discount
    :param regex_pattern (str): regex pattern for disallowed characters
    :param lowercase (bool): activate case sensitivity by setting it to False
    :param replacements (iterable): list of replacement rules e.g. [['|', 'or'], ['%', 'percent']]
    :param allow_unicode (bool): allow unicode characters
    :return (str): slugify text
    """
    return pyslugify(text, **kwargs)


def _random_string(length, punctuation=False, lowercase=True, uppercase=True, digits=True):
    if not isinstance(length, int) or length <= 0:
        raise ValueError("length must be a positive integer")

    corpus = ""
    if lowercase:
        corpus += string.ascii_lowercase
    if uppercase:
        corpus += string.ascii_uppercase
    if digits:
        corpus += string.digits
    if punctuation:
        corpus += string.punctuation
    if len(corpus) == 0:
        raise ValueError("corpus is empty, no characters to choose from")

    return "".join(choice(corpus) for _ in range(length))


# pylint: disable=abstract-method
class StringExtension(Extension):
    """
    Jinja2 extension for string manipulation.
    """

    def __init__(self, environment):
        """
        Jinja2 Extension constructor.
        """
        super().__init__(environment)

        environment.globals.update(random_string=_random_string)

        environment.filters["slugify"] = _slugify
        environment.globals.update(slugify=_slugify)
