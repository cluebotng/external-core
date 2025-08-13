#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import PosixPath


TARGET_RELEASE = "1.0.3"
TARGET_PATCH = "3"
WORKSPACE_DIR = PosixPath("/workspace")
APT_DIR = PosixPath("/tmp/apt")
DEB_FILE = PosixPath(f"/tmp/cluebotng-core-{TARGET_RELEASE}-{TARGET_PATCH}.amd64.deb")


def install_package():
    # We do this in a similar style to the `apt` layer as we cannot do a simple `apt-get install`,
    # basically download the .deb file and extract it directly.
    # Since we are only interested in the 'static' executable a little fernangle is done.

    # Download the .deb
    if not DEB_FILE.is_file():
        subprocess.run(
            [
                "curl",
                "--silent",
                "--show-error",
                "--fail",
                "-L",
                "-o",
                DEB_FILE.as_posix(),
                "https://launchpad.net/~damianzaremba/+archive/ubuntu/cluebotng-core/+files/"
                f"cluebotng-core_{TARGET_RELEASE}-{TARGET_PATCH}_amd64.deb",
            ],
            check=True,
        )

    # Extract the .deb
    if not (APT_DIR / "usr" / "bin" / "cluebotng").is_file():
        subprocess.run(
            [
                "dpkg",
                "-x",
                DEB_FILE.as_posix(),
                APT_DIR.as_posix(),
            ],
            check=True,
        )

    # Copy the install over to the workspace
    for path in (APT_DIR / "opt" / "cbng-core").iterdir():
        dst_path = WORKSPACE_DIR / path.name
        if path.is_file() and not dst_path.exists():
            shutil.copy(path.as_posix(), dst_path.as_posix())
        if path.is_dir() and not dst_path.exists():
            shutil.copytree(path.as_posix(), dst_path.as_posix())

    # Ensure the binaries are executable
    for binary in ["cluebotng", "create_ann", "create_bayes_db", "print_bayes_db"]:
        (WORKSPACE_DIR / binary).chmod(0x555)


def build_databases():
    for target, source in [
        ("bayes.db", "main_bayes_train.dat"),
        ("two_bayes.db", "two_bayes_train.dat"),
    ]:
        subprocess.run(
            [
                (WORKSPACE_DIR / "create_bayes_db").as_posix(),
                (WORKSPACE_DIR / "data" / target).as_posix(),
                (WORKSPACE_DIR / "data" / source).as_posix(),
            ],
            check=True,
        )


def cleanup():
    shutil.rmtree(APT_DIR.as_posix())
    DEB_FILE.unlink()


def appease_poetry():
    # Poetry expects a Python package from `setup.py install`, create a minimal one
    package_dir = PosixPath("/workspace/cluebotng_core")
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").open("w").close()


def main():
    install_package()
    build_databases()
    cleanup()
    appease_poetry()


if __name__ == "__main__":
    main()
