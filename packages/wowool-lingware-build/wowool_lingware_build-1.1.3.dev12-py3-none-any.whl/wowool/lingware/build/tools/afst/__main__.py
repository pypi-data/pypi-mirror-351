def main():

    import subprocess
    import sys
    from pathlib import Path
    import platform
    import os

    ext = ".exe" if "Windows" == platform.system() else ""
    cpp_app = Path(__file__).parent.parent.parent.parent.parent / "package" / "lib" / f"afst++{ext}"
    if not cpp_app.exists():
        if "WOWOOL_ROOT" in os.environ:
            cpp_app = Path(os.environ["WOWOOL_ROOT"]) / "bin" / f"afst{ext}"
            assert cpp_app.exists(), "Could not find afst application."
    sys.argv[0] = str(cpp_app)
    subprocess.run(sys.argv)


if __name__ == "__main__":
    main()
