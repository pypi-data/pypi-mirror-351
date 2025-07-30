from .point import left, up
from .rabbit import rabbit_hole, rabbit_entity
from .machine import machine

def update_tile(current_tile, chunks, chunk, tile, delete_tiles, create_tiles, tick):
    if "grow" in current_tile.attributes:
        chunks[chunk][tile] = current_tile.grow()
    elif current_tile.kind == "left":
        chunks, delete_tiles = left(chunks, chunk, tile, delete_tiles)
    elif current_tile.kind == "up":
        chunks, delete_tiles = up(chunks, chunk, tile, delete_tiles)
    elif current_tile.kind == "rabbit hole":
        chunks, create_tiles = rabbit_hole(chunks, chunk, tile, current_tile, create_tiles)
    elif "rabbit" in current_tile.attributes:
        create_tiles, delete_tiles = rabbit_entity(chunks, chunk, tile, current_tile, create_tiles, delete_tiles)
    elif "machine" in current_tile.attributes:
        chunks = machine(chunks, chunk, tile, current_tile, tick)
    return chunks, create_tiles, delete_tiles