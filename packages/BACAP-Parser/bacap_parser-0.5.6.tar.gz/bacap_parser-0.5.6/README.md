## BACAP_Parser

A Python library to parse BlazeAndCavesAdvancementsPack and its Addons 

### Requirements

- Python version 3.12 or higher
- BACAP or addon for minecraft 1.21+

### Installing

```bash
pip install BACAP-Parser
```
## Configuration

To use the library, you first need to configure the parsing parameters, specifically the possible advancement types for each datapack and the list of these datapacks. Example configuration:

```py
from pathlib import Path # All paths must be pathlib.Path classes

task = AdvType(name="task", frames="task", colors=Color("green"))
goal = AdvType(name="goal", frames="goal", colors=Color("#75E1FF"))
# Challenges can also be hidden, so configure default color for hidden advancement in BACAP
challenge = AdvType(name="challenge", frames="challenge", 
                    colors=Color("dark_purple"), hidden_color=BACAP_Parser.DEFAULT_BACAP_HIDDEN_COLOR)
super_challenge = AdvType(name="super_challenge", frames="challenge", colors=Color("#FF2A2A"))
root = AdvType(name="root", frames=("task", "challenge"), colors=Color("#CCCCCC"))
milestone = AdvType(name="milestone", frames="goal", colors=Color("yellow"), tabs="bacap")
advancement_legend = AdvType(name="advancement_legend", frames="challenge", colors=Color("gold"), tabs="bacap")
manager = AdvTypeManager([task, goal, challenge, super_challenge, root, milestone, advancement_legend])


bacap = Datapack(name="bacap", path=Path("datapacks/bacap"), 
                 adv_type_manager=manager, reward_namespace="bacap_rewards", technical_tabs="technical")

# You can use the one AdvTypeManager for many datapacks if they have the same advancement types

bacaped = Datapack(name="bacaped", path=Path("datapacks/bacaped"), 
                   adv_type_manager=manager, reward_namespace="bacaped_rewards", technical_tabs="technical")
bacaped_hardcore = Datapack(name="bacaped_hardcore", path=Path("datapacks/bacaped_hardcore"), 
                            adv_type_manager=manager, reward_namespace="bacaped_rewards", technical_tabs="technical")

parser = Parser(bacap, bacaped, bacaped_hardcore)
```

## Examples
### Get Advancements Data
```py

bacap_advs: list[Advancement | TechnicalAdvancement | InvalidAdvancement] = parser.get_datapack(
    "bacap").advancement_manager.filtered_list() # Get all advancements except technical and invalid
for adv in bacap_advs:
    print(adv.title)
    if adv.type.name == "super_challenge": 
        print(adv.description)

    if adv.type.name == "milestone":
        print(adv.criteria_list)
```
- Note: Each datapack has its own `advancement_manager`
### Filtering

There are three ways to filter advancements.

`filtered_iterator` allows searching while ignoring or keeping technical advancements, invalid advancements, and normal advancements.

```py
manager: AdvancementManager = parser.get_datapack("bacap").advancement_manager
only_technical: Iterator[TechincalAdvancement] = manager.filtered_iterator(
    skip_normal=True, skip_invalid=True, skip_technical=False)
```

`find`  provides a more flexible setup with the ability to pass filtering parameters.

```py
manager: AdvancementManager = parser.get_datapack("bacap").advancement_manager
parent = manager.find(criteria={"mc_path": adv.parent}, skip_technical=False, skip_invalid=False, limit=1)[0]
```

`deep_find` differs from `find` in three key ways:

- Support for nested attributes.
- Ability to use functions as criteria values.
- Checks for partial matches.

```py
manager = parser.get_datapack("bacap").advancement_manager
advs_with_item_rewards = [adv for adv in manager.deep_find({"reward": lambda reward: bool(trophy)})]
```

#### Get trophy with description, item color and components

```py
manager = parser.get_datapack("bacap").advancement_manager
advancements = manager.deep_find(
    {"trophy": lambda trophy: bool(trophy)})

random_advancement: Advancement = random.choice(advancements)  # Get random advancement class

trophy = random_advancement.trophy  # Trophy of the advancement

trophy_item: TrophyItem = trophy.item  # Item id of the trophy
description: str = trophy.item.description  # String with trophy description
name_color: Color = trophy.item.color  # Color class of the trophy color
```

#### Add custom tabs
If your datapack has its own tabs with advancements, you can add them by specifying a custom `TabNameMapper` when creating the datapack.

```py
...
tab_mapper = TabNameMapper({"ultimate_challenges": "The Ultimate Challenges Ever"})
bacap = Datapack(name="custom", path=Path(r"datapacks/custom"),adv_type_manager=manager,
                 reward_namespace="bacap_rewards", technical_tabs="technical", tab_name_mapper=tab_mapper)
...

```
Now, when accessing the `tab_display` attribute of advancements from the `ultimate_challenges` tab, it will correctly display its display name.

#### Get HEX/RGB/INT color codes from Minecraft Text Colors

```py

color = Color('light_purple') # Will be converted to HEX representation
rgb_c: tuple[int, int, int] = color.as_rgb  # RGB representation of the color
int_c: int = color.as_int  # Integer representation of the color

# The Color class also provides static methods for converting between these color storage types.
clr = (100, 150, 200)
new_clr = Color.rgb_to_int(clr) # Will return an Integer representation of RGB color
```
