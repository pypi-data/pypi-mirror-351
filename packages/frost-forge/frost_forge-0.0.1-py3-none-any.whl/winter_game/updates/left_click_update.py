from ..info import TILE_ATTRIBUTES, DAY_LENGTH
from ..tile_systems.tile_class import Tile
from .left_click import recipe, place, storage, enter_room, machine_storage

def left_click(
    machine_ui: str,
    grid_position: list[int, int],
    chunks,
    inventory_number: int,
    health: int,
    max_health: int,
    position,
    recipe_number: int,
    location: dict[str],
    inventory: dict[str, int],
    machine_inventory: dict[str, int],
    tick: int,
):
    if machine_ui == "game":
        is_not_tile = (grid_position[1] not in chunks[location["room"]][grid_position[0]])
        player_tile = chunks[location["room"]][location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]]
        if not is_not_tile:
            is_kind = isinstance(chunks[location["room"]][grid_position[0]][grid_position[1]].kind, str)
        else:
            is_kind = True
        if is_not_tile or not is_kind:
            chunks = place(inventory, inventory_number, is_not_tile, is_kind, health, max_health, grid_position, location, chunks)
        elif "open" in chunks[location["room"]][grid_position[0]][grid_position[1]].attributes:
            machine_ui = chunks[location["room"]][grid_position[0]][grid_position[1]].kind
            location["opened"] = (grid_position[0], grid_position[1])
            machine_inventory = chunks[location["room"]][grid_position[0]][grid_position[1]].inventory
        elif "enter" in chunks[location["room"]][grid_position[0]][grid_position[1]].attributes and location["room"] == (0, 0, 0, 0):
            chunks, location = enter_room(location, grid_position, chunks, health, max_health, inventory)
        elif "exit" in chunks[location["room"]][grid_position[0]][grid_position[1]].attributes:
            chunks[0, 0, 0, 0][0, 0][0, 2] = Tile("player", inventory, "void", health, max_health)
            chunks[location["room"]][location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]] = Tile(floor = player_tile.floor, floor_health = player_tile.floor_health, floor_unbreak = player_tile.floor_unbreak)
            location["real"] = [0, 0, 0, 2]
            location["tile"] = [*location["real"],]
            location["mined"] = ((0, 0), (0, 2))
            location["room"] = (0, 0, 0, 0)
            machine_ui = "game"
        elif "sleep" in chunks[location["room"]][grid_position[0]][grid_position[1]].attributes:
            if 9 / 16 <= (tick / DAY_LENGTH) % 1 < 15 / 16:
                tick = (tick // DAY_LENGTH + 9 / 16) * DAY_LENGTH
    elif "machine" in TILE_ATTRIBUTES.get(machine_ui, ()):
        chunks = machine_storage(position, chunks, location, inventory, machine_ui)
    elif "store" in TILE_ATTRIBUTES.get(machine_ui, ()):
        chunks = storage(position, chunks, location, inventory, machine_ui)
    elif "craft" in TILE_ATTRIBUTES.get(machine_ui, ()):
        inventory = recipe(machine_ui, recipe_number, inventory)
    return machine_ui, chunks, location, machine_inventory, tick
