from ...info import MULTI_TILES, FLOOR_TYPE, TILE_ATTRIBUTES
from ...tile_systems.tile_class import Tile

def place_tile(chunks, location, inventory_key, grid_position, is_not_tile, inventory):
    tile_size = MULTI_TILES.get(inventory_key, (1, 1))
    for x in range(0, tile_size[0]):
        for y in range(0, tile_size[1]):
            tile_coord = (int((grid_position[1][0] + x) % 16), int((grid_position[1][1] + y) % 16))
            chunk_coord = (grid_position[0][0] + (grid_position[1][0] + x) // 16, grid_position[0][1] + (grid_position[1][1] + y) // 16)
            if tile_coord in chunks[location["room"]][chunk_coord]:
                current_tile = chunks[location["room"]][chunk_coord][tile_coord]
                tile_floor_type = FLOOR_TYPE.get(current_tile.floor, "empty")
                if tile_floor_type == "block" or "grow" in TILE_ATTRIBUTES.get(inventory_key, ()) and tile_floor_type != "soil" or isinstance(current_tile.kind, str):
                    return chunks
            elif "grow" in TILE_ATTRIBUTES.get(inventory_key, ()):
                return chunks
    if location["room"] != (0, 0, 0, 0) and is_not_tile:
        return chunks
    inventory[inventory_key] -= 1
    if "multi" in TILE_ATTRIBUTES.get(inventory_key, ()):
        width, height = MULTI_TILES[inventory_key]
        for x in range(width):
            for y in range(height):
                chunk_pos = (grid_position[0][0] + (grid_position[1][0] + x) // 16, grid_position[0][1] + (grid_position[1][1] + y) // 16)
                tile_pos = ((grid_position[1][0] + x) % 16, (grid_position[1][1] + y) % 16)
                tile_type = "left" if y == 0 else "up"
                old_tile = chunks[location["room"]][chunk_pos].get(tile_pos)
                if old_tile:
                    chunks[location["room"]][chunk_pos][tile_pos].kind = Tile(tile_type, floor = old_tile.floor, floor_health = old_tile.floor_health, floor_unbreak = old_tile.floor_unbreak)
                else:
                    chunks[location["room"]][chunk_pos][tile_pos] = Tile(tile_type)
    if is_not_tile:
        chunks[location["room"]][grid_position[0]][grid_position[1]] = Tile(inventory_key)
    else:
        old_tile = chunks[location["room"]][grid_position[0]][grid_position[1]]
        chunks[location["room"]][grid_position[0]][grid_position[1]] = Tile(inventory_key, floor = old_tile.floor, floor_health = old_tile.floor_health, floor_unbreak = old_tile.floor_unbreak)
    return chunks