from pathlib import Path
import os
import json
from subprocess import run
from shutil import rmtree
from logging import getLogger

logger = getLogger("wowool.lingware.build")

PREFIX_DO_NOT_EDIT = "# DO NOT EDIT ! But don't worry your changes will be overwritten anyway."
eot_namespace = "wowool-lxware"
wowool_module = "wowool.lxware.wowool"


def python_build_folders(folder):
    for pattern in ["build", "dist", "var", "portal"]:
        for fn in Path(folder).glob(f"**/{pattern}"):
            yield fn


def clean_python_build_folders(folder):
    for fn in python_build_folders(folder):
        logger.debug(f"rm {fn}")
        rmtree(fn, ignore_errors=True)


def resolve_template(template, __globals, __locals):
    return eval("f'''" + template + "'''", __globals, __locals)


def get_filename_version(package_version: str) -> str:
    filename_version = package_version
    if ".dev" in package_version:
        filename_version = "dev"
    return filename_version


def get_stage_folder(folder: Path) -> Path:
    if "WOWOOL_STAGE" in os.environ:
        tir_stage = Path(os.environ["WOWOOL_STAGE"])
        assert tir_stage.exists(), f"WOWOOL_STAGE={tir_stage}, does not exists."
        return Path(tir_stage)
    tir_stage = folder
    return tir_stage


def get_stage_lxware_folder(folder: Path) -> Path:
    if "WOWOOL_LXWARE" in os.environ:
        lxware = Path(os.environ["WOWOOL_LXWARE"])
        assert lxware.exists(), f"WOWOOL_LXWARE={lxware}, does not exists."
        return Path(lxware)

    tir_stage = get_stage_folder(folder)
    return tir_stage / "lxware"


def update_file(src: Path, dest: Path, verbose: bool = False):
    if (not os.path.exists(dest)) or (os.stat(src).st_mtime - os.stat(dest).st_mtime > 1):
        from shutil import copy2

        if verbose:
            print(f"cp {src=}{dest=}")
        copy2(src, dest)


def get_lxcommon(folder: Path) -> Path:

    if "WOWOOL_LINGWARE" in os.environ:
        changelog_fn = Path(os.environ["WOWOOL_LINGWARE"]) / "lxcommon" / "changelog.md"
        if changelog_fn.exists():
            return folder / "lxcommon"

    changelog_fn = folder / "lxcommon" / "changelog.md"
    if changelog_fn.exists():
        return folder / "lxcommon"
    else:
        changelog_fn = folder.parent / "lxcommon" / "changelog.md"
        assert changelog_fn.exists(), f"could not find lxcommon files {changelog_fn}"
        return folder.parent / "lxcommon"


def get_linware_root() -> Path:
    if "WOWOOL_LINGWARE" in os.environ:
        return Path(os.environ["WOWOOL_LINGWARE"])


def get_language(folder: Path) -> str:
    fn = folder / "project.json"
    assert fn.exists(), f"Missing project.json in {fn}"
    with open(fn) as fh:
        jo = json.load(fh)
        assert "language" in jo, f"Missing 'language' in {fn}"
        language: str = jo["language"]
        return language


def set_build_tool_environment(env_name: str, tool: str, order=["++", ""]):

    if env_name not in os.environ:
        result = run(f"which {tool}{order[0]}", capture_output=True, shell=True)
        if result.returncode == 0:
            exec_fn = result.stdout.decode().strip()
            assert Path(exec_fn).exists()
            os.environ[env_name] = exec_fn
            return True
        elif len(order) == 2:
            result = run(f"which {tool}{order[1]}", capture_output=True, shell=True)
            if result.returncode == 0:
                exec_fn = result.stdout.decode().strip()
                assert Path(exec_fn).exists()
                os.environ[env_name] = exec_fn
                return True


def set_build_tools_environment():

    set_build_tool_environment("AFST_EXEC", "afst")
    set_build_tool_environment("WOC_EXEC", "woc")
    set_build_tool_environment("WOW_EXEC", "wow")
    set_build_tool_environment("TOK_EXEC", "wow", order=[""])
