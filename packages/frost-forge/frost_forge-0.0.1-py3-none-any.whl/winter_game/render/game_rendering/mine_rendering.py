import pygame as pg

from ...info import TILE_SIZE, CHUNK_SIZE

def render_mined(location, chunks, camera, zoom, window, images):
    if location[0] in chunks:
        if location[1] in chunks[location[0]]:
            placement = (
                camera[0]
                + (location[1][0] * TILE_SIZE + location[0][0] * CHUNK_SIZE) * zoom,
                camera[1]
                + (location[1][1] * TILE_SIZE + location[0][1] * CHUNK_SIZE + 60) * zoom,
            )
            last_mined_tile = chunks[location[0]][location[1]]
            window.blit(pg.transform.scale(images["tiny_bar"], (TILE_SIZE * zoom, 16 * zoom)), placement)
            if isinstance(chunks[location[0]][location[1]].kind, str):
                if last_mined_tile.health // last_mined_tile.max_health == 0:
                    break_image = images[f"break_{8 - (last_mined_tile.health * 8 // last_mined_tile.max_health)}"]
                    break_image.set_alpha(127)
                    window.blit(pg.transform.scale(break_image, (TILE_SIZE * zoom, TILE_SIZE * zoom)), (placement[0], placement[1] - TILE_SIZE * zoom))
                pg.draw.rect(
                    window,
                    (181, 102, 60),
                    pg.Rect(
                        placement[0] + 4 * zoom,
                        placement[1] + 4 * zoom,
                        last_mined_tile.health * 44 * zoom / last_mined_tile.max_health,
                        8 * zoom,
                    ),
                )
            elif isinstance(chunks[location[0]][location[1]].floor, str):
                if last_mined_tile.floor_health // last_mined_tile.max_floor_health == 0:
                    break_image = images[f"break_{8 - (last_mined_tile.floor_health * 8 // last_mined_tile.max_floor_health)}"]
                    break_image.set_alpha(127)
                    window.blit(pg.transform.scale(break_image, (TILE_SIZE * zoom, TILE_SIZE * zoom)), (placement[0], placement[1] - TILE_SIZE * zoom))
                pg.draw.rect(
                    window,
                    (181, 102, 60),
                    pg.Rect(
                        placement[0] + 4 * zoom,
                        placement[1] + 4 * zoom,
                        last_mined_tile.floor_health * 44 * zoom / last_mined_tile.max_floor_health,
                        8 * zoom,
                    ),
                )
    return window