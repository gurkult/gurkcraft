import yaml

from src.generators._base import BaseGenerator, GeneratorResult, GeneratorError
from src.generators._constants import CREATE_SCOREBOARD

DAILY_FLOW = """# Daily Flow
execute store result score day gp0 run time query day
scoreboard players add @a ticket_last_reset 0
execute as @a if score @s ticket_last_reset < day gp0 run scoreboard players set @s tickets_today 0
"""
NOT_SHREDDING = """# Not Shredding $item
execute as @e[tag=in_shredder,nbt={Item:{id:"$item"}}] run title @p actionbar {"text":"This item cannot be shredded","color":"dark_red"}
execute as @e[tag=in_shredder,nbt={Item:{id:"$item"}}] at @s run particle minecraft:crit ~ ~.1 ~ 0.1 .05 0.1 .1 10
"""
PROCESS_ITEM = """# Process $item
execute as @e[tag=in_shredder,nbt={Item:{id:"$item"}},limit=1] at @s run scoreboard players add @p ticket_points $points
execute as @e[tag=in_shredder,nbt={Item:{id:"$item"}},limit=1] at @s run particle minecraft:lava ~ ~.3 ~ 0 0 0 10000 1
execute as @e[tag=in_shredder,nbt={Item:{id:"$item"}},limit=1] store result score shredder_item_count gp0 run data get entity @s Item.Count
scoreboard players remove shredder_item_count gp0 1
execute as @e[tag=in_shredder,nbt={Item:{id:"$item"}},limit=1] store result entity @s Item.Count byte 1.0 run scoreboard players get shredder_item_count gp0
"""
EXCHANGE_POINTS = """# Exchange Points
scoreboard players add @a tickets_today 0
give @a[scores={tickets_today=$min..$max,ticket_points=$points..},tag=in_shredder_room] paper{display:{Name:'[{"text":"Shredder Ticket","italic":false,"color":"gold"}]',Lore:['[{"text":"Drop to exchange for 10 tokens","italic":false}]']},Enchantments:[{id:mending,lvl:1}],ExchangeValue:10} 1
execute as @a[scores={tickets_today=$min..$max,ticket_points=$points..},tag=in_shredder_room] at @s run playsound minecraft:entity.player.levelup neutral @s ~ ~ ~ 1 $pitch
scoreboard players add @a[scores={tickets_today=$min..$max,ticket_points=$points..},tag=in_shredder_room] tickets_today 1
scoreboard players remove @a[scores={tickets_today=$min..$max,ticket_points=$points..},tag=in_shredder_room] ticket_points $points
"""
CHAIN_ITEM_FLOW = "execute if entity @e[tag=in_shredder] run function generated:shredder_item\n"

SCOREBOARDS = ["ticket_points", "ticket_last_reset", "tickets_today"]

PRICE_STAGES = [5_000, 10_000, 20_000, 40_000]
STAGE_SIZE = 5


class Generator(BaseGenerator):
    name = "Generate item shredder code"

    def generate(self) -> GeneratorResult:
        with (self.FUNCTIONS / "shredder_setup.mcfunction").open("w") as file:
            for scoreboard in SCOREBOARDS:
                file.write(self._format_command(CREATE_SCOREBOARD, name=scoreboard))

        with (self.FUNCTIONS / "shredder.mcfunction").open("w") as file:
            file.write(DAILY_FLOW)
            file.write(CHAIN_ITEM_FLOW)

        with (self.INTERMEDIATE / "item_values.yaml").open() as file:
            item_values = yaml.safe_load(file)

        with (self.FUNCTIONS / "shredder_item.mcfunction").open("w") as file:
            for item, points in item_values.items():
                if points > 0:
                    file.write(self._format_command(PROCESS_ITEM, item=item, points=points))
                elif points == -1:
                    file.write(self._format_command(NOT_SHREDDING, item=item))
                else:
                    raise GeneratorError(f"Invalid points value for item {item}")

            for i, price in enumerate(PRICE_STAGES):
                file.write(
                    self._format_command(
                        EXCHANGE_POINTS,
                        min=i * STAGE_SIZE,
                        max=(i + 1) * STAGE_SIZE - 1,
                        points=price,
                        pitch=1 + 0.1 * i
                    )
                )

        return GeneratorResult(["generated:shredder_setup"], ["generated:shredder"])
