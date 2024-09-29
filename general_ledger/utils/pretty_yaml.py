import uuid
from collections import OrderedDict

import yaml
from import_export.formats.base_formats import YAML


class PrettyYAML(YAML):
    def export_data(self, dataset, **kwargs):
        """
        Export data from the dataset instance to a YAML string.
        """
        print(dataset.dict)
        yaml.add_representer(
            OrderedDict,
            lambda dumper, data: dumper.represent_mapping(
                "tag:yaml.org,2002:map", data.items()
            ),
        )
        # output = yaml.dump(my_object)
        yaml.add_representer(
            tuple,
            lambda dumper, data: dumper.represent_sequence(
                "tag:yaml.org,2002:seq", data
            ),
        )
        yaml.add_representer(
            uuid.UUID,
            lambda dumper, data: dumper.represent_scalar(
                "tag:yaml.org,2002:str",
                str(data),
            ),
        )
        stream = yaml.dump(
            dataset.dict,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            encoding="utf-8",
        )
        return stream

    def get_title(self):
        return "pretty yaml"
