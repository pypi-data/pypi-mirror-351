import argparse
import hashlib
import shutil
import json

from pathlib import Path
import urllib.request
from urllib.parse import urlparse, unquote

from .common import load_files


class FileData:
    def __init__(self, filename, url, manufacturer, filetype, revision, date, md5sum, path):
        self.filename = Path(filename if filename is not None else self.filename_from_url(url))
        self.url = url
        self.manufacturer = manufacturer
        self.filetype = filetype
        self.revision = revision
        self.date = date
        self.md5sum = md5sum
        self.path = path

    def set_destination_directory(self, destination_directory):
        manufacturer = self.manufacturer.replace(" ", "_").lower()
        file_name = f"{manufacturer}__{self.filename.stem}__{self.md5sum}"
        self.path = destination_directory.joinpath(manufacturer, file_name).with_suffix(self.filename.suffix)

    def exists(self):
        return self.path.exists() and self.path.is_file()

    def validate(self):
        return self.md5sum == calculate_md5(self.path)

    def download(self):
        local_filename, headers = urllib.request.urlretrieve(self.url)
        md5sum = calculate_md5(local_filename)
        if md5sum == self.md5sum:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(local_filename, self.path)

    def filename_from_url(self, url):
        return Path(unquote(urlparse(url).path).replace(' ', '_')).name



def main():
    parser = argparse.ArgumentParser(description="Part DB tools")
    parser.add_argument('-i', '--input', help="Path to the input file")
    parser.add_argument('-d', '--directory', help="Path to the input directory")
    parser.add_argument('-o', '--output', type=Path, required=True, help="Path to the output directory")
    parser.add_argument('-v', '--validate_only', action='store_true', help="Validate files")
    args = parser.parse_args()

    if args.input:
        input_files = [args.input]
    elif args.directory:
        input_files = load_files(args.directory)
    else:
        print("No input or directory specified")
        exit(-1)

    part_files = load_part_files(input_files)

    for f in part_files:
        f.set_destination_directory(args.output)
        if f.exists():
            print("file already exists, validating")
            if not f.validate():
                print("file validation failed")
        else:
            print(f"File missing: {f.path}")
            if not args.validate_only:
                print("Downloading")
                f.download()


def load_part_files(parts_files):
    files = []
    for part_file in parts_files:
        with open(part_file) as jsonfile:
            parts = json.load(jsonfile)
            for part in parts:
                for file_type in part["files"]:
                    file = part["files"][file_type]
                    if 'skip' in file["versions"] and file["versions"]["skip"] == True:
                        print("Skipping file, versions not supported")
                    else:
                        for version in file["versions"]:
                            file_data = FileData(
                                filename=file["filename"] if "filename" in file else None,
                                url=file["url"],
                                manufacturer=part["manufacturer"],
                                filetype=file_type,
                                revision=version,
                                date=file["versions"][version]["date"],
                                md5sum=file["versions"][version]["md5sum"],
                                path=None
                            )
                            files.append(file_data)
    return files


def calculate_md5(file):
    with open(file, "rb") as f:
        hash_md5 = hashlib.md5(f.read()).hexdigest()
        return hash_md5

def copy_and_rename_file(input_file: Path, output_dir: Path):
    manufacturer = input_file.stem.split("__")[0]
    file_name = input_file.stem.split("__")[1]
    md5_sum = calculate_md5(input_file)

    new_filename = f"{manufacturer}__{file_name}__{md5_sum}.{input_file.suffix}"
    new_file_path = output_dir.joinpath(new_filename)

    shutil.copyfile(input_file.resolve(), new_file_path.resolve())