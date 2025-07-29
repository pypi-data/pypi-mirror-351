import os
from pathlib import Path
import logging
import json
from invoke import UnexpectedExit
from wowool.build.utility import ask
from wowool.lingware.build.utilities import (
    get_filename_version,
    get_stage_lxware_folder,
    get_language,
)
from wowool.lingware.build.language.build import languages
from wowool.lingware.build.domain.build import domains


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def print_concept(a):
    attr = ""
    if a.attributes:
        attr = " @("
        cnt = 0
        for k, vs in sorted(a.attributes.items()):
            for v in sorted(vs):
                if cnt > 0:
                    attr += " "
                cnt += 1
                attr += f"{k}='{v}'"
        attr += ")"
    retval = "{uri}{attr}:{tokens}".format(uri=a.uri, tokens=a.literal, attr=attr)

    return retval


def print_morphdata(md):
    retval = f"[{md.stem}:{md.pos}]"
    if hasattr(md, "morphology"):
        for md in md.morphology:
            retval += print_morphdata(md)
    return retval


def print_token(a):
    retval = "\t" + a.literal
    if a.properties:
        retval += ","
        for prop in sorted(a.properties):
            retval += ",+" + prop

    if a.morphology:
        retval += ","
        for morphdata in a.morphology:
            retval += print_morphdata(morphdata)

    return retval


def get_concept_filter(config):
    if "annotations" in config:
        annotations = set(config["annotations"].split(","))
        return lambda c: c.uri in annotations
    else:
        return lambda c: c.uri != "Sentence"


def run_test_folder(c, folder: Path, verbose, diff, overwrite, pattern, integration=False):
    """
    General domain unit-tests
    """
    from shutil import which
    from wowool.annotation import Token, Concept
    from wowool.error import Error
    from wowool.native.core.engine import Engine
    from wowool.document import Document
    from wowool.lingware.build.utilities import get_language
    from wowool.native.core import Language, Domain

    from wowool.native.core.pipeline import Pipeline
    from wowool.lingware.build.utilities import get_stage_lxware_folder

    if not which(diff):
        diff = "diff -y"

    language = get_language(folder)

    TEST_DIR = Path(folder, "test")

    engine = Engine(lxware=get_stage_lxware_folder(folder))
    logger.info(f"TEST_DIR:{TEST_DIR}")
    print(f"Info: Starting {language=} using {engine.lxware=}, {integration=}")

    default_domains = []
    default_analyzer = None
    try:
        default_analyzer = Language(language, anaphora="false", engine=engine)
    except Error as exception:
        print(f"Warning: Cannot create default language {language} {exception}")
    try:
        default_domains = [Domain(f"{language}-entity", engine=engine)]
    except Error as exception:
        print(f"Warning: Cannot create default domain {language}-entity {exception}")

    with c.cd(str(TEST_DIR)):
        fns = TEST_DIR.glob(pattern)
        for fn in sorted(fns):
            file_size = fn.stat().st_size
            logger.info(f"TEST: '{fn}'")

            if file_size > (1024 * 26):
                logger.warning(f"ACHTUNG !!!: The file '{fn}' ({round(file_size/1024)}K) is to big for it's own safety")
            ofn = Path(fn.parent, fn.parent, "options.json")
            erfn = str(Path(fn.parent, str(Path(fn.stem)) + ".expected_results"))
            rfn = str(Path(fn.parent, str(Path(fn.stem)) + ".results"))
            json_options = {}
            if ofn.exists():
                with open(ofn, "r") as of:
                    json_options = json.loads(of.read())

            if "type" in json_options and json_options["type"] == "integration":
                if not integration:
                    logger.warning(f"!!! Skipping: {fn} has been disabled, please fix it, and enable it in the options file {ofn}")
                    continue

            if "disable" in json_options and json_options["disable"] == True:
                logger.warning(f"!!! ACHTUNG: {fn} has been disabled, please fix it, and enable it in the options file {ofn}")
                continue

            pipeline = Pipeline()
            if "pipeline" in json_options:
                pipeline = Pipeline(json_options["pipeline"])
            else:
                if "analyzer" in json_options:
                    raise DeprecationWarning("use the pipeline options instead.")
                elif "language" in json_options:
                    try:
                        pipeline.components.append(Language(json_options["language"], engine=engine))
                    except RuntimeError as ex:
                        print("No language found")
                        continue
                else:
                    pipeline.components.append(default_analyzer)

                if "domains" in json_options:
                    try:
                        for domain_name in json_options["domains"]:
                            pipeline.components.append(Domain(domain_name, engine=engine))
                    except RuntimeError as ex:
                        print(f"Skipping: {ex}")
                        continue
                else:
                    pipeline.components.extend(default_domains)

            try:
                filter = json_options["unit-tests"]["filter"]
                if filter == ["Token"]:
                    domains = []
            except:
                filter = "Concept"

            with open(fn) as jf:
                data = jf.read()
            document = pipeline(Document(data))
            assert document.analysis

            results = ""

            from operator import attrgetter

            if filter == "Concept":
                concept_filter = get_concept_filter(json_options)

                for sent in document.analysis:
                    results += "-" * 5 + "\n"
                    results += "Sentence:" + sent.text + "\n"
                    filtered_concept_list = [a for a in Concept.iter(sent, concept_filter)]
                    for a in sorted(
                        filtered_concept_list,
                        key=attrgetter("begin_offset", "end_offset", "uri"),
                    ):
                        results += print_concept(a)
                        results += "\n"
            else:
                for sent in document.analysis:
                    results += "-" * 5 + "\n"
                    results += "Sentence:" + sent.text + "\n"
                    for a in Token.iter(sent):
                        results += print_token(a)
                        results += "\n"

            if not os.path.exists(erfn) or overwrite:
                with open(erfn, "w") as erf:
                    erf.write(results)
            else:
                with open(erfn, "r") as erf:
                    expectd_results = erf.read()

                if results != expectd_results:
                    console_diff_cmd = f"diff {erfn} {rfn}"
                    print(f"ERROR: has {console_diff_cmd}")
                    with open(rfn, "w") as rf:
                        rf.write(results)

                    try:
                        import subprocess

                        diff_result = subprocess.run(console_diff_cmd, shell=True, stdout=subprocess.PIPE).stdout.decode("utf8")
                        print(f"Partial Diff result:\n{diff_result[:500]}")
                    except OSError as ex:  # Command not found
                        print(ex)

                    if diff != "none":
                        try:
                            c.run("{} {} {}".format(diff, erfn, rfn))
                        except UnexpectedExit as ex:
                            exit(-1)
                    if ask("Do you want to overwrite the results ? ", False):
                        with open(erfn, "w") as erf:
                            erf.write(results)
                else:
                    if os.path.exists(rfn):
                        os.remove(rfn)
                    with open(rfn, "w") as rf:
                        rf.write(results)
            if verbose:
                print(results)


def test_example(folder: Path, domain_folder: Path, lxware: Path, engine):
    from wowool.native.core import Pipeline
    from wowool.native.core import Engine
    from wowool.annotation import Concept
    from wowool.lingware.build.git import get_version

    version = get_version(folder)
    package_version = get_filename_version(version)

    language = get_language(folder)

    pipelines = []
    domain_name = domain_folder.stem
    name = f"wowool/{language},wowool/{language}-{domain_name}"
    logger.info(f"Examples: {name}")
    pipelines.append(Pipeline(name, engine=engine))
    # pipelines.append(Pipeline(f"{language},{domain_name}", engine=engine))

    domain = pipelines[0].domains[0]
    rdi = domain.info["dom"]
    assert "dom_filename" in rdi, "Missing domain filename."
    expected_fn = f"{lxware}/wowool/{language}-{domain_folder.name}@{package_version}.dom"
    assert rdi["dom_filename"] == expected_fn, f"""wrong filename in stage folder. '{rdi["dom_filename"]}' != '{expected_fn}' """

    assert "dom_info_filename" in rdi, "Missing domain info filename."
    expected_fn = f"{lxware}/wowool/{language}-{domain_folder.name}@{package_version}.dom_info"
    assert (
        rdi["dom_info_filename"] == expected_fn
    ), f"""wrong dom_info filename in stage folder. '{rdi["dom_info_filename"]}' != '{expected_fn}' """

    di = domain.info["dom_info"]
    assert "examples" in di, f"missing examples in {language}-{domain_name}"
    examples = di["examples"]

    if "concepts" not in di:
        logger.error(f"""    !!! ACHTUNG, Missing keyword 'concepts' in : {name}""")
        di_concepts = domain.concepts

        logger.warning(f"""using concepts from : {language}-{domain_name} concepts={di_concepts}""")
    else:
        dom_concepts = domain.concepts
        di_concepts = di["concepts"]
        for di_concept in di_concepts:
            if di_concept not in dom_concepts:
                logger.warning(f"""Concept '{di_concept}' will never produced by this dom file file.""")

    exclude = ["PersonFam", "PersonGiv"]
    for example in examples:
        if "concept" not in example:
            logger.error(f"""    !!! ACHTUNG, Missing 'concept'!!! : '{example}''""")
            exit(-1)

        concept = example["concept"]
        if concept in exclude:
            logger.debug(f"""    !!! Skipping example: {concept}""")
            continue

        if di_concepts and concept not in di_concepts:
            logger.error(f"""    !!! ACHTUNG, Missing concept({concept}) {di_concepts} sample! in : {name}""")

        if "desc" not in example:
            logger.warning(f"""    !!! ACHTUNG, Missing 'desc' !!! : '{example}''""")

        for pipeline in pipelines:
            logger.info(f"""Example: {domain_name}:{example["sample"]}""")
            sample = example["sample"]

            doc = pipeline(sample)
            logger.debug(f"""Concepts: {domain_name}:{[f"{c.uri}={c.literal}" for c in doc.analysis.concepts()]}""")
            concepts = [c for c in Concept.iter(doc, lambda c: c.uri == example["concept"])]
            if len(concepts) == 0:
                raise RuntimeError(
                    f"Could not find Concept in examples from '{domain_name}'\npipeline:{name}\n sample:'{sample}' does not return '{concept}'\n{doc=}\n try: wow -p {name} -i '{sample}'"
                )
            doc = None


def test_load_domains(folder: Path):
    lxware = get_stage_lxware_folder(folder)
    test_examples(folder, lxware)


def test_examples(folder: Path, lxware: Path):
    from wowool.native.core import Engine

    logger.info(f"Testing domains in {lxware=}")
    engine = Engine(lxware=lxware)

    for domain_folder in domains(folder):
        logger.info(f"Testing domains in {domain_folder=}")
        test_example(folder, domain_folder, lxware, engine)


def test_single_package_wheel(folder: Path):
    from shutil import rmtree, copytree
    from subprocess import run

    language = get_language(folder)
    install_python_root = folder / "_pypackage"
    install_tmp = folder / "_pypackage_tmp"

    rmtree(install_python_root, ignore_errors=True)
    rmtree(install_tmp, ignore_errors=True)
    install_python_root.mkdir()
    install_python_root_eot = install_python_root / "wowool"
    install_tmp.mkdir()
    # from logging import DEBUG

    # logger.setLevel(DEBUG)

    language = get_language(folder)
    print(f"Testing single package wheel for {language} domains and languages ...")
    output_folder = folder / "_build_package"
    lxware = output_folder / "src/wowool/lxware"

    _dist_folder = output_folder / "dist"
    fn_wheels = [fn for fn in _dist_folder.glob("*.whl")]
    assert len(fn_wheels) == 1, f"Missing {language} package in {_dist_folder}"
    install_tmp = folder / "_pypackage_tmp"
    fn_wheel = fn_wheels[0]
    cmd = f"pip install --no-deps {fn_wheel} --upgrade --target {install_tmp}"
    logger.debug(f"{cmd=}")
    run(cmd, check=True, shell=True, capture_output=True)
    copytree(install_tmp / "wowool", install_python_root_eot, dirs_exist_ok=True)

    lxware = Path(f"{install_python_root}/wowool/lxware")
    if lxware.exists():
        test_examples(folder, lxware=lxware)

    rmtree(install_python_root, ignore_errors=True)
    rmtree(install_tmp, ignore_errors=True)


def test_wheels(folder: Path):
    from shutil import rmtree, copytree
    from subprocess import run

    language = get_language(folder)
    install_python_root = folder / "_pypackage"
    install_tmp = folder / "_pypackage_tmp"
    rmtree(install_python_root, ignore_errors=True)
    rmtree(install_tmp, ignore_errors=True)
    install_python_root.mkdir()
    install_python_root_eot = install_python_root / "wowool"
    install_tmp.mkdir()
    from logging import DEBUG

    logger.setLevel(DEBUG)
    logger.info(f"Installing wheels for {language} domains and languages ...")
    for _folder in languages(folder):
        _name = _folder.stem
        _dist_folder = _folder / "dist"

        fn_wheels = [fn for fn in _dist_folder.glob("*.whl")]
        assert len(fn_wheels) == 1, f"Missing {_name} in {_dist_folder}"
        fn_wheel = fn_wheels[0]
        cmd = f"pip install --no-deps {fn_wheel} --upgrade --target {install_tmp}"
        logger.debug(f"{cmd=}")
        run(cmd, check=True, shell=True, capture_output=True)
        copytree(install_tmp / "wowool", install_python_root_eot, dirs_exist_ok=True)

    for domain_folder in domains(folder):
        domain_name = domain_folder.stem
        _name = f"{language}-{domain_name}"
        dist_folder = domain_folder / "dist"

        fn_wheels = [fn for fn in dist_folder.glob("*.whl")]
        assert len(fn_wheels) == 1, f"Missing {_name} packages to install, run: inv package"
        fn_wheel = fn_wheels[0]
        rmtree(install_tmp, ignore_errors=True)
        install_tmp.mkdir()

        cmd = f"pip install --no-deps {fn_wheel} --upgrade --target {install_tmp}"
        logger.debug(f"{cmd=}")
        results = run(cmd, check=True, shell=True, capture_output=True)
        for fn in install_tmp.glob("**/*.dom"):
            print(f" - {fn}")
        copytree(install_tmp / "wowool", install_python_root_eot, dirs_exist_ok=True)
        for fn in install_python_root.glob("**/*.dom"):
            print(f" - {fn}")

    lxware = Path(f"{install_python_root}/wowool/lxware")
    logger.info(f" lxware location: {lxware=}")
    for fn in lxware.glob("**/*.dom"):
        logger.info(f" - {fn}")
    test_examples(folder, lxware=lxware)

    rmtree(install_python_root, ignore_errors=True)
    rmtree(install_tmp, ignore_errors=True)


def test_domains(folder: Path):
    test_load_domains(folder)
    test_single_package_wheel(folder)
    # test_wheels(folder)


def test_lid(folder: Path):
    from wowool.native.core import LanguageIdentifier

    lid = LanguageIdentifier()
    for fn in folder.glob("test/*.txt"):
        text = fn.read_text()
        doc = lid(text)
        language = doc.results(LanguageIdentifier.ID)["language"]
        expected_language = fn.stem.split("-")[0]

        logger.info(f"Lid on {fn} => {language}")
        assert language == expected_language, f"Invalid language identification in {fn} result is {language=} != {expected_language=}"
