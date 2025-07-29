from subprocess import run
from pathlib import Path
import os
import shutil
import logging
from wowool.lingware.build.git import get_version
import json

from wowool.lingware.build.utilities import (
    resolve_template,
    PREFIX_DO_NOT_EDIT,
    eot_namespace,
    wowool_module,
    get_filename_version,
    get_stage_lxware_folder,
    update_file,
    get_lxcommon,
    get_language,
    set_build_tools_environment,
)

import re

logger = logging.getLogger(__name__)
WOWOOL_NROF_THREADS: int = int(os.environ.get("WOWOOL_NROF_THREADS", "8"))
thread_option = f" -j {WOWOOL_NROF_THREADS} " if WOWOOL_NROF_THREADS > 0 else " "


lxcommon_pattern = re.compile("""\\${LXCOMMON}/([a-zA-Z_0-9\\-/\\.]+)""", re.MULTILINE)


def collect_makefile_lxcommon_files(mf_fn):
    files = set()
    with open(mf_fn) as fh:
        mf_data = fh.read()

    for fn in lxcommon_pattern.findall(mf_data):
        files.add(fn)

    return files


def force_debug_message_in_github_actions(msg: str):
    Path("dummy.log").write_text(msg)
    run("cat dummy.log", shell=True)
    Path("dummy.log").unlink(missing_ok=True)


def make_language(folder: Path, target: str = "", requires_lxcommon=True):
    set_build_tools_environment()
    repo_version = get_version(folder)
    filename_version = get_filename_version(repo_version)
    lxcommon = get_lxcommon(folder) if requires_lxcommon else ""
    print(f"{repo_version=} {filename_version=} {lxcommon=}")

    lingware_bin = get_stage_lxware_folder(folder) / "wowool"

    cmd = f"make {thread_option} {target} VERSION=@{filename_version} LXCOMMON={lxcommon} LINGWARE_BIN={lingware_bin}"
    force_debug_message_in_github_actions(f"{cmd=}")
    result = run(
        cmd,
        cwd=folder,
        shell=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"!!! Could not build {folder} {cmd=}")


def languages(folder: Path):
    for language in folder.glob("languages/*"):
        if language.is_dir():
            yield language


class LanguageBuildInfo:
    def __init__(self, folder: Path, dialect_path: Path, package_lxware_wowool: Path | None = None):
        self.folder = dialect_path
        self.stage_lxware = get_stage_lxware_folder(folder)
        self.stage_lxware_eot = self.stage_lxware / "wowool"
        if package_lxware_wowool is None:
            self.package_lxware_wowool = dialect_path / "wowool" / "lxware" / "wowool"
        else:
            self.package_lxware_wowool = package_lxware_wowool

    def clean(self):
        shutil.rmtree(f"{self.folder}/dist", ignore_errors=True)
        shutil.rmtree(f"{self.folder}/build", ignore_errors=True)
        shutil.rmtree(f"{self.folder}/var", ignore_errors=True)
        shutil.rmtree(f"{self.folder}/eot", ignore_errors=True)
        for egg_info in self.folder.glob("*.egg-info"):
            shutil.rmtree(egg_info, ignore_errors=True)
        Path(f"{self.folder}/setup.py").unlink(missing_ok=True)


def add_version_info(fn: Path, filename_version: str) -> Path:
    return Path(f"wowool/{fn.stem}@{filename_version}{fn.suffix}")


def package_language(folder: Path, dialect_path: Path, package_lxware_wowool: Path | None = None, run_setup: bool = True):
    logger.info(f"build: {dialect_path.name=}")
    repo_version = get_version(folder)
    filename_version = get_filename_version(repo_version)
    language_root = get_language(folder)
    lbi = LanguageBuildInfo(folder, dialect_path, package_lxware_wowool=package_lxware_wowool)
    lbi.clean()

    files = [lc for lc in dialect_path.glob("*.language")]

    assert len(files) == 1, "to many language file in folder"
    language_fn = files[0]

    project_fn = dialect_path / "project.json"
    package_config = {}
    if project_fn.exists():
        with open(project_fn) as fh:
            package_config = json.load(fh)

    from wowool.native.core.language_info import Parser

    exculde_pattern = package_config["exclude"] if "exclude" in package_config else []

    def add_namespace(name: str):
        if name in exculde_pattern:
            return name

        fn = Path(name)
        fn_version = add_version_info(fn, filename_version)
        stage_full_fn = lbi.stage_lxware / fn_version
        if fn.suffix == ".tkz":
            # need to do something spesial to the tkz_cache file
            fn_tkz_cache = lbi.stage_lxware / Path(fn_version).with_suffix(".tkz_cache")

            assert fn_tkz_cache.exists(), f"Could not find {fn_tkz_cache}"
            fn_version_tkz_cache = fn_version.with_suffix(".tkz_cache")
            shutil.copy(fn_tkz_cache, lbi.package_lxware_wowool / fn_version_tkz_cache.name)

        assert stage_full_fn.exists(), f"Could not find {stage_full_fn}"
        shutil.copy(stage_full_fn, lbi.package_lxware_wowool / fn_version.name)
        return str(fn_version)

    language_parser = Parser(add_namespace)

    with open(language_fn) as fh:
        jo_language = json.load(fh)

    # print(f"{jo_language=}\n{lbi.stage_lxware=}")

    lbi.package_lxware_wowool.mkdir(parents=True, exist_ok=True)
    language_parser(jo_language)
    fn_version = add_version_info(language_fn, filename_version)
    shutil.copy(lbi.stage_lxware_eot / fn_version.name, lbi.package_lxware_wowool / fn_version.name)

    if run_setup:
        setup_fn = Path(dialect_path, "setup.py").resolve()
        print(f"setup_fn: {setup_fn}")
        setup_fn.unlink(missing_ok=True)

        # !!! do not remove this variable it's used in the resolve function
        name = None
        if package_config and "name" in package_config:
            package_name = package_config["name"]
        elif language_root != dialect_path.name:
            package_name = f"language-{language_root}-{dialect_path.name}"
        else:
            package_name = language_root

        setup_dependencies = []
        if package_config and "dependencies" in package_config:
            setup_dependencies = [f"wowool-lxware-language-{name}=={repo_version}" for name in package_config["dependencies"]]

        # !!! do not remove this variable it's used in the resolve function
        setup_py_requirement = f"install_requires={json.dumps(setup_dependencies)}"

        with open(setup_fn, "w") as fh:
            from wowool.lingware.build.language.templates import LANGUAGE_SETUP_TEMPLATE

            fh.write(resolve_template(LANGUAGE_SETUP_TEMPLATE, globals(), locals()))

        logger.debug(f"Run setup.py in {dialect_path}")
        run("python setup.py bdist_wheel", cwd=dialect_path, shell=True)


def package_languages(folder: Path, package_lxware_wowool: Path | None = None, run_setup=True):
    for dialect_path in languages(folder):
        package_language(folder, dialect_path, package_lxware_wowool=package_lxware_wowool, run_setup=run_setup)


def upload_language(language_folder: Path):
    from wowool.build.codeartifact import upload_pypi

    upload_pypi(language_folder)


def upload_languages(folder: Path):
    for language_folder in languages(folder):
        upload_language(language_folder)
