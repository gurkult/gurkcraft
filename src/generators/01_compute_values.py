from __future__ import annotations
import dataclasses
import json
from itertools import chain
from typing import Optional

import yaml

from src.generators._base import BaseGenerator, GeneratorResult, GeneratorError


@dataclasses.dataclass
class Recipe:
    inputs: list[Item]
    output: Item
    count: int


class Item:
    def __init__(self, name) -> None:
        self.name = name
        self.children: list[Item] = []
        self.value: Optional[int] = None
        self.recipes: list[Recipe] = []

    def update_value(self, visited: set[Item]) -> None:
        # Check if the item should be disabled
        if all(any(child.value == -1 for child in recipe.inputs) for recipe in self.recipes):
            self.value = -1
        else:
            possible_values = []

            for recipe in self.recipes:
                if all(child.value not in (-1, None) for child in recipe.inputs):
                    possible_values.append(max((sum(child.value for child in recipe.inputs) // recipe.count, 1)))

            if possible_values:
                self.value = min((*possible_values, self.value or float("inf")))

        if self.value is not None:
            for child in self.children:
                if child not in visited:
                    child.update_value(visited | {self})

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"{self.name} ({self.value})"


class Generator(BaseGenerator):
    name = "Compute item values"

    def generate(self) -> GeneratorResult:
        with open(self.EXTERNAL / "1.18_items.json") as file:
            items = {item["id"]: Item(f"minecraft:{item['name']}") for item in json.load(file)}

        with open(self.EXTERNAL / "1.18_recipes.json") as file:
            recipes = []

            for recipe in chain(*json.load(file).values()):
                inputs = [items[item] for item in recipe.get("ingredients", None) or chain(*recipe["inShape"]) if item]
                output = items[recipe["result"]["id"]]
                count = recipe["result"]["count"]

                recipes.append(Recipe(inputs, output, count))

        for recipe in recipes:
            for input in recipe.inputs:
                input.children.append(recipe.output)

            recipe.output.recipes.append(recipe)

        # Find roots
        roots = [item for item in items.values() if not item.recipes]

        base_values_file = self.META / "base_values.yaml"

        if not base_values_file.exists():
            with base_values_file.open("w") as file:
                yaml.dump({f"minecraft:{item.name}": -1 for item in roots}, file, sort_keys=False)

            raise GeneratorError("No base values file found. Dumped default file and aborting.")
        with base_values_file.open() as file:
            values = yaml.safe_load(file)

            missing_values = []

            for root in roots:
                if root.name not in values:
                    missing_values.append(root)
                else:
                    root.value = values[root.name]

        for root in roots:
            for child in root.children:
                child.update_value({root})

        if missing_values:
            raise GeneratorError(f"Missing values for {', '.join(item.name for item in missing_values)}")

        override_file = self.META / "override_values.yaml"
        if override_file.exists():
            with override_file.open() as file:
                override_values = yaml.safe_load(file)

            for name, value in override_values.items():
                for item in items.values():
                    if item.name == name:
                        item.value = value
                        item.update_value({item})
                        break
                else:
                    raise GeneratorError(f"Unknown item {name}")

        if without_values := [item.name for item in items.values() if not item.value]:
            print(f"      Items without values: {', '.join(without_values)}")

        with (self.INTERMEDIATE / "item_values.yaml").open("w") as file:
            yaml.dump({item.name: item.value for item in items.values()}, file, sort_keys=False)

        return GeneratorResult()
