import logging

from unitpackage.entry import Entry

logger = logging.getLogger("unitpackage")


class UVVEntry(Entry):
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
        return f"UVVEntry({self.identifier!r})"

    def plot(self, x_label="lambda", y_label="abs", name=None):
        r"""
        Return a plot of this entry.
        The default plot is a Cyclic Voltammogram ('j vs E').
        When `j` is not present in the data, `I` is used instead.

        EXAMPLES::

            >>> entry = CVEntry.create_examples()[0]
            >>> entry.plot()
            Figure(...)

        The plot can also be returned with custom axis dimensions (field names) available in the resource::

            >>> entry.plot(x_label='t', y_label='E')
            Figure(...)

        A plot resembling the original figure can be obtained by first rescaling::

            >>> rescaled_entry = entry.rescale('original')
            >>> rescaled_entry.plot()
            Figure(...)

        """
        fig = super().plot(x_label='lambda', y_label='abs', name=self.identifier) #name=name or figure_name())
        return fig

    @property

    def dilution_factor(self):
        dilution_factor = 1
        for i, extraction in enumerate(self['extraction']):
            extracted = extraction['sample extracted']['value']
            dilution = extraction['sample dilution']['added']['value']
            if i == 0:
                complexing = extraction['complexing agent']['added']['value']
                dilution_factor *= (extracted + complexing + dilution) / extracted
            else:
                dilution_factor *= (extracted + dilution) / extracted
        return dilution_factor

    def get_absorbance(self,wl=420):
        df_wl = self.df[self.df["lambda"].between(wl - 0.5, wl + 0.5)]
        return {
            "wavelength": {
                "value": float(df_wl["lambda"].reset_index(drop=True)[0]),
                "unit": "nm",
            },
            "absorbance": {"value": float(df_wl["abs"].reset_index(drop=True)[0])},
        }
