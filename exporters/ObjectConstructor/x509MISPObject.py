#!/usr/bin/env python3

import time

from pymisp.tools.abstractgenerator import AbstractMISPObjectGenerator


class x509MISPObject(AbstractMISPObjectGenerator):
    def __init__(self, dico_val, **kargs):
        self._dico_val = dico_val

        #  Enforce attribute date with timestamp
        super(x509MISPObject, self).__init__('x509', default_attributes_parameters={'timestamp': int(time.time())}, **kargs)
        self.name = "x509"
        self.generate_attributes()

    def generate_attributes(self):
        valid_object_attributes = self._definition['attributes'].keys()
        for object_relation, value in self._dico_val.items():
            if object_relation not in valid_object_attributes:
                continue

            if object_relation == 'timestamp':
                # Date already in ISO format, removing trailing Z
                value = value.rstrip('Z')

            if isinstance(value, dict):
                self.add_attribute(object_relation, **value)
            else:
                # uniformize value, sometimes empty array
                if len(value) == 0:
                    value = ''
                self.add_attribute(object_relation, value=value)