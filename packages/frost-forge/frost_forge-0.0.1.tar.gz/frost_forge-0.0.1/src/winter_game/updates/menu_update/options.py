from json import dumps
from os import path

from ...render.menu_rendering import SAVES_FOLDER
from ...tile_systems.serialize import serialize_chunks

def option(state, chunks):
    if state.menu_placement == "options_game":
        if 0 <= state.position[1] <= 50:
            state.menu_placement = "main_game"
        elif 100 <= state.position[1] <= 150:
            state.menu_placement = "main_menu"
            with open(path.join(SAVES_FOLDER, state.save_file_name + ".txt"), "w", encoding="utf-8") as file:
                chunks_json = dumps(serialize_chunks(chunks))
                file.write(f"{chunks_json};{state.location['tile']};{state.tick};{state.location['room']};{state.noise_offset}")
            state.save_file_name = ""
    elif state.menu_placement == "options_main":
        if 0 <= state.position[1] <= 50:
            state.menu_placement = "main_menu"
    if 200 <= state.position[1] <= 250:
        state.menu_placement = "controls_options"