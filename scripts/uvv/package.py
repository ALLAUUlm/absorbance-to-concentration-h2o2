# This code has been adapted from that found in the CLI of svgdigitizer
# It should be replaced once unitpackage provides these functions.

import json
import os
import matplotlib.pyplot as plt

from datetime import date, datetime
from uvv.uvv_loader import Loader

from ruyaml import YAML

from frictionless import Package, Resource, Schema


def create_package(metadata, csvname, outdir, fields=None):
    r"""
    Return a data package built from a :param:`metadata` dict and tabular data
    in :param:`csvname`.

    This is a helper method for :meth:`_create_outfiles`.
    """
    package = Package(
        resources=[
            Resource(
                path=os.path.basename(csvname),
                basepath=outdir or os.path.dirname(csvname),
            )
        ],
    )
    package.infer()
    resource = package.resources[0]

    resource.custom.setdefault("metadata", {})
    resource.custom["metadata"].setdefault("echemdb", metadata)

    # Update fields in the datapackage describing the data in the CSV
    package_schema = resource.schema
    # print(resource.custom["metadata"]["echemdb"]["figure description"]["fields"])
    data_description_schema = Schema.from_descriptor(
        {
            "fields": fields
            or resource.custom["metadata"]["echemdb"]["figure description"]["fields"]
        }
    )

    new_fields = []
    for name in package_schema.field_names:
        if not name in data_description_schema.field_names:
            raise KeyError(
                f"Field with name {name} is not specified in `data_description.fields`."
            )
        new_fields.append(
            data_description_schema.get_field(name).to_dict()
            | package_schema.get_field(name).to_dict()
        )

    resource.schema = Schema.from_descriptor({"fields": new_fields})
    # del resource.custom["metadata"]["echemdb"]["data description"]["fields"]

    return package


def write_metadata(out, metadata):
    r"""
    Write `metadata` to the `out` stream in JSON format.

    This is a helper method for :meth:`_create_outfiles`.
    """

    def defaultconverter(item):
        r"""
        Return `item` that Python's json package does not know how to serialize
        in a format that Python's json package does know how to serialize.
        """

        # The YAML standard knows about dates and times, so we might see these
        # in the metadata. However, standard JSON does not know about these so
        # we need to serialize them as strings explicitly.
        if isinstance(item, (datetime, date)):
            return str(item)

        raise TypeError(f"Cannot serialize ${item} of type ${type(item)} to JSON.")

    json.dump(metadata, out, default=defaultconverter, ensure_ascii=False, indent=4)
    # json.dump does not save files with a newline, which compromises the tests
    # where the output files are compared to an expected json.
    out.write("\n")


def create_outfiles(csv_file, outdir='', yamlfile=None):

    if not os.path.exists(outdir):
        os.makedirs(outdir)


    from pathlib import Path

    csvfile = Path(csv_file)

    if not yamlfile:
        yamlfile = csvfile.with_suffix('.yaml')
    outcsv = outdir + csvfile.name
    outyaml = outdir + csvfile.name + '.meta.yaml'
    outpng = outdir + csvfile.stem + '.png'
    outjson = outdir + csvfile.name + '.meta.json'

    uvv = Loader(filename=csvfile)

    # write CSV
    uvv.df.to_csv(outcsv, index=False)

    # write PNG
    # define arguments in `plot_params` as dict
    # _ = uvv.df.plot(x='lambda', y='abs', xlabel='$\lambda$ / nm', ylabel='a.u.', label=csvfile.name).get_figure().savefig(outpng)
    #plt.close()

    # write YAML

    yaml = YAML()
    yamldata = yaml.load(open(yamlfile, 'rb'))
    # append uvv metadata
    for key in uvv.metadata.keys():
        yamldata[key] = uvv.metadata[key]

    def get_dilution_factor(metadata):
        extracted = yamldata['system']['sample extracted']['value']
        complexing = yamldata['system']['complexing agent']['added']['value']
        dilution = yamldata['system']['sample dilution']['added']['value']

        return (extracted + complexing + dilution)/extracted

#    yamldata['dilution factor'] = {'ratio': get_dilution_factor(yamldata),
#                                    'description': '(Sample extracted + Complexing agent +  sample dilution) / sample extracted.'}

    yaml.default_flow_style = False
    yaml.dump(yamldata, open(outyaml, 'w'))

    # create frictionless
    from uvv.package import write_metadata, create_package

    pack = create_package(yamldata, outcsv, outdir='')
    pack

    with open(outjson, 'w') as _json:
        write_metadata(_json, pack.to_dict())
