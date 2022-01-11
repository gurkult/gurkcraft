from src.generators._base import BaseGenerator, GeneratorResult
from yaml import safe_load

BUY_ITEM = "give @a[scores={gurkoins=$price..,shop_$id=1..}] $item $amount"
BUY_EFFECT = "effect give @a[scores={gurkoins=$price..,shop_$id=1..}] $item $amount 0 true"

CREATE_TRIGGER = "scoreboard objectives add $trigger trigger\n"

BUY_FLOW = """
tellraw @a[scores={gurkoins=$price..,shop_$id=1..}] ["",{"text":"Thank you for your purchase!","bold":true},{"text":" $price GRK have been subtracted from your account"}]
tellraw @a[scores={gurkoins=..$infprice,shop_$id=1..}] ["",{"text":"Not enough funds!","bold":true,"color":"red"},{"text":" $price GRK are needed to get buy that item"}]
scoreboard players remove @a[scores={gurkoins=$price..,shop_$id=1..},gamemode=!creative] gurkoins $price
scoreboard players set @a shop_$id 0
scoreboard players enable @a shop_$id
""".strip()


class Generator(BaseGenerator):
    name = "Generate buying commands"

    def generate(self) -> GeneratorResult:
        with open(self.META / "buying_options.yaml") as file:
            options = safe_load(file)

        triggers = []
        commands = []

        for id, data in options.items():
            commands.append(f"# {id}: {data}")

            match data["type"]:
                case "item":
                    commands.append(self._format_command(BUY_ITEM, id=id, **data))
                case "effect":
                    commands.append(self._format_command(BUY_EFFECT, id=id, **data))
                case "_":
                    print("Unknown type:", data["type"])
                    commands.pop()
                    continue

            triggers.append(f"shop_{id}")
            commands.append(self._format_command(BUY_FLOW, id=id, infprice=data["price"] - 1, **data))

        with (self.FUNCTIONS / "buying.mcfunction").open("w") as file:
            file.write("\n".join(commands))

        with (self.FUNCTIONS / "buying_setup.mcfunction").open("w") as file:
            for trigger in triggers:
                file.write(self._format_command(CREATE_TRIGGER, trigger=trigger))

        return GeneratorResult(["generated:buying_setup"], ["generated:buying"])
