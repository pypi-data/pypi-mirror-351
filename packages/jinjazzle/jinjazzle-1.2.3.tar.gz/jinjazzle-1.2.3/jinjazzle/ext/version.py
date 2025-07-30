"""
Description
-----------

VersionExtension provides the capability to handle semver version strings.


.. autoclass:: VersionExtension


.. py:function:: revpkg(lhs, separator1=".", separator2=".")

    Take a version, and reverse it in the most simplistic way not taking into
    account anything that would constitute "pre-release" or "build" information in the
    context of semver.

    Available as a function and a filter. For the latter case, *lhs* is automatically specified as the left hand side of the filter.

    .. code-block:: jinja

        # Returns 3.2.1
        {{ revpkg("1.2.3") }}

"""

from jinja2.ext import Extension


def _revpkg(lhs, separator1=".", separator2="."):
    lhss = lhs.split(separator1)
    lhss = reversed(lhss)
    return separator2.join(lhss)


# pylint: disable=abstract-method
class VersionExtension(Extension):
    """
    Jinja2 extension for version manipulation.
    """

    def __init__(self, environment):
        """
        Jinja2 Extension constructor.
        """
        super().__init__(environment)

        environment.filters["revpkg"] = _revpkg
        environment.globals.update(revpkg=_revpkg)
