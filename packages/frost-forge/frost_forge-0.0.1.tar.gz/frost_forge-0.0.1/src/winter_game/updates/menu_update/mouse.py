from .load_save import save_loading
from .create_save import save_creating
from .options import option

def update_mouse(state, event, chunks):
    if state.menu_placement == "load_save":
        chunks = save_loading(state, chunks)
    elif state.menu_placement == "save_creation" and len(state.save_file_name) > 0:
        chunks = save_creating(state, chunks)
    elif state.menu_placement.startswith("options"):
        option(state, chunks)

    elif state.menu_placement == "main_menu":
        if 0 <= state.position[1] <= 50:
            state.menu_placement = "load_save"
        elif 100 <= state.position[1] <= 150:
            state.menu_placement = "options_main"
        elif 200 <= state.position[1] <= 250:
            state.run = False

    elif state.menu_placement == "controls_options":
        if 0 <= state.position[1] <= 50:
            state.menu_placement = "options_game" if len(state.save_file_name) else "options_main"
        if event.button == 4:
            state.control_adjusted = (state.control_adjusted - 1) % len(state.controls)
        elif event.button == 5:
            state.control_adjusted = (state.control_adjusted + 1) % len(state.controls)
    return chunks