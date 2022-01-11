#! /usr/bin/env python

import pathlib
from importlib import import_module
from shutil import copy, make_archive, rmtree
import json

from src.generators._base import BaseGenerator

SOURCE = pathlib.Path(".") / "src"

TARGET = pathlib.Path(".") / "build"
rmtree(TARGET, ignore_errors=True)
TARGET.mkdir(exist_ok=True)

PACK = TARGET / "gurkpack"
PACK.mkdir()

GEN_NAMESPACE = PACK / "data" / "generated"
FUNCTIONS = GEN_NAMESPACE / "functions"
FUNCTIONS.mkdir(parents=True)

MINECRAFT_TAGS = PACK / "data" / "minecraft" / "tags" / "functions"
MINECRAFT_TAGS.mkdir(parents=True)

copy(SOURCE / "pack.mcmeta", PACK / "pack.mcmeta")

GENERATORS = sorted(g for g in (SOURCE / "generators").iterdir() if g.is_file() and not g.name.startswith("_"))
STEPS = len(GENERATORS) + 1
step = 1
setup_functions = []
tick_functions = []

for generator in GENERATORS:
    module_path = ".".join(generator.parts).removesuffix(".py")

    gen: BaseGenerator = import_module(module_path).Generator()

    print(f"[{step}/{STEPS}] {gen.name}")
    result = gen.generate()

    setup_functions.extend(result.setup_hooks)
    tick_functions.extend(result.tick_hooks)

    step += 1

with open(MINECRAFT_TAGS / "tick.json", "w") as file:
    json.dump({"values": tick_functions}, file)

with open(MINECRAFT_TAGS / "load.json", "w") as file:
    json.dump({"values": setup_functions}, file)

make_archive(PACK, "zip", PACK)

print(f"[{STEPS}/{STEPS}] Pack created in {PACK}.zip")
