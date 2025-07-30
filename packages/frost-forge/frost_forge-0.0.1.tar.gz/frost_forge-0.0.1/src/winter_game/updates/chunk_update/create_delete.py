from ...tile_systems.tile_class import Tile

def create_tile(chunks, create_tiles):
    for chunk_pos, tile_pos, tile_data in create_tiles:
        chunk_tiles = chunks.setdefault(chunk_pos, {})
        if tile_pos in chunk_tiles:
            current_tile = chunk_tiles[tile_pos]
            tile_data.floor = current_tile.floor
            tile_data.floor_health = current_tile.floor_health
            tile_data.floor_unbreak = current_tile.floor_unbreak
        chunk_tiles[tile_pos] = tile_data
    return chunks

def delete_tile(chunks, delete_tiles):
    for chunk_pos, tile_pos in delete_tiles:
        tile = chunks[chunk_pos][tile_pos]
        if tile.floor is not None:
            chunks[chunk_pos][tile_pos] = Tile(
                floor=tile.floor,
                floor_health=tile.floor_health,
                floor_unbreak=tile.floor_unbreak
            )
        else:
            del chunks[chunk_pos][tile_pos]
    return chunks