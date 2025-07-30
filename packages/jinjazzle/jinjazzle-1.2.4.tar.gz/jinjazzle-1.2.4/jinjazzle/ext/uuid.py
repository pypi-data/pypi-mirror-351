"""
Description
-----------

UUIDExtension provides the capability to generate UUID version 4 (UUID4) strings directly within your templates.


.. autoclass:: UUIDExtension


.. py:function:: uuid

    Return a UUID string.

    Available as a function.

    .. code-block:: jinja

        Generated UUID: {{ uuid() }}
"""

import uuid as m_uuid

from jinja2.ext import Extension


def _uuid():
    """
    Generate UUID4.
    """
    return str(m_uuid.uuid4())


# pylint: disable=abstract-method
class UUIDExtension(Extension):
    """
    Jinja2 extension to generate uuid4 string.
    """

    def __init__(self, environment):
        """
        Jinja2 Extension constructor.
        """
        super().__init__(environment)

        environment.globals.update(uuid=_uuid)
