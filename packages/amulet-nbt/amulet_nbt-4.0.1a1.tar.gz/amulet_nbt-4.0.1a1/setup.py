import os
import subprocess
import sys
from pathlib import Path
import platform
import datetime

from setuptools import setup, Extension, Command
from setuptools.command.build_ext import build_ext

from packaging.version import Version
import versioneer

import requirements
import amulet_compiler_version


if (
    os.environ.get("AMULET_FREEZE_COMPILER", None)
    and sys.platform == "darwin"
    and platform.machine() != "arm64"
):
    raise Exception("The MacOS frozen build must be created on arm64")


def fix_path(path: str) -> str:
    return os.path.realpath(path).replace(os.sep, "/")


dependencies = requirements.get_runtime_dependencies()

cmdclass: dict[str, type[Command]] = versioneer.get_cmdclass()


class CMakeBuild(cmdclass.get("build_ext", build_ext)):
    def build_extension(self, ext):
        import pybind11
        import amulet.io
        import amulet.pybind11_extensions

        ext_dir = (
            (Path.cwd() / self.get_ext_fullpath("")).parent.resolve() / "amulet" / "nbt"
        )
        nbt_src_dir = (
            Path.cwd() / "src" / "amulet" / "nbt" if self.editable_mode else ext_dir
        )

        platform_args = []
        if sys.platform == "win32":
            platform_args.extend(["-G", "Visual Studio 17 2022"])
            if sys.maxsize > 2**32:
                platform_args.extend(["-A", "x64"])
            else:
                platform_args.extend(["-A", "Win32"])
            platform_args.extend(["-T", "v143"])
        elif sys.platform == "darwin":
            if platform.machine() == "arm64":
                platform_args.append("-DCMAKE_OSX_ARCHITECTURES=x86_64;arm64")

        if subprocess.run(
            [
                "cmake",
                *platform_args,
                f"-DPYTHON_EXECUTABLE={sys.executable}",
                f"-Dpybind11_DIR={fix_path(pybind11.get_cmake_dir())}",
                f"-Damulet_pybind11_extensions_DIR={(amulet.pybind11_extensions.__path__[0])}",
                f"-Damulet_io_DIR={fix_path(amulet.io.__path__[0])}",
                f"-Damulet_nbt_DIR={fix_path(nbt_src_dir)}",
                f"-DAMULET_NBT_EXT_DIR={fix_path(ext_dir)}",
                f"-DCMAKE_INSTALL_PREFIX=install",
                "-B",
                "build",
            ]
        ).returncode:
            raise RuntimeError("Error configuring amulet_nbt")
        if subprocess.run(
            ["cmake", "--build", "build", "--config", "Release"]
        ).returncode:
            raise RuntimeError("Error installing amulet_nbt")
        if subprocess.run(
            ["cmake", "--install", "build", "--config", "Release"]
        ).returncode:
            raise RuntimeError("Error installing amulet_nbt")


cmdclass["build_ext"] = CMakeBuild


def _get_version() -> str:
    version_str: str = versioneer.get_version()

    if os.environ.get("AMULET_FREEZE_COMPILER", None):
        version = Version(version_str)
        epoch = f"{version.epoch}!" if version.epoch else ""
        release = ".".join(map(str, version.release))
        pre = "".join(map(str, version.pre)) if version.is_prerelease else ""
        post = f".post{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}"
        local = f"+{version.local}" if version.local else ""
        version_str = f"{epoch}{release}{pre}{post}{local}"

    return version_str


setup(
    version=_get_version(),
    cmdclass=cmdclass,
    ext_modules=[Extension("amulet.nbt._amulet_nbt", [])],
    install_requires=dependencies,
)
