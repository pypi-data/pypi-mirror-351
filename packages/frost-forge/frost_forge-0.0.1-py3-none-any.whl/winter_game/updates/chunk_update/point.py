def left(chunks, chunk, tile, delete_tiles):
    left_chunk = (chunk[0] + (tile[0] - 1) // 16, chunk[1])
    left_tile = ((tile[0] - 1) % 16, tile[1])
    if left_tile not in chunks.get(left_chunk, {}):
        delete_tiles.append((chunk, tile))
    elif chunks[left_chunk][left_tile].kind is None:
        chunks[chunk][tile].kind = None
    return chunks, delete_tiles

def up(chunks, chunk, tile, delete_tiles):
    up_chunk = (chunk[0], chunk[1] + (tile[1] - 1) // 16)
    up_tile = (tile[0], (tile[1] - 1) % 16)
    if up_tile not in chunks.get(up_chunk, {}):
        delete_tiles.append((chunk, tile))
    elif chunks[up_chunk][up_tile].kind is None:
        chunks[chunk][tile].kind = None
    return chunks, delete_tiles