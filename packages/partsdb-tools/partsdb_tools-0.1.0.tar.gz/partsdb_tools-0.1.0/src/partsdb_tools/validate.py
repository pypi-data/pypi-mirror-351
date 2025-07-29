import argparse
import json

from pathlib import Path
from .common import load_manufacturers
from .common import load_files, load_part_types, load_msl_classification
from .validators.orderNumberValidator import validate_order_number_fields

msl_classification = load_msl_classification()

def main():
    parser = argparse.ArgumentParser(description='Validate the parts database')
    parser.add_argument('-m', '--manufacturers', type=Path, required=True, help="Manufacturers definition file")
    parser.add_argument('-i', '--input', type=Path, help="Input file")
    parser.add_argument('-d', '--directory', type=Path, help="Input directory")
    args = parser.parse_args()

    manufacturers = load_manufacturers(args.manufacturers)
    part_types, parameters = load_part_types()
    if args.input:
        files = [args.input]
    elif args.directory:
        files = load_files(args.directory)

    json_files = []
    for f in files:
        with open(str(f)) as jsonfile:
            json_files.append({'file': f, 'data': json.load(jsonfile)})

    for f in json_files:
        parts = f['data']
        for part in parts:
            if not validate_generic_required_fields(part):
                print("missing required field")

            if not validate_manufacturer(part, manufacturers):
                print("invalid manufacturer", part["manufacturer"])

            if not validate_part_type(part, part_types):
                print("invalid part type", part["partType"])

            if not validate_field_storage_condition(part):
                print("invalid field storage condition", part["storageConditions"])

            if not test_validate_files_field(part):
                print("invalid file field", part["files"])

            if not validate_order_number_fields(part):
                print("invalid order number field", part["order_number"])


def validate_generic_required_fields(part):
    required_fields = ["manufacturer", "partNumber", "partType"]
    for required_field in required_fields:
        if required_field not in part:
            return False
    return True


def validate_manufacturer(part, manufacturer):
    if part['manufacturer'] in  manufacturer:
        return True
    return False


def validate_part_type(part, part_types):
    if part['partType'] in part_types:
        return True
    return False

def validate_field_storage_condition(part):
    if 'storageConditions' in part:
        if 'MSLevel' not in part['storageConditions']:
            print(f"Missing MSLevel field in part {part['manufacturer']} {part['partNumber']}")
            return False
        if part['storageConditions']['MSLevel'] not in msl_classification:
            return False
    return True

def test_validate_files_field(part):
    if 'files' in part:
        if not isinstance(part['files'], dict):
            return False
        for attachment in part['files']:
            if 'url' not in part['files'][attachment]:
                return False
            # check if only allowed keys are present in file dict
            for key in part['files'][attachment]:
                if key not in ["filename", "url", "description", "versions"]:
                    print("Key not allowed", key)
                    return False
    return True
