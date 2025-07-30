from .tile_placement import place_tile
from ...info import FOOD, FLOOR, TILE_ATTRIBUTES
from ...tile_systems.tile_class import Tile

def place(inventory, inventory_number, is_not_tile, is_kind, health, max_health, grid_position, location, chunks):
    if len(inventory) > inventory_number:
        inventory_key = list(inventory.keys())[inventory_number]
        if inventory_key not in FLOOR:
            if is_not_tile or not is_kind:
                if "eat" in TILE_ATTRIBUTES.get(inventory_key, ()):
                    if health < max_health:
                        chunks[location["room"]][location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]].health = min(health + FOOD[inventory_key], max_health)
                        inventory[inventory_key] -= 1
                        return chunks
                chunks = place_tile(chunks, location, inventory_key, grid_position, is_not_tile, inventory)
        elif is_not_tile:
            inventory[inventory_key] -= 1
            chunks[location["room"]][grid_position[0]][grid_position[1]] = Tile(floor = inventory_key)
        if inventory[inventory_key] == 0:
            del inventory[inventory_key]
    return chunks