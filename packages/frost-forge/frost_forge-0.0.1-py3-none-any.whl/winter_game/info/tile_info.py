MULTI_TILES = {
    "sawbench": (2, 1),
    "manual press": (2, 1),
    "wooden cabin": (4, 3),
    "wooden bed": (1, 2),
    "obelisk": (1, 2),
    "big rock": (2, 2),
    "mushroom hut": (3, 2),
}
STORAGE = {"small crate": (9, 48), "small barrel": (1, 512), "composter": (2, 16)}
FOOD = {
    "mushroom": 1,
    "carrot": 2,
    "roasted mushroom": 3,
    "mushroom stew": 6,
    "rabbit meat": 1,
    "roasted rabbit meat": 4,
}
GROW_TILES = {
    "sapling": ("treeling", {"wood": 2, "sapling": 1}),
    "treeling": ("tree", {"wood": 4, "sapling": 2}),
    "spore": ("mushroom", {"spore": 2, "mushroom": 1}),
    "carrot": ("carroot", {"carrot": 2}),
    "rabbit child": ("rabbit adult", {"rabbit fur": 1, "rabbit meat": 2}),
}
GROW_CHANCE = {
    "sapling": 5000,
    "treeling": 10000,
    "spore": 7500,
    "carrot": 10000,
    "rabbit child": 12500,
}
PROCESSING_TIME = {"composter": 120}
UNBREAK = ("rabbit hole", "wooden door", "left", "up", "obelisk")
FLOOR = ("void", "ice", "wood floor", "dirt", "mushroom floor")
FLOOR_UNBREAK = ("void",)
FLOOR_TYPE = {"void": "block", "ice": "block", "dirt": "soil"}