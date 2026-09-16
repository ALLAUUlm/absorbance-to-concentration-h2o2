import logging

from unitpackage.collection import Collection

logger = logging.getLogger("unitpackage")


class UVVBatchCollection(Collection):
    r"""
    A collection of `frictionless data packages <https://github.com/frictionlessdata/framework>`__.

    Essentially this is just a list of data packages with some additional
    convenience wrap for use in the `echemdb <https://www.echemdb.org/cv>`_.

    EXAMPLES:

    An empty collection::

        >>> collection = UVVCollection([])
        >>> len(collection)
        0

    """
    from uvv.uvv_batchentry import UVVBatchEntry

    Entry = UVVBatchEntry