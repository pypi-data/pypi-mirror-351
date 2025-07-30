"""
Description
-----------

PythonExtension provides the capability to do actions on the python version string, but also on Python dictionaries.


.. autoclass:: PythonExtension


.. py:function:: pyversion(lhs)

    Return a Python *Major.Minor* version string and return it as a tuple (Major, Minor).

    Available as a function and a filter. For the latter case, *lhs* is automatically specified as the left hand side of the filter.

    :param lhs: Version string. eg: "3.9"

    .. code-block:: jinja

        # scaffold.python_min_version is "3.9" for example
        {% if (scaffold.python_min_version | pyversion)[1] <= 9 %}

        {% if (pyversion("3.9")[1] == 9 %}


.. py:function:: pyversion_format(lhs, fmt)

    Return a Python *Major.Minor* version string formatted according to format passed as parameter.

    Internally uses :py:meth:`str.format`.

    Available as a function and a filter. For the latter case, *lhs* is automatically specified as the left hand side of the filter.

    :param lhs: Version string. eg: "3.9"

    :param fmt: Format string. Available replacements: *major*, *minor*

    .. code-block:: jinja

        # Returns "3.9-dev"
        {{ "3.9" | pyversion_format("Python {major}.{minor}-dev") }}


.. py:function:: pyversion_sequence(lhs, stop, sep, fmt)

    Return a sequence of Python *Major.Minor* version strings formatted according to format passed as parameter.

    Internally uses :py:meth:`str.format`.

    Available as a function and a filter. For the latter case, *lhs* is automatically specified as the left hand side of the filter.

    :param lhs: Version string. eg: "3.9"
    :param stop: Generate sequence from minor version, to this value (included)
    :param fmt: Format string. Available replacements: *major*, *minor*
    :param sep: Separator to use for joining the formatted strings.

    .. code-block:: jinja

        # Returns "3.9 3.10 3.11 3.12"
        {{ "3.9" | pyversion_sequence(12) }}


.. py:function:: to_json(lhs, sort_keys=True, **kwargs)

    Converts a Python dictionary to a JSON string.

    Internally uses :py:meth:`json.dumps`.

    Available as a function and a filter. For the latter case, *lhs* is automatically specified as the left hand side of the filter.

    :param lhs: Python dictionary
    :param sort_keys: Output of dictionaries will be sorted by key
    :param kwargs: Any of the values allowed for :py:meth:`json.dumps`

    .. code-block:: jinja

        # Returns '{"foobar": 3}'
        {{ {'foobar':3} | to_json }}
"""

import json

from jinja2.ext import Extension


def _pyversion(lhs):
    """
    Take a string with format of "Major.Minor" and return it formatted as tuple (Major, Minor)
    """
    values = str(lhs).split(".")
    return int(values[0]), int(values[1])


def _pyversion_format(lhs, fmt):
    """
    Take a string with format of "Major.Minor" and return it formatted as fmt with
    keys of 'major', and 'minor'
    """
    values = _pyversion(lhs)
    return fmt.format(major=values[0], minor=values[1])


def _pyversion_sequence(lhs, stop, sep=" ", fmt="{major}.{minor}"):
    """
    Take a format value and return it formatted according to `fmt` for the
    range from minor lfs to minor stop
    """
    major, minor = _pyversion(lhs)
    values = list(range(minor, stop + 1))
    values = [fmt.format(major=major, minor=i) for i in values]
    values = sep.join(values)
    return values


def _to_json(lhs, sort_keys=True, **kwargs):
    """
    Take an object and convert it to a JSON string
    """
    return json.dumps(lhs, sort_keys=sort_keys, **kwargs)


# pylint: disable=abstract-method
class PythonExtension(Extension):
    """
    Jinja2 extension for python manipulation.
    """

    def __init__(self, environment):
        """
        Jinja2 Extension constructor.
        """
        super().__init__(environment)

        environment.filters["pyversion"] = _pyversion
        environment.globals.update(pyversion=_pyversion)

        environment.filters["pyversion_format"] = _pyversion_format
        environment.globals.update(pyversion_format=_pyversion_format)

        environment.filters["pyversion_sequence"] = _pyversion_sequence
        environment.globals.update(pyversion_sequence=_pyversion_sequence)

        environment.filters["to_json"] = _to_json
        environment.globals.update(to_json=_to_json)
