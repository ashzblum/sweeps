"""Base SweepConfig classes."""

import yaml
from pathlib import Path

from typing import Union, Dict, List

import jsonschema
from .schema import validator


def schema_violations_from_proposed_config(config: Dict) -> List[str]:

    schema_violation_messages = []
    for error in validator.iter_errors(config):
        schema_violation_messages.append(f"{error.message}")

    # validate min/max - this cannot be done with jsonschema
    # because it does not support comparing values within
    # a json document. so we do it manually here:
    for parameter_name, parameter_dict in config["parameters"].items():
        if "min" in parameter_dict and "max" in parameter_dict:
            # this comparison is type safe because the jsonschema enforces type uniformity
            if parameter_dict["min"] >= parameter_dict["max"]:
                schema_violation_messages.append(
                    f'{parameter_name}: min {parameter_dict["min"]} is not '
                    f'less than max {parameter_dict["max"]}'
                )
    return schema_violation_messages


class SweepConfig(dict):
    def __init__(self, d: Dict):
        super(SweepConfig, self).__init__(d)

        if not isinstance(d, SweepConfig):
            # ensure the data conform to the schema
            schema_violation_messages = schema_violations_from_proposed_config(d)

            if len(schema_violation_messages) > 0:
                err_msg = "\n".join(schema_violation_messages)
                raise jsonschema.ValidationError(err_msg)

    def __str__(self) -> str:
        return yaml.safe_dump(self)

    def save(self, filename: Union[Path, str]) -> None:
        with open(filename, "w") as outfile:
            yaml.safe_dump(self, outfile, default_flow_style=False)
