import json
import zipfile
from typing import List, Dict

########################################################################
# QMGeneric
# QMValue
########################################################################


class QMValue:
    """
    """

    def __init__(
        self,
        metrics_definition: Dict,
        value
    ):
        # Required
        self.key = metrics_definition['key']
        self.value = value
        # Optional
        self.visible = metrics_definition.get("visible", None)
        self.flag = metrics_definition.get("flag", None)
        self.derived_from = metrics_definition.get("derived_from", None)
        self.tooltip = metrics_definition.get("tooltip", None)

    def to_dict(self):
        return {k: v for (k, v) in self.__dict__.items() if v != None}


class QMGeneric:
    """
    """

    def __init__(self, name):
        self.name = name
        # List of QMValue objects
        self.qm_values = []

    def add_value(self, QMValue_: QMValue):
        self.qm_values.append(QMValue_)

    def add_values(self, QMValues: List[QMValue]):
        self.qm_values += QMValues

    def to_dict(self):
        return {
            #'category': self.name, # This requires a change in the data model
            'qc_values': [QMValue_.to_dict() for QMValue_ in self.qm_values]
        }

    def create_archive(self, filenames, archive_name):
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for filename in filenames:
                archive.write(filename)

    def write_json(self, filename, dict=None):
        if not dict:
            dict = self.to_dict()
        with open(filename, 'w') as fo:
            json.dump(dict, fo, sort_keys=True, indent=2)
