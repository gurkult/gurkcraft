#! /usr/bin/env python

import pathlib
from os import rmdir
from shutil import copy, make_archive, rmtree

SOURCE = pathlib.Path(".") / "src"

TARGET = pathlib.Path(".") / "build"
rmtree(TARGET, ignore_errors=True)
TARGET.mkdir(exist_ok=True)

PACK = TARGET / "gurkpack"
PACK.mkdir(exist_ok=True)

copy(SOURCE / "pack.mcmeta", PACK / "pack.mcmeta")

make_archive(PACK, "zip", PACK)
