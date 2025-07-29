from pathlib import Path
from wowool.build.git import make_version, get_version_info, _get_repository_path
from subprocess import run


def get_version(fp_repo: Path | None = None):
    """
    Get the version from the git history of the given repository folder

    :param fp_repo: Optional repository folder. If not provided, the current
                    working directory is used
    """
    fp_repo = _get_repository_path(fp_repo)

    _git_info = get_version_info(fp_repo)

    results = run("git diff --stat --exit-code HEAD", shell=True, capture_output=True)
    has_changes = results.returncode != 0
    if has_changes:
        out = results.stdout
        seen_lxcommon_not_changed = False
        only_one_changed = False
        for line in out.decode().split("\n"):
            # if 'lxcommon |  0' in out:
            line = line.strip()

            if "lxcommon | 0" in line:
                seen_lxcommon_not_changed = True
            if line.startswith("1 file changed"):
                only_one_changed = True
        if only_one_changed and seen_lxcommon_not_changed:
            has_changes = False

    return make_version(_git_info["tag"], _git_info["nr_commits"], has_changes)
