#!/usr/local/bin/python3
from pathlib import Path
import argparse
import logging
import json


logger = logging.getLogger(__name__)

def parse_arguments():
    """
    Parses the command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, help="wheel inputfile")
    parser.add_argument("-o", "--output_file", required=True, help="wheel output file")
    parser.add_argument("--filename_version", required=True, help="version of the language file")
    args = parser.parse_args()
    return args



def main(*argv):
    
    args = parse_arguments(*argv)
    from wowool.native.core.language_info import Parser

    filename_version = args.filename_version[1:] if args.filename_version[0] == '@' else args.filename_version
    def add_namespace(name :str ):
        fn = Path(name)
        fn_version = Path(f"wowool/{fn.stem}@{filename_version}{fn.suffix}")
        return str(fn_version)

    language_parser = Parser(lambda name : add_namespace(name))
    with open(args.file) as ifh , open(args.output_file, "w") as ofh:
        json_in  = json.load(ifh)
        output_json  = language_parser(json_in)
        ofh.write( json.dumps(output_json, indent=2 ))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
