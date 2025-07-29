import argparse
import json
from pathlib import Path
from .common import load_files


def main():
    parser = argparse.ArgumentParser(description='Part Database Tools')
    parser.add_argument('-f', '--file', type=Path, help='Path to the input file')
    parser.add_argument('-d', '--directory', type=Path, help='Path to the input directory')
    args = parser.parse_args()

    if args.file:
        if args.file.is_file():
            files = [args.file]
        else:
            print('Input file must be a file')
            return -1
    elif args.directory:
        files = load_files(args.directory.resolve())
    else:
        print('Missing parameter. Input file or directory must be specified')
        return -1

    for f in files:
        cleanup_and_sort_json_files(f)
    return 0


def cleanup_json_data(data):
    if isinstance(data, dict):
        return {k: cleanup_json_data(v) for k, v in data.items() if v != ""}
    elif isinstance(data, list):
        return [cleanup_json_data(e) for e in data]
    else:
        return data


def cleanup_and_sort_json_files(f):
    try:
        with open(str(f)) as jsonfile:
            content = json.load(jsonfile)
            cleanup_json = cleanup_json_data(content)
            sorted_json = sorted(cleanup_json, key=lambda x: x['manufacturer'] + x['partNumber'])
            fixed_content = json.dumps(sorted_json, indent='\t')
            jsonfile.close()
            if content != fixed_content:
                with open(str(f), 'w') as jsonfile:
                    jsonfile.write(fixed_content)
    except ValueError as e:
        print(f"Invalid JSON file {f}: {e}")
