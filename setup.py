#!/usr/bin/env python3
import os
import subprocess
from pathlib import PosixPath


TARGET_RELEASE = "v1.1.0"
WORKSPACE_DIR = PosixPath("/workspace")


def download_release():
    # Download the binaries
    for binary in ["cluebotng", "create_ann", "create_bayes_db", "print_bayes_db"]:
        target_path = WORKSPACE_DIR / binary
        if not target_path.is_file():
            subprocess.run(
                [
                    "curl",
                    "--silent",
                    "--show-error",
                    "--fail",
                    "-L",
                    "-o",
                    target_path.as_posix(),
                    f"https://github.com/cluebotng/core/releases/download/{TARGET_RELEASE}/{binary}",
                ],
                check=True,
            )
            target_path.chmod(0x555)

    # Download the databases
    (WORKSPACE_DIR / "data").mkdir(parents=True, exist_ok=True)
    for database in ["main_ann.fann", "bayes.db", "two_bayes.db"]:
        target_path = WORKSPACE_DIR / "data" / database
        if not target_path.is_file():
            subprocess.run(
                [
                    "curl",
                    "--silent",
                    "--show-error",
                    "--fail",
                    "-L",
                    "-o",
                    target_path.as_posix(),
                    f"https://github.com/cluebotng/core/releases/download/{TARGET_RELEASE}/{database}",
                ],
                check=True,
            )

    # Download the config
    if not (WORKSPACE_DIR / "conf").is_dir():
        subprocess.run(
            [
                "curl",
                "--silent",
                "--show-error",
                "--fail",
                "-L",
                "-o",
                "/tmp/conf.tar.gz",
                f"https://github.com/cluebotng/core/releases/download/{TARGET_RELEASE}/conf.tar.gz",
            ],
            check=True,
        )

        subprocess.run(
            [
                "tar",
                "-C",
                WORKSPACE_DIR.as_posix(),
                "-xf",
                "/tmp/conf.tar.gz",
            ],
            check=True,
        )

        os.remove("/tmp/conf.tar.gz")


def appease_poetry():
    # Poetry expects a Python package from `setup.py install`, create a minimal one
    package_dir = PosixPath("/workspace/cluebotng_core")
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").open("w").close()


def main():
    download_release()
    appease_poetry()


if __name__ == "__main__":
    main()
