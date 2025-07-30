from .Color import Color, MINECRAFT_TEXT_COLORS_MAP_REVERSED, MINECRAFT_TEXT_COLORS_MAP

ADV_FRAMES = frozenset(("task", "goal", "challenge"))

DEFAULT_MINECRAFT_FRAME = "task"
DEFAULT_MINECRAFT_FRAME_COLOR_MAP = {"task": Color("green"), "goal": Color("#75E1FF"), "challenge": Color("dark_purple")}
DEFAULT_MINECRAFT_DESCRIPTION_COLOR = Color("green")

DEFAULT_BACAP_HIDDEN_COLOR = Color("light_purple")

DEFAULT_BACAP_TAB_NAMES_MAP = {"adventure": "Adventure", "animal": "Animals", "bacap": "B&C Advancements", "biomes": "Biomes", "building": "Building",
                 "challenges": "Super Challenges", "enchanting": "Enchanting", "end": "The End", "farming": "Farming", "mining": "Mining",
                 "monsters": "Monsters", "nether": "Nether", "potion": "Potions", "redstone": "Redstone", "statistics": "Statistics", "weaponry": "Weaponry"}

ARABIC_TO_ROMAN_MAP = {1000: "M", 900: "CM", 500: "D", 400: "CD", 100: "C", 90: "XC", 50: "L", 40: "XL", 10: "X", 9: "IX", 5: "V", 4: "IV", 1: "I"}

MINIMAL_PACK_FORMAT = 48