from pathlib import Path
import os
import subprocess as sbp
import re
import shutil

from setuptools import setup
from setuptools.dist import Distribution


def build_csrc():
    if not os.environ.get("STOKEN_BFASST_NO_BUILD"):
        sbp.run(["cmake", "-S", "c-src", "-B", "c-build"], check=True)
        sbp.run(["cmake", "--build", "c-build"], check=True)

    artifact_rx = re.compile("^lib_stoken_bfasst\.(dylib|so|dll)$")

    for p in Path("c-build").iterdir():
        if artifact_rx.search(p.name):
            shutil.copyfile(str(p), Path("src/stoken_bfasst_core") / p.name)


class _Distribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(self, *args, **kwargs):
        return True


build_csrc()
setup(name="stoken_bfasst", version="0.0.0.1", distclass=_Distribution)
