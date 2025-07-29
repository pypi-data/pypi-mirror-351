#!/usr/local/bin/python3
from pathlib import Path
import argparse
import logging
import json
from typing import List

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
    from wowool.native.core.domain_info import Parser

    filename_version = args.filename_version[1:] if args.filename_version[0] == '@' else args.filename_version
    def add_namespace(dependencies :List[str] ) -> List[str]:
        retval = []
        for name in dependencies:
            fn = Path(name)
            fn_version = Path(f"wowool/{fn.stem}@{filename_version}{fn.suffix}")
            retval.append(str(fn_version))
            # print("-->>", fn_version)
        return retval

    domian_parser = Parser(lambda dependencies : add_namespace(dependencies))
    try:
        with open(args.file) as ifh , open(args.output_file, "w") as ofh:
            json_in  = json.load(ifh)
            output_json  = domian_parser(json_in)
            ofh.write( json.dumps(output_json, indent=2 ))
    except Exception as ex:
        logger.exception(ex)
        Path(args.output_file).unlink(missing_ok=True)

if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
