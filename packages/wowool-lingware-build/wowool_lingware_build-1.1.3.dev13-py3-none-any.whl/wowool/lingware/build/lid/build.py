from subprocess import run
from pathlib import Path
import os
import shutil
import logging
from wowool.lingware.build.git import get_version
import json
from wowool.lingware.build.utilities import resolve_template, get_filename_version, get_stage_lxware_folder, get_lxcommon

eot_namespace = "wowool"
wowool_module = "wowool.lxware"

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


def make_lid(folder: Path, target: str = "", requires_lxcommon=True):
    repo_version = get_version(folder)
    filename_version = get_filename_version(repo_version)
    print(f"{repo_version=} {filename_version=}")

    lingware_bin = get_stage_lxware_folder(folder)
    lxcommon = get_lxcommon(folder) if requires_lxcommon else ""

    cmd = f"make {thread_option} {target} VERSION=@{filename_version}  LXCOMMON={lxcommon} LINGWARE_BIN={lingware_bin}"
    print(f"{cmd=}")
    result = run(cmd, cwd=folder, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"!!! Could not build {folder} {cmd=}")


class LidBuildInfo:
    def __init__(self, folder: Path, dialect_path: Path):
        self.folder = dialect_path
        self.stage_lxware = get_stage_lxware_folder(folder)
        self.package_lxware = dialect_path / "wowool" / "lxware"

    def clean(self):
        shutil.rmtree(f"{self.folder}/dist", ignore_errors=True)
        shutil.rmtree(f"{self.folder}/build", ignore_errors=True)
        shutil.rmtree(f"{self.folder}/var", ignore_errors=True)
        shutil.rmtree(f"{self.folder}/wowool", ignore_errors=True)
        for egg_info in self.folder.glob("*.egg-info"):
            shutil.rmtree(egg_info, ignore_errors=True)
        Path(f"{self.folder}/setup.py").unlink(missing_ok=True)


def package_lid(folder: Path):
    repo_version = get_version(folder)
    filename_version = get_filename_version(repo_version)
    lbi = LidBuildInfo(folder, folder)
    lbi.clean()

    lbi.package_lxware.mkdir(parents=True)
    print(f"Copying {lbi.stage_lxware} to {lbi.package_lxware}")
    shutil.copy(lbi.stage_lxware / "lid.fst", lbi.package_lxware / "lid.fst")

    setup_fn = Path(folder, "setup.py").resolve()
    print(f"setup_fn: {setup_fn}")
    setup_fn.unlink(missing_ok=True)

    project_fn = folder / "project.json"
    package_config = None
    if project_fn.exists():
        with open(project_fn) as fh:
            package_config = json.load(fh)

    if package_config and "name" in package_config:
        package_name = package_config["name"]
    else:
        package_name = "lid"

    setup_dependencies = []
    # !!! do not remove this variable it's used in the resolve function
    setup_py_requirement = f"install_requires={json.dumps(setup_dependencies)}"

    with open(setup_fn, "w") as fh:
        from wowool.lingware.build.language.templates import LANGUAGE_SETUP_TEMPLATE
        from wowool.lingware.build.utilities import PREFIX_DO_NOT_EDIT  # noqa

        fh.write(resolve_template(LANGUAGE_SETUP_TEMPLATE, globals(), locals()))

    from wowool.build.pydist import build_wheel_package

    logger.debug(f"Run setup.py in {folder}")
    build_wheel_package(folder)


def upload_lid(language_folder: Path):
    from wowool.build.pypi import upload_pypi

    upload_pypi(language_folder)
