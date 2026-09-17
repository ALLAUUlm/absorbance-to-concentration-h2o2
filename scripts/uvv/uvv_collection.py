import logging

from unitpackage.collection import Collection
from unitpackage.entry import Entry
import pandas as pd
import shutil
import os

logger = logging.getLogger("unitpackage")


class UVVCollection(Collection):
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
    from uvv.uvv_entry import UVVEntry

    Entry = UVVEntry

    @property
    def batches(self):
        r"""
            Returns the batches in this collection
        """        
        import pandas as pd
        batches_ = [entry.system.batch for entry in self]
        batches = list(pd.unique(pd.Series(batches_)))
        return batches

    def filter_batches(self, material, wavelength, loading, sonication):
        r"""
            Returns the batches in this collection
        """ 
        mat_col = self.filter(lambda entry: entry.system.material.name == material)
        wavmat_col = mat_col.filter(lambda entry: entry.system.wavelength.value == wavelength)
        loading_col = wavmat_col.filter(lambda entry: entry.system.Loading.value == loading)
        sonication_col = loading_col.filter(lambda entry: entry.system.sonication.time.value == sonication) #TODO change "Loading" to "loading"
        return sonication_col
    
    def remove_repeated(self):
        # Collect all identifiers from entries in self
        identifiers = [entry.identifier for entry in self]

        new_identifiers = []
        for identifier in identifiers:
            uniques = []
            # Find all identifiers that contain the current identifier as a substring
            for identifier_ in identifiers:
                if identifier in identifier_:
                    uniques.append(identifier_)
            # If there are multiple matches, select the one with the longest extraction
            if len(uniques) > 1:
                extractions = {'identifier': '', 'len': 0}
                for unique in uniques:
                    len_extraction = len(self[unique].extraction)
                    if len_extraction > extractions['len']:
                        extractions = {'identifier': unique, 'len': len_extraction}
                # Add the identifier with the longest extraction to the result
                new_identifiers.append(extractions['identifier'])
            else:
                # If only one match, add it directly
                new_identifiers.append(uniques[0])

        # Filter self to only include entries with unique identifiers
        # Uses pandas to get unique values from new_identifiers
        return self.filter(lambda entry: entry.identifier in list(pd.unique(pd.Series(new_identifiers))))

    def process_and_save_batches(self, outdir):
        filtered_collections = {}

        for batch in self.batches:
            filtered_col = self.filter(lambda entry: entry.system.batch == batch)
            filtered_collections[batch] = filtered_col
            print(f"Batch: {batch}, Number of entries: {len(filtered_col)}")

        for batch, filtered_col in filtered_collections.items():
            data = {'identifier': [], 'time': [], 'abs420': [], 'dilutionfactor': [], 'exc_wavelength': [], 'loading': [], 'material_name': [], 'synthesis_date_of_material': [], 'sonication': [], 'purging': [], 'purging gas': [], 'phase': []}

            for entry in filtered_col:
                print(entry.identifier)
                data['abs420'].append(entry.get_absorbance(wl=420)["absorbance"]["value"])
                data['identifier'].append(entry.identifier)
                data['time'].append(entry.irradiation.time.value)
                data['dilutionfactor'].append(entry.dilution_factor)
                data['exc_wavelength'].append(entry.system.wavelength.value)
                data['loading'].append(entry.system.Loading.value)
                data['material_name'].append(entry.system.material.name)
                data['synthesis_date_of_material'].append(entry.system.material.synthesis_date)
                data['sonication'].append(entry.system.sonication.time.value)
                data['purging'].append(entry.system.purging.time.value)
                data['purging gas'].append(entry.system.purging.gas)
                if entry.extraction[0].sample_extracted and hasattr(entry.extraction[0].sample_extracted, 'phase'):
                    data['phase'].append(entry.extraction[0].sample_extracted.phase)
                else:
                    data['phase'].append('unknown')

            df = pd.DataFrame(data)
            df['c(H2O2)'] = df['abs420'] / 0.61 * df['dilutionfactor']

            fields = [{'name': 'loading', 'unit': 'g L-1'}, {'name': 'c(H2O2)', 'unit': 'mmol L-1'}, {'name': 'time', 'unit': 'h'}, {'name': 'exc_wavelength', 'unit': 'nm'}]

            new_entry = Entry.from_df(df=df, basename=batch.lower(), fields=fields)
            print(new_entry)
            if entry.extraction and len(entry.system.phases) > 1 and hasattr(entry.extraction[0].sample_extracted, 'phase'):
                phase = 'multiphase'
            elif entry.extraction and len(entry.system.phases) == 1 and hasattr(entry.extraction[0].sample_extracted, 'phase'):
                phase = 'monophasic'
            else:
                phase = 'unknown'
            new_entry.save(outdir=f"{outdir}/{phase}")

    def create_collections(uvcoll,uvcoll_repeated):
        repeated_measurements = [entry for entry in uvcoll_repeated if entry.identifier not in [e.identifier for e in uvcoll]]
        print("The following measurements were repeated again after this measurement:", repeated_measurements)

        split_identifiers = [entry.identifier.split("'")[0] for entry in repeated_measurements]
        print("Split identifiers:", split_identifiers)
        new_files = [f"data/processed/{identifier}.{ext}" for identifier in split_identifiers for ext in ["csv", "csv.meta.json", "csv.meta.yaml"]]
        print("New files:", len(new_files))

        destination_folder = "data/evaluation/repeated_measurements/"
        for file in new_files:
            if not os.path.exists(os.path.join(destination_folder, os.path.basename(file))):
                shutil.move(file, destination_folder)
                print(f"Moved {file} to {destination_folder}")
            else:
                print(f"File {file} already exists in {destination_folder}, skipping.")
        repeated_collection = uvcoll.from_local(destination_folder)
        return repeated_collection
    
    def get_filter_criteria(self):
        materials = list(set([entry.system.material.name for entry in self]))
        wavelengths = list(set([entry.system.wavelength.value for entry in self]))
        loadings = list(set([entry.system.Loading.value for entry in self]))
        sonications = list(set([entry.system.sonication.time.value for entry in self]))
        phases = list(set([entry.extraction[0].sample_extracted.phase for entry in self]))
        return {
            'materials': materials,
            'wavelengths': wavelengths,
            'loadings': loadings,
            'sonications': sonications,
            'phases': phases
        }
    
    def make_nice_bar_plots(self):
        from itertools import product
        import matplotlib.pyplot as plt

        def extract_filter_criteria(self):
            materials = list(set([entry.system.material.name for entry in self]))
            wavelengths = list(set([entry.system.wavelength.value for entry in self]))
            loadings = list(set([str(entry.system.Loading.value).replace('.', '-') for entry in self]))
            sonications = list(set([entry.system.sonication.time.value for entry in self]))
            sonications = [0 if sonication is None else sonication for sonication in sonications]
            phases = list(set([entry.extraction[0].sample_extracted.phase for entry in self]))
            date = list(set([entry.system.material.synthesis_date for entry in self]))
            return materials, wavelengths, loadings, sonications, phases, date

        materials, wavelengths, loadings, sonications, phases, date = extract_filter_criteria(self)
        print("Materials:", materials)
        print("Wavelengths:", wavelengths)
        print("Loadings:", loadings)
        print("Sonications:", sonications)
        print("Phases:", phases)
        print("Dates:", date)

        # Generate all possible combinations of materials, wavelengths, and loadings
        combinations = list(product(materials, wavelengths, loadings, sonications, phases, date))

        # Create a set of unique filenames
        filenames_set = {
            f"{material}_{wavelength}nm_{loading}_g_L_{sonication}min_{phase}_{date}.csv"
            for material, wavelength, loading, sonication, phase, date in combinations
        }
        print(filenames_set)
    
        # Read the CSV files for each combination and exclude files that do not exist
        filenames_dict = {}
        for filename in filenames_set:
            filepath = f'../data/old_evaluation/material_excwavelength_loading_sonication/{filename}'
            if os.path.exists(filepath):
                filenames_dict[filename] = filepath
            else:
                print(f"File not found: {filename}")

        print(filenames_dict)
        for filename, filepath in filenames_dict.items():
            df = pd.read_csv(filepath)
            df_filtered = df[df['times'].isin([1, 2, 3, 4, 6])]
            fig, ax = plt.subplots()
            ax.bar([str(time) for time in df_filtered['times']], df_filtered['average_c'], yerr=df_filtered['95% confidence interval'], align='center', alpha=1.0, ecolor='black', capsize=10, color='red')
            ax.set_ylabel('average c(H$_2$O$_2$) / mmol L$^{-1}$')
            ax.set_xticks([str(time) for time in df_filtered['times']])
            ax.set_xticklabels(df_filtered['times'])
            ax.set_xlabel('time / h')
            ax.set_title(f'{filename.replace(".csv", "")}')
            plt.tight_layout()
            plt.savefig(f'../data/old_evaluation/material_excwavelength_loading_sonication/{filename.replace(".csv", "")}.png')
            plt.show()

    def make_nice_bar_plots_ignore_synthesis_date(self):
        from itertools import product
        import matplotlib.pyplot as plt

        def extract_filter_criteria(self):
            materials = list(set([entry.system.material.name for entry in self]))
            wavelengths = list(set([entry.system.wavelength.value for entry in self]))
            loadings = list(set([str(entry.system.Loading.value).replace('.', '-') for entry in self]))
            sonications = list(set([entry.system.sonication.time.value for entry in self]))
            sonications = [0 if sonication is None else sonication for sonication in sonications]
            phases = list(set([entry.extraction[0].sample_extracted.phase for entry in self]))
            return materials, wavelengths, loadings, sonications, phases

        materials, wavelengths, loadings, sonications, phases = extract_filter_criteria(self)
        print("Materials:", materials)
        print("Wavelengths:", wavelengths)
        print("Loadings:", loadings)
        print("Sonications:", sonications)
        print("Phases:", phases)

        # Generate all possible combinations of materials, wavelengths, and loadings
        combinations = list(product(materials, wavelengths, loadings, sonications, phases))

        # Create a set of unique filenames
        filenames_set = {
            f"{material}_{wavelength}nm_{loading}_g_L_{sonication}min_{phase}.csv"
            for material, wavelength, loading, sonication, phase in combinations
        }
        print(filenames_set)

        # Read the CSV files for each combination and exclude files that do not exist
        filenames_dict = {}
        for filename in filenames_set:
            filepath = f'../data/old_evaluation/material_excwavelength_loading_sonication/ignore_synthesis_date/{filename}'
            if os.path.exists(filepath):
                filenames_dict[filename] = filepath
            else:
                print(f"File not found: {filename}")

        print(filenames_dict)
        for filename, filepath in filenames_dict.items():
            df = pd.read_csv(filepath)
            df_filtered = df[df['times'].isin([1, 2, 3, 4, 6])]
            fig, ax = plt.subplots()
            ax.bar([str(time) for time in df_filtered['times']], df_filtered['average_c'], yerr=df_filtered['95% confidence interval'], align='center', alpha=1.0, ecolor='black', capsize=10, color='red')
            ax.set_ylabel('average c(H$_2$O$_2$) / mmol L$^{-1}$')
            ax.set_xticks([str(time) for time in df_filtered['times']])
            ax.set_xticklabels(df_filtered['times'])
            ax.set_xlabel('time / h')
            ax.set_title(f'{filename.replace(".csv", "")}')
            plt.tight_layout()
            plt.savefig(f'../data/old_evaluation/material_excwavelength_loading_sonication/ignore_synthesis_date/{filename.replace(".csv", "")}.png')
            plt.show()