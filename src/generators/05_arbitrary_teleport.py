from src.generators._base import BaseGenerator, GeneratorResult

CREATE_TRIGGER = "scoreboard objectives add $trigger trigger"
CREATE_SCOREBOARD = "scoreboard objectives add arbitary_location_$axis_$id dummy"
SET_SCOREBOARD = "scoreboard players set @a arbitary_location_$axis_$id $val"
SET_TP = """
execute as @a[scores={set_tp_$id=1..}] in minecraft:overworld store result score @s arbitary_location_x_$id run $x
execute as @a[scores={set_tp_$id=1..}] in minecraft:overworld store result score @s arbitary_location_y_$id run $y
execute as @a[scores={set_tp_$id=1..}] in minecraft:overworld store result score @s arbitary_location_z_$id run $z
scoreboard players set @a set_tp_$id 0
scoreboard players enable @a set_tp_$id
""".strip()

TELEPORT_FLOW = """
tellraw @a[scores={gurkoins=$price..,shop_tp_$id=1..}] ["",{"text":"Thank you for your purchase!","bold":true},{"text":" $price GRK have been subtracted from your account"}]
tellraw @a[scores={gurkoins=..$infprice,shop_tp_$id=1..}] ["",{"text":"Not enough funds!","bold":true,"color":"red"},{"text":" $price GRK are needed to get buy that item"}]
execute as @a[scores={gurkoins=$price..,shop_tp_$id=1..}] in minecraft:overworld $x
execute as @a[scores={gurkoins=$price..,shop_tp_$id=1..}] in minecraft:overworld $y
execute as @a[scores={gurkoins=$price..,shop_tp_$id=1..}] in minecraft:overworld $z
scoreboard players set @a[scores={gurkoins=$price..,shop_tp_$id=1..}] lib_teleport_is_absolute 1
execute as @a[scores={gurkoins=$price..,shop_tp_$id=1..}] in minecraft:overworld run function generated:lib_teleport/teleport
scoreboard players remove @a[scores={gurkoins=$price..,shop_tp_$id=1..},gamemode=!creative] gurkoins $price
scoreboard players set @a shop_tp_$id 0
scoreboard players enable @a shop_tp_$id
""".strip()

class Generator(BaseGenerator):
    name = "Generate arbitary teleports"

    def generate(self) -> GeneratorResult:
        folder = self.FUNCTIONS / "arbitary_teleport"
        folder.mkdir(parents=True, exist_ok=True)

        teleports = []
        commands = []
        setups = []

        # home
        setups.append(self._format_command(CREATE_TRIGGER, trigger="shop_tp_home"))
        teleports.append({
            'x': "store result score @s lib_teleport_x run data get entity @s SpawnX",
            'y': "store result score @s lib_teleport_y run data get entity @s SpawnY",
            'z': "store result score @s lib_teleport_z run data get entity @s SpawnZ",
            'id': "home",
            'price': 100,
            'infprice': 99
        })

        # Customizable locations
        for i in range(1, 6):
            setups.append(self._format_command(CREATE_SCOREBOARD, axis='x', id=i))
            setups.append(self._format_command(CREATE_SCOREBOARD, axis='y', id=i))
            setups.append(self._format_command(CREATE_SCOREBOARD, axis='z', id=i))
            setups.append(self._format_command(SET_SCOREBOARD, axis='x', id=i, val=289.5))
            setups.append(self._format_command(SET_SCOREBOARD, axis='y', id=i, val=73.00))
            setups.append(self._format_command(SET_SCOREBOARD, axis='z', id=i, val=317.5))
            setups.append(self._format_command(CREATE_TRIGGER, trigger=f"shop_tp_{i}"))
            setups.append(self._format_command(CREATE_TRIGGER, trigger=f"set_tp_{i}"))
            teleports.append({
                'x': f"run scoreboard players operation @s lib_teleport_x = @s arbitary_location_x_{i}",
                'y': f"run scoreboard players operation @s lib_teleport_y = @s arbitary_location_y_{i}",
                'z': f"run scoreboard players operation @s lib_teleport_z = @s arbitary_location_z_{i}",
                'id': i,
                'price': 200,
                'infprice': 199
            })
            commands.append({
                'x': f"data get entity @s Pos[0]",
                'y': f"data get entity @s Pos[1]",
                'z': f"data get entity @s Pos[2]",
                'id': i
            })
        # Write stuff
        with (folder / "setup.mcfunction").open("w") as file:
            file.write('\n'.join(setups))

        with (folder / "main.mcfunction").open("w") as file:
            file.write('\n'.join([self._format_command(TELEPORT_FLOW, **teleport) for teleport in teleports]))
            file.write('\n')  # Separator
            file.write('\n'.join([self._format_command(SET_TP, **command) for command in commands]))

        return GeneratorResult(["generated:arbitary_teleport/setup"], ["generated:arbitary_teleport/main"])
