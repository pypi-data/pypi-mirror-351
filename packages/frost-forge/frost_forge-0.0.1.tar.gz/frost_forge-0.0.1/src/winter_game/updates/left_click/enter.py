from ...tile_systems.room_generation import generate_room
from ...tile_systems.tile_class import Tile

def enter_room(location, grid_position, chunks, health, max_health, inventory):
    location["room"] = (*grid_position[0], *grid_position[1],)
    location["real"] = [0, 0, 0, 0]
    location["mined"] = ((0, 0), (0, 0))
    if location["room"] in chunks:
        chunks[location["room"]][0, 0][0, 0] = Tile("player", inventory, chunks[location["room"]][0, 0][0, 0].floor, health, max_health, chunks[location["room"]][0, 0][0, 0].floor_health, chunks[location["room"]][0, 0][0, 0].floor_unbreak)
        chunks[0, 0, 0, 0][location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]] = Tile(floor = chunks[0, 0, 0, 0][location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]].floor)
        location["tile"] = [0, 0, 0, 0]
    else:
        if chunks[0, 0, 0, 0][grid_position[0]][grid_position[1]].kind == "wooden cabin":
            chunks[location["room"]] = generate_room("wood", (-5, -4), (8, 6), "wood floor")
            chunks[location["room"]][0, 0][0, 1] = Tile("wooden door")
        elif chunks[0, 0, 0, 0][grid_position[0]][grid_position[1]].kind == "mushroom hut":
            chunks[location["room"]] = generate_room("mushroom block", (-3, -2), (5, 4), "mushroom floor")
            chunks[location["room"]][0, 0][0, 1] = Tile("wooden door")
            chunks[location["room"]][-1, -1][14, 15] = Tile("mushroom shaper")
        chunks[location["room"]][0, 0][0, 0] = Tile("player", inventory, chunks[location["room"]][0, 0][0, 0].floor, health, max_health, chunks[location["room"]][0, 0][0, 0].floor_health, chunks[location["room"]][0, 0][0, 0].floor_unbreak)
        chunks[0, 0, 0, 0][(location["tile"][0], location["tile"][1])][(location["tile"][2], location["tile"][3])] = Tile(floor = chunks[0, 0, 0, 0][location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]].floor)
        location["tile"] = [0, 0, 0, 0]
    return chunks, location