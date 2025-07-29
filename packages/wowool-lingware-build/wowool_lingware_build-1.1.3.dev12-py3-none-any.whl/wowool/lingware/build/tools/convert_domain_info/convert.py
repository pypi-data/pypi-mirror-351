#!/usr/local/bin/python3
from pathlib import Path
import json
from typing import List
from logging import getLogger

logger = getLogger(__name__)

def convert(file, output_file, filename_version):
    from wowool.native.core.domain_info import Parser

    filename_version = filename_version[1:] if filename_version[0] == "@" else filename_version

    def add_namespace(dependencies: List[str]) -> List[str]:
        retval = []
        for name in dependencies:
            fn = Path(name)
            fn_version = Path(f"wowool/{fn.stem}@{filename_version}{fn.suffix}")
            retval.append(str(fn_version))
            # print("-->>", fn_version)
        return retval

    domian_parser = Parser(lambda dependencies: add_namespace(dependencies))
    try:
        with open(file) as ifh, open(output_file, "w") as ofh:
            json_in = json.load(ifh)
            output_json = domian_parser(json_in)
            ofh.write(json.dumps(output_json, indent=2))
    except Exception as ex:
        logger.exception(ex)
        Path(output_file).unlink(missing_ok=True)
