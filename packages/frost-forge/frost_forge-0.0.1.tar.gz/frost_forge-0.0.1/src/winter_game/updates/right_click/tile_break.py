from ...info import INVENTORY_SIZE
from ...tile_systems.tile_class import Tile

def break_tile(mining_kind, inventory, player_tile, grid_position, chunks, location, mining_tile):
    delete_mining_tile = False
    if mining_kind != "player":
        junk_inventory = {}
        if "no_pickup" not in mining_tile.attributes:
            inventory[mining_kind] = inventory.get(mining_kind, 0) + 1
        for item, amount in mining_tile.inventory.items():
            if item in player_tile.inventory:
                player_tile.inventory[item] += amount
                if inventory[item] > INVENTORY_SIZE[1]:
                    junk_inventory[item] = player_tile.inventory[item] - INVENTORY_SIZE[1]
                    player_tile.inventory[item] = INVENTORY_SIZE[1]
            else:
                if len(inventory) < INVENTORY_SIZE[0]:
                    player_tile.inventory[item] = amount
                else:
                    junk_inventory[item] = amount
        if "enter" in mining_tile.attributes and (*grid_position[0], *grid_position[1]) in chunks:
            del chunks[(*grid_position[0], *grid_position[1])]
        if isinstance(mining_tile.floor, str):
            mining_tile = Tile(floor = mining_tile.floor, floor_unbreak = mining_tile.floor_unbreak)
        else:
            delete_mining_tile = True
        if len(junk_inventory) > 0:
            mining_tile = Tile("junk", junk_inventory, mining_tile.floor, floor_unbreak = mining_tile.floor_unbreak)
    else:
        chunks[location["room"]][grid_position[0]][grid_position[1]] = Tile("corpse", inventory, mining_tile.floor, floor_unbreak = mining_tile.floor_unbreak)
        chunks[(0, 0, 0, 0)][(0, 0)][(0, 2)] = Tile("player", floor = "void")
        location["tile"] = [0, 0, 0, 2]
        location["real"] = [0, 0, 0, 2]
        location["room"] = (0, 0, 0, 0)
    return chunks, location, delete_mining_tile, mining_tile