from src.generators._base import BaseGenerator, GeneratorResult


CREATE_SCOREBOARD = "scoreboard objectives add lib_teleport_$var dummy\n"
RESET_SCOREBOARD = "scoreboard players reset @a lib_teleport_$var\n"

TELEPORT_COMMAND = "execute as @a[scores={lib_teleport_$axis=$range}] at @s run tp @s "
UPDATE_COMMAND = "scoreboard players $op @a[scores={lib_teleport_$axis=$range}] lib_teleport_$axis $value\n"

NORMALIZE_COMMAND = "teleport @a[scores={lib_teleport_is_absolute=1}] 0 0 0\n"
INPUTS = [*"xyz", "is_absolute"]

# Limit teleports in the [-1048575, 1048575] range
MAX_POWER = 19


class Generator(BaseGenerator):
    name = "Generate lib_teleport"

    @staticmethod
    def _map_axis(value: int, axis: str) -> str:
        if axis == "x":
            return f"~{value} ~ ~"
        elif axis == "y":
            return f"~ ~{value} ~"
        elif axis == "z":
            return f"~ ~ ~{value}"

    def generate(self) -> GeneratorResult:
        folder = self.FUNCTIONS / "lib_teleport"
        folder.mkdir(parents=True, exist_ok=True)

        with (folder / "setup.mcfunction").open("w") as file:
            for var in INPUTS:
                file.write(self._format_command(CREATE_SCOREBOARD, var=var))

        with (folder / "teleport.mcfunction").open("w") as file:
            file.write(NORMALIZE_COMMAND)
            file.write(self._format_command(RESET_SCOREBOARD, var="is_absolute"))

            for axis in "xyz":
                for direction in (1, -1):
                    for power in range(MAX_POWER, -1, -1):
                        value = 2 ** power * direction

                        if value > 0:
                            range_ = f"{value}.."
                        else:
                            range_ = f"..{value}"

                        command = self._format_command(TELEPORT_COMMAND, axis=axis, range=range_) + self._map_axis(value, axis) + "\n"
                        file.write(command)
                        command = self._format_command(UPDATE_COMMAND, op="add" if value < 0 else "remove", axis=axis, range=range_, value=abs(value))
                        file.write(command)

        return GeneratorResult(["generated:lib_teleport/setup"])
