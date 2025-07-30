RECIPES = {
    "player": (
        (("workbench", 1), (("wood", 4), ("flint", 2))),
        (("stick", 4), (("wood", 2),)),
        (("wood floor", 1), (("wood", 2),))
    ),
    "workbench": (
        (("flint sword", 1), (("stick", 2), ("flint", 4), ("ice", 1))),
        (("flint axe", 1), (("stick", 3), ("flint", 4))),
        (("flint pickaxe", 1), (("stick", 3), ("flint", 4))),
        (("flint shovel", 1), (("stick", 2), ("flint", 3))),
        (("campfire", 1), (("wood", 5), ("flint", 2), ("stick", 6))),
        (("bowl", 4), (("wood", 3), ("stick", 2))),
        (("wood pulp", 2), (("wood", 3), ("water", 2))),
        (("flint hammer", 1), (("stick", 4), ("rock", 2), ("flint", 3))),
        (("manual press", 1), (("workbench", 1), ("flint hammer", 1))),
        (("sawbench", 1), (("workbench", 1), ("flint axe", 2), ("rock", 1))),
    ),
    "campfire": (
        (("roasted mushroom", 1), (("mushroom", 1), ("stick", 1))),
        (("water", 2), (("ice", 1), ("bowl", 2))),
        (("mushroom stew", 2), (("mushroom", 3), ("carrot", 1), ("water", 2))),
        (("stone", 1), (("rock", 1),)),
        (("brick", 2), (("clay", 1),)),
        (("roasted rabbit meat", 1), (("rabbit meat", 1),)),
    ),
    "manual press": (
        (("blue dye", 2), (("bluebell", 2), ("water", 1), ("bowl", 1))),
        (("paper", 2), (("wood pulp", 3),)),
        (("blueprint", 1), (("paper", 3), ("blue dye", 2))),
    ),
    "sawbench": (
        (("handle", 1), (("stick", 4), ("blue dye", 1))),
        (("rock sword", 1), (("handle", 1), ("rock", 4), ("ice", 1))),
        (("rock axe", 1), (("handle", 2), ("rock", 4))),
        (("rock pickaxe", 1), (("handle", 2), ("rock", 4))),
        (("rock shovel", 1), (("handle", 1), ("rock", 3))),
        (("stick", 7), (("wood", 3),)),
        (("wood floor", 2), (("wood", 3),)),
        (("small crate", 1), (("wood", 6), ("stick", 4))),
        (("small barrel", 1), (("wood", 6), ("stick", 4))),
        (("stone brick", 2), (("stone", 3),)),
        (("wooden cabin", 1), (("wood", 16), ("brick", 6))),
        (("wooden bed", 1), (("wood", 10), ("blue dye", 3), ("rabbit fur", 2))),
        (("composter", 1), (("small barrel", 1), ("mushroom", 2), ("paper", 2)))
    ),
    "mushroom shaper": (
        (("mushroom block", 1), (("mushroom", 2), ("wood", 1))),
        (("mushroom floor", 1), (("mushroom block", 1), ("wood", 1))),
    ),
    "composter": (
        (("dirt", 1), (("spore", 3), ("sapling", 1))),
    )
}