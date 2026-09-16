import logging

from unitpackage.entry import Entry

logger = logging.getLogger("unitpackage")


class UVVBatchEntry(Entry):
    r"""
    A `frictionless data packages <https://github.com/frictionlessdata/framework>`_
    describing a UVVis spectrum.

    EXAMPLES:

    An entry can be created directly from a datapackage that has been created
    with `svgdigitizer's <https://echemdb.github.io/svgdigitizer/>`_ `cv` command.
    However, entries are normally obtained by opening a :class:`CVCollection` of entries::

        >>> from unitpackage.cv.cv_collection import CVCollection
        >>> collection = CVCollection.create_example()
        >>> entry = next(iter(collection))

    """

    def __repr__(self):
        r"""
        Return a printable representation of this entry.

        EXAMPLES::

            >>> entry = UVVEntry.create_examples()[0]
            >>> entry
            UVVEntry('alves_2011_electrochemistry_6010_f1a_solid')

        """
        return f"UVVBatchEntry({self.identifier!r})"
    @property
    def baseline(self):
        if self.df.time.iloc[0] != 0.0:
            baseline_value = 0
            print('Baseline value was not recorded at time = 0.0')
        else:
            baseline_value = self.df[self.df.time == 0.0]['c(H2O2)'].values[0]
            if baseline_value < 0:
                baseline_value = 0
                self.df.loc[self.df.time == 0.0, 'c(H2O2)_baseline'] = 0 #this does not have any effect on the dataframe
                print('Baseline value was recorded as negative and is thus set to zero')
        return baseline_value