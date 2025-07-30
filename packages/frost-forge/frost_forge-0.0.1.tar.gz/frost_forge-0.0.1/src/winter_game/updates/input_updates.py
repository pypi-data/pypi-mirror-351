import pygame as pg

from .player_move import move_player
from ..tile_systems.tile_class import Tile
from ..tile_systems.world_generation import generate_chunk
from ..game_state import GameState
from .mouse_update import button_press

def update_game(state: GameState, chunks):
    state.health = chunks[state.location["room"]][state.location["tile"][0], state.location["tile"][1]][state.location["tile"][2], state.location["tile"][3]].health
    state.max_health = chunks[state.location["room"]][state.location["tile"][0], state.location["tile"][1]][state.location["tile"][2], state.location["tile"][3]].max_health

    state.location["old"] = list(state.location["tile"])
    state.inventory = chunks[state.location["room"]][state.location["tile"][0], state.location["tile"][1]][state.location["tile"][2], state.location["tile"][3]].inventory
    key = pg.key.get_pressed()
    state.location, state.velocity = move_player(key, state.controls, state.velocity, state.location)

    if state.location["room"] == (0, 0, 0, 0):
        for x in range(-4, 5):
            for y in range(-4, 5):
                generate_chunk(state.location["tile"][0] + x, state.location["tile"][1] + y, chunks[state.location["room"]], state.noise_offset)

    room = state.location["room"]
    tile_chunk_coords = (state.location["tile"][0], state.location["tile"][1])
    tile_coords = (state.location["tile"][2], state.location["tile"][3])
    old_chunk_coords = (state.location["old"][0], state.location["old"][1])
    old_tile_coords = (state.location["old"][2], state.location["old"][3])

    chunk = chunks[room][tile_chunk_coords]
    old_chunk = chunks[room][old_chunk_coords]
    old_tile = old_chunk[old_tile_coords]

    if tile_coords not in chunk:
        chunk[tile_coords] = Tile("player", state.inventory, health=state.health, max_health=state.max_health)
    elif chunk[tile_coords].kind is None:
        exist_tile = chunk[tile_coords]
        chunk[tile_coords] = Tile("player", state.inventory, exist_tile.floor, state.health, state.max_health, exist_tile.floor_health, exist_tile.floor_unbreak)
    elif chunk[tile_coords].kind != "player":
        state.location["real"] = list(state.location["old"])
        state.location["tile"] = list(state.location["old"])
        state.velocity = [0, 0]

    if state.location["old"] != state.location["tile"]:
        if isinstance(old_tile.floor, str):
            old_chunk[old_tile_coords] = Tile(floor=old_tile.floor, floor_health=old_tile.floor_health, floor_unbreak=old_tile.floor_unbreak)
        else:
            del old_chunk[old_tile_coords]

    for event in pg.event.get():
        if event.type == pg.QUIT:
            state.run = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            chunks, state.location, state.machine_ui, state.machine_inventory, state.tick, state.inventory_number = button_press(
                event.button, state.position, state.zoom, chunks, state.location, state.machine_ui, state.inventory, state.health, state.max_health,
                state.machine_inventory, state.tick, state.inventory_number, chunks[state.location["room"]][state.location["opened"][0]][state.location["opened"][1]].recipe, state.camera)
        elif event.type == pg.KEYDOWN:
            keys = pg.key.get_pressed()
            if keys[state.controls[4]]:
                if state.machine_ui == "game":
                    state.machine_ui = "player"
                    state.location["opened"] = ((state.location["tile"][0], state.location["tile"][1]), (state.location["tile"][2], state.location["tile"][3]))
                else:
                    state.machine_ui = "game"
                    state.location["opened"] = ((0, 0), (0, 0))
            elif keys[state.controls[5]] or keys[state.controls[6]]:
                state.target_zoom += (keys[state.controls[5]] - keys[state.controls[6]]) / 4
                state.target_zoom = min(max(state.target_zoom, 0.5), 2)
            elif keys[pg.K_TAB]:
                state.menu_placement = "options_game"

    state.tick += 1
    state.zoom = 0.05 * state.target_zoom + 0.95 * state.zoom
    return chunks