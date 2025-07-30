import pygame as pg

def update_keys(menu_placement, save_file_name, controls, control_adjusted):
    keys = pg.key.get_pressed()
    if menu_placement == "save_creation":
        for letter in range(48, 123):
            if keys[letter]:
                save_file_name += chr(letter)
        if keys[pg.K_SPACE]:
            save_file_name += " "
        elif keys[pg.K_BACKSPACE]:
            save_file_name = save_file_name[:-1]

    elif menu_placement == "controls_options":
        for key_code in range(len(keys)):
            if keys[key_code]:
                controls[control_adjusted] = key_code
    return save_file_name, controls