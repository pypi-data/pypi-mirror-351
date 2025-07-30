from ...info import TILE_SIZE, HALF_SIZE, CHUNK_SIZE, SCREEN_SIZE, MULTI_TILES

def render_map(location, chunks, camera, zoom, scaled_image, window):
    for chunk_y in range(-3, 4):
        for chunk_x in range(-3, 4):
            chunk = (chunk_x + location["tile"][0], chunk_y + location["tile"][1])
            if chunk in chunks:
                for y in range(0, 16):
                    for x in range(0, 16):
                        tile = (x, y)
                        if tile in chunks[chunk] and "point" not in chunks[chunk][tile].attributes:
                            current_tile = chunks[chunk][tile]
                            placement = (camera[0] + (x * TILE_SIZE + chunk[0] * CHUNK_SIZE) * zoom, camera[1] + (y * TILE_SIZE + chunk[1] * CHUNK_SIZE - HALF_SIZE) * zoom,)
                            size = MULTI_TILES.get(current_tile.kind, (1, 1))
                            if -TILE_SIZE * zoom * size[0] <= placement[0] <= SCREEN_SIZE[0] and -TILE_SIZE * zoom * size[1] * 3 / 2 <= placement[1] <= SCREEN_SIZE[1]:
                                if isinstance(chunks[chunk][tile].floor, str):
                                    window.blit(scaled_image[current_tile.floor], (placement[0], placement[1] + HALF_SIZE * zoom))
                                if isinstance(chunks[chunk][tile].kind, str):
                                    window.blit(scaled_image[current_tile.kind], placement)
    return window